import sys
import os
from appdirs import AppDirs
from PySide import QtGui
from pySpellbook.db import db
from pySpellbook.newMainWindow import SpellBookWindow

def run_pyspellbook():
    dirs = AppDirs("pySpellbook")
    configdir = dirs.user_config_dir
    datadir = dirs.user_data_dir
    os.makedirs(configdir, exist_ok=True)
    os.makedirs(datadir, exist_ok=True)
    app = QtGui.QApplication(sys.argv)
    DB = db(os.path.join(datadir,"spells.db"), debug=False)
    mainWindow = SpellBookWindow(DB, os.path.join(configdir, "pyspellbook.conf"))
    mainWindow.show()
    sys.exit(app.exec_())
