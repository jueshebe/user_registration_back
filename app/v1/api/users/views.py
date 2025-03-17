"""Module with ping endpoint."""

from logging import Logger
import json
from http import HTTPStatus
from flask import Blueprint, Response, request
from pydantic import ValidationError
from app.v1.use_cases import UsersManager
from app.v1.models import Client
from app.v1.api.users.utils import GetClientValidator
from app.v1.utils.errors import SendDataError


users = Blueprint("users", __name__)


@users.route("/<int:user_id>", methods=["GET"])
def get_user(user_id: int, users_manager: UsersManager) -> Response:
    """Get user."""
    validator = GetClientValidator(**request.args)  # type: ignore
    user = users_manager.get_user(user_id)
    if (  # check if the requester knows at least 3 fields of the object
        user
        and user.document == user_id
        and user.email == validator.email
        and user.document_type == validator.document_type
    ):
        return Response(
            response=user.json(), status=200, content_type="application/json"
        )
    return Response(response="Client not found", status=404, content_type="text/plain")


@users.route("/", methods=["POST"])
def post_user(users_manager: UsersManager) -> Response:
    """Create an user."""
    user = Client(**request.json)  # type: ignore
    try:
        users_manager.upload_user(user)
        response = json.dumps({"message": "User created successfully"})
        return Response(response=response, status=200, content_type="application/json")
    except SendDataError as error:
        return Response(response="client not created", status=HTTPStatus.BAD_REQUEST, content_type="text/plain")


@users.route("/", methods=["PUT"])
def update_user(users_manager: UsersManager) -> Response:
    """Update an user."""
    user = Client(**request.json)  # type: ignore
    validator = GetClientValidator(**request.args)  # type: ignore

    current_data = users_manager.get_user(user.document)
    if (  # check if the requester knows at least 3 fields of the object
        current_data
        and user.document == current_data.document
        and validator.email == current_data.email
        and validator.document_type == current_data.document_type
    ):
        users_manager.update_user(user)
        response = json.dumps({"message": "User updated successfully"})
        return Response(response=response, status=200, content_type="application/json")
    return Response(response="Client not found", status=404, content_type="text/plain")


@users.errorhandler(ValidationError)  # type: ignore
def input_error(error: ValidationError) -> Response:
    """Handle input validation errors.

    Args:
        error (ValidationError): Error to handle.

    Returns:
        Response: Response with the error.
    """
    return Response(
        f"Input error: {str(error)}", status=HTTPStatus.BAD_REQUEST, content_type="text/plain"
    )


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
    return Response(
        str(error), status=HTTPStatus.INTERNAL_SERVER_ERROR, content_type="text/plain"
    )
