.. highlight:: toml

Configuration File
==================

Example
-------

A typical ``settings.toml`` file looks like this::

    [server]
    host = "0.0.0.0"
    hostname = "http://localhost:8140"
    port = 8140
    debug = true

    [identity_backend]
      class = "kisee.providers.demo.DemoBackend"
      [identity_backend.options]
        no = "option required"

    [email]
      host = "localhost"
      sender = "sender@example.com"

    [jwt]
      iss = "example.com"

      # Generated using:
      #
      #    openssl ecparam -name secp256k1 -genkey -noout -out secp256k1.pem
      #
      # Yes we know P-256 is a bad one, but for compatibility with JS
      # clients for the moment we can't really do better.
      private_key = '''
    -----BEGIN EC PRIVATE KEY-----
    MHQCAQEEIJJaLOWE+5qg6LNjYKOijMelSLYnexzLmTMvwG/Dy0r4oAcGBSuBBAAK
    oUQDQgAEE/WCqajmhfppNUB2uekSxX976fcWA3bbdew8NkUtCoBigl9lWkqfnkF1
    8H9fgG0gafPhGtub23+8Ldulvmf1lg==
    -----END EC PRIVATE KEY-----'''

      # Generated using:
      # openssl ec -in secp256k1.pem -pubout > secp256k1.pub
      public_key = '''
    -----BEGIN PUBLIC KEY-----
    MFYwEAYHKoZIzj0CAQYFK4EEAAoDQgAEE/WCqajmhfppNUB2uekSxX976fcWA3bb
    dew8NkUtCoBigl9lWkqfnkF18H9fgG0gafPhGtub23+8Ldulvmf1lg==
    -----END PUBLIC KEY-----'''


Logging
-------

Logging can be deeply customized via the configuration file as it uses
`dictConfig
<https://docs.python.org/3/library/logging.config.html#logging.config.dictConfig>`_
from the `logging` section, by default it is similar to::

    [logging]
    version = 1
    disable_existing_loggers = false

        [logging.formatters.full]
        format = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"

        [logging.handlers.stderr]
        class = "logging.StreamHandler"
        stream = "ext://sys.stderr"
        level = "DEBUG"
        formatter = "full"

        [logging.loggers.kisee]
        level = "DEBUG"
        handlers = ["stderr"]


Sentry
------

Sentry is optional.

For Sentry to work you'll need the `SENTRY_DSN` environment variable,
and `sentry-sdk` installed, that's it.
