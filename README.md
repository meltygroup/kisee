# Identification provider server — AioHTTP POC

This service deliver proof of identities in the form of asymetrically
signed json web tokens. It does *not*, and is not aimed at, handling
groups, impersonation, and so on, this is the role of another service,
the IdM (identity managment).

- Module identification is the shape binding (specific).
- Module shapeidp is the core (unspecific).

The API between unspecific and specific code is a class, configured in
`settings.yml`, implementing:

class DataStore:
    async def on_startup(self, app):
        """Let you open database connection or whatever.
        """

    async def on_cleanup(self, app):
        """aiohttp teardown.
        """

    async def identify(self, login, password):
        """Should return a User dictionary containing at least a 'login'
        attribute if the login/password is correct, else None.
        """


## Running

You'll need a `settings.yaml` file like:

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

And start the server using:

```
python3 -m shapeidp
```


## Contributing

To setup a dev environment, create a venv and run:

```
python3 -m pip install -e .[dev]
```

And run it using:

```
python3 -m shapeidp
```


## API

This POC, as any service, should expose an API and an admin interface
(for debugging purpose only).

The admin should be mounted on `/admin/`, and although this service
does *not* handle the notion of roles and permissions, it has the
notion of "root vs non-root" user, so only root users can access the
admin (in which they see everything and can modify everything).

The API exposes the following resources:

- A home on `/` (GET).
- JSON web tokens on `/jwt/` (GET, POST).


# TODO

- Self-service registration.
- Token invalidation (`DELETE /jwt{/jti}`).
- Self-service password reset.
- Rate-limiting?
- Better error messages (Maybe https://github.com/blongden/vnd.error?)
