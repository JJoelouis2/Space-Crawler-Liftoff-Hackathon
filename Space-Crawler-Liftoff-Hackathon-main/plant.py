import pygame
import random

class Pot(pygame.sprite.Sprite):
    def __init__(self, stage, potNumber):
        super().__init__()
        # Initializes Image
        self.image = pygame.image.load(r"assets\pot\regular_pot.png")
        self.image = pygame.transform.scale(self.image, (150, 150))

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

class Venus(pygame.sprite.Sprite):
    def __init__(self, stage, potNumber):
        # Initalizes sprite class
        super().__init__()
        self.image = pygame.image.load(r"assets\venus\venus1.png")
        #self.image = pygame.transform.scale(self.image, (150, 150))
        self.stage = stage

        self.rect = self.image.get_rect()

        # Starting Position
        self.potNumber = potNumber
        height = 300
        potNumberDict = {1:[110, height], 2:[350, height], 3:[575, height]}
        potPosition = potNumberDict[potNumber]
        self.rect.x = potPosition[0]
        self.rect.bottom = potPosition[1]

    def stageChange(self):

        # Checks if not in last stage
        if self.stage <= 1:
            imageDict = {0:r"assets\venus\venus2.png", 1:r"assets\venus\venus3.png"}
            new_image = imageDict[self.stage] # New image
            self.image = pygame.image.load(new_image)
            self.image = pygame.transform.scale(self.image, (120, 140))

            height = 200
            potNumberDict = {1:[95, height], 2:[335, height], 3:[560, height]}
            potPosition = potNumberDict[self.potNumber]
            self.rect.x = potPosition[0]
            self.rect.bottom = potPosition[1]

            self.stage += 1

class Cactus(pygame.sprite.Sprite):
    def __init__(self, stage, potNumber):
        # Initalizes sprite class
        super().__init__()
        self.image = pygame.image.load(f"assets\cactus\cactus1.png")
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.stage = stage

        self.rect = self.image.get_rect()

        # Starting Position
        self.potNumber = potNumber
        height = 250
        potNumberDict = {1:[110, height], 2:[350, height], 3:[575, height]}
        potPosition = potNumberDict[potNumber]
        self.rect.x = potPosition[0]
        self.rect.bottom = potPosition[1]

    def stageChange(self):
        # Checks if not a max stage
        if self.stage <= 1:
            imageDict = {0:"assets\cactus\cactus2.png", 1:"assets\cactus\cactus3.png"}
            new_image = imageDict[self.stage] # New image
            self.image = pygame.image.load(new_image)
            self.image = pygame.transform.scale(self.image, (100, 180))

            # Adjusts height
            height = 175
            potNumberDict = {1:[110, height], 2:[350, height], 3:[575, height]}
            potPosition = potNumberDict[self.potNumber]
            self.rect.x = potPosition[0]
            self.rect.bottom = potPosition[1]

            self.stage += 1

class Flower(pygame.sprite.Sprite):
    def __init__(self, stage, potNumber):
        # Initalizes sprite class
        super().__init__()
        self.image = pygame.image.load(r"assets\flower\flower1.png")
        #self.image = pygame.transform.scale(self.image, (150, 150))
        self.stage = stage

        self.rect = self.image.get_rect()

        # Starting Position
        self.potNumber = potNumber
        height = 300
        potNumberDict = {1:[110, height], 2:[350, height], 3:[575, height]}
        potPosition = potNumberDict[potNumber]
        self.rect.x = potPosition[0]
        self.rect.bottom = potPosition[1]

    def stageChange(self):
        # Checks if not a max stage
        if self.stage <= 1:
            imageDict = {0:r"assets\flower\flower2.png", 1:r"assets\flower\flower3.png"}
            new_image = imageDict[self.stage] # New image
            self.image = pygame.image.load(new_image)
            self.image = pygame.transform.scale(self.image, (80, 220))

            height = 130
            potNumberDict = {1:[110, height], 2:[350, height], 3:[575, height]}
            potPosition = potNumberDict[self.potNumber]
            self.rect.x = potPosition[0]
            self.rect.bottom = potPosition[1]

            self.stage += 1


