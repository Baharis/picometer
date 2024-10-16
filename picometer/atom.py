from copy import deepcopy
import logging
from typing import Dict, NamedTuple, List, Sequence

import hikari.symmetry
from hikari.dataframes import BaseFrame, CifFrame
import numpy as np
from numpy.linalg import norm
import pandas as pd

from picometer.shapes import degrees_between, Line, Plane, Shape, Vector3, are_synparallel
from picometer.utility import ustr2float


log = logging.getLogger(__name__)


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
        return self.label and self.label != 'None'


group_registry: Dict[str, List[Locator]] = {}


class AtomSet(Shape):
    """Container class w/ atoms stored in pd.Dataframe & convenience methods"""

    kind = Shape.Kind.spatial

    def __init__(self,
                 bf: BaseFrame = None,
                 table: pd.DataFrame = None,
                 ) -> None:
        log.debug(f'Init AtomSet with {bf!r} and {table!r}')
        self.base = bf
        self.table = table

    def __len__(self):
        return len(self.table) if self.table is not None else 0

    def __add__(self, other):
        if not (self.base or self.table):
            return other
        elif not (other.base or other.table):
            return self
        return AtomSet(self.base, pd.concat([self.table, other.table], axis=0))

    def __getitem__(self, item) -> 'AtomSet':
        return self.__class__(bf=self.base, table=self.table[item])

    @classmethod
    def from_cif(cls, cif_path: str, block_name: str = None) -> 'AtomSet':
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
        try:
            atoms_dict = {
                'label': cb['_atom_site_label'],
                'fract_x': [ustr2float(v) for v in cb['_atom_site_fract_x']],
                'fract_y': [ustr2float(v) for v in cb['_atom_site_fract_y']],
                'fract_z': [ustr2float(v) for v in cb['_atom_site_fract_z']],
            }
            atoms = pd.DataFrame.from_records(atoms_dict).set_index('label')
        except KeyError:
            atoms = pd.DataFrame()
        return AtomSet(bf, atoms)

    @property
    def fract_xyz(self):
        return np.vstack([self.table['fract_' + k].to_numpy() for k in 'xyz'])

    @property
    def cart_xyz(self):
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
        log.debug(f'Locate {locators} in {self}')
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
        if not any(mask):
            mask = self.table.index.str.match(label_regex)
        log.debug(f'Selected {sum(mask)} atoms with {label_regex=}')
        return self.__class__(self.base, deepcopy(self.table[mask]))

    def transform(self, symm_op_code: str) -> 'AtomSet':
        symm_op = hikari.symmetry.SymmOp.from_code(symm_op_code)
        fract_xyz = symm_op.transform(self.fract_xyz.T)
        data = deepcopy(self.table)
        data['fract_x'] = fract_xyz[:, 0]
        data['fract_y'] = fract_xyz[:, 1]
        data['fract_z'] = fract_xyz[:, 2]
        return self.__class__(self.base, data)

    @property
    def centroid(self):
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
    def origin(self, new_origin):
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
        if len(combined) == 3:  # interior angle
            return degrees_between(xyz[0] - xyz[1], xyz[2] - xyz[1])
        elif 4 <= len(combined) <= 6:  # dihedral angle
            plane1_dir = np.cross(xyz[0] - xyz[1], xyz[2] - xyz[1])
            plane2_dir = np.cross(xyz[-3] - xyz[-2], xyz[-1] - xyz[-2])
            twist_dir = np.cross(plane1_dir, plane2_dir)
            sign = +1 if are_synparallel(twist_dir, xyz[2] - xyz[1]) else -1
            return sign * degrees_between(plane1_dir, plane2_dir, normalize=False)
        else:
            return 'Input AtomSet must contain between 3 and 6 atoms'

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
