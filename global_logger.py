# Copyright (c) Raul Diaz 2023, licensed per terms in LICENSE file in https://github.com/radzfoto/extract_faces

import logging
from pathlib import Path

class GlobalLogger:
    _instance = None

    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    def __new__(cls,
                root_dir: Path = None,
                filename: Path = None,
                log_messages = logging.ERROR, 
                log_messages_to_console = False,
                format: str = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.setup(root_dir, filename, format, log_messages, log_messages_to_console)
        return cls._instance

    def setup(self, 
              root_dir: Path, 
              filename: Path, 
              format: str,
              log_level, 
              log_messages_to_console):
        # logging setup logic as you have it in your setup_logging method
        self.log = logging.getLogger(__name__)
        # ... rest of your logging setup logic
        the_root_dir: Path = root_dir
        if root_dir is None:
            the_root_dir = Path.home()
        if filename is None:
            # Create default hidden log
            filepath: Path = the_root_dir / 'log.log'
        else:
            filepath: Path = the_root_dir / filename
        if (log_level is None) or (log_level == False):
            # NOTE: Errors and Critical messages will still be logged always
            self.log.setLevel(logging.ERROR)
        elif (log_level == logging.INFO) or (log_level == logging.DEBUG):
            self.log.setLevel(log_level)
        else:
            # Shouldn't happen, but will set error log messages by default if log_level is something strange
            self.log.setLevel(logging.ERROR)

        self.formatter = logging.Formatter(format)

        # Create and config file_handler
        self.file_handler = logging.FileHandler(filepath.as_posix())
        self.file_handler.setFormatter(self.formatter)
        self.log.addHandler(self.file_handler)
        # Create and configure console_handler
        if log_messages_to_console:
            self.console_handler = logging.StreamHandler()
            self.console_handler.setFormatter(self.formatter)
            self.log.addHandler(self.console_handler)
    # end setup_logging

    @property
    def global_logger(self):
        return self.log
# end class GlobalLogger
