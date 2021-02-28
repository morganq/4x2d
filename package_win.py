import os

NAME = "HostileQuadrant"
CONTENTS = "dist\\%s" % NAME

os.system("rmdir /Q /S dist")
os.system('pyinstaller -w -n %s -i assets\\icon_2_256.ico main.py' % NAME)
os.system("mkdir %s\\assets" % CONTENTS)
os.system("mkdir %s\\levels" % CONTENTS)
os.system("cp assets\\*.png %s\\assets\\" % CONTENTS)
os.system("cp assets\\*.ttf %s\\assets\\" % CONTENTS)
os.system("cp assets\\*.wav %s\\assets\\" % CONTENTS)
os.system("cp assets\\*.ogg %s\\assets\\" % CONTENTS)
os.system("cp -r levels\\*.csv %s\\levels\\" % CONTENTS)