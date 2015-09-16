#!/usr/bin/env python3
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = ["pySpellbook",
                                "PySide",
                                "appdirs",
                                "jinja2",
                                "sqlalchemy"],
                    include_files = ["src/pySpellbook/templates/"],
                    include_msvcr = True,
                    excludes = [])

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('src/pySpellbook-qt4', base=base, targetName = 'pySpellbook.exe' if sys.platform == "win32" else "pySpellbook")
]

setup(name='pySpellbook',
      version = '0.8.0',
      description = 'A PDF spellbook creation utility for d20 games in python',
      author = 'Christoph Stahl',
      options = dict(build_exe = buildOptions),
      executables = executables)
