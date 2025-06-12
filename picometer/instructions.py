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
from glob import glob
import logging
from pathlib import Path
from typing import Any, Union, Protocol

from numpy import rad2deg
import pandas as pd
import yaml

from picometer.atom import group_registry, AtomSet, Locator
from picometer.models import ModelState, ModelStates
from picometer.shapes import ExplicitShape

logger = logging.getLogger(__name__)


# ~~~~~~~~~~~~~~~~~~~ INSTRUCTION AND ROUTINE DECLARATIONS ~~~~~~~~~~~~~~~~~~~ #


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

    def __eq__(self, other):
        if isinstance(other, Instruction):
            return self.handler == other.handler and self.kwargs == other.kwargs
        return NotImplemented

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.as_dict()})'

    @property
    def handler(self) -> 'type(BaseInstructionHandler)':
        return BaseInstructionHandlerType.REGISTRY[self.keyword]

    @property
    def kwargs(self) -> dict[str, Any]:
        expected_kwargs = self.handler.kwargs
        if expected_kwargs is None:
            return self.raw_kwargs
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

    def as_dict(self) -> dict[str: Union[str, dict]]:
        return {self.keyword: self.raw_kwargs}


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

    def as_dict(self) -> dict[str, list[dict]]:
        return {'instructions': [i.as_dict() for i in self]}

    def to_yaml(self, path: Union[str, Path]) -> None:
        with open(path, 'w') as yaml_file:
            yaml.dump(self.as_dict(), yaml_file)


# ~~~~~~~~~~~~~~~~~~~ INSTRUCTION REGISTRY AND BASE CLASSES ~~~~~~~~~~~~~~~~~~ #


class ProcessorProtocol(Protocol):
    evaluation_table: pd.DataFrame
    history: Routine
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
    Must define the following attributes and methods:
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
        logger.info('Cleared selection')

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

    def _collect_shapes(self, ms: ModelState) -> list[ExplicitShape]:
        shapes = []
        for locator in self.processor.selection:
            if (shape_label := locator.label) in ms.shapes:
                shapes.append(ms.shapes[shape_label])
            else:
                shapes.append(ms.nodes.locate([locator]))
        return shapes


# ~~~~~~~~~~~~~~~~~~~~ CONCRETE INSTRUCTIONS DECLARATIONS ~~~~~~~~~~~~~~~~~~~~ #


class LoadInstructionHandler(BaseInstructionHandler):
    name = 'load'
    kwargs = dict(path=str, block=str)

    def handle(self, instruction: Instruction) -> None:
        cif_path = instruction.kwargs['path']
        block_name = instruction.kwargs['block']
        if Path(cif_path).is_file():
            self._load_model_state(cif_path, block_name)
        else:
            for cif_path in sorted(glob(cif_path)):
                self._load_model_state(cif_path, block_name)

    def _load_model_state(self, cif_path, block_name):
        atoms = AtomSet.from_cif(cif_path=cif_path, block_name=block_name)
        label = cif_path + (':' + block_name if block_name else '')
        self.processor.model_states[label] = ModelState(atoms=atoms)
        logger.info(f'Loaded model state {label}')
        if not self.processor.settings['auto_write_unit_cell']:
            return
        et = self.processor.evaluation_table
        et.loc[label, 'unit_cell_a'] = atoms.base.a_d
        et.loc[label, 'unit_cell_b'] = atoms.base.b_d
        et.loc[label, 'unit_cell_c'] = atoms.base.c_d
        et.loc[label, 'unit_cell_al'] = rad2deg(atoms.base.al_d)
        et.loc[label, 'unit_cell_be'] = rad2deg(atoms.base.be_d)
        et.loc[label, 'unit_cell_ga'] = rad2deg(atoms.base.ga_d)
        et.loc[label, 'unit_cell_v'] = atoms.base.v_d


class SelectInstructionHandler(BaseInstructionHandler):
    name = 'select'
    kwargs = dict(label=str, symm=str, at=Locator)

    def handle(self, instruction: Instruction) -> None:
        loc = Locator.from_dict(instruction.kwargs)
        if loc:
            self.processor.selection.append(loc)
            logger.info(f'Added {loc} to current selection')
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
        logger.info(f'Recentered selection, current: {self.processor.selection}')


class GroupInstructionHandler(BaseInstructionHandler):
    name = 'group'
    kwargs = dict(label=str)

    def handle(self, instruction: Instruction) -> None:
        group = deepcopy(self.processor.selection)
        label = instruction.kwargs['label']
        group_registry[label] = group
        logger.info(f'Defined new group {label} from selection {group}')
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
        centroid = AtomSet(focus.base, atoms)
        ms.centroids += centroid
        logger.info(f'Defined centroid {label}: {centroid} for model state {ms_key}')


class LineInstructionHandler(SerialInstructionHandler):
    name = 'line'
    kwargs = dict(label=str)

    def handle_one(self, instruction: Instruction, ms_key: str, ms: ModelState) -> None:
        label = instruction.kwargs['label']
        focus = ms.nodes.locate(self.processor.selection)
        line = focus.line
        ms.shapes[label] = line
        logger.info(f'Defined line {label}: {line} for model state {ms_key}')


class PlaneInstructionsHandler(SerialInstructionHandler):
    name = 'plane'
    kwargs = dict(label=str)

    def handle_one(self, instruction: Instruction, ms_key: str, ms: ModelState) -> None:
        label = instruction.kwargs['label']
        focus = ms.nodes.locate(self.processor.selection)
        plane = focus.plane
        ms.shapes[label] = plane
        logger.info(f'Defined plane {label}: {plane} for model state {ms_key}')


class CoordinatesInstructionHandler(SerialInstructionHandler):
    name = 'coordinates'
    kwargs = None

    def handle_one(self, instruction: Instruction, ms_key: str, ms: ModelState) -> None:
        focus = ms.nodes.locate(self.processor.selection)
        for label, coords in focus.table.iterrows():
            self.processor.evaluation_table.loc[ms_key, label + '_x'] = coords.fract_x
            self.processor.evaluation_table.loc[ms_key, label + '_y'] = coords.fract_y
            self.processor.evaluation_table.loc[ms_key, label + '_z'] = coords.fract_z
        logger.info(f'Noted coordinates for current selection in model state {ms_key}')


class DisplacementInstructionHandler(SerialInstructionHandler):
    name = 'displacement'
    kwargs = None

    def handle_one(self, instruction: Instruction, ms_key: str, ms: ModelState) -> None:
        focus = ms.nodes.locate(self.processor.selection)
        for label, displacements in focus.table.iterrows():
            for suffix in 'Uiso U11 U22 U33 U23 U13 U12'.split():
                label_ = label + '_' + suffix
                value = getattr(displacements, suffix, None)
                if value is not None:
                    self.processor.evaluation_table.loc[ms_key, label_] = value
        logger.info(f'Noted displacement for current selection in model state {ms_key}')


class DistanceInstructionHandler(SerialInstructionHandler):
    name = 'distance'
    kwargs = dict(label=str)

    def handle_one(self, instruction: Instruction, ms_key: str, ms: ModelState) -> None:
        label = instruction.kwargs['label']
        shapes = self._collect_shapes(ms)
        assert len(shapes) == 2
        distance = shapes[0].distance(shapes[1])
        self.processor.evaluation_table.loc[ms_key, label] = distance
        logger.info(f'Evaluated distance {label}: {distance} for model state {ms_key}')


class AngleInstructionHandler(SerialInstructionHandler):
    name = 'angle'
    kwargs = dict(label=str)

    def handle_one(self, instruction: Instruction, ms_key: str, ms: ModelState) -> None:
        label = instruction.kwargs['label']
        shapes = self._collect_shapes(ms)
        assert len(shapes)
        angle = shapes[0].angle(*shapes[1:])
        self.processor.evaluation_table.loc[ms_key, label] = angle
        logger.info(f'Evaluated angle {label}: {angle} for model state {ms_key}')


class DihedralInstructionHandler(SerialInstructionHandler):
    name = 'dihedral'
    kwargs = dict(label=str)

    def handle_one(self, instruction: Instruction, ms_key: str, ms: ModelState) -> None:
        label = instruction.kwargs['label']
        shapes = self._collect_shapes(ms)
        assert len(shapes) == 4 and all(s.kind is s.Kind.spatial for s in shapes)
        dihedral = shapes[0].dihedral(*shapes[1:])  # noqa: shapes: list[AtomSet]
        self.processor.evaluation_table.loc[ms_key, label] = dihedral
        logger.info(f'Evaluated dihedral {label}: {dihedral} for model state {ms_key}')


class WriteInstructionHandler(BaseInstructionHandler):
    name = 'write'
    kwargs = dict(path=Path)

    def handle(self, instruction: Instruction) -> None:
        path = instruction.kwargs['path']
        self.processor.evaluation_table.to_csv(path_or_buf=path)
        logger.info(f'Saved current evaluation table to {path}')


class ClearInstructionHandler(BaseInstructionHandler):
    name = 'clear'
    kwargs = dict()

    def handle(self, instruction: Instruction) -> None:
        self.processor.__init__()
        logger.info('Reinitialized processor')


class SetInstructionHandler(BaseInstructionHandler):
    name = 'set'
    kwargs = None  # any kwarg is acceptable

    def handle(self, instruction: Instruction) -> None:
        new_settings = instruction.raw_kwargs
        self.processor.settings.update(new_settings)
