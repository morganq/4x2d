import os

NAME = "HostileQuadrant"
CONTENTS = "dist/%s.app/Contents/MacOS" % NAME

os.system("rm -rf ./dist")
os.system("pyinstaller -w -n \"%s\" -i assets/icon4x.icns --osx-bundle-identifier com.example.test main.py" % NAME)
os.system("mkdir %s/assets" % CONTENTS)
os.system("mkdir %s/assets/buildings" % CONTENTS)
os.system("mkdir %s/assets/upgrades" % CONTENTS)
os.system("mkdir %s/assets/sounds" % CONTENTS)
os.system("mkdir %s/levels" % CONTENTS)
os.system("cp assets/*.png %s/assets/" % CONTENTS)
os.system("cp assets/buildings/*.json %s/assets/buildings/" % CONTENTS)
os.system("cp assets/upgrades/*.png %s/assets/upgrades/" % CONTENTS)
os.system("cp assets/sounds/*.wav %s/assets/sounds/" % CONTENTS)
os.system("cp assets/*.ttf %s/assets/" % CONTENTS)
os.system("cp assets/*.wav %s/assets/" % CONTENTS)
os.system("cp assets/*.ogg %s/assets/" % CONTENTS)
os.system("cp levels/*.json %s/levels/" % CONTENTS)
os.system("cp assets/*.json %s/assets/" % CONTENTS)
os.system("cp assets/*.txt %s/assets/" % CONTENTS)
