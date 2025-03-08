"""Dependencies."""
from flask_injector import singleton, Binder
import logging
import os


def dependencies(binder: Binder) -> None:
    """Dependencies manager."""
    # Obtener el nivel de logs desde una variable de entorno
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    level: int = getattr(logging, log_level, logging.INFO)

    logger = logging.getLogger(__name__)
    logger.setLevel(level)
    handler = logging.StreamHandler()
    handler.setLevel(level)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    binder.bind(
        logging.Logger,
        to=logger,
        scope=singleton,
    )
    logger.info("Dependencies manager finished")
