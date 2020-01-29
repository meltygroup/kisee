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

```bash
$ pip install kisee
$ kisee --settings example-settings.toml
```

This starts Kisee with an in-memory demo backend, just so you can
play. The demo backend will print the admin credentials at startup:


```bash
$ kisee --settings example-settings.toml

Admin credentials for this session is:
username: root
password: UGINenIU

======== Running on http://0.0.0.0:8140 ========
(Press CTRL+C to quit)
```

So we can start by getting a JWT for the admin user (beware, your
password is different):

```bash
$ curl 0:8140/jwt/ -XPOST -d '{"username": "root", "password": "UGINenIU"}'
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
                "name": "username",
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

It's possible for a new user to "self-register" by posting on `/users/`:

```bash
$ curl -i 0:8140/users/ -XPOST -d '{"username": "JohnDoe", "password": "sdfswlwl", "email": "john@example.com"}'
HTTP/1.1 201 Created
Location: /users/JohnDoe/
```

Read the docs: https://kisee.readthedocs.io
