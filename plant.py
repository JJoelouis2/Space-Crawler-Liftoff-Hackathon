import pygame
import random

class Pot(pygame.sprite.Sprite):
    def __init__(self, stage, potNumber):
        super().__init__()
        # Initializes Image
        self.image = pygame.image.load("assets\PotStage0.png")
        self.image = pygame.transform.scale(self.image, (150, 150))

        random.randint = ()
        self.rect = self.image.get_rect()


        # Starting Position
        self.potNumber = potNumber
        height = 300
        potNumberDict = {1:[80, height], 2:[315, height], 3:[540, height]}
        potPosition = potNumberDict[potNumber]
        self.rect.x = potPosition[0]
        self.rect.bottom = potPosition[1]
    """
    def potVisualChange(stage):
        #Changes the visuals of the pot
        stage_change = {0:"assets\PotStage1.png", 1:"assets\PotStage2.png", 2:"assets\PotStage3.png"}
        self.image = pygame.image.load(stage_change)
    """
"""
class Plant_Venus(pygame.sprite.Sprite):
    def __init__(self, stage):
        # Initalizes sprite class
        super().__init__()
        self.image = pygame.image.load(image).convert()
        self.stage = stage


    def stageChange():

"""

    


        
