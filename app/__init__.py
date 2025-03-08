"""Flask app creation."""

from flask_injector import FlaskInjector
from flask import Flask
from app.v1.api import ping
from app.v1.module import dependencies

# Active endpoints noted as following:
# (url_prefix, blueprint_object)
PRIVATE_ENDPOINTS = (
    ("/", ping),
)
PUBLIC_ENDPOINTS = (("/", ping),)

PUBLIC_URL_PREFIX = "inscriptions"
INTERNAL_URL_PREFIX = "internal"


def create_app() -> Flask:
    """Create Flask app."""
    app = Flask(__name__)
    # accepts both /endpoint and /endpoint/ as valid URLs
    app.url_map.strict_slashes = False

    app.register_blueprint(ping, url_prefix="/", name=f"{ping.name}")
    # register each active blueprint
    for url, blueprint in PRIVATE_ENDPOINTS:
        app.register_blueprint(
            blueprint,
            url_prefix=f"/{INTERNAL_URL_PREFIX}/{url}",
            name=f"suscriber-{blueprint.name}",
        )

    for url, blueprint in PUBLIC_ENDPOINTS:
        app.register_blueprint(
            blueprint,
            url_prefix=f"/{PUBLIC_URL_PREFIX}/{url}",
            name=f"suscriber2-{blueprint.name}",
        )

    FlaskInjector(app=app, modules=[dependencies])
    return app
