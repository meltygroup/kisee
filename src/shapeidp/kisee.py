"""Entry point for the identification provider.
"""

import os
import sys
import argparse

import toml
from aiohttp import web

from shapeidp.identity_provider import import_idp

from . import views


def load_conf(settings_path: str) -> dict:
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
    return parser.parse_args(program_args)


def identification_app(settings: dict) -> web.Application:
    """Identification provider entry point: builds and run a webserver.
    """
    app = web.Application()
    app.settings = settings
    app.identity_backend = import_idp(app.settings["identity_backend"]["class"])(
        app.settings["identity_backend"]["options"]
    )

    app.on_startup.append(app.identity_backend.on_startup)
    app.on_cleanup.append(app.identity_backend.on_cleanup)
    app.add_routes(
        [
            web.get("/", views.get_root),
            web.get("/jwt/", views.get_jwts),
            web.post("/jwt/", views.post_jwt),
            web.get("/jwt/{jid}", views.get_jwt),
        ]
    )

    return app


def main() -> None:  # pragma: no cover
    """Command line entry point.
    """
    args = parse_args()
    settings = load_conf(args.settings)
    app = identification_app(settings)
    web.run_app(
        app, host=settings["server"]["host"], port=int(settings["server"]["port"])
    )
