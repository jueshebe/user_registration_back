"""Dependencies."""
from flask_injector import singleton, Binder
from logging import getLogger


def dependencies(binder: Binder) -> None:
    """Dependencies manager."""
    logger = getLogger()
    # binder.bind(
    #     LoggerWithTags,
    #     to=getLogger(),
    #     scope=singleton,
    # )
    logger.info("Dependencies manager finished")
