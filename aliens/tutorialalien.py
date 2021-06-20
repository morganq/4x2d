from aliens.alien1 import Alien1
from aliens import alien

class TutorialAlien(Alien1):
    def set_difficulty(self, difficulty):
        self.difficulty = difficulty
        self.civ.base_stats['mining_rate'] = -1

alien.ALIENS['tutorial'] = TutorialAlien