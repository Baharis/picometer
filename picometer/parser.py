from pathlib import Path
from typing import List, Union
import yaml

from picometer.routine import Routine


def parse(text: str) -> List[Routine]:
    yaml_segments = yaml.load_all(text, yaml.Loader)
    return [Routine(y) for y in yaml_segments]


def parse_path(path: Union[str, Path]) -> List[Routine]:
    with open(path, 'r') as file:
        return parse(file.read())
