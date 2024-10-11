from copy import deepcopy
from collections import UserDict
from typing import Callable, Dict, List, Union

import pandas as pd

from picometer.atom import group_registry, AtomSet, Locator
from picometer.models import ModelState, ModelStates
from picometer.routine import Routine
from picometer.settings import Settings


ImplicitInstructionArgument = Union[str, Dict[str, str]]


def explicit_kwargs(**expected_kwargs: type) -> type:
    class ExplicitInstructionArgs(UserDict):
        def __init__(self, arg):
            new = {}
            if isinstance(arg, dict):
                for key, value in arg.items():
                    assert key in expected_kwargs.keys(), f'Unknown key: {key}'
                    new[key] = expected_kwargs[key](value)
            else:
                expected_key, expected_type = list(expected_kwargs.items())[0]
                new[expected_key] = expected_type(arg)
            for expected_key in expected_kwargs.keys():
                if expected_key not in new.keys():
                    new[expected_key] = None
            super().__init__(**new)
    return ExplicitInstructionArgs


CifInstructionsDict = explicit_kwargs(path=str, block=str)
LocatorInstructionsDict = explicit_kwargs(label=str, symm=str, at=Locator)


Instruction: Dict


def registers_instructions(cls):
    """Class decorator that registers class methods in `cls.instructions`"""
    cls.instructions = {}
    for method_name in dir(cls):
        method = getattr(cls, method_name)
        if hasattr(method, '_name'):
            name = getattr(method, '_name')
            cls.instructions.update({name: method})
    return cls


def register_instruction(name: str) -> Callable:
    """Method decorator that registers this method in `cls.instructions`"""
    def decorator(processor_method: Callable) -> Callable:
        processor_method._name = name
        return processor_method
    return decorator


@registers_instructions
class Processor:
    """
    This is the main class responsible for controlling, processing,
    storing current state, importing, exporting the current state
    of work performed in picometer.
    """
    instructions: Dict[str, Callable] = {}

    def __init__(self, settings: Settings = None) -> None:
        self.evaluation_table = pd.DataFrame()
        self.model_states: ModelStates = ModelStates()
        self.selection: List[Locator] = []
        self.settings = Settings.from_yaml()
        if settings:
            self.settings.update(settings)

    def process(self, instruction: Union[Dict, str]) -> None:
        if isinstance(instruction, dict):
            if len(instruction) != 1:
                raise ValueError('Only singular instructions are accepted')
            instruction_name = list(instruction.keys())[0]
            instruction_argument = list(instruction.values())[0]
        else:
            instruction_name, instruction_argument = instruction, None
        self.instructions[instruction_name](self, instruction_argument)

    def clear_selection_after_use(self) -> None:
        if self.settings.get('clear_selection_after_use'):
            self.selection = []

    @register_instruction('load')
    def load(self, arg: ImplicitInstructionArgument) -> None:
        arg = CifInstructionsDict(arg)
        cif_path = arg['path']
        block_name = arg['block']
        atoms = AtomSet.from_cif(cif_path=cif_path, block_name=block_name)
        label = cif_path + (':' + block_name if block_name else '')
        self.model_states[label] = ModelState(atoms=atoms)

    @register_instruction('select')
    def select(self, arg: ImplicitInstructionArgument) -> None:
        arg = LocatorInstructionsDict(arg)
        loc = Locator.from_dict(arg)
        if loc:
            self.selection.append(loc)
        else:
            self.selection = []

    @register_instruction('recenter')
    def recenter(self, arg: ImplicitInstructionArgument) -> None:
        arg = LocatorInstructionsDict(arg)
        new_center = [Locator.from_dict(arg)]
        new_locators = [Locator.from_dict(dict(loc._asdict(), at=new_center))
                        for loc in self.selection]
        self.selection = new_locators

    @register_instruction('group')
    def group(self, label: str) -> None:
        group_registry[label] = deepcopy(self.selection)
        self.clear_selection_after_use()

    @register_instruction('centroid')
    def centroid(self, label: str) -> None:
        for ms_key, ms in self.model_states.items():
            focus = ms.nodes.locate(self.selection)
            c_fract = focus.fractionalise(focus.centroid)
            c_atoms = {'label': [label], 'fract_x': [c_fract[0]],
                       'fract_y': [c_fract[1]], 'fract_z': [c_fract[2]], }
            atoms = pd.DataFrame.from_records(c_atoms).set_index('label')
            ms.centroids += AtomSet(focus.base, atoms)
        self.clear_selection_after_use()

    @register_instruction('line')
    def line(self, label: str) -> None:
        for ms_key, ms in self.model_states.items():
            focus = ms.nodes.locate(self.selection)
            ms.shapes[label] = focus.line
        self.clear_selection_after_use()

    @register_instruction('plane')
    def plane(self, label: str) -> None:
        for ms_key, ms in self.model_states.items():
            focus = ms.nodes.locate(self.selection)
            ms.shapes[label] = focus.plane
        self.clear_selection_after_use()

    @register_instruction('distance')
    def distance(self, label: str) -> None:
        for ms_key, ms in self.model_states.items():
            shapes = []
            for locator in self.selection:
                if (shape_label := locator.label) in ms.shapes:
                    shapes.append(ms.shapes[shape_label])
                else:
                    shapes.append(ms.nodes.locate([locator]))
            assert len(shapes) == 2
            distance = shapes[0].distance(shapes[1])
            self.evaluation_table.loc[ms_key, label] = distance
        self.clear_selection_after_use()

    @register_instruction('angle')
    def angle(self, label: str) -> None:
        for ms_key, ms in self.model_states.items():
            shapes = []
            for locator in self.selection:
                if (shape_label := locator.label) in ms.shapes:
                    shapes.append(ms.shapes[shape_label])
                else:
                    shapes.append(ms.nodes.locate([locator]))
            assert len(shapes)
            angle = shapes[0].angle(*shapes[1:])
            self.evaluation_table.loc[ms_key, label] = angle
        self.clear_selection_after_use()

    @register_instruction('write')
    def write(self, csv_name: str) -> None:
        self.evaluation_table.to_csv(path_or_buf=csv_name)

    @register_instruction('clear')
    def clear(self, *_):
        self.__init__()

    @register_instruction('set')
    def set(self, new_settings: dict) -> None:
        self.settings.update(new_settings)


def process(routine: Routine) -> Processor:
    processor = Processor()
    for instruction in routine:
        processor.process(instruction)
    return processor


if __name__ == '__main__':
    p = Processor()
    print(p.instructions)
    print(p.instructions['load'])
    print(p.instructions['load'](p, {'block': '123'}))
