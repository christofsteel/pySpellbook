# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'config.ui'
#
# Created: Thu Sep  3 17:57:32 2015
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class ConfigDialog(object):
    def getConfig(self):
        config = {'custom': self.custom_edit.text(),
                 'prince_path': self.prince_path_edit.text()}
        if self.intern_radio.isChecked():
            config['backend'] = 'internal'
        elif self.html_radio.isChecked():
            config['backend'] = 'HTML'
        elif self.prince_radio.isChecked():
            config['backend'] = 'prince'
        elif self.custom_radio.isChecked():
            config['backend'] = 'custom'
        return config
    def loadConfig(self, config):
        if 'custom' in config.keys():
            self.custom_edit.setText(config['custom'])
        else:
            self.custom_edit.setText("html2pdf $INPUT $OUTPUT")
        if 'prince_path' in config.keys():
            self.prince_path_edit.setText(config['prince_path'])
        if 'backend' in config.keys():
            if config['backend'] == "internal":
                self.intern_radio.setChecked(True)
            elif config['backend'] == "HTML":
                self.html_radio.setChecked(True)
            elif config['backend'] == "prince":
                self.prince_radio.setChecked(True)
            elif config['backend'] == "custom":
                self.custom_radio.setChecked(True)
            else:
                self.intern_radio.setChecked(True)


    def set_path(self):
        filename, filters = QtGui.QFileDialog.getOpenFileName()
        if filename:
            self.prince_path_edit.setText(filename)

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(439, 256)
        Dialog.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.widget = QtGui.QWidget(Dialog)
        self.widget.setObjectName("widget")
        self.widget.setLayout(QtGui.QVBoxLayout())
        self.intern_radio = QtGui.QRadioButton(self.widget)
        self.intern_radio.setObjectName("intern_radio")
        self.widget.layout().addWidget(self.intern_radio)
        self.html_radio = QtGui.QRadioButton(self.widget)
        self.html_radio.setObjectName("html_radio")
        self.widget.layout().addWidget(self.html_radio)
        self.prince_radio = QtGui.QRadioButton(self.widget)
        self.prince_radio.setObjectName("prince_radio")
        self.widget.layout().addWidget(self.prince_radio)
        self.path_label = QtGui.QLabel(self.widget)
        self.path_label.setObjectName("path_label")
        self.widget.layout().addWidget(self.path_label)
        self.pathwidget = QtGui.QWidget(self.widget)
        self.pathwidget.setLayout(QtGui.QHBoxLayout())
        self.prince_path_edit = QtGui.QLineEdit(self.widget)
        self.prince_path_edit.setObjectName("prince_path_edit")
        self.prince_path_button = QtGui.QPushButton(self.widget)
        self.prince_path_button.setObjectName("prince_path_button")
        self.prince_path_button.pressed.connect(self.set_path)
        self.pathwidget.layout().addWidget(self.prince_path_edit)
        self.pathwidget.layout().addWidget(self.prince_path_button)
        self.widget.layout().addWidget(self.pathwidget)
        self.custom_radio = QtGui.QRadioButton(self.widget)
        self.custom_radio.setObjectName("custom_radio")
        self.widget.layout().addWidget(self.custom_radio)
        self.custom_edit = QtGui.QLineEdit(self.widget)
        self.custom_edit.setObjectName("custom_edit")
        self.widget.layout().addWidget(self.custom_edit)
        self.verticalLayout.addWidget(self.widget)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.path_label.setBuddy(self.prince_path_edit)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Configure Export", None, QtGui.QApplication.UnicodeUTF8))
        self.intern_radio.setText(QtGui.QApplication.translate("Dialog", "Internal PDF Renderer", None, QtGui.QApplication.UnicodeUTF8))
        self.html_radio.setText(QtGui.QApplication.translate("Dialog", "HTML output", None, QtGui.QApplication.UnicodeUTF8))
        self.prince_radio.setText(QtGui.QApplication.translate("Dialog", "Prince PDF Render", None, QtGui.QApplication.UnicodeUTF8))
        self.path_label.setText(QtGui.QApplication.translate("Dialog", "Path to prince executable:", None, QtGui.QApplication.UnicodeUTF8))
        self.prince_path_edit.setText(QtGui.QApplication.translate("Dialog", "/usr/bin/prince", None, QtGui.QApplication.UnicodeUTF8))
        self.prince_path_button.setText(QtGui.QApplication.translate("Dialog", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.custom_radio.setText(QtGui.QApplication.translate("Dialog", "Custom Command:", None, QtGui.QApplication.UnicodeUTF8))
        self.custom_edit.setText(QtGui.QApplication.translate("Dialog", "html2pdf %s -o %s", None, QtGui.QApplication.UnicodeUTF8))


