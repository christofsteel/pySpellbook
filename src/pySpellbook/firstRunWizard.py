#!/usr/bin/env python

"""Based on the PyQt4 port of the dialogs/trivialwizard example from Qt v4.x"""

import sys
import platform
import tarfile
import zipfile
import tempfile
import json
import urllib.request
from appdirs import AppDirs
import os
from PySide import QtGui, QtCore, QtNetwork

class DownloadWithProgress:
    def __init__(self, parent, url, downloaddir, finished, canceled, error, text):
        self.url = url
        self.downloaddir = downloaddir
        self.hasError = False
        self.parent = parent
        self.text = text
        self.manager = QtNetwork.QNetworkAccessManager(parent)
        self.finished = finished
        self.cancel = False
        self.error = error
        self.canceled = canceled

    def ended(self):
        if not self.cancel and not self.hasError:
            try:
                self.content = self.reply.readAll()
                if self.downloaddir:
                    fileInfo = QtCore.QFileInfo(self.url)
                    fileName = os.path.join(self.downloaddir, fileInfo.fileName())
                    f = QtCore.QFile(os.path.join(self.downloaddir, fileName))
                    f.open(QtCore.QIODevice.WriteOnly)
                    f.write(self.content)
                    f.close()
                self.finished(self.content)
            except OSError:
                QtGui.QMessageBox.critical(self.parent, "Network Error","An error occured downloading.")

    def cancelDownload(self):
        self.cancel = True
        self.reply.abort()
        if self.canceled:
            self.canceled()

    def download(self):
        self.pd = QtGui.QProgressDialog(self.text, "Abort", 0 ,100, self.parent)
        self.pd.setWindowModality(QtCore.Qt.WindowModal)
        self.pd.canceled.connect(self.cancelDownload)
        request = QtNetwork.QNetworkRequest()
        request.setUrl(QtCore.QUrl(self.url))

        self.reply = self.manager.get(request)
        self.reply.error[QtNetwork.QNetworkReply.NetworkError].connect(self.slotError)
        #self.reply.finished.connect(self.ended)
        self.reply.downloadProgress.connect(self.updateProgress)

        self.pd.exec_()
        self.ended()

    def updateProgress(self, rec, total):
        if total == -1:
            total = rec+1
        self.pd.setMaximum(total)
        self.pd.setValue(rec)




    def slotError(self):
        self.hasError = True
        if self.error:
            self.error()


    def sslErrors(self, errors):
        errorString = ", ".join([str(error.errorString()) for error in errors])

        ret = QtGui.QMessageBox.warning(self, "HTTP Example",
                "One or more SSL errors has occurred: %s" % errorString,
                QtGui.QMessageBox.Ignore | QtGui.QMessageBox.Abort)

        if ret == QtGui.QMessageBox.Ignore:
            self.http.ignoreSslErrors()


class Wizard(QtGui.QWizard):
    def createIntroPage(self):
        page = QtGui.QWizardPage()
        page.setTitle("PySpellbook")

        label = QtGui.QLabel("It seems you are running PySpellbook for the first time. Please allow this wizard to help you setting everything up.")
        label.setWordWrap(True)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(label)
        page.setLayout(layout)

        return page

    def createPrincePage(self):

        def downloadPrince(parent, statusLabel):

            filename = ""
            if sys.platform == "win32":
                if platform.machine() == "AMD64":
                    filename = "prince-10r4p1-win64.zip"
                else:
                    filename = "prince-10r4p1-win32.zip"
            elif sys.platform == "linux":
                if platform.machine() == "x86_64":
                    filename = "prince-10r4-linux-generic-x86_64.tar.gz"
                else:
                    filename = "prince-10r4-linux-generic-i686.tar.gz"
            elif sys.platform == "darwin":
                filename = "prince-10r4-macosx.tar.gz"
            else:
                raise RuntimeError("Non supported platform")

            def download():
                tempdir = tempfile.mkdtemp(prefix="pySpellbook-")
                def error():
                    pass
                def canceled():
                    os.removedirs(tempdir)

                def finished(content):
                    statusLabel.setText("Extracting...")
                    dirs = AppDirs("pySpellbook")
                    datadir = dirs.user_data_dir
                    if filename.endswith("zip"):
                        zf = zipfile.ZipFile(os.path.join(tempdir, filename))
                        zf.extractall(datadir)
                        zf.close()
                        self.parent().config["prince_path"] = os.path.join(datadir, filename.replace(".zip", ""), "bin/prince.exe")
                    else:
                        tf = tarfile.open(os.path.join(tempdir,filename))
                        tf.extractall(datadir)
                        tf.close()
                        self.parent().config["prince_path"] = os.path.join(datadir, filename.replace(".tar.gz", ""), "lib/prince/bin/prince")
                    self.parent().config["backend"] = "prince"
                    QtGui.QMessageBox.information(parent, "Success","Successfully installed PrinceXML to %s." % datadir)
                    statusLabel.setText("")
                    os.remove(os.path.join(tempdir,filename))
                    os.removedirs(tempdir)
                    with open(self.parent().configfile,'w') as f:
                        json.dump(self.parent().config, f, indent=2)

                statusLabel.setText("Downloading...")
                dl = DownloadWithProgress(parent, "http://www.princexml.com/download/%s" % filename, tempdir, finished, canceled, error, "Downloading PrinceXML")
                dl.download()

            return download

        page = QtGui.QWizardPage()
        def warn():
            if not self.parent().config["backend"] == "prince":
                QtGui.QMessageBox.information(page, "Prince","You can always download PrinceXML manually and set the path in the program settings, or just use another backend.")
            return True

        page.validatePage = warn
        page.setTitle("PySpellbook")
        page.setSubTitle("Please download a copy of PrinceXML")

        label1 = QtGui.QLabel("<p>PySpellbook uses PrinceXML to generate PDF files.</p><p>Unfortunately PrinceXML is not free software, but it is free for personal usage.</p> <p>Installing PrinceXML is not required, but recommended. </p> <p>By downloading you agree to the <a href=\"http://www.princexml.com/license/\">license agreement</a> of PrinceXML (<a href=\"http://www.princexml.com\">www.princexml.com</a>)</p>")
        label1.setOpenExternalLinks(True)
        label1.setWordWrap(True)
        button = QtGui.QPushButton("Download")
        label = QtGui.QLabel("")
        label2 = QtGui.QLabel("Alternatively you can install PrinceXML manually and set the correct path in the configure options.")
        label2.setWordWrap(True)
        button.clicked.connect(downloadPrince(page,label))

        layout = QtGui.QVBoxLayout()
        layout.addWidget(label1)
        layout.addWidget(button)
        layout.addWidget(label)
        layout.addWidget(label2)
        page.setLayout(layout)

        return page

    def createDatasetPage(self):

        page = QtGui.QWizardPage()
        page.setTitle("PySpellbook")
        page.setSubTitle("Select datasets to be downloaded")
        ds_list = QtGui.QListWidget()
        label = QtGui.QLabel("")

        def download_current():
            try:
                current = urllib.request.urlopen("http://christofsteel.github.io/pySpellbook/datasets/current.json")
                current_json = json.loads(current.readall().decode("utf-8"))
                ds_list.clear()
                for item in current_json.keys():
                    qitem = QtGui.QListWidgetItem("%s-%s.json" % (item, current_json[item]))
                    qitem.setCheckState(QtCore.Qt.Unchecked)
                    ds_list.addItem(qitem)

            except urllib.error.URLError:
                label.setText("Error downloading current releases. Please check your network settings.")
                QtGui.QMessageBox.critical(page, "Network Error","An error occured downloading.")

        def finished(content):
            spells = json.loads(str(content))
            #spells = json.loads(str(bytearray(content), encoding = "utf-8"))

            pd = QtGui.QProgressDialog("Importing Database", "Abort", 0, len(spells), self)
            pd.setWindowModality(QtCore.Qt.WindowModal)
            for i, s in enumerate(spells):
                pd.setValue(i)
                pd.setLabelText(s['name'])
                self.parent().db.add_spell_dict(s, False)

                if pd.wasCanceled():
                    break
            self.parent().db.delete_empty()
            self.parent().db.session.commit()
            pd.setValue(len(spells))
            self.parent().reloadModel()

        def download_datasets():
            for row in range(ds_list.model().rowCount()):
                item = ds_list.item(row)
                if item.checkState():
                    #dl = DownloadWithProgress(self, "http://christofsteel.github.io/pySpellbook/datasets/%s" % item.text(), None, finished, None, None, "Downloading %s" % item.text())
                    #dl.download()
                    try:
                        data = urllib.request.urlopen("http://christofsteel.github.io/pySpellbook/datasets/%s" % item.text())
                        finished(data.readall().decode("utf-8"))
                    except urllib.error.URLError:
                        QtGui.QMessageBox.critical(page, "Network Error","An error occured downloading %s." % item.text())
                        return False
            if not self.parent().db.count_spells():
                QtGui.QMessageBox.information(page, "Datasets","You can always download Datasets manually from <a href=\"https://christofsteel.github.io/pySpellbook/\">https://christofstel.github.io/pySpellbook</a> and add them through \"Datasets > Import Dataset\", or add spells manually for your homebrew campaign.")
            return True

        page.validatePage = download_datasets
        page.initializePage = download_current
        button = QtGui.QPushButton("Reload")
        button.clicked.connect(download_current)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(ds_list)
        layout.addWidget(button)
        page.setLayout(layout)

        return page


    def createConclusionPage(self):
        page = QtGui.QWizardPage()
        page.setTitle("Conclusion")

        label = QtGui.QLabel("You have successfully set up PySpellbook. You can always rerun the wizard be selecting \"Run Wizard\" from the file menu.")
        label.setWordWrap(True)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(label)
        page.setLayout(layout)

        return page


    def __init__(self, parent, db):
        super().__init__(parent)
        self.addPage(self.createIntroPage())
        self.addPage(self.createPrincePage())
        self.addPage(self.createDatasetPage())
        self.addPage(self.createConclusionPage())

        self.setWindowTitle("PySpellbook")
