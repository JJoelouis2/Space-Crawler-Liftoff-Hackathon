import pygame
import sys
import math
import random
from plant import Pot, Venus, Cactus, Flower
from pygame.locals import USEREVENT

pygame.init()
pygame.display.set_caption("Game of the Century")

from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
    MOUSEBUTTONDOWN,
)

class Hand:

    def __init__(self, satisfication, scareMeter):
        self.satisfication = satisfication
        self.scareMeter = scareMeter
        self.pos = pygame.Vector2(pygame.mouse.get_pos())

        self.image = pygame.image.load(r"assets\hands\hands1.png")
        self.image = pygame.transform.scale(self.image, (75, 75))

    def update(self):
        self.pos.xy = pygame.mouse.get_pos()

    def addSatisfication(self, added):
        self.satisfication = min(100, self.satisfication + added)


# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

background = pygame.transform.scale(
    pygame.image.load(r"assets\spaceship_bg.png").convert(),
    (SCREEN_WIDTH, SCREEN_HEIGHT),
)

table = pygame.transform.scale(pygame.image.load(r"assets\table.png"), (800, 200))
watercan1_image = pygame.image.load(r"assets\watercan\watercan1.png")
watercan1_image = pygame.transform.scale(watercan1_image, (100, 100))
watercan1_rect = watercan1_image.get_rect(topleft=(644, 430))
watercan1_image_active = True
watercan_target_area = pygame.Rect(644, 430, 100, 100)

hands_watercan_image = pygame.image.load(r"assets\hands\hands_watercan1.png")
hands_watercan_image = pygame.transform.scale(hands_watercan_image, (110, 110))
hands_watercan_rect = hands_watercan_image.get_rect()

waterdrop_image = pygame.image.load(r"assets\waterdrop.png")
waterdrop_image = pygame.transform.scale(waterdrop_image, (30, 30))  # adjust size as needed

hand = Hand(50, 0)
holding_watercan = False

# Initializing pots
pot1 = Pot(0, 1)
pot2 = Pot(0, 2)
pot3 = Pot(0, 3)
pot_list = [[pot1, False, 0], [pot2, False, 1], [pot3, False, 2]]
plant_list = ["", "", ""]

pygame.mouse.set_visible(False)

# Timers
clock = pygame.time.Clock
GROWTH_TICK = USEREVENT + 1
pygame.time.set_timer(GROWTH_TICK, 500)

WATERING_ANIMATION = USEREVENT + 2
pygame.time.set_timer(WATERING_ANIMATION, 100)

watering_animation_active = False
watering_frame = 0
watering_images = []
for i in range(1, 7):
    img = pygame.image.load(fr"assets\hands\hands-watering{i}.png")
    img = pygame.transform.scale(img, (110, 110))
    watering_images.append(img)

running = True
while running:

    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
        elif event.type == QUIT:
            running = False

        elif event.type == GROWTH_TICK:
            for plant in plant_list:
                growthRng = random.randint(1, 3)
                if plant != "" and growthRng == 1:
                    plant.stageChange()

        elif event.type == WATERING_ANIMATION:
            if watering_animation_active:
                if watering_frame < len(watering_images):
                    hand.image = watering_images[watering_frame]
                    watering_frame += 1
                else:
                    hand.image = hands_watercan_image
                    watering_animation_active = False
                    watering_frame = 0

        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                # Planting
                for pot in pot_list:
                    if pot[0].rect.collidepoint(pygame.mouse.get_pos()) and not pot[1]:
                        plant = random.randint(1, 3)
                        pot_number = pot[2]
                        pot[1] = True

                        if plant == 1:
                            new_plant = Venus(0, pot_number + 1)
                            plant_list[pot_number] = new_plant
                        elif plant == 2:
                            new_plant = Cactus(0, pot_number + 1)
                            plant_list[pot_number] = new_plant
                        else:
                            new_plant = Flower(0, pot_number + 1)
                            plant_list[pot_number] = new_plant

                # Harvesting
                for plant in plant_list:
                    if plant != "" and plant.stage == 2:
                        if plant.rect.collidepoint(pygame.mouse.get_pos()):
                            plant_list[plant.potNumber - 1] = ""
                            plant.kill()
                            hand.scareMeter += 1

                # Watering — only triggers once per stage
                if holding_watercan and not watering_animation_active:
                    for plant in plant_list:
                        # After — inflate(x, y) expands the rect by x pixels wide and y pixels tall
                        if plant != "" and plant.rect.inflate(40, 40).collidepoint(pygame.mouse.get_pos()): 
                            if not plant.watered:
                                plant.watered = True
                                watering_animation_active = True
                                watering_frame = 0
                            break

                # Returning watering can to table
                if (not watercan1_image_active) and watercan_target_area.collidepoint(pygame.mouse.get_pos()):
                    watercan1_image_active = True
                    holding_watercan = False
                    watering_animation_active = False
                    hand.image = pygame.image.load(r"assets\hands\hands1.png")
                    hand.image = pygame.transform.scale(hand.image, (75, 75))
                # Picking up watering can
                elif watercan1_rect.collidepoint(pygame.mouse.get_pos()):
                    watercan1_image_active = False
                    holding_watercan = True
                    hand.image = hands_watercan_image

    screen.blit(background, (0, 0))
    screen.blit(table, (0, 400))

    for pot in pot_list:
        screen.blit(pot[0].image, [pot[0].rect.x, pot[0].rect.bottom])

    # Displays plants
    for plant in plant_list:
        if plant != "":
            screen.blit(plant.image, [plant.rect.x, plant.rect.bottom])
            # Show waterdrop if plant needs watering and isn't fully grown
            if not plant.watered and plant.stage < 2:
                screen.blit(waterdrop_image, (plant.rect.x + plant.rect.width // 2 - 25, plant.rect.bottom + 100))

    if watercan1_image_active:
        screen.blit(watercan1_image, watercan1_rect)

    hand.update()
    hands_watercan_rect.topleft = hand.pos
    screen.blit(hand.image, hand.pos)
    pygame.display.flip()

pygame.quit()