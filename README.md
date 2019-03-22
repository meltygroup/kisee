# Kisee — Identity Provider Server

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

### Can I use Kisee to query an OAuth2 service like?

Kisee is an identity provider, like twitter, so they're side by side,
one one on top of the other, they play the same role. You can however use
Pasee to query both a Kisee and Twitter.


### Does Kisee implement groups?

No, Kisee doesn't care about groups like Twitter don't care about
groups, they're both just here to say "yes, it's this user" or "no, it
is not". Use Pasee for this.

From the Pasee point of view you'll be able to tell:

 - User foo from Kisee is in group staff
 - User bar from Twitter is in group staff too


### Does Kisee implement impersonation?

No, if we do implement this we'll do in Pasee, so a staff user
identified via Kisee can impersonate a user identified via Twitter and
vice-versa.


### Does Kisee expose self-service registration?

Optionally, only if you implement it or use a backend class implementing it.


### Does Kisee expose a password reset feature?

Yes, by sending an email that you can template in the settings.


## Internals

The `Kisee` daemon does not store `(login, password)` tuples, but uses
a Python class, a `backend` you can configure in `settings.toml` to
handle this.

`Kisee` provides some `demo backends` and `test backends` so you can
play with it. You can provide your own backend to hit your own
database, your LDAP server, or another IdP as needed.


## The backend interface

The backend class used by Kisee must implement the
`kisee.identity_provider.IdentityProvider` ABC.


## API

The API exposes the following resources:

- A json-home on `/`
- `/jwt/` to manage tokens (mainly create a new one by POSTing)
- `/forgotten-passwords/` to initiate a password lost procedure and manage it.
- `POST /users/` for self-service registration.


## Sentry

For sentry to work you'll need the `SENTRY_DSN` environment variable,
see https://docs.sentry.io/error-reporting/quickstart/?platform=python.


# TODO

- Admin interface
- Status page
- Token invalidation (`DELETE /jwt{/jti}`).
- Rate-limiting
- Better error messages (Maybe https://github.com/blongden/vnd.error?)
