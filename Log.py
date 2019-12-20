# -*- coding: utf-8 -*-

"""
Log.py
~~~~~~~~~~~~~~~~~~~~~~~~~

日志处理模块
"""

import logging


logger = logging.getLogger(__name__)
file_handler = None
screen_handler = None


def get_log_level(log_level):
    if log_level == "debug":
        level = logging.DEBUG
    elif log_level == "info":
        level = logging.INFO
    elif log_level == "warning":
        level = logging.WARNING
    elif log_level == "error":
        level = logging.ERROR
    elif log_level == "critical":
        level = logging.CRITICAL
    else:
        level = logging.NOTSET
    return level


def init_logger(log_file, log_level):
    level = logging.DEBUG
    logger.setLevel(level)
    logger_fmt = logging.Formatter('%(asctime)s %(filename)s:%(funcName)s:%(lineno)d %(levelname)s] %(message)s')

    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level=level)
    file_handler.setFormatter(logger_fmt)
    logger.addHandler(file_handler)

    screen_handler = logging.StreamHandler()
    file_handler.setLevel(level=level)
    screen_handler.setFormatter(logger_fmt)
    logger.addHandler(screen_handler)
    logger.propagate = False