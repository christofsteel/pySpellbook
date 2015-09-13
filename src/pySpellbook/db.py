import re
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_
from pySpellbook.models import create_engine, Base, Spell, Rulebook, School, Subschool, D20Class, Level, Descriptor, levels_to_spells, descriptors_to_spells

class db:
    def __init__(self, database, debug=False):
        self.engine = create_engine("sqlite:///%s" % database, echo=debug)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.database = database
        Base.metadata.create_all(self.engine)

    def clear(self):
        Base.metadata.drop_all(bind=self.engine)
        Base.metadata.create_all(self.engine)


    def list_system_names(self):
        return self.session.query(Rulebook.system).distinct().all()

    def list_rulebooks(self, system):
        return self.session.query(Rulebook).filter(Rulebook.system == system).distinct().all()

    def list_all_rulebooks(self):
        return self.session.query(Rulebook).all()

    def get_rulebook(self, name, system):
        return self.session.query(Rulebook)\
            .filter(Rulebook.name == name, Rulebook.system == system).all()

    def del_rulebook_if_empty(self, rulebook, commit=True):
        if self.count_spells(rulebook=rulebook) == 0:
            self.session.delete(rulebook)
            if commit:
                self.session.commit()
            return True
        return False

    def count_rulebooks(self):
        return self.session.query(Rulebook).count()

    def list_schools(self):
        return self.session.query(School).all()

    def count_schools(self):
        return self.session.query(School).count()

    def del_school_if_empty(self, school, commit=False):
        if self.count_spells(school=school) == 0:
            self.session.delete(school)
            if commit:
                self.session.commit()
            return True
        return False

    def list_subschools(self):
        return self.session.query(Subschool).all()

    def count_subschools(self):
        return self.session.query(Subschool).count()

    def del_subschool_if_empty(self, subschool, commit=False):
        if self.count_spells(subschool=subschool) == 0:
            self.session.delete(subschool)
            if commit:
                self.session.commit()
            return True
        return False

    def list_d20classes(self):
        return self.session.query(D20Class).all()

    def count_d20classes(self):
        return self.session.query(D20Class).count()

    def del_d20class_if_empty(self, d20class, commit=True):
        if self.count_levels(d20class) == 0:
            self.session.delete(d20class)
            if commit:
                self.session.commit()
            return True
        return False

    def list_levels(self, d20class):
        return self.session.query(Level).filter(Level.d20class == d20class).all()

    def count_levels(self, d20class):
        return self.session.query(Level).filter(Level.d20class == d20class).count()

    def del_level_if_empty(self, level, commit=True):
        d20class = level.d20class
        if self.count_spells(level=level) == 0:
            self.session.delete(level)
            self.del_d20class_if_empty(d20class, False)
            if commit:
                self.session.commit()
            return True
        return False

    def list_descriptors(self):
        return self.session.query(Descriptor).all()

    def count_descriptors(self):
        return self.session.query(Descriptor).count()

    def del_descriptor_if_empty(self, descriptor, commit=False):
        if self.count_spells(descriptor=descriptor) == 0:
            self.session.delete(descriptor)
            if commit:
                self.session.commit()
            return True
        return False


    def get_spells_for_level_d20class(self, level, d20class):
        #query = self.session.query(Spell).join(levels_to_spells, and_(levels_to_spells.c.spell_name == Spell.name, levels_to_spell.c.rulebook_name == Spell.rulebook_name, levels_to_spell.c.))
        query = self.session.query(Spell).join(levels_to_spells).join(Level).filter(Level.level == level.level, Level.d20class == d20class).all()
        return query

    def get_spell_by_nr(self, nr, name=None, system=None, rulebook=None, d20class=None,
                   level=None, school=None, subschool=None):
        query = self.session.query(Spell)
        if not name is None:
            query = query.filter(Spell.name == name)
        if not system is None:
            query = query.filter(Spell.rulebook.system == system)
        if not rulebook is None:
            query = query.filter(Spell.rulebook == rulebook)
        if not d20class is None:
            query = query.filter(Spell.levels.any(d20class = d20class))
        if not level is None:
            query = query.filter(Spell.levels.any(and_(Level.level == level.level, Level.d20class == level.d20class)))
        if not school is None:
            query = query.filter(Spell.school == school)
        if not subschool is None:
            query = query.filter(Spell.subschool == subschool)
        s = query.offset(nr).limit(1).one()
        return s

    def get_spell(self, name, system, rulebook):
        spell = self.session.query(Spell).filter(Spell.name == name, Spell.rulebook_name == rulebook, Spell.system_name == system).first()
        return spell

    def count_spells(self, name=None, system=None, rulebook=None, d20class=None,
                   level=None, school=None, subschool=None, descriptor=None):
        query = self.session.query(Spell).join(levels_to_spells).join(Level).join(descriptors_to_spells).join(Descriptor)
        if not name is None:
            query = query.filter(Spell.name == name)
        if not system is None:
            query = query.filter(Spell.rulebook.system_name == system)
        if not rulebook is None:
            query = query.filter(Spell.rulebook == rulebook)
        if not d20class is None:
            query = query.filter(Level.d20class == d20class)
        if not level is None:
            query = query.filter(Level.level == level.level, Level.d20class == level.d20class)
        if not school is None:
            query = query.filter(Spell.school == school)
        if not school is None:
            query = query.filter(Spell.school == school)
        if not subschool is None:
            query = query.filter(Spell.subschool == subschool)
        if not descriptor is None:
            query = query.filter(Descriptor.name == descriptor.name)
        return len(query.distinct().all())


    def get_spells(self, name=None, system=None, rulebook=None, d20class=None,
                   level=None, school=None, subschool=None):
        query = self.session.query(Spell).join(levels_to_spells).join(Level)
        if not name is None:
            query = query.filter(Spell.name == name)
        if not system is None:
            query = query.filter(Spell.rulebook.system_name == system)
        if not rulebook is None:
            query = query.filter(Spell.rulebook == rulebook)
        if not d20class is None:
            query = query.filter(Level.d20class == d20class)
        if not level is None:
            query = query.filter(Level.level == level.level, Level.d20class == level.d20class)
        if not school is None:
            query = query.filter(Spell.school == school)
        if not subschool is None:
            query = query.filter(Spell.subschool == subschool)
        return query.distinct().all()


    def del_spell(self, spell):
        # Manual cascading detetion
        # Not pretty, but works
        levels = spell.levels
        rulebook = spell.rulebook
        school = spell.school
        subschool = spell.subschool
        descriptors = spell.descriptors
        self.session.delete(spell)
        for level in levels:
            self.del_level_if_empty(level, False)
        self.del_rulebook_if_empty(rulebook, False)
        if not school is None:
            self.del_school_if_empty(school, False)
        if not subschool is None:
            self.del_subschool_if_empty(subschool, False)
        for descriptor in descriptors:
            self.del_descriptor_if_empty(descriptor, False)
        self.session.commit()


    def fix_spell_dict(self, spell_dict):
        keys = [ "name",
                "rulebook",
                "system",
                "classes",
                "descriptors",
                "school",
                "subschool",
                "verbal",
                "somatic",
                "material",
                "arcane_focus",
                "divine_focus",
                "xp_costs",
                "cast_time",
                "spell_range",
                "effect",
                "area",
                "target",
                "duration",
                "save",
                "spell_res",
                "short_text",
                "text"]
        for key in keys:
            if not key in spell_dict.keys():
                spell_dict[key] = None
        return spell_dict

    def generate_spell(self, spell_dict, origspell=None):
            spell_dict = self.fix_spell_dict(spell_dict)
            rulebook = self.get_rulebook(spell_dict["rulebook"], spell_dict["system"])
            if not rulebook:
                rulebook = Rulebook(spell_dict["rulebook"], spell_dict["system"])
            else:
                rulebook = rulebook[0]

            levels = []
            for d20class_name, level_level in spell_dict['classes']:
                level_level = int(level_level)
                d20class = self.session.query(D20Class).filter(D20Class.name == d20class_name).first()
                if not d20class:
                    d20class = D20Class(d20class_name)
                level = self.session.query(Level).filter(Level.d20class == d20class, Level.level == level_level).first()
                if not level:
                    level = Level(level_level, d20class)
                levels.append(level)
            descriptors = []
            if type(spell_dict['descriptors']) == str:
                #strip all Links:
                spell_dict['descriptors'] = re.sub("<.*?>", "", spell_dict['descriptors'])
                spell_dict['descriptors'] = spell_dict['descriptors'].replace(" or ", ",")
                spell_dict['descriptors'] = [d.strip().replace(" ","-").capitalize() for d in spell_dict['descriptors'].split(",")]
            if spell_dict['descriptors']:
                for descriptor_name in spell_dict['descriptors']:
                    if descriptor_name.startswith("See-text"):
                        descriptor_name = "see text"
                    if descriptor_name:
                        descriptor = self.session.query(Descriptor).filter(Descriptor.name == descriptor_name).first()
                        if not descriptor:
                            descriptor = Descriptor(descriptor_name)
                        descriptors.append(descriptor)

            if spell_dict['school']:
                school = self.session.query(School).filter(School.name == spell_dict['school']).first()
                if not school:
                    school = School(spell_dict['school'])
            else:
                school = None

            if spell_dict['subschool']:
                subschool = self.session.query(Subschool).filter(Subschool.name == spell_dict['subschool']).first()
                if not subschool:
                    subschool = Subschool(spell_dict['subschool'])
            else:
                subschool = None

            spell = None
            if origspell:
                spell = origspell
            else:
                spell = Spell()

            spell.name = spell_dict['name']
            spell.rulebook = rulebook
            spell.levels = levels
            spell.descriptors = descriptors
            spell.school = school
            spell.subschool = subschool
            spell.verbal = spell_dict['verbal']
            spell.somatic = spell_dict['somatic']
            spell.material = spell_dict['material']
            spell.arcane_focus = spell_dict['arcane_focus']
            spell.divine_focus = spell_dict['divine_focus']
            spell.xp_costs = spell_dict['xp_costs']
            spell.cast_time = spell_dict['cast_time']
            spell.spell_range = spell_dict['spell_range']
            spell.area = spell_dict['area']
            spell.target = spell_dict['target']
            spell.effect = spell_dict['effect']
            spell.duration = spell_dict['duration']
            spell.save = spell_dict['save']
            spell.spell_res = spell_dict['spell_res']
            spell.text_short = spell_dict['short_text']
            if "material_text" in spell_dict:
                spell_dict["text"] = "".join([spell_dict["text"], "<p><i>Material Component/Focus:</i> %s</p>" % spell_dict["material_text"]])
            spell.text = spell_dict['text']
            return spell

    def delete_empty(self):
        for descriptor in self.list_descriptors():
            if not descriptor.spells:
                self.session.delete(descriptor)
        for d20class in self.list_d20classes():
            for level in d20class.levels:
                if not level.spells:
                    self.session.delete(level)
            self.session.commit()
            if not d20class.levels:
                self.session.delete(d20class)
        for school in self.list_schools():
            if not school.spells:
                self.session.delete(school)
        for subschool in self.list_subschools():
            if not subschool.spells:
                self.session.delete(subschool)
        for rulebook in self.list_all_rulebooks():
            if not rulebook.spells:
                self.session.delete(rulebook)


    def add_spell_dicts(self, spell_dict_list):
        for s in spell_dict_list:
            self.add_spell_dict(s, False)
        self.delete_empty()
        self.session.commit()

    def add_spell_dict(self, spell_dict, commit=True):
        dbspell = self.get_spell(name = spell_dict['name'], rulebook = spell_dict['rulebook'], system = spell_dict['system'])
        spell = self.generate_spell(spell_dict, dbspell)
        self.session.add(spell)
        if commit:
            self.delete_empty()
            self.session.commit()

    def add_spell(self, spell):
        self.session.add(spell)
        self.session.commit()

