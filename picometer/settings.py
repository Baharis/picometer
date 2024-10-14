from collections import UserDict
from dataclasses import asdict, dataclass, fields, Field
from importlib import resources
from typing import Union

import yaml


class SettingsError(KeyError):
    """Custom `KeyError` raised when there are issues with `DefaultSettings`"""


@dataclass
class DefaultSettings:
    """Store default values of all settings. Use `AnyValue` if no default."""
    clear_selection_after_use: bool = True

    @classmethod
    def get_field(cls, key: str) -> Field:
        if fields_ := [f for f in fields(cls) if f.name == key]:  # noqa
            return fields_[0]
        raise SettingsError(f'Unknown setting name {key!r}')


class Settings(UserDict):
    """Automatically set self from `DefaultSettings` on init, handle settings"""

    @classmethod
    def from_yaml(cls, path=None) -> 'Settings':
        settings_stream = open(path, 'r') if path \
            else resources.open_text('picometer', 'settings.yaml')
        with settings_stream:
            return cls(yaml.safe_load(settings_stream)['settings'])

    def __init__(self, data: dict = None) -> None:
        super().__init__(asdict(DefaultSettings()))  # noqa
        if data:
            self.update(data)

    def __setitem__(self, key, value, /) -> None:
        field = DefaultSettings.get_field(key)
        super().__setitem__(key, field.type(value))

    def __delitem__(self, key, /) -> None:
        field = DefaultSettings.get_field(key)
        super().__setitem__(key, field.default)

    def update(self, other: Union[dict, UserDict] = None, /, **kwargs) -> None:
        other = {**other, **kwargs} if other else kwargs
        for key, value in other.items():
            self[key] = value
