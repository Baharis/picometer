from typing import List
import yaml

from picometer.routine import Routine


def parse(text: str) -> Routine:
    yaml_segments = yaml.load_all(text, yaml.Loader)
    return [Routine(y) for y in yaml_segments]


def parse_path(path: str) -> List[Routine]:
    with open(path, 'r') as file:
        return parse(file.read())
