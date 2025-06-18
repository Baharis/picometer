from copy import deepcopy
import logging
from typing import Dict, NamedTuple, List, Sequence

from hikari.dataframes import BaseFrame, CifFrame
from numpy.linalg import norm
import numpy as np
import pandas as pd

from picometer.shapes import (are_synparallel, degrees_between, Line,
                              Plane, Shape, Vector3)
from picometer.utility import ustr2float, ustr2floats


try:
    from hikari.symmetry import Operation
except ImportError:  # hikari version < 0.3.0
    from hikari.symmetry import SymmOp as Operation


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


group_registry: Dict[str, List[Locator]] = {}


class AtomSet(Shape):
    """Container class w/ atoms stored in pd.Dataframe & convenience methods"""

    kind = Shape.Kind.spatial

    def __init__(self,
                 bf: BaseFrame = None,
                 table: pd.DataFrame = None,
                 ) -> None:

        logger.debug(f'Created atom set with {bf!r} and '
                     f'{len(table) if table is not None else 0}-element table')
        self.base = bf
        self.table = table

    def __len__(self) -> int:
        return len(self.table) if self.table is not None else 0

    def __add__(self, other) -> 'AtomSet':
        if not (self.base or self.table):
            return other
        elif not (other.base or other.table):
            return self
        return self.__class__(self.base, pd.concat([self.table, other.table], axis=0))

    def __getitem__(self, item) -> 'AtomSet':
        return self.__class__(bf=self.base, table=self.table[item])

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
        atom_xs = ustr2floats(cb.get('_atom_site_fract_x', []))
        atom_ys = ustr2floats(cb.get('_atom_site_fract_y', []))
        atom_zs = ustr2floats(cb.get('_atom_site_fract_z', []))
        atom_u_isos = ustr2floats(cb.get('_atom_site_U_iso_or_equiv', []))
        for label, x, y, z in zip(atom_labels, atom_xs, atom_ys, atom_zs):
            atoms.loc[label, ['fract_x', 'fract_y', 'fract_z']] = [x, y, z]
        for label, u_iso in zip(atom_labels, atom_u_isos):
            atoms.loc[label, 'Uiso'] = u_iso

        atom_labels = cb.get('_atom_site_aniso_label', [])
        atom_u11s = ustr2floats(cb.get('_atom_site_aniso_U_11', []))
        atom_u22s = ustr2floats(cb.get('_atom_site_aniso_U_22', []))
        atom_u33s = ustr2floats(cb.get('_atom_site_aniso_U_33', []))
        atom_u12s = ustr2floats(cb.get('_atom_site_aniso_U_12', []))
        atom_u13s = ustr2floats(cb.get('_atom_site_aniso_U_13', []))
        atom_u23s = ustr2floats(cb.get('_atom_site_aniso_U_23', []))
        atom_us = zip(atom_u11s, atom_u22s, atom_u33s, atom_u12s, atom_u13s, atom_u23s)
        for label, us in zip(atom_labels, atom_us):
            atoms.loc[label, ['U11', 'U22', 'U33', 'U12', 'U13', 'U23']] = list(us)

        for col in atoms.columns:
            atoms[col] = pd.to_numeric(atoms[col], errors='coerce')
        return AtomSet(bf, atoms)

    @property
    def fract_xyz(self) -> np.ndarray:
        return np.vstack([self.table['fract_' + k].to_numpy() for k in 'xyz'])

    @property
    def cart_xyz(self) -> np.ndarray:
        return self.orthogonalise(self.fract_xyz)

    def fractionalise(self, cart_xyz: np.ndarray) -> np.ndarray:
        """Multiply 3xN vector by crystallographic matrix to get fract coord"""
        return np.linalg.inv(self.base.A_d.T) @ cart_xyz

    def orthogonalise(self, fract_xyz: np.ndarray) -> np.ndarray:
        """Multiply 3xN vector by crystallographic matrix to get Cart. coord"""
        return self.base.A_d.T @ fract_xyz

    def locate(self, locators: Sequence[Locator]) -> 'AtomSet':
        """Convenience method to select multiple fragments from locators
        while interpreting and extending groups if necessary"""
        logger.debug(f'Locate {locators} in {self}')
        new = AtomSet()
        assert len(locators) == 0 or isinstance(locators[0], Locator)
        for label, symm_op_code, at in locators:
            if label in group_registry:
                new2 = self.locate(locators=group_registry[label])
            else:
                new2 = self.select_atom(label_regex=label)
            new2 = new2.transform(symm_op_code)
            if at:
                new2.origin = self.locate(at).origin
            new += new2
        return new

    def select_atom(self, label_regex: str) -> 'AtomSet':
        mask = self.table.index == label_regex
        if not any(mask):  # noqa: mask will in fact be Iterable
            mask = self.table.index.str.match(label_regex)
        logger.debug(f'Selected {sum(mask)} atoms with {label_regex=}')
        return self.__class__(self.base, deepcopy(self.table[mask]))

    def transform(self, symm_op_code: str) -> 'AtomSet':
        symm_op = Operation.from_code(symm_op_code)
        fract_xyz = symm_op.transform(self.fract_xyz.T)
        data = deepcopy(self.table)
        data['fract_x'] = fract_xyz[:, 0]
        data['fract_y'] = fract_xyz[:, 1]
        data['fract_z'] = fract_xyz[:, 2]
        return self.__class__(self.base, data)

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
        cart_xyz = self.cart_xyz.T
        uu, dd, vv = np.linalg.svd(cart_xyz - self.centroid)
        return Line(direction=vv[0], origin=self.centroid)

    @property
    def plane(self) -> Plane:
        """A 3-vector normal to plane that best fits atoms' cartesian coords.
        Based on https://gist.github.com/amroamroamro/1db8d69b4b65e8bc66a6"""
        cart_xyz = self.cart_xyz.T
        uu, dd, vv = np.linalg.svd((cart_xyz - self.centroid).T)
        return Plane(direction=uu[:, -1], origin=self.centroid)

    @property
    def origin(self) -> Vector3:
        return self.centroid

    @origin.setter
    def origin(self, new_origin) -> None:
        """Change origin to the new one provided in cartesian coordinates"""
        new_origin_fract = self.fractionalise(new_origin)
        delta = new_origin_fract - self.fractionalise(self.centroid)
        self.table['fract_x'] += delta[0]
        self.table['fract_y'] += delta[1]
        self.table['fract_z'] += delta[2]
        assert np.allclose(new_origin, self.centroid)

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
            return np.min(np.sqrt(p - 2 * n))
        elif other.kind is self.Kind.planar:
            deltas = self.cart_xyz.T - other.origin
            return min(np.abs(np.dot(deltas, other.direction)))
        else:  # if other.kind is self.Kind.axial:
            deltas = self.cart_xyz.T - other.origin
            norms = norm(deltas, axis=1)
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
