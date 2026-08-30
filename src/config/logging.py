import logging

from .config import LoggingConfig


def configure_logging(config: LoggingConfig) -> None:
    logging.basicConfig(
        level=config.log_level_value,
        format=config.log_format,
        datefmt=config.date_format,
    )
