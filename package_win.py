import os

NAME = "HostileQuadrant"
CONTENTS = "dist\\%s" % NAME

os.system("rmdir /Q /S dist")
os.system('pyinstaller -w -n %s -i assets\\icon4x.ico main.py' % NAME)
os.system("mkdir %s\\assets" % CONTENTS)
os.system("mkdir %s\\assets\\buildings" % CONTENTS)
os.system("mkdir %s\\assets\\upgrades" % CONTENTS)
os.system("mkdir %s\\assets\\sounds" % CONTENTS)
os.system("mkdir %s\\levels" % CONTENTS)
os.system("copy assets\\buildings\\*.json %s\\assets\\buildings\\" % CONTENTS)
os.system("copy assets\\upgrades\\*.png %s\\assets\\upgrades\\" % CONTENTS)
os.system("copy assets\\*.png %s\\assets\\" % CONTENTS)
os.system("copy assets\\*.ttf %s\\assets\\" % CONTENTS)
os.system("copy assets\\sounds\\*.wav %s\\assets\\sounds\\" % CONTENTS)
os.system("copy levels\\*.json %s\\levels\\" % CONTENTS)
os.system("copy assets\\*.json %s\\assets\\" % CONTENTS)
os.system("copy assets\\*.txt %s\\assets\\" % CONTENTS)
