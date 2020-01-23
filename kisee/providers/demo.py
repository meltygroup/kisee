"""This is a really dumb identification backend: it does not store
anything and accepts almost any login/password pair.
"""
from typing import Optional
from string import ascii_letters, digits
from random import choices
import curses

from kisee.identity_provider import (
    IdentityProvider,
    User,
    ProviderError,
    UserAlreadyExist,
)


class DummyUser(User):
    """The demo has no storage, so we'll just store the password in the
    user objects in memory.
    """

    def __init__(self, password, **kwargs):
        super().__init__(**kwargs)
        self.password = password


class DemoBackend(IdentityProvider):
    """In-memory identity backend, for demo and tests purposes.

    This backend follow the following rules:
     - Any user with a username of more than 3 characters can be created.
     - root:root already exists, is supseruser.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root_password = "".join(choices(ascii_letters + digits, k=8))
        self._print_credentials(root_password)
        self.storage = {
            "root": DummyUser(
                user_id="root",
                username="root",
                password=root_password,
                email="root@example.com",
                is_superuser=True,
            )
        }

    def _print_credentials(self, password):
        try:
            curses.setupterm()
            fg_color = curses.tigetstr("setaf") or curses.tigetstr("setf") or ""
            green = str(curses.tparm(fg_color, 2), "ascii")
            no_color = str(curses.tigetstr("sgr0"), "ascii")
        except curses.error:
            green, no_color = ""
        print(green)
        print("Admin credentials for this session is:")
        print(f"login: root")
        print(f"password: {password}")
        print(no_color)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

    async def identify(self, login: str, password: str) -> Optional[User]:
        """Identifies the given login/password pair, returns a User if found.
        """
        # pylint: disable=unused-argument
        if login is None or password is None:
            raise ValueError("Missing user or password")
        user = self.storage.get(login)
        if not user:
            return None
        if user.password != password:
            return None
        return user

    async def register_user(
        self, username: str, password: str, email: str, is_superuser: bool = False
    ) -> None:
        if len(username) < 3:
            raise ProviderError("Username too short")
        if username in self.storage:
            raise UserAlreadyExist
        user = DummyUser(
            user_id=username,
            username=username,
            email=email,
            is_superuser=is_superuser,
            password=password,
        )
        self.storage[username] = user

    async def get_user_by_email(self, email) -> Optional[User]:
        """Get user with provided email address
        """
        for user in self.storage.values():
            if user.email == email:
                return user
        return None

    async def get_user_by_username(self, username) -> Optional[User]:
        """Get user with provided username.
        """
        return self.storage.get(username)

    async def set_password_for_user(self, user: User, password: str):
        self.storage[user.username].password = password

    async def is_connection_alive(self) -> bool:
        """Verify that connection is alive, always return True
        """
        return True
