from copy import deepcopy

import hikari.symmetry
from hikari.dataframes import BaseFrame, CifFrame
import numpy as np
import pandas as pd
from typing import Dict

from picometer.utility import ustr2float


class AtomSet:
    """Container class w/ atoms stored in pd.Dataframe & convenience methods"""

    def __init__(self,
                 bf: BaseFrame = None,
                 atoms: pd.DataFrame = None,
                 ) -> None:
        self.base = bf
        self.atoms = atoms

    def __len__(self):
        return len(self.atoms.index)

    def __add__(self, other):
        if not (self.base or self.atoms):
            return other
        elif not (other.base or other.atoms):
            return self
        return AtomSet(self.base, pd.concat([self.atoms, other.atoms], axis=0))

    @classmethod
    def from_cif(cls, cif_path: str) -> 'AtomSet':
        bf = BaseFrame()
        cf = CifFrame()
        cf.read(cif_path)
        first_block_name = list(cf.keys())[0]
        cb = cf[first_block_name]
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
    def atomized(self) -> Dict[str, 'AtomSet']:
        """Split the single atomset into multiple single-atom ones"""
        return {a: AtomSet(self.base, self.atoms.loc[:, a])
                for a in self.atoms.index}

    @property
    def fract_xyz(self):
        return np.vstack([self.atoms['fract_' + k].to_numpy() for k in 'xyz'])

    @property
    def cart_xyz(self):
        return self.orthogonalise(self.fract_xyz)

    def fractionalise(self, cart_xyz: np.ndarray) -> np.ndarray:
        """Multiply 3xN vector by crystallographic matrix to get fract coord"""
        return np.linalg.inv(self.base.A_d.T) @ cart_xyz

    def orthogonalise(self, fract_xyz: np.ndarray) -> np.ndarray:
        """Multiply 3xN vector by crystallographic matrix to get Cart. coord"""
        return self.base.A_d.T @ fract_xyz

    def select_atom(self, label_regex: str) -> 'AtomSet':
        mask = self.atoms.index.str.match(label_regex)
        return self.__class__(self.base, deepcopy(self.atoms[mask]))

    def transform(self, symm_op: hikari.symmetry.SymmOp) -> 'AtomSet':
        fract_xyz = symm_op.transform(self.fract_xyz.T)
        data = deepcopy(self.atoms)
        data['fract_x'] = fract_xyz[:, 0]
        data['fract_y'] = fract_xyz[:, 1]
        data['fract_z'] = fract_xyz[:, 2]
        return self.__class__(self.base, data)

    def transform2(self, symm_op_code: str) -> 'AtomSet':
        symm_op = hikari.symmetry.SymmOp.from_code(symm_op_code)
        return self.transform(symm_op)

    @property
    def centroid(self):
        """A 3-vector with average atom position."""
        return self.cart_xyz.T.mean(axis=0)

    @property
    def line(self):
        """A 3-vector describing line that best fits the cartesian
        coordinates of atoms. Based on https://stackoverflow.com/q/2298390/"""
        cart_xyz = self.cart_xyz.T
        uu, dd, vv = np.linalg.svd(cart_xyz - self.centroid)
        return vv[0]

    @property
    def plane(self):
        """A 3-vector normal to plane that best fits atoms' cartesian coords.
        Based on https://gist.github.com/amroamroamro/1db8d69b4b65e8bc66a6"""
        cart_xyz = self.cart_xyz.T
        uu, dd, vv = np.linalg.svd((cart_xyz - self.centroid).T)
        return uu[:, -1]
