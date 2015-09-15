# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'add_spell.ui'
#
# Created: Wed Aug 19 21:28:54 2015
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class AddSpellWindow(object):
    def addDescriptor(self):
        desc, ok = QtGui.QInputDialog.getText(self.Dialog, "Add Descriptor", "Enter Descriptor")
        if ok:
            self.descriptors_list.addItem(desc)

    def removeDescriptor(self):
        row = self.descriptors_list.currentRow()
        self.descriptors_list.takeItem(row)

    def addClass(self):
        classlevel, ok = QtGui.QInputDialog.getText(self.Dialog, "Add Class", "Enter Class and Level")
        if ok:
            tpl = classlevel.split(' ')
            if len(tpl) == 2 and tpl[1].isdigit:
                self.class_list.addItem(classlevel)

    def removeClass(self):
        row = self.class_list.currentRow()
        self.class_list.takeItem(row)

    def updateRulebooks(self, text):
        if type(text) == int:
            text = self.system_cbox.itemText(text)
        self.rulebook_cbox.clear()
        for rulebook in self.db.list_rulebooks(text):
            self.rulebook_cbox.addItem(rulebook.name)


    def __init__(self, db):
        self.db = db

    def loadSpell(self, spell):
        self.name_edit.setText(spell.name)
        self.system_cbox.setCurrentIndex(self.system_cbox.findText(spell.system_name))
        self.updateRulebooks(spell.system_name)
        self.rulebook_cbox.setCurrentIndex(self.rulebook_cbox.findText(spell.rulebook_name))
        for level in spell.levels:
            self.class_list.addItem("%s %s" % (level.d20class_name, level.level))
        for descriptor in spell.descriptors:
            self.descriptors_list.addItem(descriptor.name)
        self.school_edit.setText(spell.school_name)
        self.subschool_edit.setText(spell.subschool_name)
        if spell.verbal:
            self.V_box.setChecked(spell.verbal)
        if spell.somatic:
            self.S_box.setChecked(spell.somatic)
        if spell.material:
            self.M_box.setChecked(spell.material)
        if spell.divine_focus:
            self.DF_box.setChecked(spell.divine_focus)
        if spell.arcane_focus:
            self.AF_box.setChecked(spell.arcane_focus)
        self.cast_time_edit.setText(spell.cast_time)
        self.spell_range_edit.setText(spell.spell_range)
        self.area_edit.setText(spell.area)
        self.target_edit.setText(spell.target)
        self.effect_edit.setText(spell.effect)
        self.duration_edit.setText(spell.duration)
        self.save_edit.setText(spell.save)
        self.spell_res_edit.setText(spell.spell_res)
        self.text_text.setPlainText(spell.text)

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1080, 666)
        self.Dialog = Dialog
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.widget = QtGui.QWidget(Dialog)
        self.widget.setObjectName("widget")
        self.formLayout_3 = QtGui.QFormLayout(self.widget)
        self.formLayout_3.setContentsMargins(0, 0, 0, 0)
        self.formLayout_3.setObjectName("formLayout_3")
        self.widget_2 = QtGui.QWidget(self.widget)
        self.widget_2.setObjectName("widget_2")
        self.formLayout_2 = QtGui.QFormLayout(self.widget_2)
        self.formLayout_2.setContentsMargins(0, 0, 0, 0)
        self.formLayout_2.setObjectName("formLayout_2")
        self.name_label = QtGui.QLabel(self.widget_2)
        self.name_label.setObjectName("name_label")
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.LabelRole, self.name_label)
        self.name_edit = QtGui.QLineEdit(self.widget_2)
        self.name_edit.setObjectName("name_edit")
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.FieldRole, self.name_edit)
        self.system_label = QtGui.QLabel(self.widget_2)
        self.system_label.setObjectName("system_label")
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.LabelRole, self.system_label)
        self.system_cbox = QtGui.QComboBox(self.widget_2)
        self.system_cbox.setEditable(True)
        self.system_cbox.setObjectName("system_cbox")
        for system in self.db.list_system_names():
            self.system_cbox.addItems(system)
        self.system_cbox.editTextChanged.connect(self.updateRulebooks)
        self.system_cbox.currentIndexChanged.connect(self.updateRulebooks)
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.FieldRole, self.system_cbox)
        self.rulebook_label = QtGui.QLabel(self.widget_2)
        self.rulebook_label.setObjectName("rulebook_label")
        self.formLayout_2.setWidget(2, QtGui.QFormLayout.LabelRole, self.rulebook_label)
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.rulebook_cbox = QtGui.QComboBox(self.widget_2)
        self.rulebook_cbox.setEditable(True)
        self.rulebook_cbox.setObjectName("rulebook_cbox")
        self.horizontalLayout_6.addWidget(self.rulebook_cbox)
        self.page_label = QtGui.QLabel(self.widget_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.page_label.sizePolicy().hasHeightForWidth())
        self.page_label.setSizePolicy(sizePolicy)
        self.page_label.setObjectName("page_label")
        self.horizontalLayout_6.addWidget(self.page_label)
        self.page_spinner = QtGui.QSpinBox(self.widget_2)
        self.page_spinner.maximum = 1000
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.page_spinner.sizePolicy().hasHeightForWidth())
        self.page_spinner.setSizePolicy(sizePolicy)
        self.page_spinner.setObjectName("page_spinner")
        self.horizontalLayout_6.addWidget(self.page_spinner)
        self.formLayout_2.setLayout(2, QtGui.QFormLayout.FieldRole, self.horizontalLayout_6)
        self.d20class_label = QtGui.QLabel(self.widget_2)
        self.d20class_label.setObjectName("d20class_label")
        self.formLayout_2.setWidget(3, QtGui.QFormLayout.LabelRole, self.d20class_label)
        self.verticalLayout_4 = QtGui.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.class_list = QtGui.QListWidget(self.widget_2)
        self.class_list.setViewMode(QtGui.QListView.ListMode)
        self.class_list.setWordWrap(False)
        self.class_list.setObjectName("class_list")
        self.verticalLayout_4.addWidget(self.class_list)
        self.horizontalLayout_7 = QtGui.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.class_add_button = QtGui.QPushButton(self.widget_2)
        self.class_add_button.clicked.connect(self.addClass)
        self.class_add_button.setObjectName("class_add_button")
        self.horizontalLayout_7.addWidget(self.class_add_button)
        self.class_remove_button = QtGui.QPushButton(self.widget_2)
        self.class_remove_button.setObjectName("class_remove_button")
        self.class_remove_button.clicked.connect(self.removeClass)
        self.horizontalLayout_7.addWidget(self.class_remove_button)
        self.verticalLayout_4.addLayout(self.horizontalLayout_7)
        self.formLayout_2.setLayout(3, QtGui.QFormLayout.FieldRole, self.verticalLayout_4)
        self.descriptors_label = QtGui.QLabel(self.widget_2)
        self.descriptors_label.setObjectName("descriptors_label")
        self.formLayout_2.setWidget(4, QtGui.QFormLayout.LabelRole, self.descriptors_label)
        self.horizontalLayout_8 = QtGui.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.descriptors_list = QtGui.QListWidget(self.widget_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.descriptors_list.sizePolicy().hasHeightForWidth())
        self.descriptors_list.setSizePolicy(sizePolicy)
        self.descriptors_list.setMinimumSize(QtCore.QSize(309, 0))
        self.descriptors_list.setFrameShape(QtGui.QFrame.StyledPanel)
        self.descriptors_list.setMovement(QtGui.QListView.Static)
        self.descriptors_list.setProperty("isWrapping", False)
        self.descriptors_list.setViewMode(QtGui.QListView.IconMode)
        self.descriptors_list.setUniformItemSizes(True)
        self.descriptors_list.setObjectName("descriptors_list")
        self.horizontalLayout_8.addWidget(self.descriptors_list)
        self.descriptors_add_button = QtGui.QPushButton(self.widget_2)
        self.descriptors_add_button.setObjectName("descriptors_add_button")
        self.descriptors_add_button.clicked.connect(self.addDescriptor)
        self.horizontalLayout_8.addWidget(self.descriptors_add_button)
        self.descriptors_remove_button = QtGui.QPushButton(self.widget_2)
        self.descriptors_remove_button.setObjectName("descriptors_remove_button")
        self.descriptors_remove_button.clicked.connect(self.removeDescriptor)
        self.horizontalLayout_8.addWidget(self.descriptors_remove_button)
        self.formLayout_2.setLayout(4, QtGui.QFormLayout.FieldRole, self.horizontalLayout_8)
        self.school_label = QtGui.QLabel(self.widget_2)
        self.school_label.setObjectName("school_label")
        self.formLayout_2.setWidget(5, QtGui.QFormLayout.LabelRole, self.school_label)
        self.school_edit = QtGui.QLineEdit(self.widget_2)
        self.school_edit.setObjectName("school_edit")
        self.formLayout_2.setWidget(5, QtGui.QFormLayout.FieldRole, self.school_edit)
        self.subschool_label = QtGui.QLabel(self.widget_2)
        self.subschool_label.setObjectName("subschool_label")
        self.formLayout_2.setWidget(6, QtGui.QFormLayout.LabelRole, self.subschool_label)
        self.subschool_edit = QtGui.QLineEdit(self.widget_2)
        self.subschool_edit.setObjectName("subschool_edit")
        self.formLayout_2.setWidget(6, QtGui.QFormLayout.FieldRole, self.subschool_edit)
        self.components_label = QtGui.QLabel(self.widget_2)
        self.components_label.setObjectName("components_label")
        self.formLayout_2.setWidget(7, QtGui.QFormLayout.LabelRole, self.components_label)
        self.horizontalLayout_9 = QtGui.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.V_box = QtGui.QCheckBox(self.widget_2)
        self.V_box.setObjectName("V_box")
        self.horizontalLayout_9.addWidget(self.V_box)
        self.S_box = QtGui.QCheckBox(self.widget_2)
        self.S_box.setObjectName("S_box")
        self.horizontalLayout_9.addWidget(self.S_box)
        self.M_box = QtGui.QCheckBox(self.widget_2)
        self.M_box.setObjectName("M_box")
        self.horizontalLayout_9.addWidget(self.M_box)
        self.AF_box = QtGui.QCheckBox(self.widget_2)
        self.AF_box.setObjectName("AF_box")
        self.horizontalLayout_9.addWidget(self.AF_box)
        self.DF_box = QtGui.QCheckBox(self.widget_2)
        self.DF_box.setObjectName("DF_box")
        self.horizontalLayout_9.addWidget(self.DF_box)
        self.XP_box = QtGui.QCheckBox(self.widget_2)
        self.XP_box.setObjectName("XP_box")
        self.horizontalLayout_9.addWidget(self.XP_box)
        self.formLayout_2.setLayout(7, QtGui.QFormLayout.FieldRole, self.horizontalLayout_9)
        self.cast_time_label = QtGui.QLabel(self.widget_2)
        self.cast_time_label.setObjectName("cast_time_label")
        self.formLayout_2.setWidget(8, QtGui.QFormLayout.LabelRole, self.cast_time_label)
        self.cast_time_edit = QtGui.QLineEdit(self.widget_2)
        self.cast_time_edit.setObjectName("cast_time_edit")
        self.formLayout_2.setWidget(8, QtGui.QFormLayout.FieldRole, self.cast_time_edit)
        self.spell_range_label = QtGui.QLabel(self.widget_2)
        self.spell_range_label.setObjectName("spell_range_label")
        self.formLayout_2.setWidget(9, QtGui.QFormLayout.LabelRole, self.spell_range_label)
        self.spell_range_edit = QtGui.QLineEdit(self.widget_2)
        self.spell_range_edit.setObjectName("spell_range_edit")
        self.formLayout_2.setWidget(9, QtGui.QFormLayout.FieldRole, self.spell_range_edit)
        self.area_label = QtGui.QLabel(self.widget_2)
        self.area_label.setObjectName("area_label")
        self.formLayout_2.setWidget(10, QtGui.QFormLayout.LabelRole, self.area_label)
        self.area_edit = QtGui.QLineEdit(self.widget_2)
        self.area_edit.setObjectName("area_edit")
        self.formLayout_2.setWidget(10, QtGui.QFormLayout.FieldRole, self.area_edit)
        self.target_label = QtGui.QLabel(self.widget_2)
        self.target_label.setObjectName("target_label")
        self.formLayout_2.setWidget(11, QtGui.QFormLayout.LabelRole, self.target_label)
        self.target_edit = QtGui.QLineEdit(self.widget_2)
        self.target_edit.setObjectName("target_edit")
        self.formLayout_2.setWidget(11, QtGui.QFormLayout.FieldRole, self.target_edit)
        self.effect_label = QtGui.QLabel(self.widget_2)
        self.effect_label.setObjectName("effect_label")
        self.formLayout_2.setWidget(12, QtGui.QFormLayout.LabelRole, self.effect_label)
        self.effect_edit = QtGui.QLineEdit(self.widget_2)
        self.effect_edit.setObjectName("effect_edit")
        self.formLayout_2.setWidget(12, QtGui.QFormLayout.FieldRole, self.effect_edit)
        self.duration_label = QtGui.QLabel(self.widget_2)
        self.duration_label.setObjectName("duration_label")
        self.formLayout_2.setWidget(13, QtGui.QFormLayout.LabelRole, self.duration_label)
        self.duration_edit = QtGui.QLineEdit(self.widget_2)
        self.duration_edit.setObjectName("duration_edit")
        self.formLayout_2.setWidget(13, QtGui.QFormLayout.FieldRole, self.duration_edit)
        self.save_label = QtGui.QLabel(self.widget_2)
        self.save_label.setObjectName("save_label")
        self.formLayout_2.setWidget(14, QtGui.QFormLayout.LabelRole, self.save_label)
        self.spell_res_label = QtGui.QLabel(self.widget_2)
        self.spell_res_label.setObjectName("spell_res_label")
        self.formLayout_2.setWidget(15, QtGui.QFormLayout.LabelRole, self.spell_res_label)
        self.save_edit = QtGui.QLineEdit(self.widget_2)
        self.save_edit.setObjectName("save_edit")
        self.formLayout_2.setWidget(14, QtGui.QFormLayout.FieldRole, self.save_edit)
        self.spell_res_edit = QtGui.QLineEdit(self.widget_2)
        self.spell_res_edit.setObjectName("spell_res_edit")
        self.formLayout_2.setWidget(15, QtGui.QFormLayout.FieldRole, self.spell_res_edit)
        self.formLayout_3.setWidget(0, QtGui.QFormLayout.LabelRole, self.widget_2)
        self.verticalLayout_5 = QtGui.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.text_label = QtGui.QLabel(self.widget)
        self.text_label.setObjectName("text_label")
        self.verticalLayout_5.addWidget(self.text_label)
        self.text_text = QtGui.QTextEdit(self.widget)
        self.text_text.setObjectName("text_text")
        self.verticalLayout_5.addWidget(self.text_text)
        self.formLayout_3.setLayout(0, QtGui.QFormLayout.FieldRole, self.verticalLayout_5)
        self.verticalLayout.addWidget(self.widget)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.name_label.setBuddy(self.name_edit)
        self.system_label.setBuddy(self.system_cbox)
        self.rulebook_label.setBuddy(self.rulebook_cbox)
        self.page_label.setBuddy(self.page_spinner)
        self.d20class_label.setBuddy(self.class_list)
        self.descriptors_label.setBuddy(self.descriptors_list)
        self.school_label.setBuddy(self.school_edit)
        self.subschool_label.setBuddy(self.subschool_edit)
        self.cast_time_label.setBuddy(self.cast_time_edit)
        self.spell_range_label.setBuddy(self.spell_range_edit)
        self.area_label.setBuddy(self.area_edit)
        self.target_label.setBuddy(self.target_edit)
        self.effect_label.setBuddy(self.effect_edit)
        self.duration_label.setBuddy(self.duration_edit)
        self.save_label.setBuddy(self.save_edit)
        self.spell_res_label.setBuddy(self.spell_res_edit)
        self.text_label.setBuddy(self.text_text)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def generate_spell_dict(self):
        spell = {}
        spell['name'] = self.name_edit.text()
        spell['system'] = self.system_cbox.currentText()
        spell['rulebook'] = self.rulebook_cbox.currentText()
        spell['classes'] = []
        for index in range(self.class_list.count()):
            tpl = self.class_list.item(index).text().split()
            spell['classes'].append(tpl)
        spell['descriptors'] = []
        for index in range(self.descriptors_list.count()):
            spell['descriptors'].append(self.descriptors_list.item(index).text())
        spell['school'] = self.school_edit.text()
        spell['subschool'] = self.subschool_edit.text()
        spell['verbal'] = self.V_box.isChecked()
        spell['somatic'] = self.S_box.isChecked()
        spell['material'] = self.M_box.isChecked()
        spell['AF'] = self.AF_box.isChecked()
        spell['DF'] = self.DF_box.isChecked()
        spell['XP'] = self.XP_box.isChecked()
        spell['cast_time'] = self.cast_time_edit.text()
        spell['spell_range'] = self.spell_range_edit.text()
        spell['area'] = self.area_edit.text()
        spell['target'] = self.target_edit.text()
        spell['effect'] = self.effect_edit.text()
        spell['duration'] = self.duration_edit.text()
        spell['saving_throw'] = self.save_edit.text()
        spell['spell_resistance'] = self.spell_res_edit.text()
        spell['text'] = self.text_text.toPlainText()
        return spell

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Add Spell", None, QtGui.QApplication.UnicodeUTF8))
        self.name_label.setText(QtGui.QApplication.translate("Dialog", "Name", None, QtGui.QApplication.UnicodeUTF8))
        self.system_label.setText(QtGui.QApplication.translate("Dialog", "System", None, QtGui.QApplication.UnicodeUTF8))
        self.rulebook_label.setText(QtGui.QApplication.translate("Dialog", "Rulebook", None, QtGui.QApplication.UnicodeUTF8))
        self.page_label.setText(QtGui.QApplication.translate("Dialog", "Page", None, QtGui.QApplication.UnicodeUTF8))
        self.d20class_label.setText(QtGui.QApplication.translate("Dialog", "Classes", None, QtGui.QApplication.UnicodeUTF8))
        self.class_add_button.setText(QtGui.QApplication.translate("Dialog", "Add", None, QtGui.QApplication.UnicodeUTF8))
        self.class_remove_button.setText(QtGui.QApplication.translate("Dialog", "Remove", None, QtGui.QApplication.UnicodeUTF8))
        self.descriptors_label.setText(QtGui.QApplication.translate("Dialog", "Descriptors", None, QtGui.QApplication.UnicodeUTF8))
        self.descriptors_add_button.setText(QtGui.QApplication.translate("Dialog", "Add", None, QtGui.QApplication.UnicodeUTF8))
        self.descriptors_remove_button.setText(QtGui.QApplication.translate("Dialog", "Remove", None, QtGui.QApplication.UnicodeUTF8))
        self.school_label.setText(QtGui.QApplication.translate("Dialog", "School", None, QtGui.QApplication.UnicodeUTF8))
        self.subschool_label.setText(QtGui.QApplication.translate("Dialog", "Subschool", None, QtGui.QApplication.UnicodeUTF8))
        self.components_label.setText(QtGui.QApplication.translate("Dialog", "Components", None, QtGui.QApplication.UnicodeUTF8))
        self.V_box.setText(QtGui.QApplication.translate("Dialog", "V", None, QtGui.QApplication.UnicodeUTF8))
        self.S_box.setText(QtGui.QApplication.translate("Dialog", "S", None, QtGui.QApplication.UnicodeUTF8))
        self.M_box.setText(QtGui.QApplication.translate("Dialog", "M", None, QtGui.QApplication.UnicodeUTF8))
        self.AF_box.setText(QtGui.QApplication.translate("Dialog", "AF", None, QtGui.QApplication.UnicodeUTF8))
        self.DF_box.setText(QtGui.QApplication.translate("Dialog", "DF", None, QtGui.QApplication.UnicodeUTF8))
        self.XP_box.setText(QtGui.QApplication.translate("Dialog", "XP", None, QtGui.QApplication.UnicodeUTF8))
        self.cast_time_label.setText(QtGui.QApplication.translate("Dialog", "Cast Time", None, QtGui.QApplication.UnicodeUTF8))
        self.spell_range_label.setText(QtGui.QApplication.translate("Dialog", "Spell Range", None, QtGui.QApplication.UnicodeUTF8))
        self.area_label.setText(QtGui.QApplication.translate("Dialog", "Area", None, QtGui.QApplication.UnicodeUTF8))
        self.target_label.setText(QtGui.QApplication.translate("Dialog", "Target", None, QtGui.QApplication.UnicodeUTF8))
        self.effect_label.setText(QtGui.QApplication.translate("Dialog", "Effect", None, QtGui.QApplication.UnicodeUTF8))
        self.duration_label.setText(QtGui.QApplication.translate("Dialog", "Duration", None, QtGui.QApplication.UnicodeUTF8))
        self.save_label.setText(QtGui.QApplication.translate("Dialog", "Saving Throw", None, QtGui.QApplication.UnicodeUTF8))
        self.spell_res_label.setText(QtGui.QApplication.translate("Dialog", "Spell Resistance", None, QtGui.QApplication.UnicodeUTF8))
        self.text_label.setText(QtGui.QApplication.translate("Dialog", "Full Text", None, QtGui.QApplication.UnicodeUTF8))


