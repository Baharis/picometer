import abc
from dataclasses import dataclass

import pandas as pd

from atom import AtomSet
from collections import UserDict, deque
from typing import Dict, Tuple


@dataclass
class ModelState:
    """Class describing atomsets, selections, and shapes in one structure"""
    selections: Dict[str, AtomSet]


ModelStates = Dict[Tuple[str, str], ModelState]


EvaluationTable = pd.DataFrame
"""Type describing all collected measurements of distanced, angles etc."""


class Routine(UserDict):
    """A set of individual instructions to be performed in processor"""


class RoutineQueue(deque[Routine]):
    """A queue of individual routines to be performed sequentially"""


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

    @abc.abstractmethod
    def __call__(self, mss: ModelStates, et: EvaluationTable) -> ProcessOut:
        pass


class LoadProcess(BaseProcess):
    """Load crystal data from input cif file to a `ModelState`"""
    keyword = 'load'

    def __call__(self, mss: ModelStates, et: EvaluationTable) -> ProcessOut:
        # TODO: read selected block if specified
        model_states: ModelStates = {}
        for cif_block_address in self.routine['load']:
            atomset = AtomSet.from_cif(cif_path=cif_block_address['path'])
            model_state = ModelState(selections=atomset.atomized)
            label = (cif_block_address['path'], cif_block_address['block'])
            model_states[label] = model_state
        return model_states, et


class SelectProcess(BaseProcess):
    keyword = 'select'

    def __call__(self, mss: ModelStates, et: EvaluationTable) -> ProcessOut:
        selection_name = self.routine['select']
        for ms in mss.values():
            selection = AtomSet()
            for from_item in self.routine['from']:
                sel = ms.selections[from_item['name']]
                if symm_op_code := from_item.get('symm'):
                    sel.transform2(symm_op_code=symm_op_code)
                selection += sel
            ms.selections[selection_name] = selection
        return mss, et


class CentroidProcess(BaseProcess):
    keyword = 'centroid'

    def __call__(self, mss: ModelStates, et: EvaluationTable) -> ProcessOut:
        centroid_name = self.routine['centroid']
        for ms in mss.values():
            selection = AtomSet()
            for from_item in self.routine['from']:
                sel = ms.selections[from_item['name']]
                if symm_op_code := from_item.get('symm'):
                    sel.transform2(symm_op_code=symm_op_code)
                selection += sel
            c_fract = selection.fractionalise(selection.centroid)
            c_atoms = {'label': centroid_name, 'fract_x': c_fract[0],
                       'fract_y': c_fract[1], 'fract_z': c_fract[2], }
            atoms = pd.DataFrame.from_records(c_atoms).set_index('label')
            ms.selections[centroid_name] = AtomSet(selection.base, atoms)
        return mss, et


def main():
    pass


if __name__ == '__main__':
    main()
