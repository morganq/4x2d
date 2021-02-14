import pygame
import game
import text

class TutorialPopup:
    def __init__(self):
        self.elements = []
        self.width = 0
        self.height = 0
        self.running_y = 0
        self.y_offset = 132

    def add_text(self, s):
        words = s.split(" ")
        lines = [""]
        n = 0
        for word in words:
            n += len(word)
            if n >= 30:
                lines.append("")
                n = len(word)
            lines[-1] = lines[-1] + word + " " 

        for i, line in enumerate(lines):
            t = text.Text(line, "small", (0, self.running_y + i * 10), color = game.BGCOLOR, border=False)
            self.width = max(self.width, t.rect[2])
            self.elements.append(t)

        self.height += len(lines) * 10 + 10
        self.running_y += len(lines) * 10 + 10
        
    def build(self):
        pass

    def cleanup(self):
        self.bg.kill()
        for element in self.elements:
            element.kill()

    def initialize(self, scene):
        self.build()
        self.bg = pygame.sprite.Sprite()
        w = self.width + 10
        h = self.height + 20
        x = 120 - w / 2
        y = self.y_offset - h / 2
        self.bg.image = pygame.surface.Surface((w, h))
        self.bg.image.fill((247, 249, 223))
        pygame.draw.rect(self.bg.image, game.BGCOLOR, (1,1,w-2,h-14), 1)
        pygame.draw.rect(self.bg.image, game.BGCOLOR, (1,h-14,w-2,13), 0)
        self.bg.rect = (x, y, w, h)

        scene.tutorial_group.add(self.bg)
        for element in self.elements:
            element.rect = (element.rect[0] + x + 5, element.rect[1] + y + 5, element.rect[2], element.rect[3])
            scene.tutorial_group.add(element)

        t = text.Text("Press Space to continue", "small", (x + w / 2 - 59, y + h - 12), border=False)
        self.elements.append(t)
        scene.tutorial_group.add(t)            
        

class Intro1Tutorial(TutorialPopup):
    def build(self):
        self.add_text("Use the arrow keys to march.")
        self.add_text("Head over to the government building, and occupy it to win.")
        
class Intro2Tutorial(TutorialPopup):
    def build(self):
        self.add_text("Visit each factory to add workers to the march.")
        self.add_text("Every government building must be occupied to win.")

class Intro3Tutorial(TutorialPopup):
    def build(self):
        self.add_text("When you have more than one worker marching, you can not backtrack.")
        self.add_text("So be smart about your path!")

class ExtraFactsTutorial(TutorialPopup):
    def build(self):
        self.add_text("Sometimes, you may not need every worker available to get the job done.")
        self.add_text("Try to find the quickest route!")

class SimplePickerTutorial(TutorialPopup):
    def build(self):
        self.add_text("Here you have to pick a factory to start from.")
        self.add_text("Use the left and right arrow keys to select, then space to choose.")

class IntroPoliceTutorial(TutorialPopup):
    def build(self):
        self.add_text("Police really get in the way, but you can push them around.")

class PoliceLineTutorial(TutorialPopup):
    def build(self):
        self.add_text("A whole line of Police can be pushed, if your forces match theirs.")

class IntroSoldierTutorial(TutorialPopup):
    def build(self):
        self.y_offset = 54
        self.add_text("Soldiers can't be moved, but they can be won over.")
        self.add_text("If there's a worker standing next to each Soldier in a group, you can recruit them all!")

class IntroTowerTutorial(TutorialPopup):
    def build(self):
        self.add_text("Occupy the Cell Tower to briefly gain control over communications.")
        self.add_text("You can then take a single step with each Police and Soldier.")

tutorials = {
    'intro1': Intro1Tutorial,
    'intro2': Intro2Tutorial,
    'intro3': Intro3Tutorial,
    'extrafacts': ExtraFactsTutorial,
    'simplepicker': SimplePickerTutorial,
    'intropolice': IntroPoliceTutorial,
    'policeline': PoliceLineTutorial,
    'introsoldier': IntroSoldierTutorial,
    'introtower': IntroTowerTutorial,
}