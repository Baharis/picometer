from collections import UserDict
from dataclasses import asdict, dataclass, fields, Field
from importlib import resources

from picometer.parser import parse_path


class SettingsError(KeyError):
    """Custom `KeyError` raised when there is any issues with `Settings`"""


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
        with resources.path('picometer', 'settings.yaml') as settings_path:
            path = settings_path if path is None else path
            return cls({k: v for s in parse_path(path) for k, v in s.items()})

    def __init__(self, data) -> None:
        super().__init__(asdict(DefaultSettings()))  # noqa
        self.update(data)

    def __setitem__(self, key, value, /) -> None:
        field = DefaultSettings.get_field(key)
        super().__setitem__(key, field.type(value))

    def __delitem__(self, key, /) -> None:
        field = DefaultSettings.get_field(key)
        super().__setitem__(key, field.default)

    def update(self, other: dict = None, /, **kwargs) -> None:
        other = {**other, **kwargs} if other else kwargs
        for key, value in other.items():
            self[key] = value
