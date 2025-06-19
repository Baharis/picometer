import importlib.resources
import unittest

import numpy as np

from picometer.atom import AtomSet


class TestTransformations(unittest.TestCase):
    rot3_at_cobalt_code = '1-y,1+x-y,z'
    rot6_at_origin_code = 'x-y,x,z'

    @classmethod
    def setUpClass(cls) -> None:
        with importlib.resources.path('tests', 'cobalt.cif') as cif_path:
            cls.atoms = AtomSet.from_cif(str(cif_path))

    def test_transform_coordinates(self) -> None:
        t = self.atoms.table
        t3 = self.atoms.transform(self.rot3_at_cobalt_code).table
        t6 = self.atoms.transform(self.rot6_at_origin_code).table
        self.assertAlmostEqual(t.at['Co1', 'fract_x'], t3.at['Co1', 'fract_x'], places=3)
        self.assertAlmostEqual(t.at['Co1', 'fract_y'], t3.at['Co1', 'fract_y'], places=3)
        self.assertAlmostEqual(t.at['Co1', 'fract_z'], t3.at['Co1', 'fract_z'], places=3)
        self.assertNotAlmostEqual(t.at['Co1', 'fract_x'], t6.at['Co1', 'fract_x'], places=3)
        self.assertNotAlmostEqual(t.at['Co1', 'fract_y'], t6.at['Co1', 'fract_y'], places=3)
        self.assertAlmostEqual(t.at['Co1', 'fract_z'], t6.at['Co1', 'fract_z'], places=3)

    def test_transform_u_matrix(self) -> None:
        t = self.atoms.table
        t3 = self.atoms.transform(self.rot3_at_cobalt_code).table
        t6 = self.atoms.transform(self.rot6_at_origin_code).table
        us = ['U11', 'U22', 'U33', 'U12', 'U13', 'U23']
        np.testing.assert_allclose(t.loc['Co1', us], t3.loc['Co1', us], rtol=0.01)
        np.testing.assert_allclose(t.loc['Co1', us], t6.loc['Co1', us], rtol=0.01)
        with np.testing.assert_raises(AssertionError):
            np.testing.assert_allclose(t.loc['O1', us], t3.loc['O1', us], rtol=0.1)
        np.testing.assert_equal(t.loc['O1', us], np.array([.067,.066,.018,.031,-.007,-.008]))


if __name__ == '__main__':
    unittest.main()
