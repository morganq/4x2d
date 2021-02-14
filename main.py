import game
import save

s = save.Save()
game.SCALE = s.get_setting("scale")
g = game.Game(s)
g.run()