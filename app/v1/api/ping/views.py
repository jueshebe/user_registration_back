"""Module with ping endpoint."""
from logging import Logger
from flask import Blueprint, Response


ping = Blueprint("ping", __name__)


@ping.route("/ping")
def main(logger: Logger) -> Response:
    """Ping endpoint, used to know if the app is up."""
    logger.info("Ping endpoint called")
    return Response(response="pong", status=200, content_type="text/plain")
