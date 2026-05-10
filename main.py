import pygame
import sys
import math
import random
from plant import Pot, Venus, Cactus, Flower
from pygame.locals import USEREVENT
import time

pygame.init()
pygame.mixer.init()
pygame.display.set_caption("Crybabies Garden")
print("Mixer init:", pygame.mixer.get_init())
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

# constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Timers
clock = pygame.time.Clock()

# Jumpscare Stats
jumpscare_active = False
jumpscare_start = 0

# Shake stats
shake_active = False
shake_start = 0

# Background flash stats
bg_flash_active = False
bg_flash_start = 0
bg_flash_show_scary = False
bg_flash_next_toggle = 0

BG_FLASH_SCARE_THRESHOLD = 17
BG_FLASH_RNG_TARGET = 9
BG_FLASH_MIN_INTERVAL = 0.03  # seconds
BG_FLASH_MAX_INTERVAL = 0.2   # seconds

# Glitch effect stats
glitch_active = False
glitch_start = 0


GLITCH_SCARE_THRESHOLD = 0

# Blackout event stats
blackout_active = False
blackout_start = 0
blackout_spiders = []

BLACKOUT_SCARE_THRESHOLD = 11
BLACKOUT_RNG_TARGET = 6
BLACKOUT_SPIDER_COUNT_MIN = 4
BLACKOUT_SPIDER_COUNT_MAX = 7

# High-scare planting chance
SCARY_PLANT_SCARE_THRESHOLD = 12
SCARY_PLANT_CHANCE = 0.35

class Spider:
    def __init__(self):
        self.frames = [
            pygame.transform.scale(pygame.image.load(r"assets\spider-walking1.png"), (80, 60)),
            pygame.transform.scale(pygame.image.load(r"assets\spider-walking2.png"), (80, 60)),
        ]
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, 160))
        self.spawn_time = time.time()
        self.last_anim_swap = self.spawn_time
        self.last_wander_update = self.spawn_time
        self.vx = random.uniform(-220, 220)
        self.vy = random.uniform(-180, 180)

    def update(self, dt):
        now = time.time()

        if now - self.last_anim_swap > 0.1:
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]
            self.last_anim_swap = now

        # Re-randomize often so spider looks chaotic.
        if now - self.last_wander_update > random.uniform(0.04, 0.14):
            self.vx = random.uniform(-320, 320)
            self.vy = random.uniform(-260, 260)
            self.last_wander_update = now

        self.rect.x += int(self.vx * dt)
        self.rect.y += int(self.vy * dt)

        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.vx *= -1
            self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - self.rect.width))
        if self.rect.top < 40 or self.rect.bottom > 360:
            self.vy *= -1
            self.rect.y = max(40, min(self.rect.y, 360 - self.rect.height))
        

class Hand:
    def __init__(self, satisfication, scareMeter):
        self.satisfication = satisfication
        self.scareMeter = scareMeter
        self.pos = pygame.Vector2(pygame.mouse.get_pos())

        # Hand Image
        self.default_image = pygame.transform.scale(
            pygame.image.load(r"assets\hands1.png"), (75, 75)
        )
        self.spider_image = pygame.transform.scale(
            pygame.image.load(r"assets\hands-spider.png"), (75, 75)
        )
        self.watercan_image = pygame.transform.scale(
            pygame.image.load(r"assets\hands\hands-watering1.png"), (110, 110)
        )
        self.mode = "default"
        self.image = self.default_image

    def update(self):
        self.pos.xy = pygame.mouse.get_pos()

    def addSatisfication(self, added):
        self.satisfication = min(100, self.satisfication + added)

    def set_mode(self, mode):
        self.mode = mode
        if mode == "spider":
            self.image = self.spider_image
        elif mode == "watercan":
            self.image = self.watercan_image
        else:
            self.image = self.default_image

    """
    def handVisualChange(stage):
        #Changes the visuals of the pot
        stage_change = {0:"assets\hands1.png", 1:"assets\hands2.png", 2:"assets\hands3.png"}
        self.image = pygame.image.load(stage_change)
        self.image = pygame.transform.scale(self.image, (150, 150))
    """

def trigger_jumpscare():
    global jumpscare_active, jumpscare_start
    jumpscare_active = True
    jumpscare_start = time.time()

def draw_jumpscare():
    elapsed = time.time() - jumpscare_start
    # Flash by toggling every 0.1s
    if int(elapsed / 0.1) % 2 == 0:
        screen.fill((255, 0, 0))  # Red flash
        # Draw random rectangles for chaos effect
        import random
        for nothing in range(10):
            x = random.randint(0, 750)
            y = random.randint(0, 550)
            pygame.draw.rect(screen, (255, 255, 255), (x, y, 50, 50))

def trigger_shake():
    global shake_active, shake_start
    shake_active = True
    shake_start = time.time()

def get_shake_offset(elapsed, intensity=20):
    fade = max(0, 1 - elapsed / SHAKE_DURATION)
    x = random.randint(-intensity, intensity) * fade
    y = random.randint(-intensity, intensity) * fade
    return int(x), int(y)

def draw_glitch_effect():
    # Random displacement pass to create tearing/jitter.
    glitch_frame = screen.copy()
    screen.blit(glitch_frame, (random.randint(-14, 14), random.randint(-8, 8)))

    # Static bars and scanline-like artifacts.
    static_layer = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    for _ in range(random.randint(10, 18)):
        bar_y = random.randint(0, SCREEN_HEIGHT - 4)
        bar_h = random.randint(2, 10)
        alpha = random.randint(45, 120)
        shade = random.randint(140, 255)
        pygame.draw.rect(
            static_layer,
            (shade, shade, shade, alpha),
            (0, bar_y, SCREEN_WIDTH, bar_h),
        )

    # RGB split streaks for chromatic glitch feel.
    for _ in range(random.randint(4, 8)):
        streak_y = random.randint(0, SCREEN_HEIGHT - 3)
        streak_h = random.randint(1, 4)
        width = random.randint(180, SCREEN_WIDTH)
        start_x = random.randint(0, SCREEN_WIDTH - width)
        pygame.draw.rect(static_layer, (255, 0, 0, 110), (start_x - 3, streak_y, width, streak_h))
        pygame.draw.rect(static_layer, (0, 255, 255, 110), (start_x + 3, streak_y, width, streak_h))

    screen.blit(static_layer, (0, 0))

def trigger_blackout():
    global blackout_active, blackout_start, blackout_spiders
    blackout_active = True
    blackout_start = time.time()
    blackout_spiders = []

    for _ in range(random.randint(BLACKOUT_SPIDER_COUNT_MIN, BLACKOUT_SPIDER_COUNT_MAX)):
        swarm_spider = Spider()
        swarm_spider.rect.center = (
            random.randint(40, SCREEN_WIDTH - 40),
            random.randint(70, 330),
        )
        blackout_spiders.append(swarm_spider)

def apply_mad_growth_if_ready(plant):
    if not getattr(plant, "mad_growth_pending", False) or plant.stage < 2:
        return

    if isinstance(plant, Venus):
        plant.image = pygame.image.load(r"assets\venus\venusmad.png")
        plant.image = pygame.transform.scale(plant.image, (120, 140))
    elif isinstance(plant, Cactus):
        plant.image = pygame.image.load(r"assets\cactus\cactusmad.png")
        plant.image = pygame.transform.scale(plant.image, (100, 180))
    elif isinstance(plant, Flower):
        plant.image = pygame.image.load(r"assets\flower\flowermad.png")
        plant.image = pygame.transform.scale(plant.image, (80, 220))

    plant.mad_growth_pending = False

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

background = pygame.transform.scale(
    pygame.image.load(r"assets\spaceship_bg.png").convert(),
    (SCREEN_WIDTH, SCREEN_HEIGHT),
)
flash_background = pygame.transform.scale(
    pygame.image.load(r"assets\Spaceship-Backgroud.png").convert(),
    (SCREEN_WIDTH, SCREEN_HEIGHT),
)

table = pygame.transform.scale(pygame.image.load(r"assets\table\table1.png"), (800, 200))
tableChange = False
hand = Hand((50), 0)
watercan1_image = pygame.transform.scale(
    pygame.image.load(r"assets\watercan\watercan1.png"), (100, 100)
)
watercan1_rect = watercan1_image.get_rect(topleft=(644, 430))
watercan1_image_active = True
watercan_target_area = pygame.Rect(644, 430, 100, 100)
holding_watercan = False
waterdrop_image = None
try:
    waterdrop_image = pygame.transform.scale(pygame.image.load(r"assets\waterdrop.png"), (30, 30))
except pygame.error:
    waterdrop_image = None
watering_animation_active = False
watering_frame = 0
watering_images = []
for i in range(1, 7):
    img = pygame.image.load(fr"assets\hands\hands-watering{i}.png")
    img = pygame.transform.scale(img, (110, 110))
    watering_images.append(img)

spider = None
spider_target_pot = None
venus_needs_spider = [False, False, False]
carrying_spider = False

# Initalizing pots
pot1 = Pot(0, 1)
pot2 = Pot(0, 2)
pot3 = Pot(0, 3)
pot_list = [[pot1, False, 0, False], [pot2, False, 1, False], [pot3, False, 2, False]]
plant_list = ["", "", ""] # Placeholder for numbers

pygame.mouse.set_visible(False)

# Use a subtype so it doesn't collide with other USEREVENT uses
GROWTH_TICK = USEREVENT + 1
SCARY_TICK = USEREVENT + 2
WATERING_ANIMATION = USEREVENT + 3

pygame.time.set_timer(GROWTH_TICK, 1000)  # every 1000 ms push one event
tickScaling = int(1000 - 1000 * (hand.scareMeter)/20) # Scales the tick speed based on scare meter
pygame.time.set_timer(SCARY_TICK, tickScaling)  # every 1000 ms push one event
pygame.time.set_timer(WATERING_ANIMATION, 100)

# Dark overlay
dark_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
dark_overlay.fill((0, 0, 0))

# Durations
JUMPSCARE_DURATION = 0.5 * (1 + hand.scareMeter/10)  # seconds
SHAKE_DURATION = 2.0 * (1 + hand.scareMeter/10) # seconds
BG_FLASH_DURATION = 2.0 * (1 + hand.scareMeter/10) # seconds
GLITCH_DURATION = 0.45 * (1 + hand.scareMeter/10) # seconds
BLACKOUT_DURATION = 2.5 * (1 + hand.scareMeter/10)  # seconds


running = True
while running:
    # Makes game darker over time
    dark_overlay.set_alpha(min(180, hand.scareMeter * 10))  # 0 = invisible, 255 = fully black

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
                    if not plant.watered:
                        continue
                    if isinstance(plant, Venus) and plant.stage == 1:
                        # Venus must be fed a spider before final growth.
                        if venus_needs_spider[plant.potNumber - 1]:
                            continue
                    plant.stageChange()
                    apply_mad_growth_if_ready(plant)
                    if plant.stage < 2:
                        plant.watered = False

                    if isinstance(plant, Venus) and plant.stage == 1:
                        pot_idx = plant.potNumber - 1
                        venus_needs_spider[pot_idx] = True
                        if spider is None:
                            spider = Spider()
                            spider.rect.center = (
                                plant.rect.centerx + random.randint(-70, 70),
                                max(80, plant.rect.top - 30),
                            )
                            spider_target_pot = pot_idx
        
        elif event.type == WATERING_ANIMATION:
            if watering_animation_active:
                if watering_frame < len(watering_images):
                    hand.image = watering_images[watering_frame]
                    watering_frame += 1
                else:
                    watering_animation_active = False
                    watering_frame = 0
                    hand.set_mode("watercan")

        # Scary events based on scare meter
        elif event.type == SCARY_TICK:

            scareRng = random.randint(1, 10)
            if (
                hand.scareMeter >= 8
                and scareRng ==6
                and not bg_flash_active
            ):
                bg_flash_active = True
                bg_flash_start = time.time()
                bg_flash_show_scary = True
                bg_flash_next_toggle = time.time() + random.uniform(
                    BG_FLASH_MIN_INTERVAL, BG_FLASH_MAX_INTERVAL
                )
            
            elif (
                hand.scareMeter >= 10
                and scareRng == 7
                and not glitch_active
            ):
                glitch_active = True
                glitch_start = time.time()

            elif (
                hand.scareMeter >= 8
                and scareRng == BLACKOUT_RNG_TARGET
                and not blackout_active
            ):
                trigger_blackout()

            elif hand.scareMeter >= 3 and scareRng == 1 and not tableChange:
                table = pygame.transform.scale(pygame.image.load(r"assets\table\table2.png"), (800, 200))
                # Screen Shaking
                trigger_shake() 
                tableChange = True

            if hand.scareMeter >= 5 and scareRng == 3 and not jumpscare_active:
                # Jumpscare state 5, 3
                trigger_jumpscare()

            elif hand.scareMeter >= 15 and scareRng == 4 and not jumpscare_active:
                # Jumpscare state
                trigger_jumpscare()

            # Baby Pot 1
            elif hand.scareMeter >= 7 and scareRng == 2:
                potNumber = random.randint(0, 2)

                pot = pot_list[potNumber]
                if not pot[3]: # Checks if pot is normal
                    pot[0].image = pygame.image.load(r"assets\pot\baby_pot1.png")
                    pot[0].image = pygame.transform.scale(pot[0].image, (150, 150))
                    trigger_shake()
                    pot[3] = True # Changes pot state to baby pot

            # Baby Pot 2
            elif hand.scareMeter >= 10 and scareRng == 5:
                potNumber = random.randint(0, 2)

                pot = pot_list[potNumber]
                if not pot[3]: # Checks if pot is normal
                    pot[0].image = pygame.image.load(r"assets\pot\baby_pot2.png")
                    pot[0].image = pygame.transform.scale(pot[0].image, (150, 150))
                    trigger_shake()
                    pot[3] = True # Changes pot state to baby pot
            
        # Mouse Clicks
        elif event.type == MOUSEBUTTONDOWN:
            # Left Clicks
            if event.button == 1:
                spider_fed_this_click = False
                if spider and spider_target_pot is not None and not holding_watercan:
                    target_plant = plant_list[spider_target_pot]
                    if (
                        target_plant != ""
                        and isinstance(target_plant, Venus)
                        and spider.rect.collidepoint(pygame.mouse.get_pos())
                    ):
                        carrying_spider = True
                        hand.set_mode("spider")
                        spider = None

                if carrying_spider and spider_target_pot is not None:
                    target_plant = plant_list[spider_target_pot]
                    if (
                        target_plant != ""
                        and isinstance(target_plant, Venus)
                        and target_plant.rect.collidepoint(pygame.mouse.get_pos())
                    ):
                        venus_needs_spider[spider_target_pot] = False
                        target_plant.stageChange()
                        apply_mad_growth_if_ready(target_plant)
                        carrying_spider = False
                        spider_target_pot = None
                        hand.set_mode("default")
                        spider_fed_this_click = True
                        trigger_shake()

                if (not holding_watercan) and (not carrying_spider) and watercan1_image_active and watercan1_rect.collidepoint(pygame.mouse.get_pos()):
                    watercan1_image_active = False
                    holding_watercan = True
                    hand.set_mode("watercan")
                    continue

                if holding_watercan and (not watercan1_image_active) and watercan_target_area.collidepoint(pygame.mouse.get_pos()):
                    watercan1_image_active = True
                    holding_watercan = False
                    watering_animation_active = False
                    watering_frame = 0
                    hand.set_mode("default")
                    continue

                if holding_watercan and not watering_animation_active:
                    watered_this_click = False
                    for plant in plant_list:
                        if plant != "" and plant.rect.inflate(40, 40).collidepoint(pygame.mouse.get_pos()):
                            if not plant.watered:
                                plant.watered = True
                                watering_animation_active = True
                                watering_frame = 0
                            watered_this_click = True
                            break
                    if watered_this_click:
                        continue

                for pot in pot_list:
                    # Hand is touching pot
                    if pot[0].rect.collidepoint(pygame.mouse.get_pos()) and not pot[1]:
                        plant = random.randint(1, 3)
                        scary_spawn = (
                            hand.scareMeter >= SCARY_PLANT_SCARE_THRESHOLD
                            and random.random() < SCARY_PLANT_CHANCE
                        )
                        pot_number = pot[2]
                        pot[1] = True

                        # Add venus
                        if plant == 1:
                            new_plant = Venus(0, pot_number + 1)
                            new_plant.watered = False
                            new_plant.mad_growth_pending = scary_spawn
                            plant_list[pot_number] = new_plant
                            hand.scareMeter += 1
                            
                        # Add Cactus
                        elif plant == 2:
                            new_plant = Cactus(0, pot_number + 1)
                            new_plant.watered = False
                            new_plant.mad_growth_pending = scary_spawn
                            plant_list[pot_number] = new_plant

                        # Add flower
                        else:
                            new_plant = Flower(0, pot_number + 1)
                            new_plant.watered = False
                            new_plant.mad_growth_pending = scary_spawn
                            plant_list[pot_number] = new_plant

                # Harvesting plants
                if not spider_fed_this_click:
                    for plant in plant_list:
                        if plant != "" and plant.stage == 2:
                            # Hand is touching plant
                            if plant.rect.collidepoint(pygame.mouse.get_pos()):
                                harvested_pot_idx = plant.potNumber - 1
                                plant_list[plant.potNumber - 1] = "" # Removes plant from list
                                pot_list[plant.potNumber - 1][1] = False # Allows pots to be replanted
                                plant.kill()
                                venus_needs_spider[harvested_pot_idx] = False
                                if spider_target_pot == harvested_pot_idx:
                                    spider = None
                                    spider_target_pot = None
                                    carrying_spider = False
                                    if holding_watercan:
                                        hand.set_mode("watercan")
                                    else:
                                        hand.set_mode("default")
                                hand.scareMeter += 1

                                # Adds scaling
                                tickScaling = max(350, int(1000 - 1000 * (hand.scareMeter)/20)) # Scales the tick speed based on scare meter
                                pygame.time.set_timer(SCARY_TICK, tickScaling)  # every 1000 ms push one event              
                
    if shake_active:
        elapsed_shake = time.time() - shake_start
        if elapsed_shake < SHAKE_DURATION:
            ox, oy = get_shake_offset(elapsed_shake)
        else:
            shake_active = False
            ox, oy = 0, 0
    else:
        ox, oy = 0, 0

    if bg_flash_active:
        now = time.time()
        if now - bg_flash_start < BG_FLASH_DURATION:
            if now >= bg_flash_next_toggle:
                bg_flash_show_scary = not bg_flash_show_scary
                bg_flash_next_toggle = now + random.uniform(
                    BG_FLASH_MIN_INTERVAL, BG_FLASH_MAX_INTERVAL
                )
            current_background = flash_background if bg_flash_show_scary else background
        else:
            bg_flash_active = False
            current_background = background
    else:
        current_background = background

    dt = clock.get_time() / 1000.0
    if spider:
        spider.update(dt)
        if spider_target_pot is not None:
            target_plant = plant_list[spider_target_pot]
            if target_plant == "" or not isinstance(target_plant, Venus):
                spider = None
                spider_target_pot = None
                carrying_spider = False
                if holding_watercan:
                    hand.set_mode("watercan")
                else:
                    hand.set_mode("default")

    if blackout_active:
        for swarm_spider in blackout_spiders:
            swarm_spider.update(dt)

    screen.blit(current_background, (ox, oy))
    screen.blit(table, (ox, 400 + oy))

    # Displays Pots
    for pot in pot_list:
        screen.blit(pot[0].image, [pot[0].rect.x, pot[0].rect.bottom])
    
    # Displays plants
    for plant in plant_list:
        if plant != "":
            screen.blit(plant.image, [plant.rect.x, plant.rect.bottom])
            if not plant.watered and plant.stage < 2:
                if waterdrop_image:
                    screen.blit(
                        waterdrop_image,
                        (plant.rect.x + plant.rect.width // 2 - 15, plant.rect.bottom + 85),
                    )
                else:
                    pygame.draw.circle(
                        screen,
                        (80, 170, 255),
                        (plant.rect.x + plant.rect.width // 2, plant.rect.bottom + 95),
                        8,
                    )

    if watercan1_image_active:
        screen.blit(watercan1_image, watercan1_rect)

    if spider:
        screen.blit(spider.image, spider.rect)

    if blackout_active:
        for swarm_spider in blackout_spiders:
            screen.blit(swarm_spider.image, swarm_spider.rect)

    # Glitch is active
    if glitch_active:
        if time.time() - glitch_start < GLITCH_DURATION:
            draw_glitch_effect()
        else:
            glitch_active = False

    # Adds dark tint
    screen.blit(dark_overlay, (0, 0))

    if blackout_active:
        if time.time() - blackout_start < BLACKOUT_DURATION:
            blackout_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            blackout_overlay.fill((0, 0, 0, random.randint(190, 245)))
            screen.blit(blackout_overlay, (0, 0))
        else:
            blackout_active = False
            blackout_spiders = []

    if jumpscare_active:
        if time.time() - jumpscare_start < JUMPSCARE_DURATION:
            draw_jumpscare()
        else:
            jumpscare_active = False  # End jumpscare

    hand.update()
    screen.blit(hand.image, hand.pos)
    pygame.display.flip()
    clock.tick(60)
    
pygame.quit()
    
