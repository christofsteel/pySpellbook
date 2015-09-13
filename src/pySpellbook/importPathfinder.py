#!/usr/bin/env python3
try:
    from pySpellbook.importTools import Importer
except ImportError:
    from importTools import Importer
from pyquery import PyQuery as pq
import re
import sys

class PathfinderImporter(Importer):
    def __init__(self, base_url):
        super().__init__("/pathfinderRPG/prd/indices/spelllists.html", base_url=base_url)

    def getBook(self, li):
        if li.find("a").eq(0).text() == "Ablative Barrier":
            return "Ultimate Combat"
        return self.short2book[li.attr("class").split(" ")[-1][5:]]

    def parseSpell(self, link, ispell):
        spellpage = pq(filename=self.base_url + link)
        if ispell["name"] == "Thunderous Drums":
            ispell["name"] = "Thundering Drums"
        if ispell["name"] == "Banshee Blaste":
            ispell["name"] = "Banshee Blast"
        if ispell["name"] == "Polymorph Any Object":
            spellpage = pq(spellpage.html().replace("<tfoot>","<tfoot></table>"))
        if ispell["name"] == "Longstrider, Greater":
            spellpage = pq(spellpage.html().replace("â\x80©",";"))
            spellpage = pq(spellpage.html().replace("\u2029",";"))
        elem = None
        if ispell["id"]:
            elem = spellpage.find("#%s" % ispell["id"]).eq(0)
        if not elem:
            if ispell["name"].endswith("Greater"):
                elem = spellpage.find(".stat-block-title").eq(1)
            if ispell["name"].endswith("Mass") or ispell["name"].endswith("Lesser"):
                elem = spellpage.find(".stat-block-title:last")
            if not elem:
                elem = spellpage.find(".stat-block-title:first")
        assert self.normalize(ispell["name"]) == self.normalize(elem.text())
        spell_name = elem.text()
        spell_ = {}
        spell = {}
        parse_end = False
        stat_blocks = []
        text_blocks = []
        while not parse_end:
            elem = elem.next()
            if elem.is_(".stat-block-1") or elem.is_("#school")\
                    or elem.is_("#range") or elem.is_("#target"):
                stat_blocks.append(elem)
                continue
            if elem.is_(".stat-block-title") or\
                    elem.is_(".footer"):
                break
            if elem.html() == None:
                continue
            text_blocks.append(elem)
        for block in stat_blocks:
            items = block.find("b, strong").items()
            for item in items:
                label = item.text().strip()
                value_match = re.match(".*?(<b>|<strong>)\s*(?:<a[^>]*>)?\s*%s\s*(?:</a>)?\s*(</b>|</strong>)(?::)?\s*(<span class=\"body-copy-indent-char\">|)?(?P<value>([^(]*\([^)]*\) \[[^;]*|[^(]*\([^)]*\)|[^;]*))" % label, self.stripLinks(block.html()))
                value = value_match.group("value").strip()
                spell_[label] = value
        # Fix Saves:
        def replace(old, new, sdict):
            if old in sdict.keys():
                sdict[new] = sdict[old]
                del(sdict[old])
        replace("SR", "Spell Resistance", spell_)
        replace("Saving throw", "Saving Throw", spell_)
        replace("Save", "Saving Throw", spell_)
        replace("Casting time", "Casting Time", spell_)
        if "Casting" in spell_.keys(): #Visions of Hell
            if spell_["Casting"].strip().startswith("Time"):
                spell_["Casting"] = spell_["Casting"].strip()[4:].strip()
            spell_["Casting Time"] = spell_["Casting"]
            del(spell_["Casting"])
        if "Saving" in spell_.keys():
            if spell_["Saving"].strip().startswith("Throw"):
                spell_["Saving"] = spell_["Saving"].strip()[5:].strip()
            spell_["Saving Throw"] = spell_["Saving"]
            del(spell_["Saving"])

        if "Saving Throw" in spell_.keys():
            spell_["Saving Throw"] = re.sub("(<.*|;.*)","",spell_["Saving Throw"]).strip()
        if "School" in spell_.keys():
            school_match = re.search("(?P<school>[^ ]*)(?: \(\s*(?:<.*?>)?\s*(?P<subschool>[^)]*?)\s*(?:<.*?>)?\s*\))?(?: \[(?P<descriptors>[^\]]*)\])?",  spell_['School']);
            spell['school'] = school_match.group("school").lower().replace(":","").capitalize()
            spell['subschool'] = school_match.group("subschool")
            spell['descriptors'] = school_match.group("descriptors")
        if "Components" in spell_.keys() or "Component" in spell_.keys():
            clist = spell_["Components"] if "Components" in spell_.keys() else spell_["Component"]
            if "(" in clist:
                component_match = re.match("(?P<clist>[^(]*)\((?P<mtext>[^)]*)\)", clist)
                clist = component_match.group("clist")
                spell["material_text"] = component_match.group("mtext")
            clist = clist.replace("/",",")
            for component in [c.strip() for c in clist.split(',')]:
                if component.startswith('M'):
                    spell['material'] = True
                elif component == 'V':
                    spell['verbal'] = True
                elif component == 'S':
                    spell['somatic'] = True
                elif component == 'AF':
                    spell['arcane_focus'] = True
                elif component == 'DF':
                    spell['divine_focus'] = True
        sourceTargetDict = {
                            "Casting Time": "cast_time",
                            "Range": "range",
                            "Area": "area",
                            "Effect": "effect",
                            "Target": "target",
                            "Targets": "target",
                            "Target/Effect": "target",
                            "Target or Area": "target",
                            "Target or Targets": "target",
                            "Target, Effect, or Area": "target",
                            "Target, Effect, Area": "target",
                            "Area or Target": "target",
                            "Duration": "duration",
                            "Spell Resistance": "spell_res",
                            "Saving Throw": "save"
                        }
        for s, t in sourceTargetDict.items():
            self.addStat(spell_, spell, s, t)
        # Check if other labels are recognized:
        known_labels = ["School", "Component", "Components", "Level"] + list(sourceTargetDict.keys())
        for l in known_labels:
            if l in spell_.keys():
                del spell_[l]
        if list(spell_.keys()):
            print(spell_name, spell_.keys())
            sys.exit(1)
        spell['text'] = "".join(["<p>%s</p>" % self.stripLinks(p.html()) for p in text_blocks])
        spell['name'] = spell_name
        spell['rulebook'] = ispell['rulebook']
        spell['system'] = "Pathfinder"
        spell['classes'] = ispell['classes']
        if not spell['text']:
            print("EMPTYTEXT %s" % spell)
            sys.exit(1)
        return spell


    def listSpellIndex(self):
        index = pq(filename=self.base_url + self.root)
        self.short2book = {classItem.find("input").attr("id")[:-9]: classItem.find("label").text() for classItem in index.find(".shortcut-bar").eq(0).find('span').items()}
        mapping_a = [(index.find("#%s" % a.attr("for")).attr("value"),a.text().replace("\xa0", " ")) for a in index.find(".shortcut-bar").eq(1).children().children('label').items()]
        mapping = []

        for l,c in mapping_a:
            if '/' in c:
                for c2 in c.split("/"):
                    mapping.append((l,c2))
            else:
                mapping.append((l,c))
        for link, name in mapping:
            print(name)
            for level in range(10):
                spell_tuples = [(spell.find("a").eq(0).text(),spell.find("a").eq(0).attr("href"), self.getBook(spell))  for spell in index.find(".link-%s.link-%s-level" % (link,level)).children("li").items()]
                for spell_name, spell_link, spell_rulebook in spell_tuples:
                    if spell_name == "Detect Chaos/Evil/Good/Law":
                        spell_tuples.append(("Detect Chaos", "/pathfinderRPG/prd/spells/detectChaos.html#detect-chaos", "Core Rulebook"))
                        spell_tuples.append(("Detect Evil", "/pathfinderRPG/prd/spells/detectEvil.html#detect-evil", "Core Rulebook"))
                        spell_tuples.append(("Detect Good", "/pathfinderRPG/prd/spells/detectGood.html#detect-good", "Core Rulebook"))
                        spell_tuples.append(("Detect Law", "/pathfinderRPG/prd/spells/detectLaw.html#detect-law", "Core Rulebook"))
                        continue
                    if spell_name == "Dispel Chaos/Evil/Good/Law":
                        spell_tuples.append(("Dispel Chaos", "/pathfinderRPG/prd/spells/dispelChaos.html", "Core Rulebook"))
                        spell_tuples.append(("Dispel Evil", "/pathfinderRPG/prd/spells/dispelEvil.html", "Core Rulebook"))
                        spell_tuples.append(("Dispel Good", "/pathfinderRPG/prd/spells/dispelGood.html", "Core Rulebook"))
                        spell_tuples.append(("Dispel Law", "/pathfinderRPG/prd/spells/dispelLaw.html", "Core Rulebook"))
                        continue
                    if spell_name == "Magic Circle against Chaos/Evil":
                        spell_tuples.append(("Magic Circle against Chaos", "/pathfinderRPG/prd/spells/magicCircleAgainstChaos.html", "Core Rulebook"))
                        spell_tuples.append(("Magic Circle against Evil", "/pathfinderRPG/prd/spells/magicCircleAgainstEvil.html", "Core Rulebook"))
                        continue
                    if spell_name == "Magic Circle against Chaos/Evil/Good/Law":
                        spell_tuples.append(("Magic Circle against Chaos", "/pathfinderRPG/prd/spells/magicCircleAgainstChaos.html", "Core Rulebook"))
                        spell_tuples.append(("Magic Circle against Evil", "/pathfinderRPG/prd/spells/magicCircleAgainstEvil.html", "Core Rulebook"))
                        spell_tuples.append(("Magic Circle against Good", "/pathfinderRPG/prd/spells/magicCircleAgainstGood.html", "Core Rulebook"))
                        spell_tuples.append(("Magic Circle against Law", "/pathfinderRPG/prd/spells/magicCircleAgainstLaw.html", "Core Rulebook"))
                        continue
                    spell_link = spell_link.replace("'","\\'").replace(',','\,')
                    id = None
                    if '#' in spell_link:
                        spell_link, id = spell_link.split("#")
                    spell = self.findSpell(spell_name, "Pathfinder", spell_rulebook)
                    if spell_link == "/pathfinderRPG/prd/advancedClassGuide/spells/investigativeMind.html":
                        spell_link = "/pathfinderRPG/prd/advancedClassGuide/spells/investigateMind.html"
                    yield (spell_link, {'name': spell_name,
                            'rulebook': spell_rulebook,
                            'system': "Pathfinder",
                            'classes': [(name, level)],
                            'id': id
                            })

    def postParse(self):
        for spell in self._spells:
            if not 'school' in spell.keys() or not spell['school']:
                if spell['name'].endswith("Communal") or spell['name'].endswith("Mass") or spell['name'].endswith("Greater") or spell['name'].endswith("Lesser") or spell['name'].endswith("Improved"):
                    parent_spell = self.findSpellByName(spell['name'].split(",")[0].strip())
                    spell['school'] = parent_spell['school']
                    if 'subschool' in parent_spell.keys():
                        spell['subschool'] = parent_spell['subschool']
                else:
                    print("ERROR: NO SCHOOL %s" % spell['name'])
                    sys.exit(1)


if __name__ == "__main__":
    PathfinderImporter(sys.argv[1]).save(sys.argv[2])


