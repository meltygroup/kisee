"""Entry point for the identification provider.
"""

import argparse
import logging
import os
import sys
from typing import Mapping, Any, Optional

import toml
from aiohttp import web
import aiohttp_cors

import sentry_sdk
from sentry_sdk.integrations.aiohttp import AioHttpIntegration

from kisee import views
from kisee.identity_provider import import_idp
from kisee.middlewares import enforce_json

Settings = Mapping[str, Any]

AIOHTTP_LOGGERS = (
    "aiohttp.access",
    "aiohttp.client",
    "aiohttp.internal",
    "aiohttp.server",
    "aiohttp.web",
    "aiohttp.websocket",
)


def setup_logging(loglevel):  # pragma: no cover
    """Setup basic logging
    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=50 - (loglevel * 10),
        stream=sys.stdout,
        format=logformat,
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def load_conf(settings_path: str = "settings.toml") -> Settings:
    """Search for a settings.toml file and load it.
    """
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
    """Parses command line arguments.
    """
    if program_args is None:
        program_args = sys.argv[1:]
    parser = argparse.ArgumentParser(description="Shape Identity Provider")
    parser.add_argument("--settings", default="settings.toml")
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        default=0,
        help="Verbose mode (-vv for more, -vvv, …)",
        action="count",
    )
    return parser.parse_args(program_args)


def create_app(settings: Optional[Settings] = None) -> web.Application:
    """Identification provider entry point: builds and run a webserver.
    """
    settings = load_conf()
    app = web.Application(
        middlewares=[enforce_json], debug=settings["server"].get("debug", False),
    )
    app["settings"] = settings
    app["identity_backend"] = import_idp(settings["identity_backend"]["class"])(
        settings["identity_backend"].get("options", {})
    )

    async def on_startup_wrapper(app):
        """Wrapper to call __aenter__.
        """
        await app["identity_backend"].__aenter__()

    async def on_cleanup_wrapper(app):
        """Wrapper to call __exit__.
        """
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
            web.patch("/users/{username}/", views.patch_user),
            web.get("/forgotten_passwords/", views.get_forgotten_passwords),
            web.post("/forgotten_passwords/", views.post_forgotten_passwords),
            web.get("/health/", views.get_health),
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
    """Command line entry point.
    """
    args = parse_args()
    setup_logging(args.loglevel)
    settings = load_conf(args.settings)
    sentry_sdk.init(settings.get("SENTRY_DSN"), integrations=[AioHttpIntegration()])
    app = create_app(settings)
    web.run_app(
        app, host=settings["server"]["host"], port=int(settings["server"]["port"])
    )
