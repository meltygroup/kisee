Contributing
============

Quickstart
----------

To install dev dependencies, create a venv and run::

  pip install flit
  flit install --symlink

And run kisee using::

  kisee  # or python -m kisee


Internals
---------

The ``Kisee`` daemon does not store ``(login, password)`` tuples, but uses
a Python class, a ``backend`` you can configure in ``settings.toml`` to
handle this.

``Kisee`` provides some ``demo backends`` and ``test backends`` so you can
play with it. You can provide your own backend to hit your own
database, your LDAP server, or another IdP as needed.


Releasing
---------

Our version scheme is `calver <https://calver.org/>`__, specifically
``YY.MM.MICRO``, so please update it in ``kisee/__init__.py`` (single
place), git tag, commit, and push.

Then to release we're using `flit <https://flit.readthedocs.io>`__::

  flit publish
