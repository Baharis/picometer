import importlib.resources
from pathlib import Path
import string
import tempfile
from textwrap import dedent
from typing import Iterable
import unittest

import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

from picometer.atom import group_registry, Locator
from picometer.instructions import Routine, Instruction
from picometer.process import process


def get_yaml(file: str, lines: Iterable[int] = None) -> str:
    """Context-aware slicer-getter, returns `rows` of `.test_instructions.yaml`"""
    with importlib.resources.path('tests', file) as yaml_path:
        tests_path = yaml_path.parent
        with open(yaml_path, 'r') as yaml_file:
            routine_template = string.Template(yaml_file.read())
    paths_map = {(f := f'ferrocene{i}'): tests_path / (f + '.cif') for i in range(1, 7)}
    paths_map['ferrocene_results'] = tests_path / 'ferrocene_results.csv'
    full_routine = routine_template.substitute(paths_map)
    full_routine_lines = list(full_routine.splitlines())
    if not lines:
        lines = range(len(full_routine_lines))
    return '\n'.join(full_routine_lines[i] for i in lines) + '\n'


class TestRoutine(unittest.TestCase):
    def test_routine_init(self) -> None:
        routine = Routine()
        self.assertEqual(len(routine), 0)

    def test_routine_from_dict(self) -> None:
        dict_ = {
            'settings': {'setting_key': 'setting_value'},
            'instructions': [{'load': {'path': 'ferrocene1.cif'}},
                             {'load': 'ferrocene2.cif'}]
        }
        routine = Routine.from_dict(dict_)
        self.assertEqual(len(routine), 3)  # one "set", two "load" instructions
        self.assertEqual('load', routine[1].keyword)
        self.assertIn('path', routine[1].kwargs)
        self.assertIn('ferrocene1.cif', routine[1].kwargs['path'])

    def test_routine_from_string(self) -> None:
        str_ = dedent("""
        settings:
          setting_key: setting_value
        instructions:
          - load: {path: ferrocene1.cif}
          - load: ferrocene2.cif
        """)
        routine = Routine.from_string(str_)
        self.assertEqual(len(routine), 3)  # 1 "set" and 2 "load" instructions
        self.assertEqual('load', routine[1].keyword)
        self.assertIn('path', routine[1].kwargs)
        self.assertIn('ferrocene1.cif', routine[1].kwargs['path'])

    def test_routine_from_yaml(self) -> None:
        with importlib.resources.path('tests', 'test_ferrocene.yaml') as yaml_path:
            routine = Routine.from_yaml(yaml_path)
        self.assertEqual('set', routine[0].keyword)
        self.assertEqual('load', routine[5].keyword)
        self.assertEqual(len([r for r in routine if r.keyword != 'set']), 80)

    def test_routine_to_yaml(self) -> None:
        with importlib.resources.path('tests', 'test_ferrocene.yaml') as yaml_path:
            r1 = Routine.from_yaml(yaml_path)
        with tempfile.TemporaryDirectory() as temp_dir:
            yaml2_path = Path(temp_dir) / 'yaml.yaml'
            r1.to_yaml(yaml2_path)
            r2 = Routine.from_yaml(yaml2_path)
        self.assertEqual(r1, r2)

    def test_routine_concatenate(self) -> None:
        routine1 = Routine([Instruction('select')])
        routine2 = Routine([Instruction('select')])
        routine = Routine.concatenate([routine1, routine2])
        self.assertEqual(len(routine), 3)  # "routine1", "clear", "routine2"
        self.assertIs(routine[1].keyword, 'clear')


class TestBasicsInstructions(unittest.TestCase):
    def test_init(self) -> None:
        _ = Instruction({'unused_keyword': 'unused_str_argument'})  # dict input
        _ = Instruction('unused_keyword_without_argument')          # str input
        _ = Instruction(unused_keyword='unused_str_argument')       # kwargs input
        with self.assertRaises(ValueError):  # Length is 0 but must be 1
            _ = Instruction()
        with self.assertRaises(ValueError):  # Length is 0 but must be 1
            _ = Instruction({})
        with self.assertRaises(ValueError):  # Length is 2 but must be 1
            _ = Instruction({'unused_keyword1': None, 'unused_keyword2': None})

    def test_equal(self) -> None:
        i1 = Instruction({'select': {}})
        i2 = Instruction('select')
        i3 = Instruction({'select': 'atom'})
        i4 = Instruction({'select': {'label': 'atom'}})
        self.assertEqual(i1, i2)
        self.assertEqual(i3, i4)

    def test_as_dict(self) -> None:
        d = {'select': {'label': 'atom', 'symm': None, 'at': None}}
        i = Instruction(d)
        self.assertEqual(d, i.as_dict())


class TestSettingInstructions(unittest.TestCase):
    routine_prefix = get_yaml('test_instructions.yaml', lines=range(7))

    def setUp(self) -> None:
        self.routine_text = self.routine_prefix

    def test_load(self):
        p = process(Routine.from_string(self.routine_text))
        for _, ms in p.model_states.items():
            self.assertEqual(ms.atoms.table.loc['Fe', 'fract_x'], 0.0)

    def test_select_atom(self) -> None:
        self.routine_text += '  - select: Fe\n'
        p = process(Routine.from_string(self.routine_text))
        self.assertEqual(p.selection, [Locator('Fe')])

    def test_select_none(self) -> None:
        self.routine_text += '  - select: Fe\n'
        self.routine_text += '  - select'
        p = process(Routine.from_string(self.routine_text))
        self.assertFalse(p.selection)

    def test_make_group(self) -> None:
        self.routine_text += '  - select: Fe\n'
        self.routine_text += '  - group: iron'
        _ = process(Routine.from_string(self.routine_text))
        self.assertEqual(group_registry['iron'], [Locator('Fe')])

    def test_access_group(self) -> None:
        self.routine_text += '  - select: Fe\n'
        self.routine_text += '  - group: iron'
        p = process(Routine.from_string(self.routine_text))
        for _, ms in p.model_states.items():
            self.assertEqual(ms.atoms.locate([Locator('Fe')]).table.index,
                             ms.atoms.locate([Locator('iron')]).table.index)

    def test_regex_group(self):
        self.routine_text += '  - select: C.+\n'
        self.routine_text += '  - group: cp_A'
        p = process(Routine.from_string(self.routine_text))
        carbon_counts = [5, 5, 10, 10, 15, 15]
        for (_, ms), cc in zip(p.model_states.items(), carbon_counts):
            carbons = ms.atoms.locate([Locator('cp_A')]).table
            self.assertEqual(len(carbons), cc)

    def test_transformed_group(self):
        self.routine_text += '  - select: C.+\n'
        self.routine_text += '  - group: cp_A\n'
        self.routine_text += '  - select: {label: cp_A, symm: -x;-y;-z}\n'
        self.routine_text += '  - group: cp_B'
        p = process(Routine.from_string(self.routine_text))
        for _, ms in p.model_states.items():
            carbons_a = ms.atoms.locate([Locator('cp_A')]).table
            carbons_b = ms.atoms.locate([Locator('cp_B')]).table
            for key in carbons_a.keys():
                self.assertEqual(carbons_a[key].iloc[0],
                                 -carbons_b[key].iloc[0])

    def test_centroid(self):
        self.routine_text += '  - select: C.+\n'
        self.routine_text += '  - centroid: cp_A_centroid'
        p = process(Routine.from_string(self.routine_text))
        for _, ms in p.model_states.items():
            c = ms.centroids.table.loc['cp_A_centroid']
            self.assertGreater(c['fract_x'], 0.113)
            self.assertGreater(c['fract_y'], 0.154)
            self.assertGreater(c['fract_z'], 0.016)
            self.assertLess(c['fract_x'], 0.116)
            self.assertLess(c['fract_y'], 0.158)
            self.assertLess(c['fract_z'], 0.030)

    def test_line(self):
        self.routine_text += '  - select: C.+\n'
        self.routine_text += '  - centroid: cp_A_centroid\n'
        self.routine_text += '  - select: cp_A_centroid\n'
        self.routine_text += '  - select: Fe\n'
        self.routine_text += '  - line: ferrocene_axis'
        p = process(Routine.from_string(self.routine_text))
        for _, ms in p.model_states.items():
            d = ms.shapes['ferrocene_axis'].direction
            correct = np.array([0.693, 0.718, 0.064])
            self.assertTrue(np.allclose(d, correct, atol=0.03))

    def test_plane(self):
        self.routine_text += '  - select: C.+\n'
        self.routine_text += '  - plane: cp_A_plane\n'
        p = process(Routine.from_string(self.routine_text))
        for _, ms in p.model_states.items():
            d = ms.shapes['cp_A_plane'].direction
            correct = np.array([0.680, 0.730, 0.070])
            self.assertTrue(np.allclose(d, correct, atol=0.01))

    def test_line_at_symm(self):
        self.routine_text += '  - select: C.+\n'
        self.routine_text += '  - centroid: cp_A_centroid\n'
        self.routine_text += '  - select: cp_A_centroid\n'
        self.routine_text += '  - select: Fe\n'
        self.routine_text += '  - recenter: {label: Fe, symm: z+1;y;z}\n'
        self.routine_text += '  - line: ferrocene_axis_at_next_cell'
        p = process(Routine.from_string(self.routine_text))
        for _, ms in p.model_states.items():
            o = ms.shapes['ferrocene_axis_at_next_cell'].origin
            self.assertGreater(o[0], 10.442)
            self.assertLess(o[0], 10.531)

    def test_plane_at_group(self):
        self.routine_text += '  - select: Fe\n'
        self.routine_text += '  - group: iron\n'
        self.routine_text += '  - select: {label: C.+, symm: -x;-y;-z}\n'
        self.routine_text += '  - recenter: iron\n'
        self.routine_text += '  - plane: cp_A_plane_at_iron'
        p = process(Routine.from_string(self.routine_text))
        for _, ms in p.model_states.items():
            o = ms.shapes['cp_A_plane_at_iron'].origin
            f = ms.atoms.locate([Locator('iron')]).origin
            self.assertTrue(np.allclose(o, f))

    def test_group_at_group(self):
        self.routine_text += '  - select: C.+\n'
        self.routine_text += '  - group: cp_A\n'
        self.routine_text += '  - select: {label: cp_A, symm: -x;-y;-z}\n'
        self.routine_text += '  - group: cp_B\n'
        self.routine_text += '  - select: cp_B\n'
        self.routine_text += '  - recenter: cp_A\n'
        self.routine_text += '  - group: cp_B_at_cp_A'
        p = process(Routine.from_string(self.routine_text))
        for _, ms in p.model_states.items():
            o_a = ms.nodes.locate([Locator('cp_A')]).origin
            o_ba = ms.nodes.locate([Locator('cp_B_at_cp_A')]).origin
            self.assertTrue(np.allclose(o_a, o_ba))
            pd_b = ms.nodes.locate([Locator('cp_B')]).plane.direction
            pd_ba = ms.nodes.locate([Locator('cp_B_at_cp_A')]).plane.direction
            pd_ba = pd_ba if pd_ba[0] * pd_b[0] >= 0 else -pd_ba
            self.assertTrue(np.allclose(pd_b, pd_ba))


class TestMeasuringInstructions(unittest.TestCase):
    routine_prefix = get_yaml('test_instructions.yaml')

    def setUp(self) -> None:
        self.routine_text = self.routine_prefix

    def test_distance_plane_plane(self):
        self.routine_text += '  - select: cp_A_plane\n'
        self.routine_text += '  - select: cp_B_plane\n'
        self.routine_text += '  - distance: cp_A_to_cp_B_plane_distance'
        p = process(Routine.from_string(self.routine_text))
        results = p.evaluation_table['cp_A_to_cp_B_plane_distance'].to_numpy()
        correct = np.array([3.2864663644815, 3.2769672330907, 3.288974081930,
                            3.2875174042662, 3.2735236841099, 3.292997025065])
        self.assertTrue(np.allclose(results, correct))

    def test_distance_line_plane(self):
        self.routine_text += '  - select: 100_direction\n'
        self.routine_text += '  - select: 001_plane\n'
        self.routine_text += '  - distance: 100_direction_to_001_plane'
        p = process(Routine.from_string(self.routine_text))
        results = p.evaluation_table['100_direction_to_001_plane'].to_numpy()
        correct = np.array([4.99475809, 5.07262443, 4.99475809,
                            5.07262443, 4.99475809, 5.07262443])
        self.assertTrue(np.allclose(results, correct))

    def test_distance_line_line(self):
        self.routine_text += '  - select: 100_direction\n'
        self.routine_text += '  - select: 010_direction\n'
        self.routine_text += '  - distance: 100_direction_to_010_direction'
        p = process(Routine.from_string(self.routine_text))
        results = p.evaluation_table['100_direction_to_010_direction'].to_numpy()
        correct = np.array([4.99475809, 5.07262443, 4.99475809,
                            5.07262443, 4.99475809, 5.07262443])
        self.assertTrue(np.allclose(results, correct))

    def test_distance_nodes_plane(self):
        self.routine_text += '  - select: cp_A\n'
        self.routine_text += '  - select: cp_A_plane\n'
        self.routine_text += '  - distance: cp_A_cp_A_plane_offset'
        p = process(Routine.from_string(self.routine_text))
        results = p.evaluation_table['cp_A_cp_A_plane_offset'].to_numpy()
        correct = np.array([6.99964271e-05, 8.36653335e-06, 1.33526154e-03,
                            1.21160264e-03, 5.96725130e-03, 6.65771648e-03])
        self.assertTrue(np.allclose(results, correct))

    def test_distance_nodes_line(self):
        self.routine_text += '  - select: cp_A\n'
        self.routine_text += '  - select: ferrocene_axis\n'
        self.routine_text += '  - distance: cp_A_ferrocene_axis_offset'
        p = process(Routine.from_string(self.routine_text))
        results = p.evaluation_table['cp_A_ferrocene_axis_offset'].to_numpy()
        correct = np.array([1.39227974, 1.40885241, 1.23443585,
                            1.21138738, 1.19594416, 1.15219622])
        self.assertTrue(np.allclose(results, correct))

    def test_distance_nodes_nodes(self):
        self.routine_text += '  - select: cp_A\n'
        self.routine_text += '  - select: cp_B\n'
        self.routine_text += '  - distance: cp_A_cp_B_offset'
        p = process(Routine.from_string(self.routine_text))
        results = p.evaluation_table['cp_A_cp_B_offset'].to_numpy()
        correct = np.array([3.35281183, 3.34790063, 3.25804871,
                            3.23411241, 3.15891163, 3.21732243])
        self.assertTrue(np.allclose(results, correct))

    def test_angle_plane_plane(self):
        self.routine_text += '  - select: 001_plane\n'
        self.routine_text += '  - select: cp_A_plane\n'
        self.routine_text += '  - angle: 001_plane_cp_A_plane_angle'
        p = process(Routine.from_string(self.routine_text))
        results = p.evaluation_table['001_plane_cp_A_plane_angle'].to_numpy()
        correct = np.array([86.37457561, 86.04503476, 85.87846808,
                            85.57654087, 86.09193950, 86.00968187])
        self.assertTrue(np.allclose(results, correct))

    def test_angle_plane_line(self):
        self.routine_text += '  - select: cp_A_plane\n'
        self.routine_text += '  - select: ferrocene_axis\n'
        self.routine_text += '  - angle: cp_A_plane_ferrocene_axis_angle'
        p = process(Routine.from_string(self.routine_text))
        results = p.evaluation_table['cp_A_plane_ferrocene_axis_angle'].to_numpy()
        correct = np.array([88.83344787, 89.04145467, 89.18254017,
                            88.99812150, 89.50083634, 89.06814667])
        self.assertTrue(np.allclose(results, correct))

    def test_angle_line_line(self):
        self.routine_text += '  - select: 010_direction\n'
        self.routine_text += '  - select: ferrocene_axis\n'
        self.routine_text += '  - angle: 010_direction_ferrocene_axis_angle'
        p = process(Routine.from_string(self.routine_text))
        results = p.evaluation_table['010_direction_ferrocene_axis_angle'].to_numpy()
        correct = np.array([44.18189561, 44.06982134, 43.99321263,
                            43.63394452, 43.31590821, 43.52811746])
        self.assertTrue(np.allclose(results, correct))

    def test_angle_nodes(self):
        self.routine_text += '  - select: C(11)\n'
        self.routine_text += '  - select: C(12)\n'
        self.routine_text += '  - select: C(13)\n'
        self.routine_text += '  - angle: C(11)-C(12)-C(13)'
        p = process(Routine.from_string(self.routine_text))
        results = p.evaluation_table['C(11)-C(12)-C(13)'].to_numpy()
        correct = np.array([107.99651216, 107.98120182, 107.98282958,
                            108.17779184, 108.12639300, 107.63799568])
        self.assertTrue(np.allclose(results, correct))

    def test_angle_fails_on_4_atoms(self):
        self.routine_text += '  - select: C(11)\n'
        self.routine_text += '  - select: C(12)\n'
        self.routine_text += '  - select: C(13)\n'
        self.routine_text += '  - select: C(14)\n'
        self.routine_text += '  - angle: C(11)-C(12)-C(13)-C(14)'
        with self.assertRaises(AssertionError):
            _ = process(Routine.from_string(self.routine_text))

    def test_dihedral_positive(self):
        self.routine_text += '  - select: H(11)\n'
        self.routine_text += '  - select: C(11)\n'
        self.routine_text += '  - select: C(15)\n'
        self.routine_text += '  - select: Fe\n'
        self.routine_text += '  - dihedral: H(11)-C(11)-C(15)-Fe'
        p = process(Routine.from_string(self.routine_text))
        results = p.evaluation_table['H(11)-C(11)-C(15)-Fe'].to_numpy()
        correct = np.array([117.48054368, 118.56063847, 118.81095746,
                            118.03459677, 122.13488005, 120.58628219])
        self.assertTrue(np.allclose(results, correct))

    def test_dihedral_mixed(self):
        self.routine_text += '  - select: C(11)\n'
        self.routine_text += '  - select: C(12)\n'
        self.routine_text += '  - select: C(13)\n'
        self.routine_text += '  - select: C(14)\n'
        self.routine_text += '  - dihedral: C(11)-C(12)-C(13)-C(14)'
        p = process(Routine.from_string(self.routine_text))
        results = p.evaluation_table['C(11)-C(12)-C(13)-C(14)'].to_numpy()
        correct = np.array([+0.03373221, -0.00041385, +0.02161362,
                            +0.11565318, -0.03754215, -0.37636209])
        self.assertTrue(np.allclose(results, correct))

    def test_dihedral_fails_on_3_atoms(self):
        self.routine_text += '  - select: C(11)\n'
        self.routine_text += '  - select: C(12)\n'
        self.routine_text += '  - select: C(13)\n'
        self.routine_text += '  - dihedral: C(11)-C(12)-C(13)'
        with self.assertRaises(AssertionError):
            _ = process(Routine.from_string(self.routine_text))

    def test_write(self):
        routine_text = get_yaml('test_ferrocene.yaml')
        _ = process(Routine.from_string(routine_text))
        with importlib.resources.path('tests', 'test_ferrocene.yaml') as yaml_path:
            tests_path = yaml_path.parent
        correct_path = tests_path / 'ferrocene_correct.csv'
        results_path = tests_path / 'ferrocene_results.csv'
        correct = pd.read_csv(correct_path, index_col=0)
        results = pd.read_csv(results_path, index_col=0)
        results.index = correct.index  # index is env-dependent so ignore it
        assert_frame_equal(correct, results, check_exact=False,
                           rtol=1e-13, atol=1e-12)

    def test_document_history(self):
        routine_text = get_yaml('test_ferrocene.yaml')
        original_routine = Routine.from_string(routine_text)
        processor = process(original_routine)
        historic_routine = processor.history
        self.assertEqual(original_routine, historic_routine)


if __name__ == '__main__':
    unittest.main()
