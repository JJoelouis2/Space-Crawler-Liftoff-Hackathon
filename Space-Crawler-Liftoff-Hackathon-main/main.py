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
JUMPSCARE_DURATION = 0.5  # seconds

# Shake stats
shake_active = False
shake_start = 0
SHAKE_DURATION = 2.0  # seconds

# Background flash stats
bg_flash_active = False
bg_flash_start = 0
bg_flash_show_scary = False
bg_flash_next_toggle = 0
BG_FLASH_DURATION = 2.0  # seconds
BG_FLASH_SCARE_THRESHOLD = 17
BG_FLASH_RNG_TARGET = 9
BG_FLASH_MIN_INTERVAL = 0.03  # seconds
BG_FLASH_MAX_INTERVAL = 0.2   # seconds

# Glitch effect stats
glitch_active = False
glitch_start = 0
GLITCH_DURATION = 0.45  # seconds
GLITCH_SCARE_THRESHOLD = 0

# Blackout event stats
blackout_active = False
blackout_start = 0
blackout_spiders = []
BLACKOUT_DURATION = 2.5  # seconds
BLACKOUT_SCARE_THRESHOLD = 11
BLACKOUT_RNG_TARGET = 6
BLACKOUT_SPIDER_COUNT_MIN = 4
BLACKOUT_SPIDER_COUNT_MAX = 7

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
        self.image = self.default_image

    def update(self):
        self.pos.xy = pygame.mouse.get_pos()

    def addSatisfication(self, added):
        self.satisfication = min(100, self.satisfication + added)

    def set_spider_hand(self, has_spider):
        self.image = self.spider_image if has_spider else self.default_image

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

pygame.time.set_timer(GROWTH_TICK, 1000)  # every 1000 ms push one event
tickScaling = int(1000 - 1000 * (hand.scareMeter)/20) # Scales the tick speed based on scare meter
pygame.time.set_timer(SCARY_TICK, tickScaling)  # every 1000 ms push one event

# Dark overlay
dark_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
dark_overlay.fill((0, 0, 0))

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
                    if isinstance(plant, Venus) and plant.stage == 1:
                        # Venus must be fed a spider before final growth.
                        if venus_needs_spider[plant.potNumber - 1]:
                            continue
                    plant.stageChange()

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

        # Scary events based on scare meter
        elif event.type == SCARY_TICK:

            scareRng = random.randint(1, 10)
            if (
                hand.scareMeter >= BG_FLASH_SCARE_THRESHOLD
                and scareRng == BG_FLASH_RNG_TARGET
                and not bg_flash_active
            ):
                bg_flash_active = True
                bg_flash_start = time.time()
                bg_flash_show_scary = True
                bg_flash_next_toggle = time.time() + random.uniform(
                    BG_FLASH_MIN_INTERVAL, BG_FLASH_MAX_INTERVAL
                )
            
            elif (
                hand.scareMeter >= GLITCH_SCARE_THRESHOLD 
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
                if spider and spider_target_pot is not None:
                    target_plant = plant_list[spider_target_pot]
                    if (
                        target_plant != ""
                        and isinstance(target_plant, Venus)
                        and spider.rect.collidepoint(pygame.mouse.get_pos())
                    ):
                        carrying_spider = True
                        hand.set_spider_hand(True)
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
                        carrying_spider = False
                        spider_target_pot = None
                        hand.set_spider_hand(False)
                        spider_fed_this_click = True
                        trigger_shake()

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
                            hand.scareMeter += 3
                            
                        # Add Cactus
                        elif plant == 2:
                            new_plant = Cactus(0, pot_number + 1)
                            plant_list[pot_number] = new_plant

                        # Add flower
                        else:
                            new_plant = Flower(0, pot_number + 1)
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
                                    hand.set_spider_hand(False)
                                hand.scareMeter += 1

                                # Adds scaling
                                tickScaling = max(200, int(1000 - 1000 * (hand.scareMeter)/20)) # Scales the tick speed based on scare meter
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
                hand.set_spider_hand(False)

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
    