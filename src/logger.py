import logging

LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR
}


def set_params(loglevel: str):

    level = LEVELS.get(loglevel, None)
    if level is None:
        raise ValueError(f"Invalid loglevel: {loglevel}")

    logging.basicConfig(level=level)
