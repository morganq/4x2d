#import queue
#import threading

import traceback

import game
#import radio
import save

#q = queue.Queue()
#music_thread = threading.Thread(target=radio.run_radio, args=[q])
#music_thread.daemon = True
#music_thread.start()
s = save.Save()
g = game.Game(s)
g.run()
#q.put("exit")
