import logging
import sys


def get_logger(name):
    form = "[%(asctime)s][%(levelname)s][%(name)s][%(funcName)s] %(message)s"
    default_formatter = \
        logging.Formatter(form)

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(default_formatter)

    logger.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)

    return logger


class MissingFieldException(Exception):
    pass


class AccessError(Exception):
    pass


class UserError(Exception):
    pass


class UnknownUserError(UserError):
    pass


class SessionError(UserError):
    pass


class CredentialsError(UserError):
    pass
