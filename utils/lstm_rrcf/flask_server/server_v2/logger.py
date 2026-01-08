import logging
import os
import sys

_logger = None  # Internal reference to the logger

ALWAYS_LOG_LEVEL = 1  # Lower than NOTSET (0)
logging.addLevelName(ALWAYS_LOG_LEVEL, "ALWAYS")

def always(self, message, *args, **kwargs):
    self._log(ALWAYS_LOG_LEVEL, message, args, **kwargs)

logging.Logger.always = always


def get_log_level(level_str: str, default=logging.INFO) -> int:
    return {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }.get(level_str.upper(), default)

def setup_logger(name="fission-python-environment", level: str = "INFO"):
    global _logger
    if _logger is not None:
        if level:
            _logger.setLevel(get_log_level(level))
        return _logger

    log_level = get_log_level(level)

    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    _logger = logger
    return logger

# Global logger instance (can be reconfigured later)
logger = setup_logger()