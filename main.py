import pygame
import sys
import math
import random
from plant import Pot, Venus, Cactus, Flower
from pygame.locals import USEREVENT

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
    MOUSEBUTTONDOWN,
)

class Hand:
    def __init__(self, satisfication, scareMeter):
        self.satisfication = satisfication
        self.scareMeter = scareMeter
        self.pos = pygame.Vector2(pygame.mouse.get_pos())

        # Hand Image
        self.image = pygame.image.load("assets\hands1.png")
        self.image = pygame.transform.scale(self.image, (75, 75))

    def update(self):
        self.pos.xy = pygame.mouse.get_pos()

    def addSatisfication(self, added):
        self.satisfication = min(100, self.satisfication + added)

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

# constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

background = pygame.transform.scale(
    pygame.image.load(r"assets\spaceship_bg.png").convert(),
    (SCREEN_WIDTH, SCREEN_HEIGHT),
)


table = pygame.transform.scale(pygame.image.load(r"assets\table.png"), (800, 200))

hand = Hand((50), 0)

# Initalizing pots
pot1 = Pot(0, 1)
pot2 = Pot(0, 2)
pot3 = Pot(0, 3)
pot_list = [[pot1, False, 0], [pot2, False, 1], [pot3, False, 2]]
plant_list = ["", "", ""] # Placeholder for numbers

pygame.mouse.set_visible(False)

# Timers
clock = pygame.time.Clock
# Use a subtype so it doesn't collide with other USEREVENT uses
GROWTH_TICK = USEREVENT + 1

pygame.time.set_timer(GROWTH_TICK, 500)  # every 1000 ms push one event

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

        # Changes when plants are grown
        elif event.type == GROWTH_TICK:
            for plant in plant_list:
                growthRng = random.randint(1, 3)
                if plant != "" and growthRng == 1: # See if there is a plant or not
                    plant.stageChange()

        # Mouse Clicks
        elif event.type == MOUSEBUTTONDOWN:
            # Left Clicks
            if event.button == 1:
                for pot in pot_list:
                    # Hand is touching pot
                    if pot[0].rect.collidepoint(pygame.mouse.get_pos()) and not pot[1]:
                        plant = random.randint(1, 3)
                        pot_number = pot[2]
                        pot[1] = True

                        # Add venus
                        if plant == 1:
                            new_plant = Venus(0, pot_number + 1)
                            plant_list[pot_number] = new_plant
                            
                        # Add Cactus
                        elif plant == 2:
                            new_plant = Cactus(0, pot_number + 1)
                            plant_list[pot_number] = new_plant

                        # Add flower
                        else:
                            new_plant = Flower(0, pot_number + 1)
                            plant_list[pot_number] = new_plant

                # Harvesting plants
                for plant in plant_list:
                    if plant != "" and plant.stage == 2:
                        # Hand is touching plant
                        if plant.rect.collidepoint(pygame.mouse.get_pos()):
                            plant_list[plant.potNumber - 1] = "" # Removes plant from list
                            plant.kill()
                            hand.scareMeter += 1
                    
    
    screen.blit(background, (0, 0))

    
    screen.blit(table, (0, 400))

    # Displays Pots
    for pot in pot_list:
        screen.blit(pot[0].image, [pot[0].rect.x, pot[0].rect.bottom])
    

    # Displays plants
    for plant in plant_list:
        if plant != "":
            screen.blit(plant.image, [plant.rect.x, plant.rect.bottom]) 

    hand.update()
    screen.blit(hand.image, hand.pos)
    pygame.display.flip()
    
pygame.quit()
    