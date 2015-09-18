# pySpellbook
A PDF spellbook creation utility in python

## What is it?
Do you play in a d20 game and play a spellcaster? Chances are, that you 
do not know all your spells and effects by heart. This software lets you 
choose a selection of spells and generate a pdf version of the spellbook.

In addition you can browse and filter your spell library by class, rulebook,
school/subschool, descriptor and fulltextsearch.

## How to install?
### Windows
Download the current release from [Releases] (https://github.com/christofsteel/pySpellbook/releases)

### Mac OSX
Download the current release from [Releases] (https://github.com/christofsteel/pySpellbook/releases)

### Linux (Ubuntu/Debian)
See https://launchpad.net/~christofsteel/+archive/ubuntu/pyspellbook for instructions 
on how to add the PPA to your system. Debian users can pick any release, they contain 
the same files anyway.

### Linux (Archlinux)
You can install `pySpellbook` from the [AUR] (http://aur.archlinux.org)

### Linux (Other)
If you are on linux and have python 3 and pip installed, then install it
via

	pip install pySpellbook

this will fetch all python dependencies and install the binary pySpellbook.

## Prince

pySpellbook uses Prince to render the pdf output. Unfortunately Prince  is
not open source software, but free for personal use. 

The first run wizard should install Prince on your system, but you can decide
to install it manually from http://www.princexml.com.

If you do not want to use Prince, you can use an internal renderer or 
print the intermediate html with your favourite browser (Firefox recommended),
but those have serious drawbacks in terms of support for printed media css.

## How to add spells?
Either by [hand] (https://github.com/christofsteel/pySpellbook/wiki/generateDatasets), or import a dataset available here:

* Pathfinder PRD [Download] (https://christofsteel.github.io/pySpellbook/datasets/pathfinder-20150914.json)
* Pathfinder DPRD \[German\] [Download] (https://christofsteel.github.io/pySpellbook/datasets/pathfinderDE-20150914.json)
* D&D 3.5 SRD (to be added)

## Licenses
The text of every license can be found under LICENSES.
 * PySpellbook (c) 2015 Christoph Stahl is licensed under the Apache 2.0 license.
 * Feather and Quill from the PySpellbook icon (c) Adrian Park, from The Noun Project are licensed under CC BY 3.0 
 * The font "Humanitic" (c) 1998 by George Williams is licensed under the SIL Open Font License.
 * Floral Decorations (http://www.freevector.com/floral-decoration-graphics/) (c) artshare.ru licensed under CC BY 3.0
 * Free Vector Ornaments (c) http://www.vectorian.net with permission to use without limitations
 * The "Pathfinder PRD" (c) 2002-2015 Paizo, Inc. is licensed under the Open Game License 1.0a.

Since the windows binary builds also include the libraries used:
 * Python 3.4 (c) 2001-2015 Python Software Foundation is licensed under the PSL License
 * PySide and Qt (c) 2015 The Qt Company are licensed under the LGPL 2.1
 * Appdirs (c) 2010 ActiveState Software Inc. is licensed under the MIT License
 * SQLAlchemy (c) 2005-2015 the SQLAlchemy authors and contributors is licensed under the MIT License
 * Jinja2 (c) 2009 by the Jinja Team is licensed under the BSD License
 * Weasyprint (c) 2011-2014 by Simon Sapin and contributors is licensed under the BSD License
 * PyQuery (C) 2008 - Olivier Lauzanne is licensed under the BSD License
