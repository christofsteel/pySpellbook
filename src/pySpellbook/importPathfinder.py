from pyquery import PyQuery as pq
import re
import sys
import json

def addStat(source, target, sourceName, targetName):
    if sourceName in source.keys():
        target[targetName] = source[sourceName]
    else:
        target[targetName] = ""

def stripLinks(string):
    return re.sub("<a.*?>","",string).replace("</a>", "")

def replace(string):
    return string.upper().replace(",","").replace(" ", "").replace("/", "").replace("-","").replace("'","")

def findSpell(stuple, s_list):
    for spell in s_list:
        if replace(spell['name']) == replace(stuple[0]) and spell['rulebook']== stuple[2]:
            return spell
    #print("Did not find %s" % stuple[0])

def findSpellByName(name, spell_list):
    for spell in spell_list:
        if replace(spell['name']) == replace(name):
            return spell

def parseSpell(link, rulebook, name, id=None):
    #print(link)
    #print(name)
    spellpage = pq(filename=link)
    if name == "Thunderous Drums":
        name = "Thundering Drums"
    if name == "Banshee Blaste":
        name = "Banshee Blast"
    if name == "Polymorph Any Object":
        spellpage = pq(spellpage.html().replace("<tfoot>","<tfoot></table>"))
    if name == "Longstrider, Greater":
        spellpage = pq(spellpage.html().replace("â\x80©",";"))
        spellpage = pq(spellpage.html().replace("\u2029",";"))
    elem = None
    if id:
        elem = spellpage.find("#%s" % id).eq(0)
    if not elem:
    #    print("Could not find id")
        if name.endswith("Greater"):
            #print("Try Second")
            elem = spellpage.find(".stat-block-title").eq(1)
        if name.endswith("Mass") or name.endswith("Lesser"):
            #print("Try Last")
            elem = spellpage.find(".stat-block-title:last")
        if not elem:
            #print("Try First")
            elem = spellpage.find(".stat-block-title:first")
    assert replace(name) == replace(elem.text())
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
        text_blocks.append(elem)
    for block in stat_blocks:
        items = block.find("b, strong").items()
        for item in items:
            label = item.text().strip()
            value_match = re.match(".*?(<b>|<strong>)\s*(?:<a[^>]*>)?\s*%s\s*(?:</a>)?\s*(</b>|</strong>)(?::)?\s*(<span class=\"body-copy-indent-char\">|)?(?P<value>([^(]*\([^)]*\) \[[^;]*|[^(]*\([^)]*\)|[^;]*))" % label, stripLinks(block.html()))
            value = value_match.group("value").strip()
            spell_[label] = value
    # Fix Saves:
    if "Saving Throw" in spell_.keys():
        spell_["Saving Throw"] = re.sub("(<.*|;.*)","",spell_["Saving Throw"]).strip()
    if "School" in spell_.keys():
        school_match = re.search("(?P<school>[^ ]*)(?: \(\s*(?:<.*?>)?\s*(?P<subschool>[^)]*?)\s*(?:<.*?>)?\s*\))?(?: \[(?P<descriptors>[^\]]*)\])?",  spell_['School']);
        spell['school'] = school_match.group("school").lower().replace(":","").capitalize()
        spell['subschool'] = school_match.group("subschool")
        spell['descriptors'] = school_match.group("descriptors")
    if "Components" in spell_.keys():
        clist = spell_["Components"]
        if "(" in spell_["Components"]:
            component_match = re.match("(?P<clist>[^(]*)\((?P<mtext>[^)]*)\)", spell_["Components"])
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
                spell['AF'] = True
            elif component == 'DF':
                spell['DF'] = True
    sourceTargetDict = {
                        "Casting Time": "cast_time",
                        "Range": "range",
                        "Target": "target",
                        "Duration": "duration",
                        "Spell Resistance": "spell_resistance",
                        "Saving Throw": "saving_throw"
                       }
    for s, t in sourceTargetDict.items():
        addStat(spell_, spell, s, t)
    spell['text'] = "".join(["<p>%s</p>" % p.html() for p in text_blocks])
    #if not "Level" in spell_.keys():
    #    print (spell_)
    #    sys.exit(1)
    #else:
    #    levels = [cl for cl in [s.strip().split(" ") for s in spell_['Level'].split(',')]]
    #    spell['classes'] = []
    #    for level in levels:
    #        if '/' in level[0]:
    #            for d20class in level[0].split("/"):
    #                spell['classes'].append((d20class.capitalize(),level[1]))
    #        else:
    #            spell['classes'].append((level[0].capitalize(), level[1]))
    #if not spell["classes"]:
    #    print (spell_)
    #    print (spell)
    #    sys.exit(1)
    spell['name'] = spell_name
    spell['rulebook'] = rulebook
    spell['system'] = "Pathfinder"
    spell['classes'] = []
    if not spell['text']:
        print("EMPTYTEXT %s" % spell)
        sys.exit(1)
    return spell



"""
index = pq(filename="/home/christoph/vcs/pySpellBook/pathfinder/paizo.com/pathfinderRPG/prd/indices/spells.html")
spells = [(li.attr("class").split(" ")[-1][5:], li.find("a").text(), li.find("a").attr('href')) for li in index.find('#spell-index-wrapper ul li').items()]
short2book = {classItem.find("input").attr("id")[:-9]: classItem.find("label").text() for classItem in index.find(".shortcut-bar").eq(1).find('span').items()}
skip = False
spells_list = []
for spell in spells:
    if spell[1] == "Planar Ally":
        skip = False
    #if spell[1] != "Longstrider, Greater":
    #    skip = True
    #else:
    #    skip = False
    if skip:
        continue
    if spell[1] == "Dimensional" or spell[1] == "Summon Monster Table" or spell[1] == "Summon Nature's Ally Table" or spell[1] == "Greater Command" or spell[1] == "Lesser Restoration":
        continue
    spell_link = spell[2].replace("'","\\'").replace(',','\,')
    id = None
    if '#' in spell_link:
        spell_link, id = spell_link.split("#")
    if spell_link == "/pathfinderRPG/prd/advancedClassGuide/spells/investigativeMind.html":
        spell_link = "/pathfinderRPG/prd/advancedClassGuide/spells/investigateMind.html"
    spells_list.append(parseSpell(base_url+spell_link, short2book[spell[0]], spell[1], id))
"""
#Now fix class/levels...
spells_list=[]
base_url="/home/christoph/vcs/pySpellBook/pathfinder/paizo.com"
index = pq(filename=base_url+"/pathfinderRPG/prd/indices/spelllists.html")
short2book = {classItem.find("input").attr("id")[:-9]: classItem.find("label").text() for classItem in index.find(".shortcut-bar").eq(0).find('span').items()}
mapping_a = [(index.find("#%s" % a.attr("for")).attr("value"),a.text().replace("\xa0", " ")) for a in index.find(".shortcut-bar").eq(1).children().children('label').items()]
mapping = []

for l,c in mapping_a:
    if '/' in c:
        for c2 in c.split("/"):
            mapping.append((l,c2))
    else:
        mapping.append((l,c))

def getBook(li):
    if li.find("a").eq(0).text() == "Ablative Barrier":
        return "Ultimate Combat"
    return short2book[li.attr("class").split(" ")[-1][5:]]

#skip = True
for link, name in mapping:
    print(name)
    for level in range(10):
        spell_tuples = [(spell.find("a").eq(0).text(),spell.find("a").eq(0).attr("href"), getBook(spell))  for spell in index.find(".link-%s.link-%s-level" % (link,level)).children("li").items()]
        for spell_tuple in spell_tuples:
            #if spell_tuple[0] == "Minor Dream":
            #    skip = False
            #else:
            #    skip = True
            #if skip:
            #    continue
            if spell_tuple[0] == "Detect Chaos/Evil/Good/Law":
                spell_tuples.append(("Detect Chaos", "/pathfinderRPG/prd/spells/detectChaos.html#detect-chaos", "Core Rulebook"))
                spell_tuples.append(("Detect Evil", "/pathfinderRPG/prd/spells/detectEvil.html#detect-evil", "Core Rulebook"))
                spell_tuples.append(("Detect Good", "/pathfinderRPG/prd/spells/detectGood.html#detect-good", "Core Rulebook"))
                spell_tuples.append(("Detect Law", "/pathfinderRPG/prd/spells/detectLaw.html#detect-law", "Core Rulebook"))
                continue
            if spell_tuple[0] == "Dispel Chaos/Evil/Good/Law":
                spell_tuples.append(("Dispel Chaos", "/pathfinderRPG/prd/spells/dispelChaos.html", "Core Rulebook"))
                spell_tuples.append(("Dispel Evil", "/pathfinderRPG/prd/spells/dispelEvil.html", "Core Rulebook"))
                spell_tuples.append(("Dispel Good", "/pathfinderRPG/prd/spells/dispelGood.html", "Core Rulebook"))
                spell_tuples.append(("Dispel Law", "/pathfinderRPG/prd/spells/dispelLaw.html", "Core Rulebook"))
                continue
            if spell_tuple[0] == "Magic Circle against Chaos/Evil":
                spell_tuples.append(("Magic Circle against Chaos", "/pathfinderRPG/prd/spells/magicCircleAgainstChaos.html", "Core Rulebook"))
                spell_tuples.append(("Magic Circle against Evil", "/pathfinderRPG/prd/spells/magicCircleAgainstEvil.html", "Core Rulebook"))
                continue
            if spell_tuple[0] == "Magic Circle against Chaos/Evil/Good/Law":
                spell_tuples.append(("Magic Circle against Chaos", "/pathfinderRPG/prd/spells/magicCircleAgainstChaos.html", "Core Rulebook"))
                spell_tuples.append(("Magic Circle against Evil", "/pathfinderRPG/prd/spells/magicCircleAgainstEvil.html", "Core Rulebook"))
                spell_tuples.append(("Magic Circle against Good", "/pathfinderRPG/prd/spells/magicCircleAgainstGood.html", "Core Rulebook"))
                spell_tuples.append(("Magic Circle against Law", "/pathfinderRPG/prd/spells/magicCircleAgainstLaw.html", "Core Rulebook"))
                continue
            spell = findSpell(spell_tuple, spells_list)
            if not spell:
                id = None
                spell_link = spell_tuple[1].replace("'","\\'").replace(',','\,')
                if '#' in spell_link:
                    spell_link, id = spell_link.split("#")
                if spell_link == "/pathfinderRPG/prd/advancedClassGuide/spells/investigativeMind.html":
                    spell_link = "/pathfinderRPG/prd/advancedClassGuide/spells/investigateMind.html"
                spell = parseSpell(base_url+spell_link, spell_tuple[2], spell_tuple[0], id)
                spells_list.append(spell)
            spell['classes'].append((name, level))
# fix Schools and Subschools in Communal, Mass, Greater and Lesser Spells
for spell in spells_list:
    if not 'school' in spell.keys() or not spell['school']:
        if spell['name'].endswith("Communal") or spell['name'].endswith("Mass") or spell['name'].endswith("Greater") or spell['name'].endswith("Lesser") or spell['name'].endswith("Improved"):
            parent_spell = findSpellByName(spell['name'].split(",")[0].strip(), spells_list)
            spell['school'] = parent_spell['school']
            if 'subschool' in parent_spell.keys():
                spell['subschool'] = parent_spell['subschool']
        else:
            print("ERROR: NO SCHOOL %s" % spell['name'])
            sys.exit(1)

with open("pathfinder.json", 'w') as f:
    json.dump(sorted(spells_list, key=lambda spell: spell['name']), f)

