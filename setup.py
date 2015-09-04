#!/usr/bin/env python
from setuptools import setup, find_packages
import sys

install_requires = ['sqlalchemy',
                    'PySide',
                    'jinja2',
                    'pyquery',
                    'weasyprint',
                    'appdirs']


if sys.platform.startswith("win32"):
    install_requires = ['sqlalchemy',
                        'PySide',
                        'jinja2',
                        'pyquery',
                        'appdirs']


setup(
    name = "pySpellbook",
    version = "0.7",
    packages = find_packages('src'),
    package_dir = {'':'src'},
    package_data = {'pySpellbook':['templates/html/resources/*','templates/html/template.html']},
    entry_points={
          'console_scripts': [
              'pySpellbook = pySpellbook.qt:run_pyspellbook'
          ]},
    install_requires = install_requires
)
