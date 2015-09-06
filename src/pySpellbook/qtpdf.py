from PySide import QtWebKit, QtCore, QtGui
import os

class Printer(QtCore.QObject):
    def __init__(self, parent):
        super().__init__(parent)

    def load(self, url):
        print(url)
        self.url = url


    def print(self, filename):
        print(filename)
        self.filename = filename
        self.printer = QtGui.QPrinter()
        self.printer.setPageSize(QtGui.QPrinter.A4)
        self.printer.setColorMode(QtGui.QPrinter.Color)
        self.printer.setOutputFormat(QtGui.QPrinter.PdfFormat)
        self.printer.setOutputFileName(filename)
        self.page = QtWebKit.QWebPage(self.parent())
        self.page.mainFrame().load("file://%s" % self.url)
        self.view = QtWebKit.QWebView()
        self.view.setPage(self.page)
        #self.view.show()
        self.page.mainFrame().loadFinished.connect(self.print_)

    def print_(self, ok):
        self.page.mainFrame().print_(self.printer)
