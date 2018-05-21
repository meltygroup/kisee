#!/usr/bin/env python3

"""Setup.py for the aiohttp-id project.
"""

from setuptools import setup, find_packages


def setup_package():
    setup(
        name='aiohttp-id',
        version='0.0.1',
        description='HTTP server managing identities.',
        long_description='',
        author='Julien Palard',
        author_email='julien@palard.fr',
        license="mit",
        url='https://github.com/meltygroup/aiohttp-id',
        classifiers=[
            'Development Status :: 2 - Pre-Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Natural Language :: English',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6'
        ],
        package_dir={'': 'src'},
        install_requires=[
            'aiohttp',
            'pyyaml',
            'bcrypt',
            'pyjwt',
            'cryptography',
            'shortuuid',
        ],
        extras_require={
            'dev': [
                'flake8',
                'pylint',
                'pytest',
                'pytest-cov',
                'detox',
                'mypy',
            ]
        },
        packages=find_packages('src'))


if __name__ == "__main__":
    setup_package()
