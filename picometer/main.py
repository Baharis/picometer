import abc
from typing import Dict, List, Tuple

import pandas as pd

from picometer.atom import alias_registry, AtomSet, Locator
from picometer.routine import Routine, RoutineQueue
from picometer.shapes import Shape, ExplicitShape, degrees_between

# TODO use multipledispatch for calculating distances, angles?


class ModelState:
    """Class describing atomsets, selections, and shapes in one structure"""
    def __init__(self,
                 atoms: AtomSet,
                 centroids: AtomSet = AtomSet(),
                 shapes: Dict[str, ExplicitShape] = None):
        self.atoms: AtomSet = atoms
        self.centroids: AtomSet = centroids
        self.shapes: Dict[str, ExplicitShape] = shapes if shapes else {}

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
        return [Locator.from_dict(from_item)
                for from_item in self.routine['from']]


class LoadProcess(BaseProcess):
    """Load crystal data from input cif file to a `ModelState`"""
    keyword = 'load'

    def __call__(self, mss: ModelStates, et: EvaluationTable) -> ProcessOut:
        # TODO: read selected block if specified
        model_states: ModelStates = {}
        for cif_block_address in self.routine['load']:
            cif_path = cif_block_address['path']
            block_name = cif_block_address.get('block')
            atoms = AtomSet.from_cif(cif_path=cif_path, block_name=block_name)
            label = cif_path + (':' + block_name if block_name else '')
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


class LineProcess(BaseProcess):
    keyword = 'line'

    def __call__(self, mss: ModelStates, et: EvaluationTable) -> ProcessOut:
        line_name = self.routine[self.keyword]
        for ms_key, ms in mss.items():
            focus = ms.nodes.locate(self.routine_locator_list)
            ms.shapes[line_name] = focus.line
        return mss, et


class PlaneProcess(BaseProcess):
    keyword = 'plane'

    def __call__(self, mss: ModelStates, et: EvaluationTable) -> ProcessOut:
        plane_name = self.routine[self.keyword]
        for ms_key, ms in mss.items():
            focus = ms.nodes.locate(self.routine_locator_list)
            ms.shapes[plane_name] = focus.plane
        return mss, et


class DistanceProcess(BaseProcess):
    keyword = 'distance'

    def __call__(self, mss: ModelStates, et: EvaluationTable) -> ProcessOut:
        dist_name = self.routine[self.keyword]
        for ms_key, ms in mss.items():
            shapes: List[Shape] = []
            for from_item in self.routine['from']:
                if shape_name := from_item['name'] in ms.shapes:
                    shapes.append(ms.shapes[shape_name])
                else:
                    loc = Locator.from_dict(from_item)
                    shapes.append(ms.nodes.locate([loc]))
            assert len(shapes) == 2
            et[ms_key, dist_name] = shapes[0].distance(shapes[1])
        return mss, et


class AngleProcess(BaseProcess):
    keyword = 'angle'

    def __call__(self, mss: ModelStates, et: EvaluationTable) -> ProcessOut:
        angle_name = self.routine[self.keyword]
        for ms_key, ms in mss.items():
            shapes: List[Shape] = []
            for from_item in self.routine['from']:
                if shape_name := from_item['name'] in ms.shapes:
                    shapes.append(ms.shapes[shape_name])
                else:
                    loc = Locator(from_item['name'], from_item.get('symm'))
                    shapes.append(ms.nodes.locate([loc]))
            if len(shapes) == 2:
                assert not any(s.kind is Shape.Kind.spatial for s in shapes)
                et[ms_key, angle_name] = shapes[0].angle(shapes[1])
            if len(shapes) in {3, 4}:
                assert all(isinstance(s, AtomSet) for s in shapes)
                shapes: List[AtomSet]
                line1 = (shapes[0] + shapes[1]).line
                line2 = (shapes[-1] + shapes[-2]).line
                et[ms_key, angle_name] = line1.angle(line2)
        return mss, et


class WriteProcess(BaseProcess):
    keyword = 'write'

    def __call__(self, mss: ModelStates, et: EvaluationTable) -> ProcessOut:
        et.to_csv(path_or_buf=self.routine['write'])
        return mss, et


def process_routine_queue(rq: RoutineQueue) -> ProcessOut:
    mss = ModelStates()
    et = EvaluationTable()
    for routine in rq:
        process = BaseProcess.from_routine(routine)
        mss, et = process(mss, et)
    return mss, et


def main():
    from picometer.parser import parse_path
    routine_queue = parse_path('../example.yaml')
    process_routine_queue(routine_queue)


if __name__ == '__main__':
    main()
