import abc
from collections import UserDict
from dataclasses import dataclass
from typing import Dict, List, Tuple

import pandas as pd

from picometer.atom import alias_registry, AtomSet, Locator
from picometer.routine import Routine, RoutineQueue


@dataclass
class ModelState:
    """Class describing atomsets, selections, and shapes in one structure"""
    atoms: AtomSet
    centroids: AtomSet = AtomSet()

    @property
    def nodes(self):
        return self.atoms + self.centroids


class ModelStates(Dict[Tuple[str, str], ModelState]):
    pass


EvaluationTable = pd.DataFrame
"""Type describing all collected measurements of distanced, angles etc."""


class ProcessRegistrar(abc.ABCMeta):
    """Metaclass for processors which registers them under their `keyword`"""
    REGISTRY = {}

    def __new__(mcs, name, bases, attrs):
        new_cls = type.__new__(mcs, name, bases, attrs)
        if hasattr(new_cls, 'keyword') and new_cls.keyword:
            mcs.REGISTRY[new_cls.keyword] = new_cls
        return new_cls


ProcessOut = Tuple[ModelStates, EvaluationTable]


class BaseProcess(metaclass=ProcessRegistrar):
    """Base class for every processor"""

    def __init__(self, routine: Routine) -> None:
        self.routine = routine

    @classmethod
    def from_routine(cls, routine: Routine) -> 'BaseProcess':
        registered_processes = ProcessRegistrar.REGISTRY.keys()
        for registered_process in registered_processes:
            if registered_process in routine.keys():
                return ProcessRegistrar.REGISTRY[registered_process](routine)

    @abc.abstractmethod
    def __call__(self, mss: ModelStates, et: EvaluationTable) -> ProcessOut:
        pass

    @property
    def routine_locator_list(self) -> List[Locator]:
        return [Locator(from_item['name'], from_item.get('symm', None))
                for from_item in self.routine['from']]


class LoadProcess(BaseProcess):
    """Load crystal data from input cif file to a `ModelState`"""
    keyword = 'load'

    def __call__(self, mss: ModelStates, et: EvaluationTable) -> ProcessOut:
        # TODO: read selected block if specified
        model_states: ModelStates = {}
        for cif_block_address in self.routine['load']:
            atoms = AtomSet.from_cif(cif_path=cif_block_address['path'])
            label = (cif_block_address['path'], cif_block_address['block'])
            model_states[label] = ModelState(atoms=atoms)
        return model_states, et


class AliasProcess(BaseProcess):
    keyword = 'alias'

    def __call__(self, mss: ModelStates, et: EvaluationTable) -> ProcessOut:
        alias_name = self.routine[self.keyword]
        alias_registry[alias_name] = self.routine_locator_list
        return mss, et


class CentroidProcess(BaseProcess):
    keyword = 'centroid'

    def __call__(self, mss: ModelStates, et: EvaluationTable) -> ProcessOut:
        centroid_name = self.routine[self.keyword]
        for ms_key, ms in mss.items():
            focus = ms.nodes.locate(self.routine_locator_list)
            c_fract = focus.fractionalise(focus.centroid)
            c_atoms = {'label': centroid_name, 'fract_x': c_fract[0],
                       'fract_y': c_fract[1], 'fract_z': c_fract[2], }
            atoms = pd.DataFrame.from_records(c_atoms).set_index('label')
            ms.centroids += AtomSet(focus.base, atoms)
        return mss, et


def process_routine_queue(rq: RoutineQueue):
    mss = ModelStates()
    et = EvaluationTable()
    for routine in rq:
        process = BaseProcess.from_routine(routine)
        mss, et = process(mss, et)
    return et


def main():
    from picometer.parser import parse_path
    routine_queue = parse_path('../example.yaml')
    print(routine_queue)
    process_routine_queue(routine_queue)


if __name__ == '__main__':
    main()
