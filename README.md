# pySpellbook
A PDF spellbook creation utility in python

## What is it?
Do you play a spellcaster in a d20 like game? Chances are, that you do 
not know all your spells and effects by heart. This software lets you 
browse, filter and organize your spells and choose a selection of spells
to generate a pdf version of the spellbook for printing and looking awesome
at the table.

## Previews

| <img src="https://christofsteel.github.io/pySpellbook/images/all/allplay-0.png" height=250px/> | <img src="https://christofsteel.github.io/pySpellbook/images/all/allplay-1.png" height=250px/> | <img src="https://christofsteel.github.io/pySpellbook/images/all/allplay-2.png" height=250px/> |
|---|---|---|
| <img src="https://christofsteel.github.io/pySpellbook/images/all/allplay-6.png" height=250px/> | <img src="https://christofsteel.github.io/pySpellbook/images/all/allplay-7.png" height=250px/> | <img src="https://christofsteel.github.io/pySpellbook/images/all/allplay-8.png" height=250px/> |

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
You can install `pyspellbook` from the [AUR] (http://aur.archlinux.org)

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
Either by [hand] (https://github.com/christofsteel/pySpellbook/wiki/generateDatasets), or import a dataset through the wizard or download it here:

* PRD [Download] (https://christofsteel.github.io/pySpellbook/datasets/pfrpg-20150914.json)
* DPRD \[German\] [Download] (https://christofsteel.github.io/pySpellbook/datasets/pfrpg_ger-20150914.json)
* D20SRD [Download] (https://christofsteel.github.io/pySpellbook/datasets/d20srd-20150928.json)

## Licenses
The text of every license can be found under LICENSES.
 * PySpellbook (c) 2015 Christoph Stahl is licensed under the [Apache 2.0 license] (https://christofsteel.github.io/pySpellbook/LICENSE.txt).
 * Feather and Quill from the PySpellbook icon (c) Adrian Park, from The Noun Project are licensed under [CC BY 3.0] (https://christofsteel.github.io/pySpellbook/LICENSES/cc-by-3.0.txt).
 * The font "Humanitic" (c) 1998 by George Williams is licensed under the [SIL Open Font License] (https://christofsteel.github.io/pySpellbook/LICENSES/SIL%20Open%20Font%20Lincense.txt).
 * Floral Decorations (http://www.freevector.com/floral-decoration-graphics/) (c) artshare.ru licensed under [CC BY 3.0] (https://christofsteel.github.io/pySpellbook/LICENSES/cc-by-3.0.txt).
 * Free Vector Ornaments (c) http://www.vectorian.net with permission to use without limitations
 * The "Pathfinder PRD" (c) 2002-2015 Paizo, Inc. is licensed under the [Open Game License 1.0a] (https://christofsteel.github.io/pySpellbook/LICENSES/Open%20Game%20License%201.0a.txt).

Since the windows binary builds also include the libraries used:
 * Python 3.4 (c) 2001-2015 Python Software Foundation is licensed under the [PSF License] (https://christofsteel.github.io/pySpellbook/LICENSES/psf-license.txt).
 * PySide and Qt (c) 2015 The Qt Company are licensed under the [LGPL 2.1] (https://christofsteel.github.io/pySpellbook/LICENSES/lgpl-2.1.txt).
 * Appdirs (c) 2010 ActiveState Software Inc. is licensed under the [MIT License] (https://christofsteel.github.io/pySpellbook/LICENSES/mit.txt).
 * SQLAlchemy (c) 2005-2015 the SQLAlchemy authors and contributors is licensed under the [MIT License] (https://christofsteel.github.io/pySpellbook/LICENSES/mit.txt).
 * Jinja2 (c) 2009 by the Jinja Team is licensed under the [BSD License] (https://christofsteel.github.io/pySpellbook/LICENSES/bsd.txt).
 * Weasyprint (c) 2011-2014 by Simon Sapin and contributors is licensed under the [BSD License] (https://christofsteel.github.io/pySpellbook/LICENSES/bsd.txt).
 * PyQuery (C) 2008 - Olivier Lauzanne is licensed under the [BSD License] (https://christofsteel.github.io/pySpellbook/LICENSES/bsd.txt).
