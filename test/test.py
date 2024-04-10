from pathlib import Path
from typing import Iterable
import unittest

import numpy as np

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


if __name__ == '__main__':
    unittest.main()
