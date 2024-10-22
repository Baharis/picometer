from pathlib import Path
import logging
from typing import Any, Callable, Union


formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def _get_logger() -> logging.Logger:
    """Set up logging, but don't log yet in case picometer is used as package"""
    logger_ = logging.getLogger('picometer')
    logger_.setLevel(logging.DEBUG)
    logger_.addHandler(logging.NullHandler())
    return logger_


logger = _get_logger()


def add_file_handler(path: Union[str, Path]) -> logging.FileHandler:
    """If used as program, allow logging directly to a file using `FileHandler`"""
    # now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    # path = str((p := Path(path)).with_suffix('')) + '_' + now + p.suffix
    file_handler = logging.FileHandler(path)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return file_handler


class LogEventHandler(logging.Handler):
    """Custom handler for external log processing, see `register_log_listener`"""
    def __init__(self, log_callback) -> None:
        super().__init__()
        self.log_callback = log_callback  # A callback to process log events

    def emit(self, record) -> None:
        log_entry = self.format(record)
        self.log_callback(log_entry)  # Send log entry to the callback


def register_log_listener(log_callback: Callable[[str], Any]) -> LogEventHandler:
    """A simple implementation, register function to call it for each log entry"""
    log_event_handler = LogEventHandler(log_callback)
    log_event_handler.setLevel(logging.DEBUG)
    log_event_handler.setFormatter(formatter)
    logger.addHandler(log_event_handler)
    return log_event_handler
