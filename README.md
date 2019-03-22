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


## Running

You'll need a `settings.toml` file like the provided
`example-settings.yoml`, install kisee (`python3 -m pip install -e
.`), then start the server using:

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
kisee --settings example-settings.toml
```


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
