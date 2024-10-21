from pathlib import Path
import tempfile
import unittest

from picometer.logging import add_file_handler, register_log_listener
from picometer.instructions import Routine
from picometer.process import process
from tests.test_instructions import get_yaml


class TestLogging(unittest.TestCase):

    def setUp(self) -> None:
        self.routine = Routine.from_string(get_yaml('test_ferrocene.yaml'))

    def test_file_handler(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / 'picometer.log'
            handler = add_file_handler(log_path)
            _ = process(self.routine)
            handler.close()
            with open(log_path, 'r') as log_file:
                lines = log_file.readlines()
                self.assertGreater(len(lines), 1600)

    def test_log_listener(self) -> None:
        snatched_log_msg = []
        snatch_log_msg = lambda s: snatched_log_msg.append(s)
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / 'picometer.log'
            handler = add_file_handler(log_path)
            register_log_listener(snatch_log_msg)
            _ = process(self.routine)
            handler.close()
            with open(log_path, 'r') as log_file:
                self.assertEqual(snatched_log_msg, log_file.read().splitlines())
