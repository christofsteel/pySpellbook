from sqlalchemy import Column, Boolean, Integer, String, create_engine, ForeignKey, Table, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy

Base = declarative_base()

class Rulebook(Base):
    __tablename__ = "rulebook"
    name = Column(String, primary_key=True)
    system = Column(String, primary_key=True)
    shortname = Column(String)
    third_party = Column(Boolean)

    def __repr__(self):
        return "Rulebook(%s, %s, %s, %s)" % (self.name,
                                             self.shortname,
                                             self.system,
                                             "3rd" if self.third_party else "1st")

    def __str__(self):
        return self.name

    def __init__(self, name, system, shortname=None, third_party=False):
        self.name = name
        self.system = system
        self.third_party = third_party
        if shortname is None:
            self.shortname = ''.join([c[0] for c in name.split()])
        else:
            self.shortname = shortname


class D20Class(Base):
    __tablename__ = "d20class"
    name = Column(String, primary_key=True)

    def __repr__(self):
        return "D20Class(%s)" % self.name

    def __str__(self):
        return self.name

    def __init__(self, name):
        self.name = name

class Level(Base):
    __tablename__ = "level"
    level = Column(Integer, primary_key=True)
    d20class_name = Column(String, ForeignKey("d20class.name"), primary_key=True)
    d20class = relationship("D20Class", backref="levels")

    def __repr__(self):
        return "Level(%d, %s)" % (self.level, self.d20class_name)

    def __str__(self):
        return "%s %d" % (self.d20class_name, self.level)

    def __init__(self, level, d20class):
        self.level = level
        self.d20class = d20class


class School(Base):
    __tablename__ = "school"
    name = Column(String, primary_key=True)

    def __repr__(self):
        return "School(%s)" % self.name

    def __str__(self):
        return self.name

    def __init__(self, name):
        self.name = name

class Subschool(Base):
    __tablename__ = "subschool"
    name = Column(String, primary_key=True)

    def __repr__(self):
        return "Subschool(%s)" % self.name

    def __str__(self):
        return self.name

    def __init__(self, name):
        self.name = name

class Descriptor(Base):
    __tablename__ = "descriptor"
    name = Column(String, primary_key=True)

    def __repr__(self):
        return "Descriptor(%s)" % self.name

    def __str__(self):
        return self.name

    def __init__(self, name):
        self.name = name

class Spell(Base):
    __tablename__ = "spell"
    name = Column(String, primary_key=True)
    school_name = Column(String, ForeignKey('school.name'))
    school = relationship("School", backref='spells')
    rulebook_name = Column(String, primary_key=True)
    system_name = Column(String, primary_key=True)
    rulebook = relationship("Rulebook", backref="spells")
    page = Column(Integer)
    levels = relationship("Level", primaryjoin="and_(Spell.name == levels_to_spells.c.spell_name, Spell.rulebook_name == levels_to_spells.c.rulebook_name, Spell.system_name == levels_to_spells.c.system_name)",
                          secondaryjoin="and_(levels_to_spells.c.level_level == Level.level, levels_to_spells.c.d20class_name == Level.d20class_name)",
                          secondary="levels_to_spells", backref="spells")
    school_name = Column(String, ForeignKey("school.name"))
    school = relationship("School", backref="spells")
    subschool_name = Column(String, ForeignKey("subschool.name"))
    subschool = relationship("Subschool", backref="spells")
    descriptors = relationship("Descriptor", secondary="descriptors_to_spells", backref="spells")

    verbal = Column(Boolean)
    somatic = Column(Boolean)
    material = Column(Boolean)
    arcane_focus = Column(Boolean)
    divine_focus = Column(Boolean)
    xp_costs = Column(Boolean)

    cast_time = Column(String)
    spell_range = Column(String)
    area = Column(String)
    effect = Column(String)
    target = Column(String)
    duration = Column(String)

    save = Column(String)
    spell_res = Column(String)

    text = Column(String)
    text_short = Column(String)

    __table_args__ = ( ForeignKeyConstraint(['rulebook_name', 'system_name'],
                                            ['rulebook.name', 'rulebook.system']),)

descriptors_to_spells = Table('descriptors_to_spells', Base.metadata,
                         Column('spell_name', String),
                         Column('rulebook_name', String),
                         Column('system_name', String),
                         Column('descriptor_name', String, ForeignKey("descriptor.name")),
                         ForeignKeyConstraint(['spell_name', 'rulebook_name', 'system_name'],
                                               ['spell.name', 'spell.rulebook_name', 'spell.system_name']))

levels_to_spells = Table('levels_to_spells', Base.metadata,
                         Column('spell_name', String),
                         Column('rulebook_name', String),
                         Column('system_name', String),
                         Column('level_level', Integer),
                         Column('d20class_name', String),
                         ForeignKeyConstraint(['spell_name', 'rulebook_name', 'system_name'],
                                               ['spell.name', 'spell.rulebook_name', 'spell.system_name']),
                         ForeignKeyConstraint(['level_level', 'd20class_name'],
                                               ['level.level', 'level.d20class_name']))

