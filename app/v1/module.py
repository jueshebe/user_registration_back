"""Dependencies."""

import os
import logging
from flask_injector import singleton, Binder
from app.v1.clients import PirposConnector, DummyConnector, SystemProvider
from app.v1.use_cases import UsersManager


def dependencies(binder: Binder) -> None:
    """Dependencies manager."""
    # Logger
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    level: int = getattr(logging, log_level, logging.INFO)

    logger = logging.getLogger(__name__)
    logger.setLevel(level)
    handler = logging.StreamHandler()
    handler.setLevel(level)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    binder.bind(logging.Logger, to=logger, scope=singleton)

    # Clients
    user_name = os.getenv("PIRPOS_USER_NAME", None)
    password = os.getenv("PIRPOS_PASSWORD", None)
    if not user_name or not password:
        logger.warning("Pirpos credentials not found")
        pos_client: SystemProvider = DummyConnector()
    else:
        pos_client = PirposConnector(user_name, password, logger)
    users_manager = UsersManager(pos_client, logger)
    binder.bind(UsersManager, to=users_manager, scope=singleton)

    logger.info("Dependencies manager finished")
