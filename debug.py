import pygame
import text
from v2 import V2

def debug_render(screen, scene):
    surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    for ship in scene.get_ships():
        if ship.target:
            pygame.draw.line(surf, (255,128,255, 120), ship.pos.tuple(), ship.target.pos.tuple())
            if hasattr(ship, "state"):
                text.FONTS['tiny'].render_to(surf, (ship.pos + V2(5,5)).tuple(), ship.state, (255,128,255,120))
            if hasattr(ship, "current_dogfight_target") and ship.current_dogfight_target:
                pygame.draw.line(surf, (255,0,0, 120), ship.pos.tuple(), ship.current_dogfight_target.pos.tuple())
            
    for planet in scene.get_civ_planets(scene.enemy.civ):
        text.FONTS['tiny'].render_to(surf, (planet.pos + V2(-15,15)).tuple(), str(planet.ships['alien-fighter']) + " fighters", (255,128,255,120))
            

    #surf.set_alpha(50)
    screen.blit(surf, (0,0))