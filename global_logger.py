# Copyright (c) Raul Diaz 2023, licensed per terms in LICENSE file in https://github.com/radzfoto/find_faces

import logging
from pathlib import Path

class GlobalLogger:
    _instance = None

    DEBUG: int = logging.DEBUG
    INFO: int = logging.INFO
    WARNING: int = logging.WARNING
    ERROR: int = logging.ERROR
    CRITICAL: int = logging.CRITICAL

    def __new__(cls,
                root_dir: Path = Path(),
                filename: str = "",
                log_messages: int = logging.ERROR, 
                log_messages_to_console: bool = False,
                format: str = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.setup(root_dir, filename, format, log_messages, log_messages_to_console)
        return cls._instance

    def setup(self, 
              root_dir: Path, 
              filename: str, 
              format: str,
              log_level: int, 
              log_messages_to_console: bool) -> None:
        # logging setup logic as you have it in your setup_logging method
        self.log = logging.getLogger(__name__)
        # ... rest of your logging setup logic
        log_root_dir: Path = root_dir
        if root_dir == Path():
            log_root_dir = Path.home()  # Create default log_root_dir
        if filename == "":
            # Create default log
            filepath: Path = log_root_dir / 'logfile.log'
        else:
            filepath: Path = log_root_dir / filename

        if not ((log_level == logging.DEBUG) or \
                (log_level == logging.INFO) or \
                (log_level == logging.WARNING) or \
                (log_level == logging.ERROR) or \
                (log_level == logging.CRITICAL)):
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
