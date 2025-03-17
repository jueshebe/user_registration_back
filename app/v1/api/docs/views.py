"""Module with Docs endpoints."""

import os
from flask import Blueprint, send_from_directory, Response
from http import HTTPStatus


docs = Blueprint("docs", __name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Obtiene la ruta del script
STATIC_DIR = os.path.join(BASE_DIR, "static/swagger-ui")  # Ruta absoluta

project_path = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
)

swagger_path = os.path.join(project_path, "swagger-ui")


@docs.route("/")
def swagger_ui() -> None:
    return send_from_directory(swagger_path, "index.html")


@docs.route("/<path:filename>")
def swagger_files(filename: str) -> None:
    return send_from_directory(swagger_path, filename)


@docs.route("/openapi.yaml")
def swagger_yaml() -> None:
    return send_from_directory(swagger_path, "openapi.yaml")


@docs.errorhandler(Exception)  # pragma: no cover
def handle_all_errors(error: Exception) -> Response:
    return Response(str(error), status=HTTPStatus.INTERNAL_SERVER_ERROR)
