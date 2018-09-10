"""Abstract class representing an identity provider
"""


from abc import ABC, abstractmethod
from importlib import import_module
from typing import AsyncContextManager, Type, Optional


class User:
    """Represents a logged-in, correctly identified, person.
    """

    def __init__(self, login: str, is_superuser: bool = False) -> None:
        self.login = login
        self.is_superuser = is_superuser


class IdentityProvider(ABC, AsyncContextManager):  # pragma: no cover
    """Abtract class representing an identity provider
    """

    def __init__(self, options: dict) -> None:
        self.options = options
        super().__init__()

    @abstractmethod
    async def identify(self, login: str, password: str) -> Optional[User]:
        """Identifies the given login/password pair, returns a dict if found.
        """

    @abstractmethod
    async def register_user(
        self, username: str, password: str, is_superuser: bool = False
    ):
        """Create user with login/password pair
        """

    @abstractmethod
    async def is_connection_alive(self) -> bool:
        """Verify that connection with identity provider datastore is alive
        """


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
