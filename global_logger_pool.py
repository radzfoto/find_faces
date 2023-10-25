# Copyright (c) Raul Diaz 2023, licensed per terms in LICENSE file in https://github.com/radzfoto/find_faces

import sys
import logging
from pathlib import Path

class LogPoolManager:
    def __init__(self, pool) -> None:
        self.pool = pool
        return
    # end __init__()

    def __enter__(self):
        self.obj = self.pool.acquire()
        return self.obj
    # end __enter__()
    
    def __exit__(self, type, value, traceback) -> None:
        self.pool.release(self.obj)
        return
    # end __exit__()
# end class LogPoolManager

class GlobalLogger(logging.Logger):

    def __init__(self,
                 logger_name: str = 'GlobalLogger',
                 log_level: int = logging.NOTSET
                 ) -> None:
        super().__init__(name=logger_name,
                         level=log_level)
        # Set the logger class to GlobalLogger
        logging.setLoggerClass(GlobalLogger)
        self.__is_configured = False

    def configure(self,
                 log_dir: Path = Path(),
                 log_filename: str = 'logfile.log',
                 log_level: int = logging.NOTSET,
                 log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
                 log_to_file: bool = True,
                 log_to_console: bool = False,
                 debug_mode: bool = False) -> None:

        if not self.__is_configured:
            log_root_dir: Path = log_dir
            if log_root_dir == Path():
                if debug_mode:
                    log_root_dir = Path(__file__).parent  # Create default debugging log directory
                else:
                    log_root_dir = Path.home()  # Create default log directory
            filepath: Path = log_root_dir / log_filename

            self.setLevel(level=log_level)
            formatter = logging.Formatter(log_format)

            if log_to_file:
                file_handler = logging.FileHandler(filepath.as_posix())
                file_handler.setFormatter(formatter)
                self.addHandler(file_handler)

            if log_to_console:
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setFormatter(formatter)
                self.addHandler(console_handler)

            self.__is_configured = True
    # end configure()

    @property
    def is_configured(self) -> bool:
        return self.__is_configured
    # end property is_configure()
# end class GlobalLogger

class LoggerPool:
    def __init__(self, 
                 logger_name_list: list[str]=['GlobalLogger'], 
                 log_level=logging.NOTSET) -> None:
        self.__logger_name_list = logger_name_list
        self.__free: list[GlobalLogger] = []
        self.__in_use: list[GlobalLogger] = []
        for logger_name in self.__logger_name_list:
            # Create a GlobalLogger instance and append it
            self.__free.append(GlobalLogger(logger_name, logging.NOTSET))
        return
    # end __init__()
    
    def acquire(self) -> GlobalLogger:
        if len(self.__free) <= 0:
            raise Exception("No loggers available in object pool")
        r: GlobalLogger = self.__free[0]
        self.__free.remove(r)
        self.__in_use.append(r)
        return r
    # end acquire()
    
    def release(self, r: GlobalLogger) -> None:
        self.__in_use.remove(r)
        self.__free.append(r)
    # end release()
# end LoggerPool

# logger_pool = LoggerPool(logger_name_list=['GlobalLogger'])

# log = LogPoolManager(logger_pool)