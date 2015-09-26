#!/usr/bin/env python3
from setuptools import setup, find_packages
import sys

install_requires = ['sqlalchemy',
                    'PySide',
                    'jinja2',
                    'appdirs']
extras = {
    'weasy': 'weasyprint',
    'import': 'pyquery'
}

if sys.platform != "win32":
    data_files=[('share/applications/', ['src/pySpellbook.desktop']),
                ('share/pixmaps/', ['src/icons/pySpellbook.png'])]
else:
    data_files = []

setup(
    name = "pySpellbook",
    author = "Christoph Stahl",
    author_email = "christoph.stahl@uni-dortmund.de",
    url = "https://github.com/christofsteel/pyspellbook",
    description = "A PDF spellbook creation utility for d20 games in python",
    license = "apache2",
    platforms = ["posix", "win32", "win64"],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Topic :: Games/Entertainment :: Role-Playing'

    ],
    version = "0.8.1",
    packages = find_packages('src'),
    package_dir = {'':'src'},
    extras_require = extras,
    data_files = data_files,
    package_data = {'pySpellbook':['templates/html/resources/*','templates/html/template.html']},
    scripts = [ "src/scripts/pySpellbook", "src/scripts/pySpellbook-importpathfinder", "src/scripts/pySpellbook-importpathfinderDE" ],
    install_requires = install_requires,
)


