"""Module with ping endpoint."""
from flask import Blueprint, Response


ping = Blueprint("ping", __name__)


@ping.route("/ping")
def main() -> Response:
    """Ping endpoint, used to know if the app is up."""
    return Response(response="pong", status=200, content_type="text/plain")
