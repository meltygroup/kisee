"""Entry point for the identification provider.
"""

import os

import yaml
from aiohttp import web

from idserver.utils.module_loading import import_string

from . import views


def load_conf():
    """Search for a settings.yaml file and load it.
    """
    candidate = os.path.join(os.getcwd(), 'settings.yaml')
    if os.path.exists(candidate):
        with open(candidate) as candidate_file:
            return yaml.load(candidate_file)
    return None


def identification_app():
    """Identification provider entry point: builds and run a webserver.
    """
    app = web.Application()
    app.settings = load_conf()
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


identification_app()
