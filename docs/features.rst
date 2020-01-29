Features
========

Overview
--------

Kisee is an API giving JWTs in exchange for valid usernames/password
pairs. That's it.

Kisee is better used as a backend of the
`Pasee <https://github.com/meltygroup/pasee/>`_ identity manager: Pasee
handle groups and can handle multiple identity backends (one or many
Kisee instances, twitter, facebook, ...).

Kisee can use your existing database (or use a dedicated one) to query
the username and passwords if you're willing to implement a simple
Python class to query it, so Kisee can query anything: LDAP, a flat
file, a PostgreSQL database with a strange schema, whatever.


The backend interface
---------------------

The backend class used by Kisee must implement the
`kisee.identity_provider.IdentityProvider` ABC, meaning the following methods like::

    async def identify(self, username: str, password: str) -> Optional[User]:
        """Identifies the given username/password pair, returns a dict if found.
        """


By implementing the backend ABC, you can make your ``kisee`` instance
use your own backend: your own database schema, or anything storing
your usernames and passwords.

To use your backend, specify it in ``settings.toml`` like this::

    [identity_backend]
      class = "impart.path.to.your.backend.Class"
      [identity_backend.options]
        no = "option required"

The ``options`` dictionary will be passed as a ``options`` parameter
of your backend. This is were you store typically the hostname,
username, and password of your database if any, or path of your
backend file, whatever needed.
