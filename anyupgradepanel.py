from panel import Panel
from upgrade import upgrades, upgradeicon
from v2 import V2
from colors import *
from text import Text

class AnyUpgradePanel(Panel):
    def __init__(self, pos, onclick):
        super().__init__(pos, None)

        ups = {}
        for cat in ['buildings', 'ships', 'tech']:
            ups[cat] = {}
            for res in ['iron', 'ice', 'gas']:
                ups[cat][res] = {}

        for uc in upgrades.UPGRADE_CLASSES.values():
            if uc.alien:
                continue
            f = ups[uc.category][uc.resource_type]
            ft = uc.family['tree']
            if ft in f:
                f[ft].append(uc)
            else:
                f[ft] = [uc]

        for ci,cat in enumerate(ups.keys()):
            category = ups[cat]
            self.add(Text(cat, "big", V2(ci * 180 + 10, 5), PICO_WHITE), V2(ci * 180 + 10, 5))
            y = 25
            for res in category.keys():
                resource = category[res]
                self.add(Text(res, "small", V2(ci * 180 + 10, y), PICO_WHITE), V2(ci * 180 + 10, y))
                y += 10
                for fam in ups[cat][res]:
                    family = resource[fam]
                    x = 0
                    for up in sorted(family, key=lambda x:int("".join([i for i in x.name if i.isdigit()]))):
                        self.add(
                            upgradeicon.UpgradeIcon(V2(ci * 180 + 10 + x, y), up.name, tooltip=True, onclick=onclick),
                            V2(ci * 180 + 10 + x, y)
                        )
                        x += 25
                    y += 25
                y += 10    

        self.redraw()

    def position_nicely(self, scene):
        self.pos = V2(10,10) 
        self._reposition_children()