"""
Read an Olex2 correlation matrix stored in a composite text-binary .npy file,
determine the largest correlations, and save it in a human-readable format.
Courtesy of Florian Meurer via Florian Kleemiss, cleaned up by Daniel Tchoń.
"""
from pathlib import Path
import warnings

from hikari.dataframes import BaseFrame, CifFrame
from picometer.utility import ustr2float, ustr2floats
import numpy as np
import pandas as pd
import uncertainties as uc


warnings.filterwarnings("ignore", message="Using UFloat objects with std_dev==0.*")


class Covariance:
    """Read, store, apply covariance information. Currently, for olex2 only."""

    def __init__(self, table: pd.DataFrame):
        self.table: pd.DataFrame = table

    @property
    def matrix(self):
        return self.table.to_numpy()

    @classmethod
    def read_from_olex2_npy(cls, path: Path):
        with open(path, "rb") as npy_file:
            first_line = npy_file.readline()
            assert first_line == b"VCOV\n", f'Incorrect file format: {npy_file}'
            labels = [a.decode('UTF-8') for a in npy_file.readline().split()]
            n = len(labels)
            cov_triangular_upper_vector = np.load(npy_file)
        covariance_matrix = np.zeros((n, n))
        covariance_matrix[np.triu_indices(n)] = cov_triangular_upper_vector
        covariance_matrix += np.triu(covariance_matrix, 1).T
        data = pd.DataFrame(covariance_matrix, index=labels, columns=labels)
        data.loc[:, data.columns.str.endswith('u11')] *= 6.9196 * 6.9196
        data.loc[:, data.columns.str.endswith('u22')] *= 14.5749 * 14.5749
        data.loc[:, data.columns.str.endswith('u33')] *= 9.7248 * 9.7248
        data.loc[:, data.columns.str.endswith('u12')] *= 6.9196 * 14.5749
        data.loc[:, data.columns.str.endswith('u13')] *= 6.9196 * 9.7248
        data.loc[:, data.columns.str.endswith('u23')] *= 9.7248 * 14.5749
        data.loc[data.index.str.endswith('u11'), :] *= 6.9196 * 6.9196
        data.loc[data.index.str.endswith('u22'), :] *= 14.5749 * 14.5749
        data.loc[data.index.str.endswith('u33'), :] *= 9.7248 * 9.7248
        data.loc[data.index.str.endswith('u12'), :] *= 6.9196 * 14.5749
        data.loc[data.index.str.endswith('u13'), :] *= 6.9196 * 9.7248
        data.loc[data.index.str.endswith('u23'), :] *= 9.7248 * 14.5749
        # TODO for the love of God and all that'ss Holy do it with cif loading
        return Covariance(data)


def joint_read_cif_cov(cif_path: str, cov_path: str, block_name: str = None):
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

    cif_values = {}
    ls = cb.get('_atom_site_aniso_label', [])
    u11s = ustr2floats(cb.get('_atom_site_aniso_U_11', []))
    u22s = ustr2floats(cb.get('_atom_site_aniso_U_22', []))
    u33s = ustr2floats(cb.get('_atom_site_aniso_U_33', []))
    u12s = ustr2floats(cb.get('_atom_site_aniso_U_12', []))
    u13s = ustr2floats(cb.get('_atom_site_aniso_U_13', []))
    u23s = ustr2floats(cb.get('_atom_site_aniso_U_23', []))
    for i, l in enumerate(ls):
        cif_values[f'{l}.u11'] = u11s[i]
        cif_values[f'{l}.u22'] = u22s[i]
        cif_values[f'{l}.u33'] = u33s[i]
        cif_values[f'{l}.u12'] = u12s[i]
        cif_values[f'{l}.u13'] = u13s[i]
        cif_values[f'{l}.u23'] = u23s[i]

    ls = cb.get('_atom_site_label', [])
    xs = ustr2floats(cb.get('_atom_site_fract_x', []))
    ys = ustr2floats(cb.get('_atom_site_fract_y', []))
    zs = ustr2floats(cb.get('_atom_site_fract_z', []))
    us = ustr2floats(cb.get('_atom_site_U_iso_or_equiv', []))
    os = ustr2floats(cb.get('_atom_site_occupancy', []))
    for l, x, y, z, u, o in zip(ls, xs, ys, zs, us, os):
        cif_values |= {f'{l}.x': x, f'{l}.y': y, f'{l}.z': z, f'{l}.occ': o}
        if f'{l}.u11' not in cif_values:
            cif_values[f'{l}.uiso'] = u

    cov = Covariance.read_from_olex2_npy(Path(cov_path))
    assert set(cov.table.keys()).issubset(cif_values.keys())

    certain = [cif_values[k] for k in cov.table.keys()]
    uncertain = uc.correlated_values(nom_values=certain, covariance_mat=cov.matrix)
    uncertain_dict = {k: u for k, u in zip(cov.table.keys(), uncertain)}

    return {k: uncertain_dict.get(k, uc.ufloat(v, 0)) for k, v in cif_values.items()}



if __name__ == '__main__':
    cif = r"C:\Users\tchon\AppData\Roaming\Olex2Data\78c6e52b114a649262d65d638a295626\samples\THPP\thpp.cif"
    cov = r"C:\Users\tchon\AppData\Roaming\Olex2Data\78c6e52b114a649262d65d638a295626\samples\THPP\thpp.npy"
    for k, v in joint_read_cif_cov(cif, cov).items():
        print(f'{k:12s}: {v!s}')
