import copy
from pathlib import Path
from typing import Iterable
import unittest


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

    def slice_routine_queue(self, routine_ids: Iterable[int]) -> RoutineQueue:
        return RoutineQueue([Routine(r) for i, r in enumerate(self.full_routine_queue)
                if i in routine_ids])

    def test_load(self):
        routine_queue = self.slice_routine_queue([0, ])
        mss, _ = process_routine_queue(routine_queue)
        for _, ms in mss.items():
            self.assertEqual(ms.atoms.atoms.loc['Fe', 'fract_x'], 0.0)

    def test_make_alias(self) -> None:
        routine_queue = self.slice_routine_queue([0, 1])
        _, _ = process_routine_queue(routine_queue)
        self.assertEqual(alias_registry['iron'], [Locator('Fe1')])

    def test_access_alias(self) -> None:
        routine_queue = self.slice_routine_queue([0, 1])
        mss, _ = process_routine_queue(routine_queue)
        for _, ms in mss.items():
            self.assertEqual(ms.atoms.locate([Locator('Fe')]).atoms.index,
                             ms.atoms.locate([Locator('iron')]).atoms.index)


if __name__ == '__main__':
    unittest.main()
