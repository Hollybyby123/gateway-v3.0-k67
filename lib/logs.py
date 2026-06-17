import logging
import os
import threading
from logging.handlers import RotatingFileHandler

class Log():
    _handler = None
    _handler_pid = None
    _lock = threading.Lock()
    _log_file = "gateway.log"
    _max_bytes = 5 * 1024 * 1024
    _backup_count = 3

    def __init__(self, name):
        self.__name = name

       # Loggers
        self.__logger = logging.getLogger(self.__name)
        self.__logger.setLevel(logging.DEBUG)
        self.__logger.propagate = False

        # Formatters
        self.__formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%d/%m/%Y %H:%M:%S %p")

        self.__fileHandler = self.__get_file_handler()

        for handler in list(self.__logger.handlers):
            if getattr(handler, "_gateway_log_handler", False) and handler is not self.__fileHandler:
                self.__logger.removeHandler(handler)
                handler.close()

        if self.__fileHandler not in self.__logger.handlers:
            self.__logger.addHandler(self.__fileHandler)

    def __get_file_handler(self):
        pid = os.getpid()
        with Log._lock:
            if Log._handler is None or Log._handler_pid != pid:
                if Log._handler is not None:
                    Log._handler.close()

                handler = RotatingFileHandler(
                    Log._log_file,
                    maxBytes=Log._max_bytes,
                    backupCount=Log._backup_count,
                    delay=True,
                )
                handler._gateway_log_handler = True
                handler.setLevel(logging.DEBUG)
                handler.setFormatter(self.__formatter)
                Log._handler = handler
                Log._handler_pid = pid

            return Log._handler
    
    def debug(self, mes):
        """Use for debug process"""
        self.__logger.debug(mes)

    def info(self, mes):
        """Use for watching logics flow"""
        self.__logger.info(mes)

    def error(self, mes):
        """Use when there is an exception happened but not tracing back"""
        self.__logger.error(mes)

    def exception(self, mes):
        """Use when there is an exception happened"""
        self.__logger.exception(mes)

if __name__=="__main__":
    pass
