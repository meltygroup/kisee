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


Building the API doc
--------------------

We have a description of the kisee API using OpenAPI v3, that can be checked using::

  pip install openapi-spec-validator
  openapi-spec-validator kisee.yaml

so we can generate some things from here, like a documentation, for
example::

  wget https://repo1.maven.org/maven2/org/openapitools/openapi-generator-cli/5.0.0-beta2/openapi-generator-cli-5.0.0-beta2.jar -O openapi-generator-cli.jar
  java -jar openapi-generator-cli.jar generate -g html2 -i kisee.yaml -o apidocs/


Or by using `the plain old standalone HTML/CSS/JS swagger-ui
<https://github.com/swagger-api/swagger-ui/blob/master/docs/usage/installation.md#plain-old-htmlcssjs-standalone>`_.


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
  python -m build --sdist --wheel .
  twine upload dist/*
