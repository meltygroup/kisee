"""Abstract class representing an identity provider
"""


from abc import ABC
from importlib import import_module
from typing import Union, Type

from aiohttp import web


class IdentityProvider(ABC):
    """Abtract class representing an identity provider
    """

    def __init__(self, options: dict) -> None:
        self.options = options

    async def on_startup(self, app: web.Application):
        """Called by aiohttp on startup.
        """
        pass

    async def on_cleanup(self, app: web.Application):
        """Called by aiohttp on cleanup.
        """
        pass

    async def identify(self, login: str, password: str) -> Union[dict, None]:
        """Identifies the given login/password pair, returns a dict if found.
        """
        pass


def import_idp(dotted_path: str) -> Type[IdentityProvider]:
    """Import a dotted module path and return the attribute/class
    designated by the last name in the path. Raise ImportError if the
    import failed.
    """
    try:
        module_path, class_name = dotted_path.rsplit(".", 1)
    except ValueError as err:
        raise ImportError("%s doesn't look like a module path" % dotted_path) from err

    module = import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError as err:
        raise ImportError(
            'Module "%s" does not define a "%s" attribute/class'
            % (module_path, class_name)
        ) from err
