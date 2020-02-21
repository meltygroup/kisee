"""This is a really dumb identification backend: it does not store
anything and accepts almost any username/password pair.
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


def _colored_print(*args, sep=" ", end="\n") -> None:
    try:  # pragma: no cover  (no term in pytest)
        curses.setupterm()
        fg_color = curses.tigetstr("setaf") or curses.tigetstr("setf") or b""
        green = str(curses.tparm(fg_color, 2), "ascii")
        no_color = str(curses.tigetstr("sgr0"), "ascii")
    except curses.error:
        green, no_color = "", ""
    print(green)
    print(*args, sep=sep, end=end)
    print(no_color)


class DemoBackend(IdentityProvider):
    """In-memory identity backend, for demo and tests purposes.

    This backend follow the following rules:
     - Any user with a username of more than 3 characters can be created.
     - root:root already exists, is supseruser.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.password_reset_tokens = []  # So we can fetch it back from the tests.
        root_password = "".join(choices(ascii_letters + digits, k=8))
        _colored_print(
            "Admin credentials for this session is:",
            f"username: root",
            f"password: {root_password}",
            sep="\n",
        )

        self.storage = {
            "root": DummyUser(
                user_id="root",
                username="root",
                password=root_password,
                email="root@example.com",
                is_superuser=True,
            )
        }

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

    async def identify(self, username: str, password: str) -> Optional[User]:
        """Identifies the given username/password pair, returns a User if found.
        """
        if username is None or password is None:
            raise ValueError("Missing user or password")
        user = self.storage.get(username)
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

    async def send_reset_password_challenge(self, user: User, challenge: str):
        _colored_print(
            f"Password reset challenge for user {user.username} is {challenge}"
        )
        self.password_reset_tokens.append(challenge)

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
