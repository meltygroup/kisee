# Kisee — Identity Provider Server

[![Documentation Status](https://readthedocs.org/projects/kisee/badge/?version=latest)](https://kisee.readthedocs.io/en/latest/?badge=latest)
[![Package on PyPI](https://img.shields.io/pypi/v/kisee.svg)](https://pypi.org/project/kisee/)
[![Build status](https://travis-ci.org/meltygroup/kisee.svg?branch=master)](https://travis-ci.org/meltygroup/kisee)


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

```
$ pip install kisee
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

Read the docs: https://kisee.readthedocs.io
