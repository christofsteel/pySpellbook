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
#if sys.platform.startswith("win32"):
#    try:
#        from cx_Freeze import setup, Executable
#    except:
#        class Executable:
#            def __init__(self, p1, base):
#                pass
#    base = "WIN32GUI"
#    build_exe_options = {"include_files": "src/pySpellbook/templates/", 'include_msvcr': True}
#    setup(
#        name = "pySpellbook",
#        version = "0.7.2",
#        packages = find_packages('src'),
#        package_dir = {'':'src'},
#        scripts = ["src/pySpellbook-qt4", "src/pySpellbook/importPathfinder.py"],
#        package_data = {'pySpellbook':['templates/html/resources/*','templates/html/template.html']},
#        entry_points={
#            'console_scripts': [
#                'pySpellbook = pySpellbook.qt:run_pyspellbook'
#            ]},
#        install_requires = install_requires,
#        extras_require = extras,
#        options = {"build_exe": build_exe_options},
#        executables = [Executable("src/pySpellbook-qt4", base=base)]
#    )
#else:
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
    version = "0.8.0",
    packages = find_packages('src'),
    package_dir = {'':'src'},
    extras_require = extras,
    scripts = ['src/pySpellbook/importPathfinder.py'],
    package_data = {'pySpellbook':['templates/html/resources/*','templates/html/template.html']},
    entry_points={
        'console_scripts': [
            'pySpellbook = pySpellbook.qt:run_pyspellbook',
            'importPathfinder = pySpellbook.importPathfinder:main [import]'
        ]},
    install_requires = install_requires,
)


