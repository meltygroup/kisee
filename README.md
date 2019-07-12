# Kisee — Identity Provider Server

[![Documentation Status](https://readthedocs.org/projects/kisee/badge/?version=latest)](https://kisee.readthedocs.io/en/latest/?badge=latest)


## Name

The name "Kisee", inspired from "KISS" ("Keep it simple, stupid.") is
spoken as the french phrase "Qui c'est ?", `[kis‿ɛ]`.


## Overview

Kisee is an API giving JWTs in exchange for valid usernames/password
pairs. That's it.

Kisee is better used as a backend of the
[Pasee](https://github.com/meltygroup/pasee/) identity manager: Pasee
handle groups and can handle multiple identity backends (one or many
Kisee instances, twitter, facebook, ...).

Kisee can use your existing database (or use a dedicated one) to query
the username and passwrds if you're willing to implement a simple
Python class to query it, so Kisee can query anything: LDAP, a flat
file, a PostgreSQL database with a strange schema, whatever.


## Quick start

Once you've cloned the repo and created a venv, install kisee in it:

```
$ python3 -m pip install -e .[dev]
```

Start kisee:

```
$ kisee --settings example-settings.toml
```

This starts Kisee with a very dumb backend, just so you can play.

The dumb backend works like this:
 - Any user exists.
 - Any password less or equal than 4 characters will be considered wrong.
 - Any other password will pass.

So now we can query it:

```
$ curl http://0.0.0.0:8140/jwt/ -XPOST -d '{"login": "John", "password": "secure"}'
{
    "_type": "document",
    "_meta": {
        "url": "/jwt/",
        "title": "JSON Web Tokens"
    },
    "tokens": [
        "eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiJ9.eyJpc3MiOiJleGFtcGxlLmNvbSIsInN1YiI6IkpvaG4iLCJleHAiOjE1NTMyNzQyNjEsImp0aSI6IjlXb0piV1g2OGpmQVo5N1dNRWRjNDQifQ.iYAgA-018VHQo9tWLfk7XIxtrDKYk_CTWhHXo7bMBGDz9HGKRIwV_mh0Wla6tf6z-_JH5KRTQRnQl5DLLlIelg"
    ],
    "add_token": {
        "_type": "link",
        "action": "post",
        "title": "Create a new JWT",
        "description": "POSTing to this endpoint create JWT tokens.",
        "fields": [
            {
                "name": "login",
                "required": true
            },
            {
                "name": "password",
                "required": true
            }
        ]
    }
}
```

## FAQ


## Internals

The `Kisee` daemon does not store `(login, password)` tuples, but uses
a Python class, a `backend` you can configure in `settings.toml` to
handle this.

`Kisee` provides some `demo backends` and `test backends` so you can
play with it. You can provide your own backend to hit your own
database, your LDAP server, or another IdP as needed.


# TODO

- Admin interface
- Status page
- Token invalidation (`DELETE /jwt{/jti}`).
- Rate-limiting
- Better error messages (Maybe https://github.com/blongden/vnd.error?)
