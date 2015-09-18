#!/usr/bin/env python3
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.


# Change some default MSI options
bdist_msi_options = {'upgrade_code': '0a059d05-7e7a-444a-8419-45957ad7b2a3'}

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
    Executable('src/script/pySpellbook', base=base, targetName = 'pySpellbook.exe' if sys.platform == "win32" else "pySpellbook",
               icon='src/icons/pySpellbook.ico', shortcutName="PySpellbook", shortcutDir="StartMenuFolder")
]

setup(name='pySpellbook',
      version = '0.8.0',
      description = 'A PDF spellbook creation utility for d20 games in python',
      author = 'Christoph Stahl',
      options = dict(build_exe = buildOptions, build_msi = bdist_msi_options),
      executables = executables)
