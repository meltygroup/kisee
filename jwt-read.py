#!/usr/bin/env python3

import sys

import jwt
import toml


with open("example-settings.toml") as settings_file:
    settings = toml.load(settings_file)

print(jwt.decode(sys.argv[1], settings["public_key"], algorithms=["ES256"]))
