from pathlib import Path
from typing import Any, Callable, Iterable, Optional
import re

from picometer.utility import AnyPath, ustr2float, ustr2floats, ustr2ufloats

from hikari.dataframes import BaseFrame, CifBlock, CifFrame
import numpy as np
import pandas as pd
import uncertainties as uc


# warnings.filterwarnings("ignore", message="Using UFloat objects with std_dev==0.*")

CovLoader = Callable[[AnyPath], pd.DataFrame]
Ustr2xsFunc = Callable[[Iterable[str]], list[Any]]


def matrix_triu2symm(vector: np.ndarray) -> np.ndarray:
    """Convert a vector with upper-triangular info into symmetric matrix."""
    n = np.floor(np.sqrt(2 * len(vector)))  # because n < √n(n+1) = 2*len < n+1
    symmetric_matrix = np.zeros((n, n))
    symmetric_matrix[np.triu_indices(n)] = vector
    symmetric_matrix += np.triu(symmetric_matrix, 1).T
    return symmetric_matrix


class StructuralDataLoader:
    """Handle loading the crystal structure from .cif and covariance files."""

    def __init__(self, cif: Optional[CifBlock] = None, cov: Optional[pd.DataFrame] = None) -> None:
        """Reads & handles cif and covariance matrix (as a symmetric df)."""
        self.cif: Optional[CifBlock] = cif
        self.cov: Optional[pd.DataFrame] = cov

    def get_base(self) -> BaseFrame:
        base_frame = BaseFrame()
        a = ustr2float(self.cif['_cell_length_a'])
        b = ustr2float(self.cif['_cell_length_b'])
        c = ustr2float(self.cif['_cell_length_c'])
        al = ustr2float(self.cif['_cell_angle_alpha'])
        be = ustr2float(self.cif['_cell_angle_beta'])
        ga = ustr2float(self.cif['_cell_angle_gamma'])
        base_frame.edit_cell(a=a, b=b, c=c, al=al, be=be, ga=ga)
        return base_frame

    def _get_atoms(self, ustr2xs_func: Ustr2xsFunc) -> pd.DataFrame:
        c = self.cif
        atoms = pd.DataFrame()
        atom_labels = c.get('_atom_site_label', [])
        atom_xs = ustr2xs_func(c.get('_atom_site_fract_x', []))
        atom_ys = ustr2xs_func(c.get('_atom_site_fract_y', []))
        atom_zs = ustr2xs_func(c.get('_atom_site_fract_z', []))
        atom_u_isos = ustr2xs_func(c.get('_atom_site_U_iso_or_equiv', []))
        for label, x, y, z in zip(atom_labels, atom_xs, atom_ys, atom_zs):
            atoms.loc[label, ['x', 'y', 'z']] = [x, y, z]
        for label, u_iso in zip(atom_labels, atom_u_isos):
            atoms.loc[label, 'Uiso'] = u_iso
        atom_labels = c.get('_atom_site_aniso_label', [])
        atom_u11s = ustr2xs_func(c.get('_atom_site_aniso_U_11', []))
        atom_u22s = ustr2xs_func(c.get('_atom_site_aniso_U_22', []))
        atom_u33s = ustr2xs_func(c.get('_atom_site_aniso_U_33', []))
        atom_u12s = ustr2xs_func(c.get('_atom_site_aniso_U_12', []))
        atom_u13s = ustr2xs_func(c.get('_atom_site_aniso_U_13', []))
        atom_u23s = ustr2xs_func(c.get('_atom_site_aniso_U_23', []))
        atom_us = zip(atom_u11s, atom_u22s, atom_u33s, atom_u12s, atom_u13s, atom_u23s)
        for label, us in zip(atom_labels, atom_us):
            atoms.loc[label, ['U11', 'U22', 'U33', 'U12', 'U13', 'U23']] = list(us)
        return atoms

    def get_atoms_certain(self) -> pd.DataFrame:
        """Produce a dataframe with atom parameters as certain Python floats"""
        return self._get_atoms(ustr2xs_func=ustr2floats)

    def get_atoms_uncorrelated(self) -> pd.DataFrame:
        """Produce a dataframe with atom parameters as uncorrelated UFloats"""
        return self._get_atoms(ustr2xs_func=ustr2ufloats)

    def get_atoms_correlated(self) -> pd.DataFrame:
        """Produce a dataframe with atom parameters as correlated UFloats"""
        atoms = self.get_atoms_uncorrelated()
        cov_labels = list(self.cov.columns)
        cov_matrix = self.cov.to_numpy()
        correlated_values = []
        atoms_params = [label.rsplit('.', 2) for label in cov_labels]
        for label, (atom, param) in zip(cov_labels, atoms_params):
            correlated_values.append(atoms.at[param, atom].nominal_value)
        correlated = uc.correlated_values(correlated_values, cov_matrix)
        for corr, (atom, param) in zip(correlated, atoms_params):
            atoms[param, atom] = corr
        return atoms

    def covariance_star_to_cif(self, cov: pd.DataFrame) -> pd.DataFrame:
        """Scale Uij in cov. matrix by N-1 (10.1107/S0021889802008580, 4a)."""
        scaled = cov.copy()
        base = self.get_base()
        n_matrix_diag = (1 / base.a_r, 1 / base.b_r, 1 / base.c_r)
        covariance_u_scaling_factors = {
            'u11': n_matrix_diag[0] * n_matrix_diag[0],
            'u22': n_matrix_diag[1] * n_matrix_diag[1],
            'u33': n_matrix_diag[2] * n_matrix_diag[2],
            'u12': n_matrix_diag[0] * n_matrix_diag[1],
            'u13': n_matrix_diag[0] * n_matrix_diag[2],
            'u23': n_matrix_diag[1] * n_matrix_diag[2],
        }
        for suffix, scaling_factor in covariance_u_scaling_factors.items():
            mask = scaled.columns.str.endswith(suffix)
            scaled[:, mask] *= scaling_factor
            scaled[mask, :] *= scaling_factor
        scaled_labels = [re.sub(r'\.u(\d\d)$', r'U\1', c) for c in scaled.index]
        scaled.columns = scaled_labels
        scaled.index = scaled_labels
        return scaled

    def load_cif(self, path: AnyPath, block: Optional[str] = None) -> None:
        cif_frame = CifFrame()
        cif_frame.read(str(path))
        block_name = block if block else list(cif_frame.keys())[0]
        self.cif: CifBlock = cif_frame[block_name]

    def load_cov(self, path: AnyPath) -> None:
        """Covariance matrix that could be read using one of `COV_LOADERS`."""
        for cov_loader in [self.load_cov_olex2]:
            try:
                cov_loader(path)
            except IOError:
                pass
            else:
                return
        raise RuntimeError('Could not load covariance matrix using any of the loaders')

    def load_cov_olex2(self, path: AnyPath) -> None:
        with open(Path(path), "rb") as npy_file:
            first_line = npy_file.readline()
            assert first_line == b"VCOV\n", f'Incorrect file format: {npy_file}'
            labels = [a.decode('UTF-8') for a in npy_file.readline().split()]
            covariance_matrix = matrix_triu2symm(vector=np.load(npy_file))
        assert len(labels) == covariance_matrix.shape[0], 'Inconsistent matrix size'
        cov = pd.DataFrame(covariance_matrix, index=labels, columns=labels)
        self.cov = self.covariance_star_to_cif(cov)










