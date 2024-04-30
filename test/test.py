import csv
from pathlib import Path
from typing import Iterable
import unittest

import numpy as np
import pandas as pd

from picometer.atom import alias_registry, Locator
from picometer.parser import parse, parse_path
from picometer.routine import Routine, RoutineQueue
from picometer.main import process_routine_queue


class TestParser(unittest.TestCase):
    def setUp(self) -> None:
        self.paths = [Path(__file__).parent.joinpath(f'ferrocene{n}.cif')
                      for n in [1, 2, 3, 4, 5, 6]]

    def test_parse_snippet(self) -> None:
        instructions = "load:\n"
        for path in self.paths:
            instructions += f"  - path: {path}\n"
        routine_queue = parse(instructions)
        routine = routine_queue[0]
        self.assertIn('load', routine)
        self.assertIn('path', routine['load'][0])
        self.assertEqual(len(routine['load']), 6)

    def test_parse_file(self) -> None:
        routine_path = Path(__file__).parent.joinpath(f'ferrocene.yaml')
        routine_queue = parse_path(routine_path)
        routine = routine_queue[0]
        self.assertIn('load', routine)
        self.assertIn('path', routine['load'][0])
        self.assertEqual(len(routine['load']), 6)


class TestProcedures(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        routine_path = Path(__file__).parent.joinpath(f'ferrocene.yaml')
        cls.full_routine_queue = parse_path(routine_path)

    def slice_routine_queue(self, step_ids: Iterable[int]) -> RoutineQueue:
        rs = [r for i, r in enumerate(self.full_routine_queue) if i in step_ids]
        return RoutineQueue(rs)

    def test_load(self):
        routine_queue = self.slice_routine_queue([0, ])
        mss, _ = process_routine_queue(routine_queue)
        for _, ms in mss.items():
            self.assertEqual(ms.atoms.table.loc['Fe', 'fract_x'], 0.0)

    def test_make_alias(self) -> None:
        routine_queue = self.slice_routine_queue([0, 1])
        _, _ = process_routine_queue(routine_queue)
        self.assertEqual(alias_registry['iron'], [Locator('Fe')])

    def test_access_alias(self) -> None:
        routine_queue = self.slice_routine_queue([0, 1])
        mss, _ = process_routine_queue(routine_queue)
        for _, ms in mss.items():
            self.assertEqual(ms.atoms.locate([Locator('Fe')]).table.index,
                             ms.atoms.locate([Locator('iron')]).table.index)

    def test_regex_alias(self):
        routine_queue = self.slice_routine_queue([0, 2])
        mss, _ = process_routine_queue(routine_queue)
        carbon_counts = [5, 5, 10, 10, 15, 15]
        for (_, ms), cc in zip(mss.items(), carbon_counts):
            carbons = ms.atoms.locate([Locator('cp_A')]).table
            self.assertEqual(len(carbons), cc)

    def test_transformed_alias(self):
        routine_queue = self.slice_routine_queue([0, 2, 3])
        mss, _ = process_routine_queue(routine_queue)
        for _, ms in mss.items():
            carbons_a = ms.atoms.locate([Locator('cp_A')]).table
            carbons_b = ms.atoms.locate([Locator('cp_B')]).table
            for key in carbons_a.keys():
                self.assertEqual(carbons_a[key].iloc[0],
                                 -carbons_b[key].iloc[0])

    def test_centroid(self):
        routine_queue = self.slice_routine_queue([0, 2, 4])
        mss, _ = process_routine_queue(routine_queue)
        for _, ms in mss.items():
            c = ms.centroids.table.loc['cp_A_centroid']
            self.assertGreater(c['fract_x'], 0.113)
            self.assertGreater(c['fract_y'], 0.154)
            self.assertGreater(c['fract_z'], 0.016)
            self.assertLess(c['fract_x'], 0.116)
            self.assertLess(c['fract_y'], 0.158)
            self.assertLess(c['fract_z'], 0.030)

    def test_line(self):
        routine_queue = self.slice_routine_queue([0, 1, 2, 4, 5])
        mss, _ = process_routine_queue(routine_queue)
        for _, ms in mss.items():
            d = ms.shapes['ferrocene_axis'].direction
            d = d if d[0] >= 0 else -d
            correct = np.array([0.693, 0.718, 0.064])
            self.assertTrue(np.allclose(d, correct, atol=0.03))

    def test_plane(self):
        routine_queue = self.slice_routine_queue([0, 2, 6])
        mss, _ = process_routine_queue(routine_queue)
        for _, ms in mss.items():
            d = ms.shapes['cp_A_plane'].direction
            d = d if d[0] >= 0 else -d
            correct = np.array([0.680, 0.730, 0.070])
            self.assertTrue(np.allclose(d, correct, atol=0.01))

    def test_line_at_symm(self):
        routine_queue = self.slice_routine_queue([0, 1, 2, 4, 5, 7])
        mss, _ = process_routine_queue(routine_queue)
        for _, ms in mss.items():
            o = ms.shapes['ferrocene_axis_at_next_cell'].origin
            self.assertGreater(o[0], 10.442)
            self.assertLess(o[0], 10.531)

    def test_plane_at_alias(self):
        routine_queue = self.slice_routine_queue([0, 1, 2, 6, 8])
        mss, _ = process_routine_queue(routine_queue)
        for _, ms in mss.items():
            o = ms.shapes['cp_A_plane_at_iron'].origin
            f = ms.atoms.locate([Locator('iron')]).origin
            self.assertTrue(np.allclose(o, f))

    def test_alias_at_alias(self):
        routine_queue = self.slice_routine_queue([0, 2, 3, 9])
        mss, _ = process_routine_queue(routine_queue)
        for _, ms in mss.items():
            o_a = ms.nodes.locate([Locator('cp_A')]).origin
            o_ba = ms.nodes.locate([Locator('cp_B_at_cp_A')]).origin
            self.assertTrue(np.allclose(o_a, o_ba))
            pd_b = ms.nodes.locate([Locator('cp_B')]).plane.direction
            pd_ba = ms.nodes.locate([Locator('cp_B_at_cp_A')]).plane.direction
            pd_ba = pd_ba if pd_ba[0] * pd_b[0] >= 0 else -pd_ba
            self.assertTrue(np.allclose(pd_b, pd_ba))

    def test_distance_plane_plane(self):
        routine_queue = self.slice_routine_queue([0, 2, 3, 9, 10, 11, 12])
        mss, et = process_routine_queue(routine_queue)
        results = et['cpA_to_cpB_plane_distance'].to_numpy()
        correct = np.array([3.2864663644815, 3.2769672330907, 3.288974081930,
                            3.2875174042662, 3.2735236841099, 3.292997025065])
        self.assertTrue(np.allclose(results, correct))

    def test_distance_line_plane(self):
        routine_queue = self.slice_routine_queue([0, 1, 13, 14, 15])
        mss, et = process_routine_queue(routine_queue)
        results = et['100_direction_to_001_plane'].to_numpy()
        correct = np.array([4.99475809, 5.07262443, 4.99475809,
                            5.07262443, 4.99475809, 5.07262443])
        self.assertTrue(np.allclose(results, correct))

    def test_distance_line_line(self):
        routine_queue = self.slice_routine_queue([0, 1, 14, 16, 17])
        mss, et = process_routine_queue(routine_queue)
        results = et['100_direction_to_010_direction'].to_numpy()
        correct = np.array([4.99475809, 5.07262443, 4.99475809,
                            5.07262443, 4.99475809, 5.07262443])
        self.assertTrue(np.allclose(results, correct))

    def test_distance_nodes_plane(self):
        routine_queue = self.slice_routine_queue([0, 2, 6, 18])
        mss, et = process_routine_queue(routine_queue)
        results = et['cp_A_cp_A_plane_offset'].to_numpy()
        correct = np.array([6.99964271e-05, 8.36653335e-06, 1.33526154e-03,
                            1.21160264e-03, 5.96725130e-03, 6.65771648e-03])
        self.assertTrue(np.allclose(results, correct))

    def test_distance_nodes_line(self):
        routine_queue = self.slice_routine_queue([0, 1, 2, 4, 5, 19])
        mss, et = process_routine_queue(routine_queue)
        results = et['cp_A_ferrocene_axis_offset'].to_numpy()
        correct = np.array([1.39227974, 1.40885241, 1.23443585,
                            1.21138738, 1.19594416, 1.15219622])
        self.assertTrue(np.allclose(results, correct))

    def test_distance_nodes_nodes(self):
        routine_queue = self.slice_routine_queue([0, 2, 3, 20])
        mss, et = process_routine_queue(routine_queue)
        results = et['cp_A_cp_B_offset'].to_numpy()
        correct = np.array([3.35281183, 3.34790063, 3.25804871,
                            3.23411241, 3.15891163, 3.21732243])
        self.assertTrue(np.allclose(results, correct))

    def test_angle_plane_plane(self):
        routine_queue = self.slice_routine_queue([0, 1, 2, 6, 13, 21])
        mss, et = process_routine_queue(routine_queue)
        results = et['001_plane_cp_A_plane_angle'].to_numpy()
        correct = np.array([86.37457561, 86.04503476, 85.87846808,
                            85.57654087, 86.09193950, 86.00968187])
        self.assertTrue(np.allclose(results, correct))

    def test_angle_plane_line(self):
        routine_queue = self.slice_routine_queue([0, 1, 2, 4, 5, 6, 22])
        mss, et = process_routine_queue(routine_queue)
        results = et['cp_A_plane_ferrocene_axis_angle'].to_numpy()
        correct = np.array([88.83344787, 89.04145467, 89.18254017,
                            88.99812150, 89.50083634, 89.06814667])
        self.assertTrue(np.allclose(results, correct))

    def test_angle_line_line(self):
        routine_queue = self.slice_routine_queue([0, 1, 2, 4, 5, 16, 23])
        mss, et = process_routine_queue(routine_queue)
        results = et['010_direction_ferrocene_axis_angle'].to_numpy()
        correct = np.array([44.18189561, 44.06982134, 43.99321263,
                            43.63394452, 43.31590821, 43.52811746])
        self.assertTrue(np.allclose(results, correct))

    def test_angle_interior_nodes(self):
        routine_queue = self.slice_routine_queue([0, 24])
        mss, et = process_routine_queue(routine_queue)
        results = et['C(11)-C(12)-C(13)'].to_numpy()
        correct = np.array([107.99651216, 107.98120182, 107.98282958,
                            108.17779184, 108.12639300, 107.63799568])
        self.assertTrue(np.allclose(results, correct))

    def test_angle_dihedral_nodes(self):
        routine_queue = self.slice_routine_queue([0, 25])
        mss, et = process_routine_queue(routine_queue)
        results = et['C(11)-C(12)-C(13)-C(14)'].to_numpy()
        correct = np.array([0.03373221, 0.00041385, 0.02161362,
                            0.11565318, 0.03754215, 0.37636209])
        self.assertTrue(np.allclose(results, correct))

    def test_write(self):
        routine_queue = self.full_routine_queue
        _, _ = process_routine_queue(routine_queue)
        correct_path = Path(__file__).parent / 'ferrocene_correct.csv'
        results_path = Path(__file__).parent / 'ferrocene_results.csv'
        correct = pd.read_csv(correct_path)
        results = pd.read_csv(results_path)
        self.assertTrue(correct.equals(results))


if __name__ == '__main__':
    unittest.main()
