import re
import os
import json

class Importer:
    def __init__(self, root, base_url=""):
        self.root = root
        self.base_url = os.path.abspath(base_url)
        self._spells = []

    def getSpells(self):
        for link, spell in self.listSpellIndex():
            if 'name' in spell.keys() and spell['name'] and\
                    'system' in spell.keys() and spell['system'] and\
                    'rulebook' in spell.keys() and spell['rulebook']:
                existing_spell = self.findSpell(spell['name'], spell['system'], spell['rulebook'])
                if existing_spell:
                    if 'classes' in spell.keys() and spell['classes']:
                        for d20class, level in spell['classes']:
                            existing_spell['classes'].append((d20class, level))
                else:
                    spell = self.parseSpell(link, spell)
                    self._spells.append(spell)
        self.postParse()
        return self._spells

    def findSpellByName(self, name):
        for spell in self._spells:
            if self.normalize(spell['name']) == self.normalize(name):
                return spell

    def save(self, filename):
        spells = self.getSpells()
        with open(filename, 'w') as f:
            json.dump(sorted(spells, key=lambda spell: spell['name']), f)



    def postParse(self):
        pass

    def addStat(self, source, target, sourceName, targetName):
        """
        Adds the value of source[sourceName] to target[targetName]
        or target[targetName] = "" if source[sourceName] does not exist
        """
        if sourceName in source.keys():
            target[targetName] = source[sourceName]
        else:
            target[targetName] = ""

    def listSpellIndex(self):
        """
        Returns a list of tuples of a link and a initial spell
        dictionary.
        """
        raise NotImplementedError()

    def parseSpell(self, link, init_spell_dict):
        """
        Returns a spell dictionary.
        """
        raise NotImplementedError()

    def stripLinks(self, string):
        """
        Strips a string of all links
        """
        return re.sub("<a.*?>","",string).replace("</a>", "")

    def findSpell(self, name, system, rulebook):
        for spell in self._spells:
            if self.normalize(spell['name']) == self.normalize(name) and spell['rulebook'] == rulebook and spell['system'] == system:
                return spell

    def normalize(self, string):
        """
        Returns a normalized String
        """
        return string.upper().replace(",","").replace(" ", "").replace("/", "").replace("-","").replace("'","").replace("-","")


