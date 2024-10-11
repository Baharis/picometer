from dataclasses import fields
import unittest

from picometer.settings import DefaultSettings, Settings


class TestSettings(unittest.TestCase):
    def setUp(self):
        self.settings = Settings()

    def test_settings_pull_defaults(self) -> None:
        self.assertGreater(len(self.settings), 0)
        self.assertIn('clear_selection_after_use', self.settings)

    def test_settings_change(self) -> None:
        known_setting = fields(DefaultSettings)[0]  # noqa
        self.settings[known_setting.name] = known_setting.type(True)
        known_setting_value1 = self.settings[known_setting.name]
        self.settings[known_setting.name] = known_setting.type(False)
        known_setting_value2 = self.settings[known_setting.name]
        self.assertNotEqual(known_setting_value1, known_setting_value2)

    def test_getting_unknown_raises(self) -> None:
        unknown_setting_name = 'undefined_setting_definitely_unused_!@#$%^&*()'
        with self.assertRaises(KeyError):
            _ = self.settings[unknown_setting_name]

    def test_setting_unknown_raises(self) -> None:
        unknown_setting_name = 'undefined_setting_definitely_unused_!@#$%^&*()'
        with self.assertRaises(KeyError):
            self.settings[unknown_setting_name] = ''

    def test_deleting_reverts_to_defaults(self) -> None:
        known_setting = fields(DefaultSettings)[0]  # noqa
        default_value = self.settings[known_setting.name]
        new_value = v if (v := known_setting.type(True)) != default_value \
            else known_setting.type(False)
        self.settings[known_setting.name] = new_value
        self.assertNotEqual(self.settings[known_setting.name], default_value)
        del self.settings[known_setting.name]
        self.assertEqual(self.settings[known_setting.name], default_value)
