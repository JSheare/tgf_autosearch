"""A module containing a function that sets up logging for the application."""
import logging
import pathlib
import platformdirs
from logging import handlers

import tgf_autosearch.config.parameters as params


def configure_logging(log_level: int) -> None:
    """A function that performs logging setup for the application."""

    logging.captureWarnings(True)
    app_logger = logging.getLogger(params.APPLICATION_NAME)
    app_logger.setLevel(log_level)
    log_directory = pathlib.Path(platformdirs.user_log_path(params.APPLICATION_NAME, appauthor=False))
    if not log_directory.is_dir():
        log_directory.mkdir(parents=True)

    handler = logging.handlers.RotatingFileHandler(
        filename=f'{log_directory}/{params.APPLICATION_NAME}.txt',
        encoding='utf-8',
        maxBytes=params.MAX_LOG_SIZE_BYTES,
        backupCount=params.MAX_LOG_ROLLOVERS)
    handler.setFormatter(logging.Formatter("{asctime} - {levelname} - {name} - {message}",
                                           style="{",
                                           datefmt="%Y-%m-%d %H:%M:%S"))
    app_logger.addHandler(handler)
