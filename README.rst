pySpellbook
===========

A PDF spellbook creation utility in python

What is it?
-----------

Do you play in a d20 game and play a spellcaster? Chances are, that you
do not know all your spells and effects by heart. This software lets you
choose a selection of spells and generate a pdf version of the
spellbook.

In addition you can browse and filter your spell library by class,
rulebook, school/subschool, descriptor and fulltextsearch.

How to install?
---------------

Simply via

::

    pip install pySpellbook

this will fetch all python dependencies and install the binary
pySpellbook.

Prince
------

pySpellbook uses Prince to render the pdf output. Unfortunately Prince
is not open source software, but free for personal use.

The first run wizard should install Prince on your system, but you can
decide to install it manually from http://www.princexml.com.

If you do not want to use Prince, you can use an internal renderer or
print the intermediate html with your favourite browser (Firefox
recommended), but those have serious drawbacks in terms of support for
printed media css.

How to add spells?
------------------

Either by [hand]
(https://github.com/christofsteel/pySpellbook/wiki/generateDatasets), or
import a dataset available here:

-  Pathfinder PRD [Download]
   (https://christofsteel.github.io/pySpellbook/datasets/pathfinder-20150914.json)
-  Pathfinder DPRD [German] [Download]
   (https://christofsteel.github.io/pySpellbook/datasets/pathfinderDE-20150914.json)
-  D&D 3.5 SRD (to be added)

