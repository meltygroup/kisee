"""Entry point for the identification provider.
"""

import os

import yaml
from aiohttp import web

from shapeidp.utils.module_loading import import_string

from . import views


def load_conf(settings_path):
    """Search for a settings.yaml file and load it.
    """
    candidates = (settings_path,
                  os.path.join(os.getcwd(), settings_path),
                  os.path.join(os.getcwd(), 'settings.yaml'),
                  os.path.expanduser("~/settings.yaml"),
                  os.path.expanduser(os.path.join("~/", settings_path)),
                  '/etc/settings.yaml',
                  os.path.join("/etc/", settings_path))
    for candidate in candidates:
        if os.path.exists(candidate):
            with open(candidate) as candidate_file:
                return yaml.load(candidate_file)
    return None


def parse_args():
    """Parses command line arguments.
    """
    import argparse
    parser = argparse.ArgumentParser(
        description="Shape Identity Provider")
    parser.add_argument('--settings', default='settings.yaml')
    return parser.parse_args()


def identification_app(settings_path):
    """Identification provider entry point: builds and run a webserver.
    """
    app = web.Application()
    app.settings = load_conf(settings_path)
    app.identity_backend = import_string(
        app.settings['identity_backend']['class'])(
            app.settings['identity_backend']['options'])

    app.on_startup.append(app.identity_backend.on_startup)
    app.on_cleanup.append(app.identity_backend.on_cleanup)
    app.add_routes(
        [web.get('/', views.get_root),
         web.get('/jwt/', views.get_jwts),
         web.post('/jwt/', views.post_jwt),
         web.get('/jwt/{jid}', views.get_jwt)])

    web.run_app(app)


def main():
    """Command line entry point.
    """
    args = parse_args()
    identification_app(args.settings)


main()
