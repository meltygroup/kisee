#!/usr/bin/env python3

import sys

import jwt
import yaml


with open('settings.yaml') as settings_file:
    settings = yaml.load(settings_file)

print(jwt.decode(sys.argv[1], settings['public_key'], algorithms=['ES256']))
