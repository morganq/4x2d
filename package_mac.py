import os

NAME = "PicketPuzzle"
CONTENTS = "dist/%s.app/Contents/MacOS"

os.system("rm -rf ./dist")
os.system("pyinstaller -w -n %s -i assets/icon_2_256.icns --osx-bundle-identifier com.example.test main.py" % NAME)
os.system("mkdir %s/assets" % CONTENTS)
os.system("mkdir %s/levels" % CONTENTS)
os.system("cp assets/*.png %s/assets/" % CONTENTS)
os.system("cp assets/*.ttf %s/assets/" % CONTENTS)
os.system("cp assets/*.wav %s/assets/" % CONTENTS)
os.system("cp assets/*.ogg %s/assets/" % CONTENTS)
os.system("cp -r levels/*.csv %s/levels/" % CONTENTS)