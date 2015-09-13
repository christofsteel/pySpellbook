from PySide.QtCore import Qt, Signal, QSize
from PySide.QtGui import QStandardItemModel, QStandardItem, QSortFilterProxyModel

class SpellItem(QStandardItem):
    def __init__(self, spell):
        super().__init__("%s (%s)" % (spell.name, spell.rulebook))
        self.spell = spell
        self.loaded = True
        self.checkstate = 0

    def load(self):
        pass

class LevelItem(QStandardItem):
    def __init__(self, level):
        super().__init__("Level %s" % level.level)
        self.level = level
        self.loaded = False

    def safeload(self):
        if not self.loaded:
            self.load()

    def load(self):
        for spell in sorted(self.level.spells, key=lambda s:s.name):
            self.appendRow(SpellItem(spell))
        self.loaded = True

class ClassItem(QStandardItem):
    def __init__(self, d20class):
        super().__init__(d20class.name)
        self.d20class = d20class
        self.loaded = False
        self.load()

    def safeload(self):
        if not self.loaded:
            self.load()

    def load(self):
        for level in sorted(self.d20class.levels, key=lambda l:l.level):
            self.appendRow(LevelItem(level))
        self.loaded = True

class SpellModel(QStandardItemModel):
    spellChecked = Signal()
    def spellItemFor(self, d20class_name, level_level, spell_name, rulebook_name, system_name, load=False):
        root = self.invisibleRootItem()
        nrClasses = root.rowCount()
        for i in range(nrClasses):
            if root.child(i).d20class.name == d20class_name:
                if load:
                    root.child(i).safeload()
                nrLevels = root.child(i).rowCount()
                for j in range(nrLevels):
                    if root.child(i).child(j).level.level == level_level:
                        if load:
                            root.child(i).child(j).safeload()
                        nrSpells = root.child(i).child(j).rowCount()
                        for k in range(nrSpells):
                            spell_item = root.child(i).child(j).child(k)
                            if spell_item.spell.name == spell_name \
                                    and spell_item.spell.rulebook_name == rulebook_name \
                                    and spell_item.spell.system_name == system_name:
                                return spell_item


    def __init__(self, db):
        super().__init__()
        self.db = db
        d20classes = db.list_d20classes()
        self.invisibleRootItem().appendRows([ClassItem(d20class) for d20class in \
                                             sorted(d20classes, key=lambda c:c.name)])
        self.modified = False

    def reload(self):
        spells = self.getCheckedSpells()
        self.clear()
        d20classes = self.db.list_d20classes()
        self.invisibleRootItem().appendRows([ClassItem(d20class) for d20class in \
                                             sorted(d20classes, key=lambda c:c.name)])
        self.setCheckedSpells(spells)
        """
        root = self.invisibleRootItem().clone()
        self.clear()
        nrClasses = root.rowCount()
        old_d20classes = [root.child(i) for i in range(nrClasses)]
        d20classes = self.db.list_d20classes()
        new_d20classItems = []
        for d20class in sorted(d20classes, key=lambda c:c.name):
            d20_item = [o for o in old_d20classes if o.d20class.name == d20class.name]
            new_d20_item = ClassItem(d20class)
            if d20_item and d20_item[0].loaded:
                nrLevels = d20_item[0].rowCount()
                old_levels = [d20_item[0].child(i) for i in range(nrLevels)]
                levels = d20class.levels
                new_levels = []
                for level in sorted(levels, key=lambda c:c.level):
                    level_item = [o for o in old_levels if o.level.level == level.level]
                    new_level_item = LevelItem(level)
                    if level_item and level_item[0].loaded:
                        nrSpells = level_item[0].rowCount()
                        old_spells = [level_item[0].child(i) for i in range(nrSpells)]
                        spells = level.spells
                        new_spells = []
                        for spell in sorted(spells, key=lambda c:c.name):
                            spell_item = [o for o in old_spells if o.spell.name == spell.name and o.spell.rulebook_name == spell.rulebook_name and o.spell.system_name == spell.system_name]
                            checkstate = 0
                            if spell_item:
                                checkstate = spell_item[0].checkstate
                            new_spell_item = SpellItem(spell)
                            new_spell_item.checkstate = checkstate
                            new_spells.append(new_spell_item)
                        for si in sorted(new_spells, key=lambda c: c.spell.name):
                            new_level_item.appendRow(si)
                    new_levels.append(new_level_item)
                    print(new_levels)
                for li in sorted(new_levels, key=lambda c: c.level.level):
                    new_d20_item.appendRow(li)
            new_d20classItems.append(new_d20_item)
        for di in sorted(new_d20classItems, key=lambda c: c.d20class.name):
            self.invisibleRootItem().appendRow(di)
        """



    def flags(self, index):
        return super().flags(index)|Qt.ItemIsUserCheckable

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        item = self.itemFromIndex(index)
        if not item.loaded:
            item.load()
        if role == Qt.CheckStateRole and type(item) == SpellItem:
            return item.checkstate
        if role == Qt.UserRole:
            return item
        if role == Qt.SizeHintRole:
            size = QSize()
            size.setHeight(48)
            return size
        return super().data(index, role)

    def clearChecked(self):
        self.modified = False
        root_index = self.indexFromItem(self.invisibleRootItem())
        d20classes_count = self.rowCount(root_index)
        d20classes_indexes = [self.index(i,0,root_index) for i in range(d20classes_count)]
        for d20class_index in d20classes_indexes:
            if not self.itemFromIndex(d20class_index).loaded:
                continue
            level_count = self.rowCount(d20class_index)
            level_indexes = [self.index(i,0,d20class_index) for i in range(level_count)]
            for level_index in level_indexes:
                if not self.itemFromIndex(level_index).loaded:
                    continue
                self.itemFromIndex(level_index).safeload()
                spell_count = self.rowCount(level_index)
                spells_items = [self.itemFromIndex(self.index(i,0,level_index)) for i in range(spell_count)]
                for spell in spells_items:
                    spell.checkstate = 0

    def setCheckedSpells(self, spells, overwriteLoad=False):
        self.modified = False
        root_index = self.indexFromItem(self.invisibleRootItem())
        d20classes_count = self.rowCount(root_index)
        d20classes_indexes = [self.index(i,0,root_index) for i in range(d20classes_count)]
        for d20class_index in d20classes_indexes:
            d20class_name = self.data(d20class_index)
            if not d20class_name in spells.keys():
                continue
            if overwriteLoad:
                self.itemFromIndex(d20class_index).load()
            else:
                self.itemFromIndex(d20class_index).safeload()

            level_count = self.rowCount(d20class_index)
            level_indexes = [self.index(i,0,d20class_index) for i in range(level_count)]
            for level_index in level_indexes:
                level_level = str(self.itemFromIndex(level_index).level.level)
                if not level_level in [str(k) for k in spells[d20class_name].keys()]:
                    continue
                if overwriteLoad:
                    self.itemFromIndex(level_index).load()
                else:
                    self.itemFromIndex(level_index).safeload()
                spell_count = self.rowCount(level_index)
                spells_items = [self.itemFromIndex(self.index(i,0,level_index)) for i in range(spell_count)]
                for spell in spells_items:
                    if spells[d20class_name][level_level][0] and type(spells[d20class_name][level_level][0]) == list:
                        compareObj = [spell.spell.rulebook_name, spell.spell.system_name, spell.spell.name]
                        if compareObj in spells[d20class_name][level_level]:
                            spell.checkstate = 2
                    else: # Assume model.Spell object
                        if (spell.spell.name, spell.spell.rulebook_name, spell.spell.system_name)\
                            in [(s.name, s.rulebook_name, s.system_name) for s in spells[d20class_name][level_level]]:
                            spell.checkstate = 2


    def getCheckedSpells(self):
        self.modified = False
        spells = {}
        root_index = self.indexFromItem(self.invisibleRootItem())
        d20classes_count = self.rowCount(root_index)
        d20classes_indexes = [self.index(i,0,root_index) for i in range(d20classes_count)]
        for d20class_index in d20classes_indexes:
            level_count = self.rowCount(d20class_index)
            level_indexes = [self.index(i,0,d20class_index) for i in range(level_count)]
            for level_index in level_indexes:
                spell_count = self.rowCount(level_index)
                spells_items = [self.itemFromIndex(self.index(i,0,level_index)) for i in range(spell_count)]
                for spell in spells_items:
                    if spell.checkstate:
                        d20class_name = self.data(d20class_index)
                        level_level = self.itemFromIndex(level_index).level.level
                        if not d20class_name in spells.keys():
                            spells[d20class_name] = {}
                        if not str(level_level) in spells[d20class_name].keys():
                            spells[d20class_name][str(level_level)] = []
                        spells[d20class_name][str(level_level)].append(spell.spell)
        return spells


    def isModified(self):
        return self.modified

    def setData(self, index, value, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        item = self.itemFromIndex(index)
        if role == Qt.CheckStateRole and type(item) == SpellItem:
            item.checkstate = value
            self.modified = True
            self.spellChecked.emit()
            return True


class FilterModel(QSortFilterProxyModel):
    filterAdded = Signal()
    def __init__(self):
        super().__init__()
        self.deep_filtered = False
        self.rulebookFilter = []
        self.schoolFilter = []
        self.subschoolFilter = []
        self.descriptorFilter = []
        self.selectedOnly = False
        self.classFilter = ""
        self.searchText = ""

    def setSelectedOnly(self, option):
        self.deep_filtered = True
        self.selectedOnly = option
        self.filterAdded.emit()

    def setSearchText(self, text):
        self.deep_filtered = True
        self.searchText = text
        self.filterAdded.emit()


    def setDescriptorFilter(self, descriptors):
        self.deep_filtered = True
        self.descriptorFilter = descriptors
        self.filterAdded.emit()

    def setRulebookFilter(self, rulebooks):
        self.deep_filtered = True
        self.rulebookFilter = rulebooks
        self.filterAdded.emit()

    def setSubschoolFilter(self, subschool):
        self.deep_filtered = True
        self.subschoolFilter = subschool
        self.filterAdded.emit()

    def setSchoolFilter(self, school):
        self.deep_filtered = True
        self.schoolFilter = school
        self.filterAdded.emit()

    def setClassFilter(self, text):
        self.classFilter = text
        self.filterAdded.emit()
    def isModified(self):
        return self.sourceModel().isModified()

    def filterAcceptsRow(self, row, parent):
        index = self.sourceModel().index(row,0,parent)
        item = self.sourceModel().data(index, Qt.UserRole)
        if type(item) == ClassItem:
            if not self.classFilter in item.d20class.name:
                return False
        if self.deep_filtered:
            if type(item) == SpellItem:
                if self.selectedOnly and not item.checkstate:
                    return False
                if not self.searchText.upper() in item.spell.text.upper() and \
                        not self.searchText.upper() in item.spell.name.upper():
                    return False
                if item.spell.rulebook_name in self.rulebookFilter:
                    return False
                if item.spell.subschool_name in self.subschoolFilter:
                    return False
                if item.spell.school_name in self.schoolFilter:
                    return False
                if not item.spell.descriptors:
                    if None in self.descriptorFilter:
                        return False
                else:
                    if not set([d.name for d in item.spell.descriptors]).difference(set(self.descriptorFilter)):
                        return False

            else:
                count = item.rowCount()
                show_me = False
                for row2 in range(count):
                    show_me = show_me or self.filterAcceptsRow(row2, index)
                if not show_me:
                    return False
        return True

