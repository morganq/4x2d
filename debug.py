import pygame
import text
import math
from v2 import V2

def debug_render(screen, scene):
    surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    for ship in scene.get_ships():
        if ship.chosen_target:
            pygame.draw.line(surf, (0,255,0, 120), (ship.pos + V2(1,1)).tuple(), (ship.chosen_target.pos + V2(1,1)).tuple())
        if ship.effective_target:
            pygame.draw.line(surf, (255,128,255, 120), ship.pos.tuple(), ship.effective_target.pos.tuple())
            if hasattr(ship, "state"):
                text.FONTS['tiny'].render_to(surf, (ship.pos + V2(5,5)).tuple(), ship.state, (255,128,255,120))
            if hasattr(ship, "current_dogfight_target") and ship.current_dogfight_target:
                pygame.draw.line(surf, (255,0,0, 120), ship.pos.tuple(), ship.current_dogfight_target.pos.tuple())
        
        #velmag = (ship.velocity.magnitude() * 20) ** 0.75
        #pygame.draw.line(surf, (255,255,0, 120), ship.pos.tuple(), (ship.pos + ship.velocity.normalized() * velmag).tuple())

        #velmag = (ship.target_velocity.magnitude() * 20) ** 0.75
        #pygame.draw.line(surf, (255,128,0, 120), ship.pos.tuple(), (ship.pos + ship.target_velocity.normalized() * velmag).tuple())

        #velmag = (ship.fleet_forces.magnitude() * 20) ** 0.75
        #pygame.draw.line(surf, (128,128,255, 120), ship.pos.tuple(), (ship.pos + ship.fleet_forces.normalized() * velmag).tuple())        

            
    #for planet in scene.get_civ_planets(scene.enemy.civ):
    #    text.FONTS['tiny'].render_to(surf, (planet.pos + V2(-15,15)).tuple(), str(planet.ships['alien-fighter']) + " fighters", (255,128,255,120))
            

    #surf.set_alpha(50)
    screen.blit(surf, (0,0))