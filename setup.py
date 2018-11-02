#!/usr/bin/env python3

"""Setup.py for the aiohttp-id project.
"""

import setuptools


setuptools.setup(
    name="kisee",
    version="0.0.2",
    description="HTTP server managing identities.",
    long_description="",
    author="Julien Palard",
    author_email="julien@palard.fr",
    license="mit",
    url="https://github.com/meltygroup/aiohttp-id",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    install_requires=[
        "aiohttp>=3.2.1,<4",
        "aiomysql>=0.0.15",
        "bcrypt>=3.1.4,<4",
        "coreapi>=2.3.3,<3",
        "cryptography>=2.2.2,<3",
        "pyjwt>=1.6.3,<2",
        "shortuuid>=0.5.0",
        "toml==0.9.4",
        "psutil",
        "asyncpg",
    ],
    extras_require={
        "test": [
            "pytest==3.6.3",
            "pytest-cov==2.5.1",
            "pytest-aiohttp==0.3.0",
            "flake8==3.5.0",
            "pylint==2.0.1",
            "black==18.6b4",
            "bandit",
            "mypy==0.610",
            "detox==0.12",
            "aiohttp==3.3.2",
        ]
    },
    packages=setuptools.find_packages(exclude=["tests"]),
    entry_points={"console_scripts": ["kisee=kisee.kisee:main"]},
)
