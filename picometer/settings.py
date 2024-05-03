from pathlib import Path

from picometer.parser import parse_path

default_settings_path = Path(__file__).parent / 'settings.yaml'
default_settings = parse_path(default_settings_path)[0]
