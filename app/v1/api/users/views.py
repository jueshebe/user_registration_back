"""Module with ping endpoint."""
from logging import Logger
import json
from flask import Blueprint, Response, request
from http import HTTPStatus
from app.v1.use_cases import UsersManager
from app.v1.models import Client


users = Blueprint("users", __name__)


@users.route("/<int:user_id>", methods=["GET"])
def get_user(user_id: int, users_manager: UsersManager, logger: Logger) -> Response:
    """Get user."""
    user = users_manager.get_user(user_id)
    if user and user.document == user_id:
        return Response(response=user.json(), status=200, content_type="application/json")
    return Response(response="Client not found", status=404, content_type="text/plain")


@users.route("/", methods=["POST"])
def post_user(users_manager: UsersManager, logger: Logger) -> Response:
    """Create an user."""
    user = Client(**request.json)  # type: ignore
    users_manager.upload_user(user)
    response = json.dumps({"message": "User created successfully"})
    return Response(response=response, status=200, content_type="application/json")


@users.route("/", methods=["PUT"])
def update_user(users_manager: UsersManager, logger: Logger) -> Response:
    """Update an user."""
    user = Client(**request.json)  # type: ignore
    users_manager.update_user(user)
    response = json.dumps({"message": "User updated successfully"})
    return Response(response=response, status=200, content_type="application/json")


@users.errorhandler(Exception)  # type: ignore
def handle_all_errors(error: Exception, logger: Logger) -> Response:
    """Handle all errors.

    Args:
        error (Exception): Error to handle.
        logger (Logger): Logger

    Returns:
        Response: Response with the error.
    """
    logger.error(f"System error {error}")
    return Response(str(error), status=HTTPStatus.INTERNAL_SERVER_ERROR, content_type="text/plain")
