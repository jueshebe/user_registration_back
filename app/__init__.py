"""Flask app creation."""

from flask_injector import FlaskInjector
from flask import Flask
from flask_cors import CORS
from app.v1.api import ping, users
from app.v1.module import dependencies

# Active endpoints noted as following:
# (url_prefix, blueprint_object)
PUBLIC_ENDPOINTS = (
    ("/", ping),
    ("/users", users),
)

PUBLIC_URL_PREFIX = "pos-connector"


def create_app() -> Flask:
    """Create Flask app."""
    app = Flask(__name__)
    CORS(app)  # TODO: change this for an nginx routing
    # accepts both /endpoint and /endpoint/ as valid URLs
    app.url_map.strict_slashes = False

    app.register_blueprint(ping, url_prefix="/", name=f"{ping.name}")
    # register each active blueprint
    for url, blueprint in PUBLIC_ENDPOINTS:
        app.register_blueprint(
            blueprint,
            url_prefix=f"/{PUBLIC_URL_PREFIX}/{url}",
            name=f"suscriber-{blueprint.name}",
        )

    FlaskInjector(app=app, modules=[dependencies])
    return app
