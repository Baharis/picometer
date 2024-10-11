"""
Picometer routine file in a yaml file that contains a list of settings
and instructions to be sequentially executed by the parser.
In accordance with the yaml format, the file can comprise several
"yaml files" / "picometer routines" seperated by "\n---".
However, these "files"/"routines" are ultimately concatenated
and converted into a list of instructions.
"""


from collections import UserList
from pathlib import Path
from typing import Union
import yaml


class Routine(UserList):
    """A list of subsequent instructions originating from a single yaml file"""

    @classmethod
    def concatenate(cls, routines: list['Routine']):
        new_routine = routines.pop(0) if routines else Routine()
        while routines:
            new_routine.append('clear')
            new_routine.extend(routines.pop(0))
        return cls(new_routine)

    @classmethod
    def from_dict(cls, dict_: dict) -> 'Routine':
        new_routine = []
        if settings := dict_.get('settings'):
            new_routine.append({'set': settings})
        if instructions := dict_.get('instructions'):
            new_routine.extend(instructions)
        return cls(new_routine)

    @classmethod
    def from_string(cls, text: str) -> 'Routine':
        yaml_segments = yaml.load_all(text, yaml.SafeLoader)
        return cls.concatenate([cls.from_dict(y) for y in yaml_segments])

    @classmethod
    def from_yaml(cls, path: Union[str, Path]) -> 'Routine':
        with open(path, 'r') as yaml_file:
            return cls.from_string(yaml_file.read())
