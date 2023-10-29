# Copyright (c) Raul Diaz 2023, licensed per terms in LICENSE file in https://github.com/radzfoto/find_faces

import logging
from pathlib import Path

_logger_configured: list[str] = []

def configure_logger(log_name: str = 'global_logger',
                     log_file: Path = Path("logfile.log"),
                     log_level: int = logging.INFO,
                     log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
                     log_messages_to_console: bool = True,
                     debug = False
                    ) -> logging.Logger:
    global _logger_configured

    if log_name in _logger_configured:
        return logging.getLogger(log_name)
    else:
        _logger_configured.append(log_name)

    config_log_level: int = logging.DEBUG if debug else log_level
    if log_file.is_absolute():
        config_log_file = log_file
    else:
        log_filename: str = Path(log_file).name
        log_dir: Path = Path(__file__).parent if debug else Path.cwd()
        config_log_file: Path = log_dir / log_filename

    # Create a logger object
    logger: logging.Logger = logging.getLogger(log_name)
    logger.setLevel(config_log_level)  # Set the logging level

    # Create a file handler that logs debug and higher level messages
    file_handler = logging.FileHandler(config_log_file.as_posix())
    
    file_handler.setLevel(log_level)

    # Create a console handler with a higher log level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    # Create a formatter and set it for both handlers
    formatter = logging.Formatter(log_format)
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    if log_messages_to_console:
        logger.addHandler(console_handler)

    return logger


# class GlobalLogger:
#     _instance = None

#     DEBUG: int = logging.DEBUG
#     INFO: int = logging.INFO
#     WARNING: int = logging.WARNING
#     ERROR: int = logging.ERROR
#     CRITICAL: int = logging.CRITICAL

#     def __new__(cls,
#                 log_dir: Path = Path(),
#                 log_filename: str = 'logfile.log',
#                 log_level: int = logging.ERROR, 
#                 log_messages_to_console: bool = False,
#                 format: str = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
#                 debug_mode = False):
#         if cls._instance is None:
#             cls._instance = super().__new__(cls)
#             cls._instance.setup(log_dir, log_filename, format, log_level, log_messages_to_console, debug_mode)
#         return cls._instance

#     def setup(self, 
#               log_dir: Path, 
#               log_filename: str, 
#               format: str,
#               log_level: int, 
#               log_messages_to_console: bool,
#               debug_mode: bool) -> None:
#         # logging setup logic as you have it in your setup_logging method
#         self._log = logging.getLogger(__name__)
#         # ... rest of your logging setup logic

#         log_root_dir: Path = log_dir
#         if log_dir == Path():
#             if debug_mode:
#                 log_root_dir = Path(__file__).parent  # Create default debugging log directory
#             else:
#                 log_root_dir = Path.home()  # Create default log directory

#         filepath: Path = log_root_dir / log_filename

#         assert ((log_level == logging.DEBUG) or \
#                 (log_level == logging.INFO) or \
#                 (log_level == logging.WARNING) or \
#                 (log_level == logging.ERROR) or \
#                 (log_level == logging.CRITICAL)), \
#             'ERROR: log_level must be one of logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL'

#         self.log_level: int = log_level
#         self._log.setLevel(self.log_level)
#         self.formatter = logging.Formatter(format)

#         # Create and config file_handler
#         self.file_handler = logging.FileHandler(filepath.as_posix())
#         self.file_handler.setFormatter(self.formatter)
#         self._log.addHandler(self.file_handler)
#         # Create and configure console_handler
#         if log_messages_to_console:
#             self.console_handler = logging.StreamHandler()
#             self.console_handler.setFormatter(self.formatter)
#             self._log.addHandler(self.console_handler)
#     # end setup_logging

#     @property
#     def global_logger(self) -> logging.Logger:
#         return self._log

# # end class GlobalLogger


# def test() -> None:
#     logging_info = GlobalLogger(log_dir=Path(__file__).parent, log_filename = 'global_logger.log',
#                                 log_level = GlobalLogger.DEBUG,
#                                 log_messages_to_console=True)
#     log = logging_info.global_logger

#     print(f'DEBUG: {GlobalLogger.DEBUG}, {logging.DEBUG}')
#     print(f'INFO: {GlobalLogger.INFO}, {logging.INFO}')
#     print(f'WARNING: {GlobalLogger.WARNING}, {logging.WARNING}')
#     print(f'ERROR: {GlobalLogger.ERROR}, {logging.ERROR}')
#     print(f'CRITICAL: {GlobalLogger.CRITICAL}, {logging.CRITICAL}')
#     log.debug('Test Debug message')
#     log.info('Test Info message')
#     log.warning('Test Warning message')
#     log.error('Test Error message')
#     log.critical('Test Critical message')
#     return
# # end test()

# if __name__ == '__main__':
#     test()
