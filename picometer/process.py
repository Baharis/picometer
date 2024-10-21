import logging
from typing import Callable, Dict, List

import pandas as pd

from picometer.atom import Locator
from picometer.models import ModelStates
from picometer.instructions import Instruction, Routine
from picometer.settings import Settings


logger = logging.getLogger(__name__)


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
