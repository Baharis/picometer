import copy
from pathlib import Path
from typing import Iterable
import unittest


from picometer.parser import parse, parse_path
from picometer.routine import RoutineQueue


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
        return [RoutineQueue(r) for i, r in enumerate(self.full_routine_queue)
                if i in routine_ids]

    def test_alias_atom(self) -> None:
        routine_queue = self.slice_routine_queue([0, 1])



if __name__ == '__main__':
    unittest.main()
