Contributing
============

Quickstart
----------

To install dev dependencies, create a venv and run::

  pip install flit
  flit install --symlink

And run kisee using::

  kisee  # or python -m kisee


Releasing
---------

Our version scheme is `calver <https://calver.org/>`__, specifically
``YY.MM.MICRO``, so please update it in ``kisee/__init__.py`` (single
place), git tag, commit, and push.

Then to release we're using `flit <https://flit.readthedocs.io>`__::

  flit publish
