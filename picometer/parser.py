import yaml

from picometer.routine import Routine, RoutineQueue


def parse(text: str) -> RoutineQueue:
    yaml_segments = yaml.load_all(text, yaml.Loader)
    return RoutineQueue([Routine(y) for y in yaml_segments])


def parse_path(path: str) -> RoutineQueue:
    with open(path, 'r') as file:
        return parse(file.read())
