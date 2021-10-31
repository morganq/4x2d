import os

NAME = "HostileQuadrant"
CONTENTS = "dist\\%s" % NAME

os.system("rmdir /Q /S dist")
os.system('pyinstaller -w -n %s -i assets\\icon4x.ico main.py' % NAME)
os.system("mkdir %s\\assets" % CONTENTS)
os.system("mkdir %s\\assets\\sounds" % CONTENTS)
os.system("mkdir %s\\levels" % CONTENTS)
os.system("cp assets\\*.png %s\\assets\\" % CONTENTS)
os.system("cp assets\\*.ttf %s\\assets\\" % CONTENTS)
os.system("cp assets\\sounds\\*.wav %s\\assets\\sounds\\" % CONTENTS)
os.system("cp assets\\*.ogg %s\\assets\\" % CONTENTS)
os.system("cp -r levels\\*.csv %s\\levels\\" % CONTENTS)
os.system("cp -r assets\\*.json %s\\" % CONTENTS)
os.system("cp -r assets\\*.txt %s\\" % CONTENTS)
