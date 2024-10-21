from collections import UserDict

import logging
from typing import Callable, Dict, List, Union

import pandas as pd

from picometer.atom import Locator
from picometer.models import ModelStates
from picometer.instructions import Instruction, Routine
from picometer.settings import Settings


logger = logging.getLogger(__name__)


def explicit_kwargs(**expected_kwargs: type) -> type:  # TODO RM
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


@registers_instructions  # TODO RM END
class Processor:
    """
    This is the main class responsible for controlling, processing,
    storing current state, importing, exporting the current state
    of work performed in picometer.
    """
    instructions: Dict[str, Callable] = {}

    def __init__(self, settings: Settings = None) -> None:
        self.evaluation_table = pd.DataFrame()
        self.history = Routine()
        self.model_states: ModelStates = ModelStates()
        self.selection: List[Locator] = []
        self.settings = Settings.from_yaml()
        if settings:
            self.settings.update(settings)
        logger.info(f'Initialized processor {self}')

    def process(self, instruction: Instruction) -> None:
        handler = instruction.handler(self)
        handler.handle(instruction)
        self.history.append(instruction)
        logger.info(f'{self} processed {instruction}')


def process(routine: Routine) -> Processor:
    logger.info(f'Bulk-processing {routine}')
    processor = Processor()
    for instruction in routine:
        processor.process(instruction)
    return processor

# TODO RM
if __name__ == '__main__':
    p = Processor()
    print(p.instructions)
    print(p.instructions['load'])
    print(p.instructions['load'](p, {'block': '123'}))
