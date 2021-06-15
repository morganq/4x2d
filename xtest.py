import xbrz
import pygame
from PIL import Image
import io

factor = 4

pygame.init()
screen = pygame.display.set_mode((400,400))
s = pygame.image.load("assets/o2-full.png")

print([int(x) for x in s.get_buffer().raw[32:50]], pygame.SRCALPHA)

#s2 = pygame.Surface((s.get_width() * factor, s.get_height() * factor), pygame.SRCALPHA)
buf = bytearray(s.get_buffer().raw)
s2 = pygame.image.frombuffer(xbrz.scale(buf, factor, *s.get_size(), xbrz.ColorFormat.RGBA), (s.get_width() * factor, s.get_height() * factor), "RGBA")

running = True
while running:
    screen.fill((128,128,128,255))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.blit(s2, (0,0))
    pygame.display.update()