"""Module with ping endpoint."""

from logging import Logger
import json
from http import HTTPStatus
from flask import Blueprint, Response, request
from pydantic import ValidationError
from app.v1.use_cases import InvoicesManager
from app.v1.models import Client
from app.v1.api.users.utils import GetClientValidator, validate_user
from app.v1.utils.errors import SendDataError


invoices = Blueprint("invoices", __name__)


@invoices.route("/<string:prefix>/<int:invoice_number>", methods=["GET"])
def get_user(
    prefix: str, invoice_number: int, invoices_manager: InvoicesManager
) -> Response:
    """Get user."""
    invoice = invoices_manager.get_invoice(prefix, invoice_number)
    if invoice:  # check if the requester knows at least 3 fields of the object
        return Response(
            response=invoice.model_dump_json(), status=200, content_type="application/json"
        )
    return Response(response="Invoice not found", status=404, content_type="text/plain")


@invoices.errorhandler(ValidationError)  # type: ignore
def input_error(error: ValidationError) -> Response:
    """Handle input validation errors.

    Args:
        error (ValidationError): Error to handle.

    Returns:
        Response: Response with the error.
    """
    return Response(
        f"Input error: {str(error)}",
        status=HTTPStatus.BAD_REQUEST,
        content_type="text/plain",
    )


@invoices.errorhandler(Exception)  # type: ignore
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
