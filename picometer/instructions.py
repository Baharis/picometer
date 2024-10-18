"""
Picometer routine file in a yaml file that contains a list of settings
and instructions to be sequentially executed by the parser.
In accordance with the yaml format, the file can comprise several
"yaml files" / "picometer routines" seperated by "\n---".
However, these "files"/"routines" are ultimately concatenated
and converted into a list of instructions.
"""
import abc
from collections import deque
from copy import deepcopy
from pathlib import Path
from typing import Any, Union, Protocol

import pandas as pd
import yaml

from picometer.atom import group_registry, AtomSet, Locator
from picometer.models import ModelState, ModelStates


class Instruction:
    """An individual atomic instruction to be processed by the processor"""
    def __init__(self, raw_instruction: Union[dict, str] = None, /, **kwargs):
        input_ = {}
        if raw_instruction is not None:
            if isinstance(raw_instruction, str):
                input_.update({raw_instruction: {}})
            else:  # if isinstance(raw_instruction, dict)
                input_.update(raw_instruction)
        if kwargs:
            input_.update(kwargs)
        if len(input_) != 1:
            raise ValueError(f'{input_=} must contain exactly one key:value pair')
        self.keyword: str = next(iter(input_.keys()))
        self.raw_kwargs: Union[str, dict[str, Any]] = next(iter(input_.values()))

    @property
    def handler(self) -> 'BaseInstructionHandler':
        return BaseInstructionHandlerType.REGISTRY[self.keyword]

    @property
    def kwargs(self) -> dict[str, Any]:
        expected_kwargs = self.handler.kwargs
        kwargs_ = {ek_key: None for ek_key in expected_kwargs.keys()}
        if isinstance(self.raw_kwargs, dict):
            for raw_kwarg_key, raw_kwarg_value in self.raw_kwargs.items():
                if raw_kwarg_key not in expected_kwargs.keys():
                    raise KeyError(f'Unknown instruction argument: {raw_kwarg_key}')
                expected_kwarg_type = expected_kwargs[raw_kwarg_key]
                kwargs_[raw_kwarg_key] = expected_kwarg_type(raw_kwarg_value)
        else:  # if isinstance(self.raw_kwargs, str)
            expected_kwarg_key = list(expected_kwargs.keys())[0]
            expected_kwarg_type = list(expected_kwargs.values())[0]
            kwargs_[expected_kwarg_key] = expected_kwarg_type(self.raw_kwargs)
        return kwargs_


class Routine(deque[Instruction]):
    """
    A queue of subsequent `Instruction`s to be executed by the processor.
    It can be created either in a single step from an input file,
    or by iteratively right-appending individual instructions.
    """

    @classmethod
    def concatenate(cls, routines: list['Routine']):
        new_routine = routines.pop(0) if routines else Routine()
        while routines:
            new_routine.append(Instruction('clear'))
            new_routine.extend(routines.pop(0))
        return cls(new_routine)

    @classmethod
    def from_dict(cls, dict_: dict) -> 'Routine':
        new_routine = []
        if settings := dict_.get('settings'):
            for k, v in settings.items():
                new_routine.append(Instruction(set={k: v}))
        if instructions := dict_.get('instructions'):
            for raw_instruction in instructions:
                new_routine.append(Instruction(raw_instruction))
        return cls(new_routine)

    @classmethod
    def from_string(cls, text: str) -> 'Routine':
        yaml_segments = yaml.load_all(text, yaml.SafeLoader)
        return cls.concatenate([cls.from_dict(y) for y in yaml_segments])

    @classmethod
    def from_yaml(cls, path: Union[str, Path]) -> 'Routine':
        with open(path, 'r') as yaml_file:
            return cls.from_string(yaml_file.read())


class ProcessorProtocol(Protocol):
    evaluation_table: pd.DataFrame
    model_states: ModelStates
    selection: list[Locator]
    settings: dict[str, Any]


class BaseInstructionHandlerType(type):
    """Metaclass that automatically registers new handlers in `REGISTRY`"""
    REGISTRY = {}

    def __new__(mcs, *args, **kwargs) -> 'BaseInstructionHandlerType':
        new_cls = type.__new__(mcs, *args, **kwargs)
        if name := getattr(new_cls, 'name', ''):
          mcs.REGISTRY[name] = new_cls
        return new_cls


class BaseInstructionHandler(metaclass=BaseInstructionHandlerType):
    """
    Base `InstructionHandler` class to be used for managing all instructions.
    Must define the following attrubutes and methods:
    - `name`: if given, auto-registers handler in the REGISTRY
    - `kwargs`: if given, auto-converts string arguments into dict
    - `handle()`: the method called be processor to handle instruction
    """

    # Abstract class attributes and methods to be defined by all child handlers

    name: str = None
    kwargs: dict[str: type] = None

    @abc.abstractmethod
    def handle(self, instruction: Instruction) -> None:
        """Alter the state of the processor according to the instruction"""

    # Common base methods accessible to all child handlers

    def __init__(self, processor: ProcessorProtocol) -> None:
        self.processor = processor

    def clear_selection(self):
        self.processor.selection = []

    def clear_selection_after_use(self) -> None:
        if self.processor.settings.get('clear_selection_after_use'):
            self.clear_selection()


class SerialInstructionHandler(BaseInstructionHandler):
    """Handlers that handle model states independently and exhausts selection"""
    def handle(self, instruction: Instruction) -> None:
        for ms_key, ms in self.processor.model_states.items():
            self.handle_one(instruction, ms_key, ms)
        self.clear_selection_after_use()

    @abc.abstractmethod
    def handle_one(self, instruction: Instruction, ms_key: str, ms: ModelState) -> None:
        """Abstract function to handle a process a single model state"""


class LoadInstructionHandler(BaseInstructionHandler):
    name = 'load'
    kwargs = dict(path=str, block=str)

    def handle(self, instruction: Instruction) -> None:
        cif_path = instruction.kwargs['path']
        block_name = instruction.kwargs['block']
        atoms = AtomSet.from_cif(cif_path=cif_path, block_name=block_name)
        label = cif_path + (':' + block_name if block_name else '')
        self.processor.model_states[label] = ModelState(atoms=atoms)


class SelectInstructionHandler(BaseInstructionHandler):
    name = 'select'
    kwargs = dict(label=str, symm=str, at=Locator)

    def handle(self, instruction: Instruction) -> None:
        loc = Locator.from_dict(instruction.kwargs)
        print(loc)
        print(type(loc))
        if loc:
            self.processor.selection.append(loc)
        else:
            self.clear_selection()


class RecenterInstructionHandler(BaseInstructionHandler):
    name = 'recenter'
    kwargs = dict(label=str, symm=str, at=Locator)

    def handle(self, instruction: Instruction) -> None:
        new_center = [Locator.from_dict(instruction.kwargs)]
        new_locators = [Locator.from_dict(dict(loc._asdict(), at=new_center))
                        for loc in self.processor.selection]
        self.processor.selection = new_locators


class GroupInstructionHandler(BaseInstructionHandler):
    name = 'group'
    kwargs = dict(label=str)

    def handle(self, instruction: Instruction) -> None:
        group = deepcopy(self.processor.selection)
        label = instruction.kwargs['label']
        group_registry[label] = group
        self.clear_selection_after_use()


class CentroidInstructionHandler(SerialInstructionHandler):
    name = 'centroid'
    kwargs = dict(label=str)

    def handle_one(self, instruction: Instruction, ms_key: str, ms: ModelState) -> None:
        label = instruction.kwargs['label']
        focus = ms.nodes.locate(self.processor.selection)
        c_fract = focus.fractionalise(focus.centroid)
        c_atoms = {'label': [label], 'fract_x': [c_fract[0]],
                   'fract_y': [c_fract[1]], 'fract_z': [c_fract[2]], }
        atoms = pd.DataFrame.from_records(c_atoms).set_index('label')
        ms.centroids += AtomSet(focus.base, atoms)


class LineInstructionHandler(SerialInstructionHandler):
    name = 'line'
    kwargs = dict(label=str)

    def handle_one(self, instruction: Instruction, ms_key: str, ms: ModelState) -> None:
        label = instruction.kwargs['label']
        focus = ms.nodes.locate(self.processor.selection)
        ms.shapes[label] = focus.line


class PlaneInstructionsHandler(SerialInstructionHandler):
    name = 'plane'
    kwargs = dict(label=str)

    def handle_one(self, instruction: Instruction, ms_key: str, ms: ModelState) -> None:
        label = instruction.kwargs['label']
        focus = ms.nodes.locate(self.processor.selection)
        ms.shapes[label] = focus.plane


class DistanceInstructionHandler(SerialInstructionHandler):
    name = 'distance'
    kwargs = dict(label=str)

    def handle_one(self, instruction: Instruction, ms_key: str, ms: ModelState) -> None:
        label = instruction.kwargs['label']
        shapes = []
        for locator in self.processor.selection:
            if (shape_label := locator.label) in ms.shapes:
                shapes.append(ms.shapes[shape_label])
            else:
                shapes.append(ms.nodes.locate([locator]))
        assert len(shapes) == 2
        distance = shapes[0].distance(shapes[1])
        self.processor.evaluation_table.loc[ms_key, label] = distance


class AngleInstructionHandler(SerialInstructionHandler):
    name = 'angle'
    kwargs = dict(label=str)

    def handle_one(self, instruction: Instruction, ms_key: str, ms: ModelState) -> None:
        label = instruction.kwargs['label']
        shapes = []
        for locator in self.processor.selection:
            if (shape_label := locator.label) in ms.shapes:
                shapes.append(ms.shapes[shape_label])
            else:
                shapes.append(ms.nodes.locate([locator]))
        assert len(shapes)
        angle = shapes[0].angle(*shapes[1:])
        self.processor.evaluation_table.loc[ms_key, label] = angle


class WriteInstructionHandler(BaseInstructionHandler):
    name = 'write'
    kwargs = dict(path=Path)

    def handle(self, instruction: Instruction) -> None:
        path = instruction.kwargs['path']
        self.processor.evaluation_table.to_csv(path_or_buf=path)


class ClearInstructionHandler(BaseInstructionHandler):
    name = 'clear'
    kwargs = dict()

    def handle(self, instruction: Instruction) -> None:
        self.processor.__init__()


class SetInstructionHandler(BaseInstructionHandler):
    name = 'set'
    kwargs = None  # any kwarg is acceptable

    def handle(self, instruction: Instruction) -> None:
        new_settings = instruction.raw_kwargs
        self.processor.settings.update(new_settings)
