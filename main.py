import pygame
from game import Game

pygame.init()
screen = pygame.display.set_mode((1200, 800))
pygame.display.set_caption("X-Vector")
clock = pygame.time.Clock()
game = Game(screen)
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        game.update(event)
    game.draw()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()