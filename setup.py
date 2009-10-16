"""
Setup.py for tiddlyweb-plugins
"""

import os
from setuptools import setup, find_packages

VERSION = 0.7

setup(
        name = 'tiddlywebplugins',
        namespace_packages = ['tiddlywebplugins'],
        long_description=file(os.path.join(os.path.dirname(__file__), 'README')).read(),
        version = VERSION,
        description = 'Tools and methods for managing TiddlyWeb plugins',
        author = 'Chris Dent',
        author_email = 'cdent@peermore.com',
        url = 'http://pypi.python.org/pypi/tiddlywebplugins',
        packages = find_packages(),
        platforms = 'Posix; MacOS X; Windows',
        install_requires = ['setuptools', 'tiddlyweb'],
        )
