from PySide import QtGui, QtCore
from jinja2 import Template

import os
import json
from pySpellbook.qmodel import SpellModel, FilterModel
from pySpellbook.template import LatexGenerator, HTMLGenerator
from pySpellbook.addSpellWindow import AddSpellWindow
from pySpellbook.config_window import ConfigDialog

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


    def __init__(self, db, configfile):
        super().__init__()
        self.db = db
        self.configfile = configfile
        self.config = {}
        if os.path.exists(self.configfile):
            with open(self.configfile) as f:
                self.config = json.load(f)
        else:
            self.config['backend'] = 'internal'
            self.config['custom'] = 'html2pdf $INPUT $OUTPUT'
            self.config['prince_path'] = '/usr/bin/prince'
            with open(self.configfile,'w') as f:
                json.dump(self.config, f, indent=2)

        # Setting up the window
        self.setWindowTitle("PySpellbook")
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
        self.d20filterEdit = QtGui.QLineEdit()
        self.d20filterEdit.setPlaceholderText("Filter classes")
        self.d20classArea.layout().addWidget(self.d20filterEdit)
        self.d20classlist = QtGui.QListView(self.spellArea)
        self.d20classArea.layout().addWidget(self.d20classlist)
        self.d20classlist.setAlternatingRowColors(True)
        self.levellist = QtGui.QListView(self.spellArea)
        self.spelllist = QtGui.QListView(self.spellArea)
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

        self.d20filterEdit.textChanged.connect(self.filterClasses)
        self.d20classlist.clicked.connect(self.showLevels)
        self.levellist.clicked.connect(self.showSpells)

        # Setting up menus
        self.menuBar = QtGui.QMenuBar(self)
        self.setMenuBar(self.menuBar)
        self.filterSpellsEdit = QtGui.QLineEdit()
        self.filterSpellsEdit.setPlaceholderText("Search...")
        self.menuBar.setCornerWidget(self.filterSpellsEdit)
        self.fileMenu = self.menuBar.addMenu("&File")
        self.spellBookMenu = self.menuBar.addMenu("Spell&book")
        self.dbMenu = self.menuBar.addMenu("&Database")
        self.filterMenu = self.menuBar.addMenu("F&ilter")
        self.filterSystemMenu = self.filterMenu.addMenu("&Rulebooks")
        self.filterSchoolMenu = self.filterMenu.addMenu("&School")
        self.filterSubschoolMenu = self.filterMenu.addMenu("Su&bschool")
        self.filterDescriptorMenu = self.filterMenu.addMenu("&Descriptor")
        self.newAction = QtGui.QAction("&New", self)
        self.newAction.setShortcut(QtCore.Qt.CTRL + QtCore.Qt.Key_N)
        self.fileMenu.addAction(self.newAction)
        self.openAction = QtGui.QAction(self)
        self.openAction.setText("&Open...")
        self.openAction.setShortcut(QtCore.Qt.CTRL + QtCore.Qt.Key_O)
        self.fileMenu.addAction(self.openAction)
        self.fileMenu.addSeparator()
        self.saveAction = QtGui.QAction(self)
        self.saveAction.setText("&Save...")
        self.saveAction.setShortcut(QtCore.Qt.CTRL + QtCore.Qt.Key_S)
        self.fileMenu.addAction(self.saveAction)
        self.saveasAction = QtGui.QAction(self)
        self.saveasAction.setText("&Save As...")
        self.fileMenu.addAction(self.saveasAction)
        self.fileMenu.addSeparator()
        self.quitAction = QtGui.QAction(self)
        self.quitAction.setText("&Quit")
        self.quitAction.setShortcut(QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.quitAction.setIcon(QtGui.QIcon.fromTheme("application-exit"))
        self.fileMenu.addAction(self.quitAction)

        self.setNameAction = QtGui.QAction("Set &Name...", self)
        self.spellBookMenu.addAction(self.setNameAction)
        self.setAuthorAction = QtGui.QAction("Set &Author...", self)
        self.spellBookMenu.addAction(self.setAuthorAction)
        #self.selectImageAction = QtGui.QAction("Select &Image...", self)
        #self.spellBookMenu.addAction(self.selectImageAction)
        self.spellBookMenu.addSeparator()
        #self.selectTemplateAction = QtGui.QAction("Select &Template...", self)
        #self.spellBookMenu.addAction(self.selectTemplateAction)
        self.configExportAction = self.spellBookMenu.addAction("&Configure Export...")
        self.spellBookMenu.addSeparator()
        self.exportBookAction = QtGui.QAction("&Export Spellbook...", self)
        self.spellBookMenu.addAction(self.exportBookAction)
        #self.exportHtmlAction = QtGui.QAction("Export HTML...", self)
        #self.spellBookMenu.addAction(self.exportHtmlAction)

        self.addSpellAction = QtGui.QAction("&Add Spell...", self)
        self.dbMenu.addAction(self.addSpellAction)
        self.dbMenu.addSeparator()
        self.importDBAction = QtGui.QAction("&Import DB...", self)
        self.dbMenu.addAction(self.importDBAction)
        self.exportDBAction = self.dbMenu.addAction("&Export DB...")
        #self.dbMenu.addAction("Export Selection...")

        self.editSpellAction = QtGui.QAction("Edit...", self)
        self.deleteSpellAction = QtGui.QAction("Delete", self)
        self.spelllist.addAction(self.editSpellAction)
        self.spelllist.addAction(self.deleteSpellAction)

        self.editSpellAction.triggered.connect(self.showEditSpell)
        self.deleteSpellAction.triggered.connect(self.deleteSpell)

        self.filterSpellsEdit.textChanged.connect(self.search)

        self.newAction.triggered.connect(self.new)
        self.openAction.triggered.connect(self.openBook)
        self.saveAction.triggered.connect(self.saveBook)
        self.saveasAction.triggered.connect(self.saveAsBook)
        self.quitAction.triggered.connect(self.close)
        self.setAuthorAction.triggered.connect(self.setAuthor)
        self.setNameAction.triggered.connect(self.setName)
        #self.exportPdfAction.triggered.connect(self.generatePDF)
        self.exportBookAction.triggered.connect(self.generateBook)
        self.addSpellAction.triggered.connect(self.showAddSpell)
        self.importDBAction.triggered.connect(self.importDB)
        self.configExportAction.triggered.connect(self.showConfig)

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
        self.spellBookName="New Spellbook"
        self.spellBookAuthor="Unknown Author"
        self.modified = False
        self.updateWindowName()

    def importDB(self):
        filename, filters = QtGui.QFileDialog.getOpenFileName()
        if filename:
            with open(filename) as f:
                spells = json.load(f)
                pd = QtGui.QProgressDialog("Importing Database", "Abort", 0, len(spells), self)
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


    def new(self):
        if self.isModified():
            msgBox = QtGui.QMessageBox()
            msgBox.setText("The spellbook has been modified.")
            msgBox.setInformativeText("Do you want to save your changes?")
            msgBox.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel)
            msgBox.setDefaultButton(QtGui.QMessageBox.Yes)
            ret = msgBox.exec_()

            if ret == QtGui.QMessageBox.No:
                self.spellBookName="New Spellbook"
                self.spellBookAuthor="Unknown Author"
                self.updateWindowName()
                self.model.clearChecked()
                self.modified = False
            elif ret == QtGui.QMessageBox.Yes:
                self.saveBook()
        else:
            self.spellBookName="New Spellbook"
            self.spellBookAuthor="Unknown Author"
            self.updateWindowName()
            self.model.clearChecked()

    def updateWindowName(self):
        if self.filename:
            self.setWindowTitle("PySpellbook - %s by %s (%s)" % (self.spellBookName, self.spellBookAuthor, os.path.basename(self.filename)))
        else:
            self.setWindowTitle("PySpellbook - %s by %s (unsaved)" % (self.spellBookName, self.spellBookAuthor))

    def setName(self):
        newName, ok = QtGui.QInputDialog.getText(self, "Set Name", "Name yout spellbook", text=self.spellBookName)
        if ok:
            self.spellBookName = newName
            self.updateWindowName()
            self.modified = True

    def setAuthor(self):
        newAuthor, ok = QtGui.QInputDialog.getText(self, "Set Author", "Set the displayed authorname", text=self.spellBookAuthor)
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
        self.d20classlist.setModel(self.filtermodel)
        self.levellist.setModel(self.filtermodel)
        self.spelllist.setModel(self.filtermodel)
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
            check_all = systemMenu.addAction("Select All")
            uncheck_all = systemMenu.addAction("Deselect All")
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
        check_all = self.filterDescriptorMenu.addAction("Select All")
        uncheck_all = self.filterDescriptorMenu.addAction("Deselect All")
        uncheck_all.triggered.connect(self.uncheck(self.filterDescriptorMenu))
        check_all.triggered.connect(self.check(self.filterDescriptorMenu))
        self.filterDescriptorMenu.addSeparator()
        descriptorAction = self.filterDescriptorMenu.addAction("No Descriptor")
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
        check_all = self.filterSubschoolMenu.addAction("Select All")
        uncheck_all = self.filterSubschoolMenu.addAction("Deselect All")
        uncheck_all.triggered.connect(self.uncheck(self.filterSubschoolMenu))
        check_all.triggered.connect(self.check(self.filterSubschoolMenu))
        self.filterSubschoolMenu.addSeparator()
        subschoolAction = self.filterSubschoolMenu.addAction("No Subschool")
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
        check_all = self.filterSchoolMenu.addAction("Select All")
        uncheck_all = self.filterSchoolMenu.addAction("Deselect All")
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

    def createDescriptorFilter(self, descriptor):
        def filter_descriptor(checked):
            if checked:
                self.filterDescriptors.discard(descriptor)
            else:
                self.filterDescriptors.add(descriptor)
            self.filtermodel.setDescriptorFilter(list(self.filterDescriptors))
        return filter_descriptor

    def createRulebookFilter(self, rulebook):
        def filter_rulebook(checked):
            if checked:
                self.filterRulebooks.discard(rulebook)
            else:
                self.filterRulebooks.add(rulebook)
            self.filtermodel.setRulebookFilter(list(self.filterRulebooks))
        return filter_rulebook

    def createSubschoolFilter(self, subschool):
        def filter_subschool(checked):
            if checked:
                self.filterSubschools.discard(subschool)
            else:
                self.filterSubschools.add(subschool)
            self.filtermodel.setSubschoolFilter(list(self.filterSubschools))
        return filter_subschool

    def createSchoolFilter(self, school):
        def filter_school(checked):
            if checked:
                self.filterSchools.discard(school)
            else:
                self.filterSchools.add(school)
            self.filtermodel.setSchoolFilter(list(self.filterSchools))
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
        Dialog = QtGui.QDialog()
        cd = ConfigDialog()
        cd.setupUi(Dialog)
        cd.loadConfig(self.config)
        if Dialog.exec_():
            self.config = cd.getConfig()
            with open(self.configfile, 'w') as f:
                json.dump(self.config, f, indent=2)

    def openBook(self):
        filename, filters = QtGui.QFileDialog.getOpenFileName()
        if filename:
            SpellBookHandler.open(filename, self)
            self.filename = filename
            self.updateWindowName()

    def saveAsBook(self):
        filename, filters = QtGui.QFileDialog.getSaveFileName()
        if filename:
            SpellBookHandler.save(filename, self)
            self.filename = filename
            self.updateWindowName()

    def saveBook(self):
        if self.filename:
            filename = self.filename
        else:
            filename, filters = QtGui.QFileDialog.getSaveFileName()
        if filename:
            SpellBookHandler.save(filename, self)
            self.filename = filename
            self.updateWindowName()

    def generateBook(self):
        g = HTMLGenerator(self.model, self.spellBookName, self.spellBookAuthor)
        filename, filters = QtGui.QFileDialog.getSaveFileName()
        if filename:
            g.make_book(filename, self.config)

    def generatePDF(self):
        g = LatexGenerator('fancy', self.model)
        filename, filters = QtGui.QFileDialog.getSaveFileName()
        g.compile_to_pdf(filename, None)