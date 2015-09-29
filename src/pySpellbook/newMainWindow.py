from PySide import QtGui, QtCore
from jinja2 import Template

import os
import json
import sys
import urllib.request
import subprocess
from distutils.version import LooseVersion

import pySpellbook.bw_icons_rc as icons
from pySpellbook.qmodel import SpellModel, FilterModel
from pySpellbook.template import LatexGenerator, HTMLGenerator
from pySpellbook.addSpellWindow import AddSpellWindow
from pySpellbook.config_window import ConfigDialog
from pySpellbook.firstRunWizard import Wizard

class UpdateNotifier(QtCore.QThread):
    updateAvailable = QtCore.Signal()
    def __init__(self, version):
        super().__init__()
        self.version = version

    def run(self):
        try:
            blatest = urllib.request.urlopen("https://christofsteel.github.io/pySpellbook/latest")
            slatest = blatest.read().decode('utf-8').strip()
            latest_version = LooseVersion(slatest)
            current_version = LooseVersion(self.version)
            if (latest_version > current_version):
                print("Update available %s. Current version in %s." % (latest_version, current_version))
                self.updateAvailable.emit()
        except urllib.error.URLError:
            print("Error loading url")



class SpellBookHandler:
    def getSelection(window):
        model = window.model
        spellbook = {}
        spellbook['spells'] = {}
        s = model.getCheckedSpells()
        for d20class, levels in s.items():
            spellbook['spells'][d20class] = {}
            for level, spells in levels.items():
                spellbook['spells'][d20class][level] = []
                for spell in spells:
                    spellbook['spells'][d20class][level].append((spell.rulebook_name, spell.system_name, spell.name))
        spellbook['author'] = window.spellBookAuthor
        spellbook['title'] = window.spellBookName
        return spellbook

    def save(filename, window):
        with open(filename, 'w') as fp:
            spellbook = SpellBookHandler.getSelection(window)
            json.dump(spellbook, fp)

    def load(spellbook, window, model=None):
        #print("Loading %s" % spellbook)
        if not model:
            model = window.model
        model.clearChecked()
        model.setCheckedSpells(spellbook['spells'])
        window.spellBookAuthor = spellbook['author']
        window.spellBookName = spellbook['title']

    def open(filename, window):
        with open(filename, 'r') as fp:
            spellbook = json.load(fp)
            SpellBookHandler.load(spellbook, window)


class SpellBookWindow(QtGui.QMainWindow):
    def updateRecents(self):
        if self.config["recents"] == []:
            self.config["recents"] = [self.filename]
            return
        if self.filename != self.config["recents"][0]:
            if self.filename in self.config["recents"]:
                self.config["recents"].remove(self.filename)
            else:
                self.config["recents"] = self.config["recents"][:4]
            self.config["recents"].insert(0, self.filename)
        self.updateRecentsActions()

    def updateRecentsActions(self):
        self.openRecentsMenu.clear()
        for recent in self.config["recents"]:
            action = self.openRecentsMenu.addAction(recent)
            action.triggered.connect(self.openRecent(recent))

    def openRecent(self, recent):
        def inner():
            if self.isModified():
                msgBox = QtGui.QMessageBox()
                msgBox.setText(self.tr("The spellbook has been modified."))
                msgBox.setInformativeText(self.tr("Do you want to save your changes?"))
                msgBox.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel)
                msgBox.setDefaultButton(QtGui.QMessageBox.Yes)
                ret = msgBox.exec_()
                if ret == QtGui.QMessageBox.No:
                    SpellBookHandler.open(recent, self)
                    self.filename = recent
                    self.modified = False
                    self.updateRecents()
                    with open(self.configfile,'w') as f:
                        json.dump(self.config, f, indent=2)
                    self.updateWindowName()
                elif ret == QtGui.QMessageBox.Yes:
                    self.saveBook()
            else:
                SpellBookHandler.open(recent, self)
                self.modified = False
                self.filename = recent
                self.updateRecents()
                with open(self.configfile,'w') as f:
                    json.dump(self.config, f, indent=2)
                self.updateWindowName()
        return inner


    def showSpell(self, index):
        template = """
        <h1>{{ spell.name }}</h1>
        <p>
        <emph>{{ spell.rulebook }} ({{ spell.system_name }})</emph>
        </p>
            School: {{ spell.school }} {% if spell.subschool %} ({{ spell.subschool }}) {% endif %}
            {%- if spell.descriptors -%}
            {%- for d in spell.descriptors -%}
            {% if loop.first -%}
            [
            {%- endif -%}
            {{d.name}}
            {%- if loop.last -%}
            ]
            {%- else -%}
            ,&nbsp;
            {%- endif -%}
            {%- endfor%}
            {% endif %}
				<table>
					{% if spell.verbal or spell.material or spell.somatic or spell.arcane_focus or spell.divine_focus or spell.xp_costs %}
					<tr>
						<td class="label">Components</td>
						<td class="value">
							{% if spell.verbal %} V {% endif %}
							{% if spell.somatic %} S {% endif %}
							{% if spell.material %} M {% endif %}
							{% if spell.arcane_focus %} AF {% endif %}
							{% if spell.divine_focus %} DF {% endif %}
							{% if spell.xp_costs %} XP {% endif %}
						</td>
					</tr>
					{% endif %}
					{% if spell.cast_time %}
					<tr>
						<td class="label">Casting&nbsp;time</td>
						<td class="value">{{ spell.cast_time }}</td>
					</tr>
					{% endif %}
					{% if spell.spell_range %}
					<tr>
						<td class="label">Range</td>
						<td class="value">{{ spell.spell_range }}</td>
					</tr>
					{% endif %}
					{% if spell.area %}
					<tr>
						<td class="label">Area</td>
						<td class="value">{{ spell.area }}</td>
					</tr>
					{% endif %}
					{% if spell.target %}
					<tr>
						<td class="label">Target</td>
						<td class="value">{{ spell.target }}</td>
					</tr>
					{% endif %}
					{% if spell.effect %}
					<tr>
						<td class="label">Effect</td>
						<td class="value">{{ spell.effect }}</td>
					</tr>
					{% endif %}
					{% if spell.duration %}
					<tr>
						<td class="label">Duration</td>
						<td class="value">{{ spell.duration }}</td>
					</tr>
					{% endif %}
					{% if spell.save %}
					<tr>
						<td class="label">Saving&nbsp;throw</td>
						<td class="value">{{ spell.save }}</td>
					</tr>
					{% endif %}
					{% if spell.spell_res %}
					<tr>
						<td class="label">Spell&nbsp;resistance</td>
						<td class="value">{{ spell.spell_res }}</td>
					</tr>
					{% endif %}
				</table>
            {{ spell.text }}
            """
        item = self.model.data(self.filtermodel.mapToSource(index), QtCore.Qt.UserRole)
        ttemplate = Template(template)
        self.spelldetails.setText(ttemplate.render(spell=item.spell))

    def showLevels(self, index):
        self.spelldetails.setText("")
        self.spelllist.setHidden(True)
        self.levellist.setRootIndex(index)
        self.levellist.setHidden(False)


    def showSpells(self, index):
        self.spelldetails.setText("")
        self.spelllist.setRootIndex(index)
        self.spellselections = self.spelllist.selectionModel()
        self.spellselections.currentChanged.connect(self.showSpell)
        self.spelllist.setHidden(False)


    def __init__(self, db, configfile, version):
        super().__init__()
        # This will deactivate the unused warning in vim
        if icons:
            pass
        self.setUnifiedTitleAndToolBarOnMac(True)
        self.version = version
        self.db = db
        self.configfile = configfile
        self.config = {}
        self.config['backend'] = 'internal'
        self.config['custom'] = 'html2pdf $INPUT $OUTPUT'
        self.config['prince_path'] = '/usr/bin/prince'
        self.config['filters'] = { 'selected_only': False,
                                   'descriptors': [],
                                   'schools': [],
                                   'subschools': [],
                                   'rulebooks': []
                                 }
        self.config['recents'] = []
        self.firstRun = True
        if os.path.exists(self.configfile):
            with open(self.configfile) as f:
                self.config.update(json.load(f))
                self.firstRun = False
        else:
            with open(self.configfile,'w') as f:
                json.dump(self.config, f, indent=2)

        # Setting up the window
        self.setWindowTitle("PySpellbook")
        self.setWindowIcon(QtGui.QIcon(":icons/pySpellbook.png"))
        self.cw = QtGui.QWidget()
        self.setCentralWidget(self.cw)
        self.cw.setLayout(QtGui.QVBoxLayout())
        self.cw.layout().setContentsMargins(0,0,0,0)
        self.spellArea = QtGui.QWidget(self.cw)
        self.cw.layout().addWidget(self.spellArea)
        self.spellArea.setLayout(QtGui.QHBoxLayout())
        self.spellArea.layout().setContentsMargins(0,0,0,0)
        self.spellAreaSplitter = QtGui.QSplitter(self.spellArea)
        self.spellAreaSplitter.setHandleWidth(2)
        self.d20classArea = QtGui.QWidget(self.spellArea)
        self.d20classArea.setLayout(QtGui.QVBoxLayout())
        self.d20classArea.layout().setContentsMargins(0,0,0,0)
        self.d20classArea.layout().setSpacing(0)
        #self.d20filterEdit = QtGui.QLineEdit()
        #self.d20filterEdit.setPlaceholderText("Filter classes")
        #self.d20classArea.layout().addWidget(self.d20filterEdit)
        self.d20classlist = QtGui.QListView(self.spellArea)
        self.d20classArea.layout().addWidget(self.d20classlist)
        self.d20classlist.setAlternatingRowColors(True)
        self.d20classlist.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.levellist = QtGui.QListView(self.spellArea)
        self.levellist.setAlternatingRowColors(True)
        self.levellist.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.spelllist = QtGui.QListView(self.spellArea)
        self.spelllist.setAlternatingRowColors(True)
        self.spelllist.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.spelldetails = QtGui.QTextEdit()
        self.spelldetails.setReadOnly(True)
        self.spellArea.layout().addWidget(self.spellAreaSplitter)
        self.spellAreaSplitter.addWidget(self.d20classArea)
        self.spellAreaSplitter.addWidget(self.levellist)
        self.spellAreaSplitter.addWidget(self.spelllist)
        self.spellAreaSplitter.addWidget(self.spelldetails)
        self.spellAreaSplitter.setStretchFactor(0,0)
        self.spellAreaSplitter.setStretchFactor(1,0)
        self.spellAreaSplitter.setStretchFactor(2,0)
        self.spellAreaSplitter.setStretchFactor(3,1)

        #self.d20filterEdit.textChanged.connect(self.filterClasses)
        self.d20classlist.clicked.connect(self.showLevels)
        self.levellist.clicked.connect(self.showSpells)

        # Setting up menus
        self.menuBar = QtGui.QMenuBar(self) if sys.platform != "darwin" else QtGui.QMenuBar()
        self.setMenuBar(self.menuBar)
        self.filterSpellsEdit = QtGui.QLineEdit()
        self.filterSpellsEdit.setPlaceholderText(self.tr("Search..."))
        self.fileMenu = self.menuBar.addMenu(self.tr("&File"))
        self.spellBookMenu = self.menuBar.addMenu(self.tr("Spell&book"))
        self.dbMenu = self.menuBar.addMenu(self.tr("&Database"))
        self.filterMenu = self.menuBar.addMenu(self.tr("F&ilter"))
        self.filterSystemMenu = self.filterMenu.addMenu(self.tr("&Rulebooks"))
        self.filterSchoolMenu = self.filterMenu.addMenu(self.tr("&School"))
        self.filterSubschoolMenu = self.filterMenu.addMenu(self.tr("Su&bschool"))
        self.filterDescriptorMenu = self.filterMenu.addMenu(self.tr("&Descriptor"))
        self.filterSelectedAction = self.filterMenu.addAction(self.tr("Show &only selected"))
        self.filterSelectedAction.setCheckable(True)
        self.newAction = QtGui.QAction(self.tr("&New"), self)
        self.newAction.setIcon(QtGui.QIcon.fromTheme("document-new", QtGui.QIcon(":icons/document-new.png")))
        self.newAction.setShortcut(QtCore.Qt.CTRL + QtCore.Qt.Key_N)
        self.fileMenu.addAction(self.newAction)
        self.openAction = QtGui.QAction(self)
        self.openAction.setText(self.tr("&Open..."))
        self.openAction.setIcon(QtGui.QIcon.fromTheme("document-open", QtGui.QIcon(":icons/document-open.png")))
        self.openAction.setShortcut(QtCore.Qt.CTRL + QtCore.Qt.Key_O)
        self.fileMenu.addAction(self.openAction)
        self.openRecentsMenu = self.fileMenu.addMenu(self.tr("Open &Recents..."))
        self.fileMenu.addSeparator()
        self.saveAction = QtGui.QAction(self)
        self.saveAction.setText(self.tr("&Save..."))
        self.saveAction.setIcon(QtGui.QIcon.fromTheme("document-save", QtGui.QIcon(":icons/document-save.png")))
        self.saveAction.setShortcut(QtCore.Qt.CTRL + QtCore.Qt.Key_S)
        self.fileMenu.addAction(self.saveAction)
        self.saveasAction = QtGui.QAction(self)
        self.saveasAction.setIcon(QtGui.QIcon.fromTheme("document-save-as", QtGui.QIcon(":icons/document-save-as.png")))
        self.saveasAction.setText(self.tr("&Save As..."))
        self.fileMenu.addAction(self.saveasAction)
        self.fileMenu.addSeparator()
        self.rerunWizardAction = self.fileMenu.addAction(self.tr("Run Wizard"))
        self.fileMenu.addSeparator()
        self.quitAction = QtGui.QAction(self)
        self.quitAction.setIcon(QtGui.QIcon.fromTheme("application-exit", QtGui.QIcon(":icons/application-exit.png")))
        self.quitAction.setText(self.tr("&Quit"))
        self.quitAction.setShortcut(QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.fileMenu.addAction(self.quitAction)

        self.setNameAction = QtGui.QAction(self.tr("Set &title..."), self)
        self.spellBookMenu.addAction(self.setNameAction)
        self.setAuthorAction = QtGui.QAction(self.tr("Set &author..."), self)
        self.spellBookMenu.addAction(self.setAuthorAction)
        #self.selectImageAction = QtGui.QAction("Select &Image...", self)
        #self.spellBookMenu.addAction(self.selectImageAction)
        self.spellBookMenu.addSeparator()
        #self.selectTemplateAction = QtGui.QAction("Select &Template...", self)
        #self.spellBookMenu.addAction(self.selectTemplateAction)
        self.configExportAction = self.spellBookMenu.addAction(self.tr("&Configure export..."))
        self.configExportAction.setIcon(QtGui.QIcon.fromTheme("preferences-system", QtGui.QIcon(":icons/preferences-system.png")))
        self.spellBookMenu.addSeparator()
        self.exportBookAction = QtGui.QAction(self.tr("&Export to PDF..."), self)
        self.exportBookAction.setIcon(QtGui.QIcon.fromTheme("office-book", QtGui.QIcon(":icons/office-book.png")))
        self.exportBookAction.setShortcut(QtCore.Qt.CTRL + QtCore.Qt.Key_E)
        self.spellBookMenu.addAction(self.exportBookAction)
        self.exportAsBookAction = QtGui.QAction(self.tr("Export to PDF &as..."), self)
        self.spellBookMenu.addAction(self.exportAsBookAction)

        self.addSpellAction = QtGui.QAction(self.tr("&Add spell..."), self)
        self.addSpellAction.setIcon(QtGui.QIcon.fromTheme("list-add", QtGui.QIcon(":icons/list-add.png")))
        self.dbMenu.addAction(self.addSpellAction)
        self.dbMenu.addSeparator()
        self.importDBAction = QtGui.QAction(self.tr("&Import dataset..."), self)
        self.dbMenu.addAction(self.importDBAction)
        self.exportDBAction = self.dbMenu.addAction(self.tr("&Export dataset..."))
        self.exportSelectedDBAction = self.dbMenu.addAction(self.tr("Export &selected dataset.."))
        self.dbMenu.addSeparator()
        self.clearDBAction = self.dbMenu.addAction(self.tr("Clear database"))

        self.selectAllLevelAction = QtGui.QAction(self.tr("Select All"), self)
        self.selectAllClassAction = QtGui.QAction(self.tr("Select All"), self)
        self.deselectAllLevelAction = QtGui.QAction(self.tr("Deselect All"), self)
        self.deselectAllClassAction = QtGui.QAction(self.tr("Deselect All"), self)
        self.editSpellAction = QtGui.QAction(self.tr("Edit..."), self)
        self.deleteSpellAction = QtGui.QAction(self.tr("Delete"), self)
        self.spelllist.addAction(self.editSpellAction)
        self.spelllist.addAction(self.deleteSpellAction)
        self.levellist.addAction(self.selectAllLevelAction)
        self.levellist.addAction(self.deselectAllLevelAction)
        self.d20classlist.addAction(self.selectAllClassAction)
        self.d20classlist.addAction(self.deselectAllClassAction)

        self.editSpellAction.triggered.connect(self.showEditSpell)
        self.deleteSpellAction.triggered.connect(self.deleteSpell)
        self.selectAllClassAction.triggered.connect(self.selectAllClass)
        self.deselectAllClassAction.triggered.connect(self.deselectAllClass)
        self.selectAllLevelAction.triggered.connect(self.selectAllLevel)
        self.deselectAllLevelAction.triggered.connect(self.deselectAllLevel)

        self.filterSpellsEdit.textChanged.connect(self.search)

        self.newAction.triggered.connect(self.new)
        self.openAction.triggered.connect(self.openBook)
        self.saveAction.triggered.connect(self.saveBook)
        self.saveasAction.triggered.connect(self.saveAsBook)
        self.rerunWizardAction.triggered.connect(self.rerunWizard)
        self.quitAction.triggered.connect(self.close)
        self.setAuthorAction.triggered.connect(self.setAuthor)
        self.setNameAction.triggered.connect(self.setName)
        self.exportBookAction.triggered.connect(self.exportBook)
        self.exportAsBookAction.triggered.connect(self.exportAsBook)
        self.addSpellAction.triggered.connect(self.showAddSpell)
        self.importDBAction.triggered.connect(self.importDB)
        self.exportDBAction.triggered.connect(self.exportDB)
        self.exportSelectedDBAction.triggered.connect(self.exportSelectedDB)
        self.clearDBAction.triggered.connect(self.clearDB)
        self.configExportAction.triggered.connect(self.showConfig)

        self.filterSelectedAction.toggled.connect(self.filterSelected)

        # Tooolbar
        self.toolbar = self.addToolBar(self.tr("Toolbar"))
        self.toolbar.setFloatable(False)
        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.toolbar.addAction(self.newAction)
        self.toolbar.addAction(self.openAction)
        self.toolbar.addAction(self.saveAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.exportBookAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.addSpellAction)
        self.emptyWidget = QtGui.QWidget()
        self.emptyWidget.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        self.updateNotify = QtGui.QLabel("")
        self.updateThread = UpdateNotifier(self.version)
        self.updateThread.updateAvailable.connect(self.setUpdate)
        self.updateThread.start()
        self.updateNotify.setOpenExternalLinks(True)
        self.toolbar.addWidget(self.emptyWidget)
        self.toolbar.addWidget(self.updateNotify)
        self.toolbar.addWidget(self.filterSpellsEdit)
        self.resize(1024,600)

        self.classFilter = ""
        self.searchText = ""
        self.filterRulebooks = set()
        self.filterSchools = set()
        self.filterSubschools = set()
        self.filterDescriptors = set()
        self.pauseFilters = False

        self.model = SpellModel(self.db)
        self.filtermodel = FilterModel()
        self.filtermodel.setSourceModel(self.model)
        self.connectModels()
        self.fillSystems()
        self.fillSchools()
        self.fillSubschools()
        self.fillDescriptors()
        self.filename = ""
        self.pdffilename = ""
        self.spellBookName=self.tr("New Spellbook")
        self.spellBookAuthor=self.tr("Unknown Author")
        self.modified = False
        self.updateWindowName()

        if self.firstRun:
            wizard = Wizard(self, db)
            wizard.exec_()

    def setUpdate(self):
        self.updateNotify.setText("<b><a href='https://github.com/christofsteel/pySpellbook/releases'>%s</a></b> " % self.tr("Update available!"))
    def rerunWizard(self):
        wizard = Wizard(self, self.db)
        wizard.exec_()

    def exportSelectedDB(self):
        self.exportDB(True)

    def exportDB(self, only_selected=False):
        def findSpell(stuple, s_list):
            for spell in s_list:
                if spell['name'] == stuple[0] and spell['system'] == stuple[1] and spell['rulebook'] == stuple[2]:
                    return spell
        filename, filters = QtGui.QFileDialog.getSaveFileName(options=QtGui.QFileDialog.DontUseNativeDialog)
        if filename:
            with open(filename, 'w') as f:
                spell_list = []
                for d20class_i in [self.model.invisibleRootItem().child(i) for i in range(self.model.invisibleRootItem().rowCount())]:
                    d20class_i.safeload()
                    for level_i in [d20class_i.child(i) for i in range(d20class_i.rowCount())]:
                        level_i.safeload()
                        for spell_i in [level_i.child(i) for i in range(level_i.rowCount())]:
                            spell = spell_i.spell
                            if only_selected and not spell_i.checkstate:
                                continue
                            spell_dict = findSpell((spell.name, spell.system_name, spell.rulebook_name), spell_list)
                            if not spell_dict:
                                spell_dict = {}
                                spell_dict["name"] = spell.name
                                spell_dict["rulebook"] = spell.rulebook_name
                                spell_dict["system"] = spell.system_name
                                spell_dict["classes"] = []
                                spell_dict["descriptors"] = [d.name for d in spell.descriptors]
                                spell_dict["school"] = spell.school_name
                                spell_dict["subschool"] = spell.subschool_name
                                spell_dict["verbal"] = spell.verbal
                                spell_dict["somatic"] = spell.somatic
                                spell_dict["material"] = spell.material
                                spell_dict["AF"] = spell.arcane_focus
                                spell_dict["DF"] = spell.divine_focus
                                spell_dict["XP"] = spell.xp_costs
                                spell_dict["cast_time"] = spell.cast_time
                                spell_dict["range"] = spell.spell_range
                                spell_dict["area"] = spell.area
                                spell_dict["effect"] = spell.effect
                                spell_dict["target"] = spell.target
                                spell_dict["duration"] = spell.duration
                                spell_dict["saving_throw"] = spell.save
                                spell_dict["spell_resistance"] = spell.spell_res
                                spell_dict["text"] = spell.text
                                spell_list.append(spell_dict)
                            spell_dict["classes"].append((d20class_i.d20class.name, level_i.level.level))
                json.dump(spell_list, f)


    def clearDB(self):
        ret = QtGui.QMessageBox().critical(self, self.tr("Are you sure"), self.tr("This will delete all spells in your database close your spellbook without saving. Continue?"), buttons=QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.Yes:
            self.db.clear()
            self.reloadModel()
            self.modified = False
            self.new()


    def importDB(self):
        filename, filters = QtGui.QFileDialog.getOpenFileName(options=QtGui.QFileDialog.DontUseNativeDialog)
        if filename:
            with open(filename) as f:
                spells = json.load(f)
                pd = QtGui.QProgressDialog(self.tr("Importing Database"), self.tr("Abort"), 0, len(spells), self)
                pd.setWindowModality(QtCore.Qt.WindowModal)
                for i, s in enumerate(spells):
                    pd.setValue(i)
                    pd.setLabelText(s['name'])
                    self.db.add_spell_dict(s, False)

                    if pd.wasCanceled():
                        break
                self.db.delete_empty()
                self.db.session.commit()
                pd.setValue(len(spells))
                self.reloadModel()

    def deleteSpell(self):
        spellIndex = self.spellselections.currentIndex()
        spellIndex = self.filtermodel.mapToSource(spellIndex)
        spell = self.model.itemFromIndex(spellIndex).spell
        self.db.session.delete(spell)
        self.db.delete_empty()
        self.reloadModel()

    def deselectAllLevel(self):
        levelIndex = self.levellist.selectionModel().currentIndex()
        levelIndex = self.filtermodel.mapToSource(levelIndex)
        level = self.model.itemFromIndex(levelIndex)
        level.safeload()
        for spell_i in range(level.rowCount()):
                level.child(spell_i).checkstate = 0
        self.refreshViews()

    def deselectAllClass(self):
        classIndex = self.d20classlist.selectionModel().currentIndex()
        classIndex = self.filtermodel.mapToSource(classIndex)
        d20class = self.model.itemFromIndex(classIndex)
        for level_i in range(d20class.rowCount()):
            d20class.child(level_i).safeload()
            for spell_i in range(d20class.child(level_i).rowCount()):
                d20class.child(level_i).child(spell_i).checkstate = 0
        self.refreshViews()

    def selectAllLevel(self):
        levelIndex = self.levellist.selectionModel().currentIndex()
        levelIndex = self.filtermodel.mapToSource(levelIndex)
        level = self.model.itemFromIndex(levelIndex)
        level.safeload()
        for spell_i in range(level.rowCount()):
                level.child(spell_i).checkstate = 2
        self.refreshViews()

    def selectAllClass(self):
        classIndex = self.d20classlist.selectionModel().currentIndex()
        classIndex = self.filtermodel.mapToSource(classIndex)
        d20class = self.model.itemFromIndex(classIndex)
        for level_i in range(d20class.rowCount()):
            d20class.child(level_i).safeload()
            for spell_i in range(d20class.child(level_i).rowCount()):
                d20class.child(level_i).child(spell_i).checkstate = 2
        self.refreshViews()


    def new(self):
        if self.isModified():
            msgBox = QtGui.QMessageBox()
            msgBox.setText(self.tr("The spellbook has been modified."))
            msgBox.setInformativeText(self.tr("Do you want to save your changes?"))
            msgBox.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel)
            msgBox.setDefaultButton(QtGui.QMessageBox.Yes)
            ret = msgBox.exec_()

            if ret == QtGui.QMessageBox.No:
                self.spellBookName=self.tr("New Spellbook")
                self.spellBookAuthor=self.tr("Unknown Author")
                self.filename = None
                self.pdffilename = None
                self.exportBookAction.setText(self.tr("&Export to PDF..."))
                self.updateWindowName()
                self.model.clearChecked()
                self.refreshViews()
                self.modified = False
                self.spelllist.setHidden(True)
                self.levellist.setHidden(True)
                self.spelldetails.setText("")
            elif ret == QtGui.QMessageBox.Yes:
                self.saveBook()
        else:
            self.spellBookName=self.tr("New Spellbook")
            self.spellBookAuthor=self.tr("Unknown Author")
            self.filename = None
            self.pdffilename = None
            self.updateWindowName()
            self.model.clearChecked()
            self.refreshViews()

    def updateWindowName(self):
        if self.filename:
            self.setWindowTitle("PySpellbook - %s %s %s (%s)" % (self.spellBookName, self.tr("by"), self.spellBookAuthor, os.path.basename(self.filename)))
        else:
            self.setWindowTitle("PySpellbook - %s %s %s (%s)" % (self.spellBookName, self.tr("by"), self.spellBookAuthor, self.tr("unsaved")))

    def setName(self):
        newName, ok = QtGui.QInputDialog.getText(self, self.tr("Set title"), self.tr("Name your spellbook"), text=self.spellBookName)
        if ok:
            self.spellBookName = newName
            self.updateWindowName()
            self.modified = True

    def setAuthor(self):
        newAuthor, ok = QtGui.QInputDialog.getText(self, self.tr("Set author"), self.tr("Set the displayed authorname"), text=self.spellBookAuthor)
        if ok:
            self.spellBookAuthor = newAuthor
            self.updateWindowName()
            self.modified = True

    def beginPauseFilters(self):
        self.pauseFilters = True

    def endPauseFilters(self):
        self.pauseFilters = False
        self.refreshViews()

    def refreshViews(self):
        if not self.pauseFilters:
            old_spell_root = self.filtermodel.mapToSource(self.spelllist.rootIndex())
            old_level_root = self.filtermodel.mapToSource(self.levellist.rootIndex())
            self.filtermodel.invalidateFilter()
            filter_spell_index = self.filtermodel.mapFromSource(old_spell_root)
            filter_level_index = self.filtermodel.mapFromSource(old_level_root)
            if filter_spell_index.isValid():
                self.spelllist.setRootIndex(filter_spell_index)
            else:
                self.spelllist.setHidden(True)
                self.spelldetails.setText("")
            if filter_level_index.isValid():
                self.levellist.setRootIndex(filter_level_index)
            else:
                self.levellist.setHidden(True)
                self.spelllist.setHidden(True)
                self.spelldetails.setText("")


    def reloadModel(self):
        self.model.reload()
        self.fillSystems()
        self.fillSchools()
        self.fillSubschools()
        self.fillDescriptors()


    def connectModels(self):
        self.filtermodel.filterAdded.connect(self.refreshViews)
        self.model.spellChecked.connect(self.refreshViews)
        self.d20classlist.setModel(self.filtermodel)
        self.levellist.setModel(self.filtermodel)
        self.spelllist.setModel(self.filtermodel)
        if self.config["filters"]["selected_only"]:
            self.filterSelectedAction.setChecked(True)
        self.filterRulebooks = set(self.config["filters"]["rulebooks"])
        self.filtermodel.setRulebookFilter(list(self.filterRulebooks))
        self.filterSchools = set(self.config["filters"]["schools"])
        self.filtermodel.setSchoolFilter(list(self.filterSchools))
        self.filterSubschools = set(self.config["filters"]["subschools"])
        self.filtermodel.setSubschoolFilter(list(self.filterSubschools))
        self.filterDescriptors = set(self.config["filters"]["descriptors"])
        self.filtermodel.setDescriptorFilter(list(self.filterDescriptors))
        self.updateRecentsActions()

        self.refreshViews()

    def check(self, menu):
        def do_uncheck():
            self.beginPauseFilters()
            for action in menu.actions():
                action.setChecked(True)
            self.endPauseFilters()
        return do_uncheck

    def uncheck(self, menu):
        def do_uncheck():
            self.beginPauseFilters()
            for action in menu.actions():
                action.setChecked(False)
            self.endPauseFilters()
        return do_uncheck

    def isModified(self):
        return self.modified or self.model.isModified()

    def fillSystems(self):
        self.filterSystemMenu.clear()
        systems = [result[0] for result in self.db.list_system_names()]
        self.beginPauseFilters()
        for system in sorted(systems):
            escaped_system = system.replace("&", "&&")
            systemMenu = self.filterSystemMenu.addMenu(escaped_system)
            rulebooks = [rulebook.name for rulebook in self.db.list_rulebooks(system)]
            check_all = systemMenu.addAction(self.tr("All"))
            uncheck_all = systemMenu.addAction(self.tr("None"))
            uncheck_all.triggered.connect(self.uncheck(systemMenu))
            check_all.triggered.connect(self.check(systemMenu))
            systemMenu.addSeparator()
            for rulebook in sorted(rulebooks):
                escaped_rulebook = rulebook.replace("&", "&&")
                rulebookAction = systemMenu.addAction(escaped_rulebook)
                rulebookAction.setCheckable(True)
                if not rulebook in self.filterRulebooks:
                    rulebookAction.setChecked(True)
                rulebookAction.toggled.connect(self.createRulebookFilter(rulebook))
        self.endPauseFilters()

    def fillDescriptors(self):
        self.filterDescriptorMenu.clear()
        descriptors = [result.name for result in self.db.list_descriptors()]
        self.beginPauseFilters()
        check_all = self.filterDescriptorMenu.addAction(self.tr("All"))
        uncheck_all = self.filterDescriptorMenu.addAction(self.tr("None"))
        uncheck_all.triggered.connect(self.uncheck(self.filterDescriptorMenu))
        check_all.triggered.connect(self.check(self.filterDescriptorMenu))
        self.filterDescriptorMenu.addSeparator()
        descriptorAction = self.filterDescriptorMenu.addAction(self.tr("No Descriptor"))
        descriptorAction.setCheckable(True)
        if not None in self.filterDescriptors:
            descriptorAction.setChecked(True)
        descriptorAction.toggled.connect(self.createDescriptorFilter(None))
        for descriptor in sorted(descriptors):
            escaped_descriptor = descriptor.replace("&", "&&")
            descriptorAction = self.filterDescriptorMenu.addAction(escaped_descriptor)
            descriptorAction.setCheckable(True)
            if not descriptor in self.filterDescriptors:
                descriptorAction.setChecked(True)
            descriptorAction.toggled.connect(self.createDescriptorFilter(descriptor))
        self.endPauseFilters()

    def fillSubschools(self):
        self.filterSubschoolMenu.clear()
        subschools = [result.name for result in self.db.list_subschools()]
        self.beginPauseFilters()
        check_all = self.filterSubschoolMenu.addAction(self.tr("All"))
        uncheck_all = self.filterSubschoolMenu.addAction(self.tr("None"))
        uncheck_all.triggered.connect(self.uncheck(self.filterSubschoolMenu))
        check_all.triggered.connect(self.check(self.filterSubschoolMenu))
        self.filterSubschoolMenu.addSeparator()
        subschoolAction = self.filterSubschoolMenu.addAction(self.tr("No Subschool"))
        subschoolAction.setCheckable(True)
        subschoolAction.toggled.connect(self.createSubschoolFilter(None))
        if not None in self.filterSubschools:
            subschoolAction.setChecked(True)
        for subschool in sorted(subschools):
            escaped_subschool = subschool.replace("&", "&&")
            subschoolAction = self.filterSubschoolMenu.addAction(escaped_subschool)
            subschoolAction.setCheckable(True)
            if not subschool in self.filterSubschools:
                subschoolAction.setChecked(True)
            subschoolAction.toggled.connect(self.createSubschoolFilter(subschool))
        self.endPauseFilters()

    def fillSchools(self):
        self.filterSchoolMenu.clear()
        schools = [result.name for result in self.db.list_schools()]
        self.beginPauseFilters()
        check_all = self.filterSchoolMenu.addAction(self.tr("All"))
        uncheck_all = self.filterSchoolMenu.addAction(self.tr("None"))
        uncheck_all.triggered.connect(self.uncheck(self.filterSchoolMenu))
        check_all.triggered.connect(self.check(self.filterSchoolMenu))
        self.filterSchoolMenu.addSeparator()
        for school in sorted(schools):
            escaped_school = school.replace("&", "&&")
            schoolAction = self.filterSchoolMenu.addAction(escaped_school)
            schoolAction.setCheckable(True)
            if not school in self.filterSchools:
                schoolAction.setChecked(True)
            schoolAction.toggled.connect(self.createSchoolFilter(school))
        self.endPauseFilters()

    def search(self, searchText):
        self.searchText = searchText
        self.filtermodel.setSearchText(self.searchText)

    def filterClasses(self, d20class):
        self.classFilter = d20class
        self.filtermodel.setClassFilter(self.classFilter)

    def filterSelected(self, checked):
        self.filtermodel.setSelectedOnly(checked)
        self.config["filters"]["selected_only"] = checked
        with open(self.configfile,'w') as f:
            json.dump(self.config, f, indent=2)

    def createDescriptorFilter(self, descriptor):
        def filter_descriptor(checked):
            if checked:
                self.filterDescriptors.discard(descriptor)
            else:
                self.filterDescriptors.add(descriptor)
            self.filtermodel.setDescriptorFilter(list(self.filterDescriptors))
            self.config["filters"]["descriptors"] = list(self.filterDescriptors)
            with open(self.configfile,'w') as f:
                json.dump(self.config, f, indent=2)
        return filter_descriptor

    def createRulebookFilter(self, rulebook):
        def filter_rulebook(checked):
            if checked:
                self.filterRulebooks.discard(rulebook)
            else:
                self.filterRulebooks.add(rulebook)
            self.filtermodel.setRulebookFilter(list(self.filterRulebooks))
            self.config["filters"]["rulebooks"] = list(self.filterRulebooks)
            with open(self.configfile,'w') as f:
                json.dump(self.config, f, indent=2)
        return filter_rulebook

    def createSubschoolFilter(self, subschool):
        def filter_subschool(checked):
            if checked:
                self.filterSubschools.discard(subschool)
            else:
                self.filterSubschools.add(subschool)
            self.filtermodel.setSubschoolFilter(list(self.filterSubschools))
            self.config["filters"]["subschools"] = list(self.filterSubschools)
            with open(self.configfile,'w') as f:
                json.dump(self.config, f, indent=2)
        return filter_subschool

    def createSchoolFilter(self, school):
        def filter_school(checked):
            if checked:
                self.filterSchools.discard(school)
            else:
                self.filterSchools.add(school)
            self.filtermodel.setSchoolFilter(list(self.filterSchools))
            self.config["filters"]["schools"] = list(self.filterSchools)
            with open(self.configfile,'w') as f:
                json.dump(self.config, f, indent=2)
        return filter_school

    def showEditSpell(self):
        spellIndex = self.spellselections.currentIndex()
        spellIndex = self.filtermodel.mapToSource(spellIndex)
        spell = self.model.itemFromIndex(spellIndex).spell
        Dialog = QtGui.QDialog()
        asw = AddSpellWindow(self.db)
        asw.setupUi(Dialog)
        asw.loadSpell(spell)
        if Dialog.exec_():
            spell_dict = asw.generate_spell_dict()
            self.db.add_spell_dict(spell_dict)
            self.db.delete_empty()
            self.reloadModel()

    def showAddSpell(self):
        Dialog = QtGui.QDialog()
        asw = AddSpellWindow(self.db)
        asw.setupUi(Dialog)
        if Dialog.exec_():
            spell_dict = asw.generate_spell_dict()
            self.db.add_spell_dict(spell_dict)
            self.reloadModel()

    def showConfig(self):
        oldbackend = self.config["backend"]
        Dialog = QtGui.QDialog()
        cd = ConfigDialog()
        cd.setupUi(Dialog)
        cd.loadConfig(self.config)
        if Dialog.exec_():
            self.config = cd.getConfig()
            if self.config["backend"] == "HTML" and self.config["backend"] != oldbackend:
                self.pdffilename = None
                self.exportBookAction.setText(self.tr("&Export to HTML..."))
            elif oldbackend == "HTML" and self.config["backend"] != oldbackend:
                self.pdffilename = None
                self.exportBookAction.setText(self.tr("&Export to PDF..."))
            with open(self.configfile, 'w') as f:
                json.dump(self.config, f, indent=2)

    def openBook(self):
        directory = os.path.expanduser("~")
        if self.filename:
            directory = os.path.dirname(self.filename)
        if self.isModified():
            msgBox = QtGui.QMessageBox()
            msgBox.setText(self.tr("The spellbook has been modified."))
            msgBox.setInformativeText(self.tr("Do you want to save your changes?"))
            msgBox.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel)
            msgBox.setDefaultButton(QtGui.QMessageBox.Yes)
            ret = msgBox.exec_()
            if ret == QtGui.QMessageBox.No:
                filename, filters = QtGui.QFileDialog.getOpenFileName(self, dir=directory, filter=self.tr("Spellbooks (*.book);;All Files (*)"), options=QtGui.QFileDialog.DontUseNativeDialog)
                if filename:
                    SpellBookHandler.open(filename, self)
                    self.modified = False
                    self.filename = filename
                    self.updateRecents()
                    with open(self.configfile,'w') as f:
                        json.dump(self.config, f, indent=2)
                    self.updateWindowName()
            elif ret == QtGui.QMessageBox.Yes:
                self.saveBook()
        else:
            filename, filters = QtGui.QFileDialog.getOpenFileName(self, dir=directory, filter=self.tr("Spellbooks (*.book);;All Files (*)"), options=QtGui.QFileDialog.DontUseNativeDialog)
            if filename:
                SpellBookHandler.open(filename, self)
                self.modified = False
                self.filename = filename
                self.updateRecents()
                with open(self.configfile,'w') as f:
                    json.dump(self.config, f, indent=2)
                self.updateWindowName()

    def saveAsBook(self):
        directory = os.path.expanduser("~")
        if self.filename:
            directory = os.path.dirname(self.filename)
        saveDialog = QtGui.QFileDialog(self, "Save")
        saveDialog.setNameFilter("Spellbooks (*.book)")
        saveDialog.setDirectory(directory)
        saveDialog.setAcceptMode(QtGui.QFileDialog.AcceptSave)
        saveDialog.setDefaultSuffix("book")
        saveDialog.setFileMode(QtGui.QFileDialog.AnyFile)
        if saveDialog.exec_():
            filename = saveDialog.selectedFiles()[0]
            SpellBookHandler.save(filename, self)
            self.modified = False
            self.filename = filename
            self.updateRecents()
            with open(self.configfile,'w') as f:
                json.dump(self.config, f, indent=2)
            self.updateWindowName()

    def saveBook(self):
        if self.filename:
            filename = self.filename
        else:
            saveDialog = QtGui.QFileDialog(self, "Save")
            saveDialog.setNameFilter("Spellbooks (*.book)")
            saveDialog.setAcceptMode(QtGui.QFileDialog.AcceptSave)
            saveDialog.setDefaultSuffix("book")
            saveDialog.setFileMode(QtGui.QFileDialog.AnyFile)
            if saveDialog.exec_():
                filename = saveDialog.selectedFiles()[0]
            else:
                return
        if filename:
            SpellBookHandler.save(filename, self)
            self.modified = False
            self.filename = filename
            self.updateRecents()
            with open(self.configfile,'w') as f:
                json.dump(self.config, f, indent=2)
            self.updateWindowName()

    def exportBook(self):
        if self.pdffilename:
            self.generateBook(self.pdffilename)
        else:
            self.exportAsBook()

    def exportAsBook(self):
        ffilter=self.tr("PDF Files (*.pdf);;All Files (*)")
        if self.config["backend"] == "HTML":
            ffilter=self.tr("HTML Files (*.html);;All Files (*)")
        directory = os.path.expanduser("~")
        if self.pdffilename:
            directory = os.path.dirname(self.pdffilename)
        filename, filters = QtGui.QFileDialog.getSaveFileName(self, dir=directory, filter=ffilter, options=QtGui.QFileDialog.DontUseNativeDialog)
        if filename:
            self.pdffilename = filename
            self.exportBookAction.setText(self.tr("Export to %s") % os.path.basename(self.pdffilename))
            try:
                self.generateBook(filename)
                if self.config["backend"] != "HTML":
                    ans = QtGui.QMessageBox.question(self, self.tr("Open book"), self.tr("Open pdf in external viewer?"), QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                    if ans == QtGui.QMessageBox.Yes:
                        if sys.platform == "win32":
                            os.startfile(self.pdffilename)
                        elif sys.platform == "darwin":
                            subprocess.call(["open", self.pdffilename])
                        else:
                            subprocess.call(["xdg-open", self.pdffilename])
            except TypeError:
                QtGui.QMessageBox.warning(self, self.tr("Something went wrong"), self.tr("Could not create %s, please check export settings.") % filename)


    def generateBook(self, filename):
        g = HTMLGenerator(self.model, self.spellBookName, self.spellBookAuthor, parent=self)
        g.make_book(filename, self.config)

    def generatePDF(self):
        g = LatexGenerator('fancy', self.model)
        filename, filters = QtGui.QFileDialog.getSaveFileName()
        g.compile_to_pdf(filename, None)
