import logging

class Logger(logging.getLoggerClass()):
    def __init__(self, logger_name='default_logger'):
        self.name = logger_name

