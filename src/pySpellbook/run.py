import sys
import os
import signal
from appdirs import AppDirs
from PySide import QtGui, QtCore
from pySpellbook.db import db
from pySpellbook.newMainWindow import SpellBookWindow

VERSION="0.8.1"

def run_pyspellbook():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    dirs = AppDirs("pySpellbook")
    configdir = dirs.user_config_dir
    datadir = dirs.user_data_dir
    os.makedirs(configdir, exist_ok=True)
    os.makedirs(datadir, exist_ok=True)
    app = QtGui.QApplication(sys.argv)
    if sys.platform == "darwin":
        app.setAttribute(QtCore.Qt.AA_DontShowIconsInMenus)
    DB = db(os.path.join(datadir,"spells.db"), debug=False)
    mainWindow = SpellBookWindow(DB, os.path.join(configdir, "pyspellbook.conf"), VERSION)
    mainWindow.show()
    sys.exit(app.exec_())
