"""Entry point for the identification provider.
"""

import os
import sys
import argparse
from typing import Union

import toml
from aiohttp import web

from shapeidp.utils.module_loading import import_string

from . import views


def load_conf(settings_path: str) -> Union[dict, None]:
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
    return None


def parse_args(program_args=None) -> argparse.Namespace:
    """Parses command line arguments.
    """
    if program_args is None:
        program_args = sys.argv[1:]
    parser = argparse.ArgumentParser(description="Shape Identity Provider")
    parser.add_argument("--settings", default="settings.toml")
    return parser.parse_args(program_args)


def identification_app(settings_path: str) -> None:
    """Identification provider entry point: builds and run a webserver.
    """
    app = web.Application()
    app.settings = load_conf(settings_path)
    app.identity_backend = import_string(app.settings["identity_backend"]["class"])(
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

    web.run_app(
        app,
        host=app.settings["server"]["host"],
        port=int(app.settings["server"]["port"]),
    )


def main() -> None:
    """Command line entry point.
    """
    args = parse_args()
    identification_app(args.settings)


main()
