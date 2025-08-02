from copy import deepcopy
from typing import Annotated, Dict, Literal, NamedTuple, Sequence
import logging

from hikari.dataframes import BaseFrame, CifFrame
from numpy.linalg import norm
import numpy as np
import numpy.typing as npt
import pandas as pd
import uncertainties.unumpy as unp

from picometer.shapes import (are_synparallel, degrees_between, Line,
                              Plane, Shape, Vector3)
from picometer.utility import norm, ustr2float, ustr2ufloats


try:
    from hikari.symmetry import Operation
except ImportError:  # hikari version < 0.3.0
    from hikari.symmetry import SymmOp as Operation


UFloatArray = npt.NDArray[np.object_]
UFloatArray3x3 = Annotated[npt.NDArray[np.object_], Literal[3, 3]]
UFloatArrayNx3 = Annotated[npt.NDArray[np.object_], Literal['N', 3]]
UFloatArrayNx3x3 = Annotated[npt.NDArray[np.object_], Literal['N', 3, 3]]


logger = logging.getLogger(__name__)



class Locator(NamedTuple):
    label: str
    symm: str = 'x,y,z'
    at: 'Sequence[Locator]' = None

    @classmethod
    def from_dict(cls, d: dict) -> 'Locator':
        symm = d.get('symm')
        at = d.get('at')
        return Locator(label=d['label'],
                       symm=symm if symm else 'x,y,z',
                       at=at if at else None)

    def __bool__(self):
        return self.label is not None


group_registry: Dict[str, list[Locator]] = {}


class AtomSet(Shape):
    """Container class w/ atoms stored in pd.Dataframe & convenience methods"""

    kind = Shape.Kind.spatial

    def __init__(self,
                 base: BaseFrame = None,
                 table: pd.DataFrame = None,
                 ) -> None:
        self.base = base
        self.table = table
        logger.debug(f'Created AtomSet with {base!r} and {len(self)}-elements')

    def __len__(self) -> int:
        return len(self.table) if self.table is not None else 0

    def __add__(self, other) -> 'AtomSet':
        if not (self.base or self.table):
            return other
        elif not (other.base or other.table):
            return self
        return self.copy(table=pd.concat([self.table, other.table], axis=0))

    def __getitem__(self, key: str) -> 'AtomSet':
        """A slice of self with subset of atoms selected with label or regex."""
        mask = self.table.index == key
        if not any(mask):  # noqa: mask will in fact be Iterable
            mask = self.table.index.str.match(key)
        logger.debug(f'Selected {sum(mask)} atoms with {key=}')
        return self.copy(table=deepcopy(self.table[mask]))

    @classmethod
    def from_cif(cls, cif_path: str, block_name: str = None) -> 'AtomSet':
        """Initialize from cif file using hikari's `BaseFrame` and `CifFrame`"""
        bf = BaseFrame()
        cf = CifFrame()
        cf.read(cif_path)
        block_name = block_name if block_name else list(cf.keys())[0]
        cb = cf[block_name]
        bf.edit_cell(a=ustr2float(cb['_cell_length_a']),
                     b=ustr2float(cb['_cell_length_b']),
                     c=ustr2float(cb['_cell_length_c']),
                     al=ustr2float(cb['_cell_angle_alpha']),
                     be=ustr2float(cb['_cell_angle_beta']),
                     ga=ustr2float(cb['_cell_angle_gamma']))

        atoms = pd.DataFrame()

        atom_labels = cb.get('_atom_site_label', [])
        atom_xs = ustr2ufloats(cb.get('_atom_site_fract_x', []))
        atom_ys = ustr2ufloats(cb.get('_atom_site_fract_y', []))
        atom_zs = ustr2ufloats(cb.get('_atom_site_fract_z', []))
        atom_u_isos = ustr2ufloats(cb.get('_atom_site_U_iso_or_equiv', []))
        for label, x, y, z in zip(atom_labels, atom_xs, atom_ys, atom_zs):
            atoms.loc[label, ['x', 'y', 'z']] = [x, y, z]
        for label, u_iso in zip(atom_labels, atom_u_isos):
            atoms.loc[label, 'Uiso'] = u_iso

        atom_labels = cb.get('_atom_site_aniso_label', [])
        atom_u11s = ustr2ufloats(cb.get('_atom_site_aniso_U_11', []))
        atom_u22s = ustr2ufloats(cb.get('_atom_site_aniso_U_22', []))
        atom_u33s = ustr2ufloats(cb.get('_atom_site_aniso_U_33', []))
        atom_u12s = ustr2ufloats(cb.get('_atom_site_aniso_U_12', []))
        atom_u13s = ustr2ufloats(cb.get('_atom_site_aniso_U_13', []))
        atom_u23s = ustr2ufloats(cb.get('_atom_site_aniso_U_23', []))
        atom_us = zip(atom_u11s, atom_u22s, atom_u33s, atom_u12s, atom_u13s, atom_u23s)
        for label, us in zip(atom_labels, atom_us):
            atoms.loc[label, ['U11', 'U22', 'U33', 'U12', 'U13', 'U23']] = list(us)

        return AtomSet(base=bf, table=atoms)

    @property
    def fract_xyz(self) -> UFloatArrayNx3:
        """A 3xN numpy array with the fractional coordinates as UFloats."""
        return np.vstack([self.table[k].to_numpy() for k in 'xyz'])

    @property
    def cart_xyz(self) -> UFloatArrayNx3:
        return self.orthogonalise(self.fract_xyz)

    @property
    def fract_uij(self) -> UFloatArrayNx3x3:
        """Return a 3D array i.e. stack of 3x3 fract. displacement tensors."""
        t = self.table
        default = pd.Series([np.nan] * len(t), index=t.index)
        uij = np.zeros((len(t), 3, 3), dtype=np.object_)
        uij[:, 0, 0] = t.get('U11', default)
        uij[:, 1, 1] = t.get('U22', default)
        uij[:, 2, 2] = t.get('U33', default)
        uij[:, 0, 1] = uij[:, 1, 0] = t.get('U12', default)
        uij[:, 0, 2] = uij[:, 2, 0] = t.get('U13', default)
        uij[:, 1, 2] = uij[:, 2, 1] = t.get('U23', default)
        return uij

    def copy(self, **kwargs) -> 'AtomSet':
        """A deep copy of self with some attr replaced via kwargs if needed"""
        attr_names = ('base', 'table')
        new = {n: kwargs.get(n, deepcopy(getattr(self, n))) for n in attr_names}
        return self.__class__(**new)

    def fractionalise(self, cart_xyz: UFloatArrayNx3) -> UFloatArrayNx3:
        """Multiply 3xN vector by crystallographic matrix to get fract coord"""
        return np.linalg.inv(self.base.A_d.T) @ cart_xyz  # noqa: float @ ufloat

    def orthogonalise(self, fract_xyz: UFloatArrayNx3) -> UFloatArrayNx3:
        """Multiply 3xN vector by crystallographic matrix to get Cart. coord"""
        return self.base.A_d.T @ fract_xyz

    def locate(self, locators: Sequence[Locator]) -> 'AtomSet':
        """Convenience method to select multiple fragments from locators
        while interpreting and extending groups if necessary"""
        logger.debug(f'Locate {locators} in {self}')
        new = AtomSet(base=self.base)
        assert len(locators) == 0 or isinstance(locators[0], Locator)
        for label, symm_op_code, at in locators:
            if label in group_registry:
                new2 = self.locate(locators=group_registry[label])
            else:
                new2 = self[label]
            new2 = new2.transform(symm_op_code)
            if at:
                new2.origin = self.locate(at).origin
            new += new2
        return new

    def transform(self, symm_op_code: str) -> 'AtomSet':
        transformation = Operation.from_code(symm_op_code)
        fract_xyz = transformation.transform(self.fract_xyz.T)
        transformed = deepcopy(self.table)
        transformed['x'] = fract_xyz[:, 0]
        transformed['y'] = fract_xyz[:, 1]
        transformed['z'] = fract_xyz[:, 2]
        if {'U11', 'U22', 'U33', 'U12', 'U13', 'U23'}.issubset(transformed.columns):
            uij = self.fract_uij  # shape: (n_atoms, 3, 3)
            isnan = np.vectorize(lambda x: isinstance(x, float) and np.isnan(x))
            mask = ~isnan(uij).all(axis=(1, 2))
            if np.any(mask):
                uij_rot = (s := transformation.tf) @ uij[mask] @ s.T
                transformed.loc[mask, 'U11'] = uij_rot[:, 0, 0]
                transformed.loc[mask, 'U22'] = uij_rot[:, 1, 1]
                transformed.loc[mask, 'U33'] = uij_rot[:, 2, 2]
                transformed.loc[mask, 'U12'] = uij_rot[:, 0, 1]
                transformed.loc[mask, 'U13'] = uij_rot[:, 0, 2]
                transformed.loc[mask, 'U23'] = uij_rot[:, 1, 2]
        return self.copy(table=transformed)

    @property
    def u_cartesian_eigenvalues(self):
        u_columns = ['U11', 'U12', 'U13', 'U22', 'U23', 'U33']
        eigenvalues = np.full((len(self), 3), np.nan)
        if not set(u_columns).issubset(self.table.keys()):
            return eigenvalues
        u_fract = self.fract_uij  # Nx3n3 stack of abc-normalized U_cif tensors
        a_mat = self.base.A_d.T  # fractional to orthogonal cartesian metric
        n_mat = np.diag([self.base.a_r, self.base.b_r, self.base.c_r])
        u_star = (n_mat @ u_fract) @ n_mat  # eq. 4b @ S0021889802008580
        u_cart = (a_mat @ u_star) @ a_mat.T  # eq. 3a @ S0021889802008580
        mask = ~self.table[u_columns].isna().any(axis=1)
        eigenvalues[mask, :] = np.linalg.eigh(unp.nominal_values(u_cart[mask, :, :]))[0]
        return eigenvalues

    @property
    def centroid(self) -> np.ndarray:
        """A 3-vector with average atom position."""
        return self.cart_xyz.T.mean(axis=0)

    @property
    def direction(self) -> Vector3:
        return None

    @property
    def line(self) -> Line:
        """A 3-vector describing line that best fits the cartesian
        coordinates of atoms. Based on https://stackoverflow.com/q/2298390/"""
        uu, dd, vv = np.linalg.svd(unp.nominal_values(self.cart_xyz.T - self.centroid))
        return Line(direction=vv[0], origin=self.centroid)

    @property
    def plane(self) -> Plane:
        """A 3-vector normal to plane that best fits atoms' cartesian coords.
        Based on https://gist.github.com/amroamroamro/1db8d69b4b65e8bc66a6"""
        uu, dd, vv = np.linalg.svd(unp.nominal_values((self.cart_xyz.T - self.centroid).T))  # TODO
        return Plane(direction=uu[:, -1], origin=self.centroid)

    @property
    def origin(self) -> Vector3:
        return self.centroid

    @origin.setter
    def origin(self, new_origin) -> None:
        """Change origin to the new one provided in cartesian coordinates"""
        new_origin_fract = self.fractionalise(new_origin)
        delta = new_origin_fract - self.fractionalise(self.centroid)
        self.table['x'] += delta[0]
        self.table['y'] += delta[1]
        self.table['z'] += delta[2]
        assert np.allclose(unp.nominal_values(new_origin),
                           unp.nominal_values(self.centroid))

    def _angle(self, *others: 'Shape') -> float:
        assert all(o.kind is o.Kind.spatial for o in [self, *others])
        combined = sum(others, self)
        xyz = combined.cart_xyz.T
        assert len(combined) == 3, 'Input AtomSet must contain exactly 3 atoms'
        return degrees_between(xyz[0] - xyz[1], xyz[2] - xyz[1])

    def _distance(self, other: 'Shape') -> float:
        if other.kind is self.Kind.spatial:
            # https://stackoverflow.com/a/43359192/8279065 bloody brilliant
            other: 'AtomSet'
            xy1, xy2 = self.cart_xyz.T, other.cart_xyz.T
            p = np.add.outer(np.sum(xy1**2, axis=1), np.sum(xy2**2, axis=1))
            n = np.dot(xy1, xy2.T)
            return np.min(unp.sqrt(p - 2 * n))
        elif other.kind is self.Kind.planar:
            deltas = self.cart_xyz.T - other.origin
            return min(np.abs(np.dot(deltas, other.direction)))
        else:  # if other.kind is self.Kind.axial:
            deltas = self.cart_xyz.T - other.origin
            norms = np.array([norm(row) for row in deltas])
            # norms = norm(deltas, axis=1)
            along = np.abs(np.dot(deltas, other.direction))
            return min(norms ** 2 - along ** 2)

    def dihedral(self, *others: 'AtomSet') -> float:
        assert all(o.kind is o.Kind.spatial for o in [self, *others])
        combined = sum(others, self)
        xyz = combined.cart_xyz.T
        assert len(combined) == 4, 'Input AtomSet must contain exactly 4 atoms'
        plane1_dir = np.cross(xyz[0] - xyz[1], xyz[2] - xyz[1])
        plane2_dir = np.cross(xyz[-3] - xyz[-2], xyz[-1] - xyz[-2])
        twist_dir = np.cross(plane1_dir, plane2_dir)
        sign = +1 if are_synparallel(twist_dir, xyz[2] - xyz[1]) else -1
        return sign * degrees_between(plane1_dir, plane2_dir, normalize=False)
