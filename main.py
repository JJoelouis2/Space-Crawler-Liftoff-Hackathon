import pygame
import sys
import math
from plant import Pot

pygame.init()
pygame.display.set_caption("Game of the Century")

from pygame.locals import (
    K_UP, # up arrow
    K_DOWN, # down arrow
    K_LEFT, # left arrow
    K_RIGHT, # right arrow
    K_ESCAPE, # escape
    KEYDOWN, # key is pressed down
    QUIT, # X button pressed
)

class Hand:
    def __init__(self, satisfication, scareMeter):
        self.satisfication = satisfication
        self.scareMeter = scareMeter
        self.pos = pygame.Vector2(pygame.mouse.get_pos())

        # Hand Image
        self.image = pygame.image.load("assets\hands0.png")
        self.image = pygame.transform.scale(self.image, (150, 150))

    def update(self):
        self.pos.xy = pygame.mouse.get_pos()

    """
    def handVisualChange(stage):
        #Changes the visuals of the pot
        stage_change = {0:"assets\hands1.png", 1:"assets\hands2.png", 2:"assets\hands3.png"}
        self.image = pygame.image.load(stage_change)
        self.image = pygame.transform.scale(self.image, (150, 150))
    """

""" #Potentially makea later
def blit_images(window):
    # Window is the pygame screen
    screen.blit(hand.image, hand.pos)
    screen.blit(stats_panel, (0, 400))
    screen.blit(Pot1, )
"""

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
stats_panel = pygame.Surface((800,200))
stats_panel.fill((255,0,0))

hand = Hand((50), 0)
pot1 = Pot(0, 1)
pot2 = Pot(0, 2)
pot3 = Pot(0, 3)

pygame.mouse.set_visible(False)


running = True
while running:

    for event in pygame.event.get(
    ):  # every user input --> an event. This gets each of the events in a list.
        if event.type == KEYDOWN:
            # Check if the user clicked the escape key
            if event.key == K_ESCAPE:
                running = False
        # The User closed the window
        elif event.type == QUIT:  
            running = False
            
    
    screen.fill((0, 0, 0))
    hand.update()

    screen.blit(hand.image, hand.pos)
    screen.blit(stats_panel, (0, 400))
    screen.blit(pot1.image, [pot1.rect.x, pot1.rect.bottom])
    screen.blit(pot2.image, [pot2.rect.x, pot2.rect.bottom])
    screen.blit(pot3.image, [pot3.rect.x, pot3.rect.bottom])
    
    pygame.display.flip()
    
pygame.quit()
    