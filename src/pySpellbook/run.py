import sys
import os
import signal
from pkg_resources import resource_filename
from appdirs import AppDirs
from PySide import QtGui, QtCore
from pySpellbook.db import db
from pySpellbook.newMainWindow import SpellBookWindow

VERSION="0.9"
def find_data_file(filename):
    if getattr(sys, 'frozen', False):
        # The application is frozen
        return os.path.join(os.path.dirname(sys.executable), filename)
    else:
        # The application is not frozen
        # Change this bit to match where you store your data files:
        return resource_filename(__name__, filename)


def run_pyspellbook():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    dirs = AppDirs("pySpellbook")
    configdir = dirs.user_config_dir
    datadir = dirs.user_data_dir
    os.makedirs(configdir, exist_ok=True)
    os.makedirs(datadir, exist_ok=True)
    app = QtGui.QApplication(sys.argv)
    locale = QtCore.QLocale.system().name()
    translator = QtCore.QTranslator()
    translator.load(find_data_file("i18n/%s" % locale))
    app.installTranslator(translator)
    if sys.platform == "darwin":
        app.setAttribute(QtCore.Qt.AA_DontShowIconsInMenus)
    DB = db(os.path.join(datadir,"spells.db"), debug=False)
    mainWindow = SpellBookWindow(DB, os.path.join(configdir, "pyspellbook.conf"), VERSION)
    mainWindow.show()
    sys.exit(app.exec_())
