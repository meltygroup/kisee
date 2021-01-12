Contributing
============

Quickstart
----------

To install dev dependencies, create a venv and run::

  pip install -r requirements-dev.txt
  pip install -e .
  cp example-settings.toml settings.toml

And run kisee in development mode using::

  adev runserver kisee/kisee.py


Internals
---------

The ``Kisee`` daemon does not store ``(username, password)`` tuples, but uses
a Python class, a ``backend`` you can choose in ``settings.toml`` to
handle the actual storage..

``Kisee`` provides some ``demo backends`` and ``test backends`` so you can
play with them. You can provide your own backend to hit your own
database, your LDAP server, or another IdP as needed.


Releasing
---------

Our version scheme is `calver <https://calver.org/>`__, specifically
``YY.MM.MICRO``, so please update it in ``kisee/__init__.py`` (single
place), git tag, commit, and push.

Then to release::

  git clean -dfqx
  build --sdist --wheel .
  twine upload dist/*
