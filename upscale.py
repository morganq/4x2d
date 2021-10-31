import pygame
import xbrz


def xbr(surf, factor):
    buf2 = xbrz.scale(bytearray(pygame.image.tostring(surf,"RGBA")), factor, surf.get_width(), surf.get_height(), xbrz.ColorFormat.RGB)
    surf = pygame.image.frombuffer(buf2, (surf.get_width() * factor, surf.get_height() * factor), "RGBX")
    return surf

def pixel(surf, factor):
    return pygame.transform.scale(surf, (surf.get_width() * factor, surf.get_height() * factor))
