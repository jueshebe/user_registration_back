"""Here are define pytest fixtures, hooks and plugins."""
import pytest
# from typing import Any, Dict
# from unittest.mock import patch, Mock
from flask import Flask
from app import create_app


@pytest.fixture
def app() -> Flask:
    """App fixture."""
    flask_app = create_app()
    yield flask_app
