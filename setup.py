#!/usr/bin/env python3

"""Setup.py for the aiohttp-id project.
"""

from setuptools import setup, find_packages


def setup_package():
    setup(
        name='shapeidp',
        version='0.0.2',
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
            'aiohttp>=3.2.1,<4',
            'aiomysql>=0.0.15',
            'bcrypt>=3.1.4,<4',
            'coreapi>=2.3.3,<3',
            'cryptography>=2.2.2,<3',
            'pyjwt>=1.6.3,<2',
            'pyyaml>=3.12,<4',
            'shortuuid>=0.5.0',
        ],
        extras_require={
            'dev': [
                'flake8',
                'pylint==2.0.0.dev',  # Don't work on py37 without v2
                'astroid==2.0.0.dev',  # Don't work on py37 without v2
                'pytest',
                'pytest-cov',
                'detox',
                'mypy',
            ]
        },
        packages=find_packages('src'))


if __name__ == "__main__":
    setup_package()
