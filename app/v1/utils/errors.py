"""Application errors."""


class CredentialsError(Exception):
    """Raised when the app can't authenticate with the server."""


class FetchDataError(Exception):
    """Raised when the app can't get data from the server."""
