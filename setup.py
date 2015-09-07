#!/usr/bin/env python
from setuptools import setup, find_packages
class Executable:
    def __init__(self, *args, **kwargs):
        print("Foo")
        pass
try:
    from cx_Freeze import setup, Executable
except:
    pass
import sys



base = None
if sys.platform.startswith("win32"):
    install_requires = ['sqlalchemy',
                        'PySide',
                        'jinja2',
                        'pyquery',
                        'appdirs']
    base = "WIN32GUI"
    build_exe_options = {"include_files": "src/pySpellbook/templates/"}
    setup(
        name = "pySpellbook",
        version = "0.7.2",
        packages = find_packages('src'),
        package_dir = {'':'src'},
        scripts = ["src/pySpellbook-qt4", "src/pySpellbook/importPathfinder.py"],
        package_data = {'pySpellbook':['templates/html/resources/*','templates/html/template.html']},
        entry_points={
            'console_scripts': [
                'pySpellbook = pySpellbook.qt:run_pyspellbook'
            ]},
        install_requires = install_requires,
        options = {"build_exe": build_exe_options},
        executables = [Executable("src/pySpellbook-qt4", base=base)]
    )
else:
    install_requires = ['sqlalchemy',
                        'PySide',
                        'jinja2',
                        'pyquery',
                        'weasyprint',
                        'appdirs']
    setup(
        name = "pySpellbook",
        version = "0.7.2",
        packages = find_packages('src'),
        package_dir = {'':'src'},
        scripts = ['src/pySpellbook/importPathfinder.py'],
        package_data = {'pySpellbook':['templates/html/resources/*','templates/html/template.html']},
        entry_points={
            'console_scripts': [
                'pySpellbook = pySpellbook.qt:run_pyspellbook'
            ]},
        install_requires = install_requires,
    )


