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
                log_dir: Path = Path(),
                log_filename: str = 'logfile.log',
                log_level: int = logging.ERROR, 
                log_messages_to_console: bool = False,
                format: str = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
                debug_mode = False):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.setup(log_dir, log_filename, format, log_level, log_messages_to_console, debug_mode)
        return cls._instance

    def setup(self, 
              log_dir: Path, 
              log_filename: str, 
              format: str,
              log_level: int, 
              log_messages_to_console: bool,
              debug_mode: bool) -> None:
        # logging setup logic as you have it in your setup_logging method
        self._log = logging.getLogger(__name__)
        # ... rest of your logging setup logic

        log_root_dir: Path = log_dir
        if log_dir == Path():
            if debug_mode:
                log_root_dir = Path(__file__).parent  # Create default debugging log directory
            else:
                log_root_dir = Path.home()  # Create default log directory

        filepath: Path = log_root_dir / log_filename

        assert ((log_level == logging.DEBUG) or \
                (log_level == logging.INFO) or \
                (log_level == logging.WARNING) or \
                (log_level == logging.ERROR) or \
                (log_level == logging.CRITICAL)), \
            'ERROR: log_level must be one of logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL'

        self.formatter = logging.Formatter(format)

        # Create and config file_handler
        self.file_handler = logging.FileHandler(filepath.as_posix())
        self.file_handler.setFormatter(self.formatter)
        self._log.addHandler(self.file_handler)
        # Create and configure console_handler
        if log_messages_to_console:
            self.console_handler = logging.StreamHandler()
            self.console_handler.setFormatter(self.formatter)
            self._log.addHandler(self.console_handler)
    # end setup_logging

    @property
    def global_logger(self) -> logging.Logger:
        return self._log

# end class GlobalLogger


def test():
    logging_info = GlobalLogger(log_dir=Path(__file__).parent, log_filename = 'global_logger.log',
                                log_level = GlobalLogger.DEBUG,
                                log_messages_to_console=True)
    log = logging_info.global_logger

    log.debug('Debug message')
    log.info('Info message')
    log.warning('Warning message')

# end test()

if __name__ == '__main__':
    test()
