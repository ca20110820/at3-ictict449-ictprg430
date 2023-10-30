from functools import partial
import os
import json
import logging
from logging import FileHandler
from typing import List

import smartpark


PROJECT_ROOT_DIR = os.path.dirname(os.path.abspath(os.path.dirname(smartpark.__file__)))
LOGS_DIR = os.path.join(PROJECT_ROOT_DIR, "logs")


class LimitedFileHandler(FileHandler):
    def __init__(self, filename, max_lines=20000, mode='a', encoding=None, delay=False):
        super().__init__(filename, mode, encoding, delay)
        self.max_lines = max_lines

    def emit(self, record):
        super().emit(record)
        self.check_lines()

    def check_lines(self):
        try:
            with open(self.baseFilename, 'r') as f:
                # TODO: Fix Logger - It tries to read the whole file content which slows the processing.
                lines = f.readlines()
            if len(lines) > self.max_lines:
                with open(self.baseFilename, 'w') as f:
                    f.writelines(lines[-self.max_lines:])
        except Exception as e:
            print(f"Error while checking log lines: {e}")


# TODO: Create a Decorator for Logging
def get_logger(log_filename, logger_name, logging_level=logging.DEBUG):
    # Example: get_logger("carpark.txt", "carpark_logger", logging_level=logging.DEBUG)
    handler = LimitedFileHandler(get_log_filepath(log_filename))
    formatter = logging.Formatter('[%(asctime)s] [module:%(module)s] [lineno:%(lineno)d] [%(levelname)s] | %(message)s')
    handler.setFormatter(formatter)

    logger = logging.getLogger(logger_name)
    logger.addHandler(handler)
    logger.setLevel(logging_level)
    return logger


def get_log_filepath(filename: str):
    return os.path.join(LOGS_DIR, filename)


# TODO: Feature - Create a Writer to CSV and/or JSON
def write_to_file(data_str: str, file_path: str, *args, **kwargs) -> None:
    with open(file_path, 'a') as file:
        # json.dump([data_str], file, *args, **kwargs)
        file.write(data_str + "\n")


def log_data(data_str: str, file_name: str):
    write_to_file(data_str, get_log_filepath(file_name))


if __name__ == "__main__":
    with open(get_log_filepath('cars.txt'), 'r') as file:
        for line in file:
            line = line.rstrip()
            dct = json.loads(line)
            print(type(dct["exit_time"]))  # TODO: Parse the Dictionary String Values to their appropriate types
