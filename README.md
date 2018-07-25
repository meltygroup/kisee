# Kisee — Identity Provider Server

## Name

The name "Kisee", inspired from "KISS" ("Keep it simple, stupid.") is
spoken as the french phrase "Qui c'est ?", `[kis‿ɛ]`.


## Overview

This service deliver proof of identities in the form of asymetrically
signed JSON web tokens. It does not (and will not) handle groups,
impersonation, and so on, which is the role of another service, an IdM
(identity managment).


An exception to the rule, Kisee handles a single bit attached to a
user: `superuser`. A `superuser` is an administrative account allowed
to connect to the admin interface, mainly for debugging purposes.

The `superuser` flag is *not* exposed as a claim in the JWTs, it's a
internal flag.


## Internals

The `Kisee` daemon does not store `(login, password)` tuples, but uses
a Python class, a `backend` you can configure in `settings.yml` to
handle this.

`Kisee` provides some `demo backends` and `test backends` so you can
play with it. You can provide your own backend to hit your own
database, your LDAP server, or another IdP as needed.


## The backend interface

The backend class used by Kisee must implement the following methods:

```
class User:
    """A authenticated User instance.
    You can implement it as a namedtuple, a class, whatever...
    """
    @property
    def login(self) -> str:
        ...

    @property
    def is_superuser(self) -> bool:
        ...


class Backend:
    def __init__(self, options: dict):
        """options is the identity_backend.options value of settings.yml.
        """
        ...

    async def __aenter__(self):
        """Let you open database connection or whatever initialisation you need.
        """

    async def __aexit__(self):
        """Let you close your database connection or whatever.
        """

    async def identify(self, login: str, password: str) -> User:
        """Return a User instance if login and password matches,
        returns None if not.
        """
```

## Running

You'll need a `settings.yaml` file like:

```
---

identity_backend:
  class: identification.backend.mysql.DataStore
  options:
    host: sql2.eeple.fr
    user: melty
    password: Ktt9ubHZv7NxfDpj
    database: actuados

jwt:
  iss: idp.meltylab.fr

# Generated using:
#
#    openssl ecparam -name secp256k1 -genkey -noout -out secp256k1.pem
#
# Yes we know P-256 is a bad one, but for compatibility with JS
# clients for the moment we can't really do better.
private_key: |
    -----BEGIN EC PRIVATE KEY-----
    ...

# Generated using:
# openssl ec -in secp256k1.pem -pubout > secp256k1.pub
public_key: |
  -----BEGIN PUBLIC KEY-----
  MFYwEAYHKoZIzj0CAQYFK4EEAAoDQgAEEVgsgM7Aliru0XU+OggGC5jxRoZUI4/C
  fsNJ8ZUlTKxjn8VzO4Db2ITFvUdyRCQjGRuq5QRJt7a46ZyfrDb+6w==
  -----END PUBLIC KEY-----
```


And start the server using:

```
kisee
```


## Contributing

To setup a dev environment, create a venv and run:

```
python3 -m pip install -e .[dev]
```

And run it using:

```
kisee --settings-file example-settings.yaml
```


## API

The admin should be mounted on `/admin/`, and although this service
does *not* handle the notion of roles and permissions, it has the
notion of "root vs non-root" user, so only root users can access the
admin (in which they see everything and can modify everything).

The API exposes the following resources:

- A home on `/` (GET).
- JSON web tokens on `/jwt/` (GET, POST).


# TODO

- Admin interface
- Status page
- Self-service registration.
- Token invalidation (`DELETE /jwt{/jti}`).
- Self-service password reset.
- Rate-limiting?
- Better error messages (Maybe https://github.com/blongden/vnd.error?)
