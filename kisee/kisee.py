"""Entry point for the identification provider.
"""

import argparse
import logging.config
import os
import sys
from typing import Any, Mapping, Optional

import aiohttp_cors

try:
    import sentry_sdk
    from sentry_sdk.integrations.aiohttp import AioHttpIntegration  # pragma: no cover
except ImportError:
    sentry_sdk = None  # type: ignore
import toml
from aiohttp import web
from aiojobs.aiohttp import setup

import kisee
from kisee import views
from kisee.identity_provider import import_idp
from kisee.middlewares import enforce_json, vary_origin

Settings = Mapping[str, Any]

AIOHTTP_LOGGERS = (
    "aiohttp.access",
    "aiohttp.client",
    "aiohttp.internal",
    "aiohttp.server",
    "aiohttp.web",
    "aiohttp.websocket",
)

logger = logging.getLogger(__name__)

DEFAULT_LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "full": {
            "format": "[%(asctime)s] %(levelname)s:%(name)s:%(message)s",
        }
    },
    "handlers": {
        "stderr": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
            "level": "DEBUG",
            "formatter": "full",
        }
    },
    "loggers": {"kisee": {"level": "DEBUG", "handlers": ["stderr"]}},
}


def setup_logging(settings: dict):  # pragma: no cover
    """Setup basic logging
    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    conf = settings["logging"] if "logging" in settings else DEFAULT_LOGGING_CONFIG
    logging.config.dictConfig(conf)
    logger.info("Kisee %s starting!", kisee.__version__)


def load_conf(settings_path: str = "settings.toml") -> Settings:
    """Search for a settings.toml file and load it."""
    candidates = (
        settings_path,
        os.path.join(os.getcwd(), settings_path),
        os.path.join(os.getcwd(), "settings.toml"),
        os.path.expanduser("~/settings.toml"),
        os.path.expanduser(os.path.join("~/", settings_path)),
        "/etc/settings.toml",
        os.path.join("/etc/", settings_path),
    )
    for candidate in candidates:
        if os.path.exists(candidate):
            with open(candidate) as candidate_file:
                return toml.load(candidate_file)
    print("Failed to locate the settings.toml file.", file=sys.stderr)
    sys.exit(1)


def parse_args(program_args=None) -> argparse.Namespace:
    """Parses command line arguments."""
    if program_args is None:
        program_args = sys.argv[1:]
    parser = argparse.ArgumentParser(description="Shape Identity Provider")
    parser.add_argument("--settings", default="settings.toml")
    return parser.parse_args(program_args)


def create_app(settings: Optional[Settings] = None) -> web.Application:
    """Identification provider entry point: builds and run a webserver."""
    settings = settings or load_conf()
    app = web.Application(middlewares=[enforce_json, vary_origin])
    setup(app)
    app["settings"] = settings
    app["identity_backend"] = import_idp(settings["identity_backend"]["class"])(
        options=settings["identity_backend"].get("options", {})
    )

    async def on_startup_wrapper(app):
        """Wrapper to call __aenter__."""
        await app["identity_backend"].__aenter__()

    async def on_cleanup_wrapper(app):
        """Wrapper to call __exit__."""
        await app["identity_backend"].__aexit__(None, None, None)

    app.on_startup.append(on_startup_wrapper)
    app.on_cleanup.append(on_cleanup_wrapper)

    app.add_routes(
        [
            web.get("/", views.get_root),
            web.get("/users/", views.get_users),
            web.post("/users/", views.post_users),
            web.get("/jwt/", views.get_jwts),
            web.post("/jwt/", views.post_jwt),
            web.get("/jwt/{jid}", views.get_jwt),
            web.get("/users/", views.get_users),
            web.patch("/users/{user_id}/", views.patch_user),
            web.get("/password_recoveries/", views.get_password_recoveries),
            web.post("/password_recoveries/", views.post_password_recoveries),
            web.get("/health", views.get_health),
        ]
    )

    cors = aiohttp_cors.setup(
        app,
        defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods=["GET", "OPTIONS", "PUT", "POST", "DELETE", "PATCH"],
            )
        },
    )

    for route in list(app.router.routes()):
        cors.add(route)

    return app


def main() -> None:  # pragma: no cover
    """Command line entry point."""
    args = parse_args()
    settings = load_conf(args.settings)
    setup_logging(settings)
    if sentry_sdk:
        sentry_sdk.init(  # pylint: disable=abstract-class-instantiated
            # see https://github.com/getsentry/sentry-python/issues/1081
            settings.get("SENTRY_DSN"),
            integrations=[AioHttpIntegration()],
        )
    app = create_app(settings)
    web.run_app(
        app, host=settings["server"]["host"], port=int(settings["server"]["port"])
    )
