from pathlib import Path
from typing import Optional
import re

from utility import ustr2float, ustr2ufloats

from hikari.dataframes import BaseFrame, CifBlock, CifFrame
import numpy as np
import pandas as pd
import uncertainties as uc


def matrix_triu2symm(vector: np.ndarray) -> np.ndarray:
    """Convert a vector with upper-triangular info into symmetric matrix."""
    n = np.floor(np.sqrt(2 * len(vector)))  # because n < √n(n+1) = 2*len < n+1
    symmetric_matrix = np.zeros((n, n))
    symmetric_matrix[np.triu_indices(n)] = vector
    symmetric_matrix += np.triu(symmetric_matrix, 1).T
    return symmetric_matrix


class StructuralDataLoader:
    def __init__(self):
        """Reads & handles cif and covariance matrix (as a symmetric df)."""
        self.cif: Optional[CifBlock] = None
        self.cov: Optional[pd.DataFrame] = None

    @property
    def base(self) -> BaseFrame:
        base_frame = BaseFrame()
        a = ustr2float(self.cif['_cell_length_a'])
        b = ustr2float(self.cif['_cell_length_b'])
        c = ustr2float(self.cif['_cell_length_c'])
        al = ustr2float(self.cif['_cell_angle_alpha'])
        be = ustr2float(self.cif['_cell_angle_beta'])
        ga = ustr2float(self.cif['_cell_angle_gamma'])
        base_frame.edit_cell(a=a, b=b, c=c, al=al, be=be, ga=ga)
        return base_frame

    @property
    def atoms_uncorrelated(self) -> pd.DataFrame:
        """Produce a dataframe with atom parameters as uncorrelated UFloats"""
        c = self.cif
        atoms = pd.DataFrame()
        atom_labels = c.get('_atom_site_label', [])
        atom_xs = ustr2ufloats(c.get('_atom_site_fract_x', []))
        atom_ys = ustr2ufloats(c.get('_atom_site_fract_y', []))
        atom_zs = ustr2ufloats(c.get('_atom_site_fract_z', []))
        atom_u_isos = ustr2ufloats(c.get('_atom_site_U_iso_or_equiv', []))
        for label, x, y, z in zip(atom_labels, atom_xs, atom_ys, atom_zs):
            atoms.loc[label, ['x', 'y', 'z']] = [x, y, z]
        for label, u_iso in zip(atom_labels, atom_u_isos):
            atoms.loc[label, 'Uiso'] = u_iso
        atom_labels = c.get('_atom_site_aniso_label', [])
        atom_u11s = ustr2ufloats(c.get('_atom_site_aniso_U_11', []))
        atom_u22s = ustr2ufloats(c.get('_atom_site_aniso_U_22', []))
        atom_u33s = ustr2ufloats(c.get('_atom_site_aniso_U_33', []))
        atom_u12s = ustr2ufloats(c.get('_atom_site_aniso_U_12', []))
        atom_u13s = ustr2ufloats(c.get('_atom_site_aniso_U_13', []))
        atom_u23s = ustr2ufloats(c.get('_atom_site_aniso_U_23', []))
        atom_us = zip(atom_u11s, atom_u22s, atom_u33s, atom_u12s, atom_u13s, atom_u23s)
        for label, us in zip(atom_labels, atom_us):
            atoms.loc[label, ['U11', 'U22', 'U33', 'U12', 'U13', 'U23']] = list(us)
        return atoms

    @property
    def correlated_atoms(self) -> pd.DataFrame:
        """Produce a dataframe with atom parameters as correlated UFloats"""
        # TODO consistent typing of symmetrical numpy and annotated dataframe
        # TODO allow both certain (faster) and uncertain (with error) calculations
        atoms = self.atoms_uncorrelated
        cov_labels = list(self.cov.columns)
        cov_matrix = self.cov.to_numpy()
        cov_std_dev = np.sqrt(np.diag(cov_matrix))
        # TODO: assert std dev from cif and from covariance agree

        to_correlate = {}
        atom_par = [label.rsplit('.', 2) for label in cov_labels]
        for label, (atom, par) in zip(cov_labels, atom_par):
            to_correlate[label] = atoms.at[par, atom].nominal_value
        correlated = uc.correlated_values(
            nom_values=to_correlate.values(),
            covariance_mat=cov_matrix)
        for corr, (atom, par) in zip(correlated, atom_par):
            atoms[par, atom] = corr
        return atoms

    def covariance_star_to_cif(self, cov: pd.DataFrame) -> pd.DataFrame:
        """Scale Uij in cov. matrix by N-1 (10.1107/S0021889802008580, 4a)."""
        scaled = cov.copy()
        n_matrix_diag = (1 / self.base.a_r, 1 / self.base.b_r, 1 / self.base.c_r)
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

    def load_cif(self, path: Path) -> None:
        cif_frame = CifFrame()
        cif_frame.read(str(path))
        self.cif: CifBlock = cif_frame[list(cif_frame.keys())[0]]

    def load_olex2_covariance(self, path: Path) -> None:
        with open(path, "rb") as npy_file:
            first_line = npy_file.readline()
            assert first_line == b"VCOV\n", f'Incorrect file format: {npy_file}'
            labels = [a.decode('UTF-8') for a in npy_file.readline().split()]
            covariance_matrix = matrix_triu2symm(vector=np.load(npy_file))
        assert len(labels) == covariance_matrix.shape[0], 'Inconsistent matrix size'
        cov = pd.DataFrame(covariance_matrix, index=labels, columns=labels)
        self.cov = self.covariance_star_to_cif(cov)










