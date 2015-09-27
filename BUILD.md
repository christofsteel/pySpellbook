How to build and distribute
===========================

Linux
-----

### Pypi

        git pull
        rm dist/*
        python setup.py sdist
        twine upload dist/*

### Ubuntu (14.04)

        git pull
        rm -rf src/pySpellbook.egg-info
        pip3 install --user -e ,
        python3 setup.py --command-packages=stdeb.command bdist_deb
        mkdir tmp
        cd tmp
        dpkg-source -x ../deb_dist/pyspellbook_<VERSION>-1.dsc
        cd pyspelllbook-<VERSION>
        sed -i 's/unstable/trusty/' debian/changelog # Change this, if compiling for different Ubuntu version
        debuild -S -sa
        cd ..
        dput ppa:/christofsteel/pyspellbook pyspellbook_<VERSION>-1_source.changes

### Archlinux

        git pull # The AUR Package
        vim PKGBUILD # Replace old version number with new one
        makepkg -g >> PKGBUILD
        mkscrinfo
        git add PKGBUILD
        git add .SRCINFO
        git commit -m "Version bump from upstream"
        git push

Mac OSX
-------

        git pull
        pip install --user -e .
        rm -rf ~/Library/Python/3.4/lib/python/site-packages/PySide*
        # Install pyside via macports
        python cx.py bdist_dmg

Windows
-------

In Git bash:

        git pull
        
In cmd:

        del src\pySpellbool.egg-info
        pip install --user -e .
        C:\Pthon34\python.exe cx.py bdist_msi
