import math

import pygame

import helper
import text

V2 = pygame.math.Vector2


def debug_render(screen, scene):
    surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    for ship in scene.get_ships():
        p2 = ship.pos + helper.from_angle(ship.angle) * 10
        pygame.draw.line(surf, (255,0,0,180), ship.pos, p2, 1)
        p3 = ship.pos + helper.from_angle(ship.debug_rotation_num / 8 * 6.2818) * 10
        pygame.draw.line(surf, (0,255,0,180), ship.pos, p3, 1)
            
    for planet in scene.get_civ_planets(scene.enemy.civ):
        text.FONTS['tiny'].render_to(surf, (planet.pos + V2(-15,15)), "%s" % sum(planet.ships.values()), (255,128,255,120))


    #text.FONTS['tiny'].render_to(surf, (250, 5), ["feeling safe","in fear"][scene.enemy.fear_attack], (255,128,255,120))
    text.FONTS['tiny'].render_to(surf, (250, 15), "%d ups" % len(scene.enemy.civ.upgrades_stocked), (255,128,255,120))
            

    #surf.set_alpha(50)
    screen.blit(surf, (0,0))
