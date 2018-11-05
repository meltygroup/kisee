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

The backend class used by Kisee must implement the `kisee.identity_provider.IdentityProvider` ABC.


## Running

You'll need a `settings.toml` file like the provided
`example-settings.yoml`, instart kisee (`python3 -m pip install -e
.`), then start the server using:

```
kisee
```


## Contributing

To setup a dev environment, create a venv and run:

```
python3 -m pip install -e .[test]
```

And run it using:

```
kisee --settings example-settings.toml
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
