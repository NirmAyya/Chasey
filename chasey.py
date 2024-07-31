import pygame
from pygame import mixer
import math
import random

pygame.init()

# Screen resolution
RES = (800, 600)
screen = pygame.display.set_mode(RES)
pygame.display.set_caption('Chasey')
clock = pygame.time.Clock()

# Fonts
FONT = pygame.font.Font("Chasey/Fonts/arial.ttf", 50)

# Load images
BROWN = pygame.image.load("Chasey/Characters/8bitBrownie.png").convert_alpha()
BROWN = pygame.transform.scale(BROWN, (50, 50))

NIRM_IMAGE = pygame.image.load("Chasey/Characters/8bitNirmR.png").convert_alpha()
NIRM_IMAGE = pygame.transform.scale(NIRM_IMAGE, (50, 100))

GRASS = pygame.image.load('Chasey/objects/background.jpg')
GRASS = pygame.transform.scale(GRASS, RES)

# Load sounds
bark_sound = pygame.mixer.Sound('Chasey/objects/brownieBark.mp3')
footsteps_sound = pygame.mixer.Sound('Chasey/objects/Footsteps.mp3')

# Score
score_value = 0

def update_score():
    global score_value
    score_value += 1
    return FONT.render(f"{score_value}", False, (0, 0, 0))

# Randomizer for movements
def randBool():
    return random.choice([True, False])

# Distance function
def distance(rectA, rectB):
    return math.hypot(rectA.x - rectB.x, rectA.y - rectB.y)

# Play footsteps sound in a loop while the player is moving
def play_footsteps(playing):
    if playing:
        if not pygame.mixer.get_busy():  # Check if any sound is currently playing
            footsteps_sound.play(-1)  # Loop indefinitely
    else:
        footsteps_sound.stop()  # Stop playing

# Play a random bark sound
def play_random_bark():
    if random.random() < 0.01:  # Adjust the probability as needed
        bark_sound.play()

# Enemy sprite class
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = BROWN
        # Random position on the top half of the screen
        self.respawn()
        self.patrol_points = [(200, 200), (600, 200), (600, 400), (200, 400)]
        self.current_point = 0
        self.patrol_speed = 2
        self.flee_speed = 4
        self.state = 'patrolling'
        self.flee_timer = 0
        self.max_flee_time = 120  # Number of frames to flee

    def respawn(self):
        walls = [
            (random.randint(0, RES[0]), 0),                      # Top wall
            (random.randint(0, RES[0]), RES[1]),                  # Bottom wall
            (0, random.randint(0, RES[1])),                      # Left wall
            (RES[0], random.randint(0, RES[1]))                  # Right wall
        ]
        self.rect = self.image.get_rect(center=random.choice(walls))
        
    def update(self, player_rect):
        if self.state == 'patrolling':
            self.patrol()
            if distance(self.rect, player_rect) < 150:  # Distance to switch to flee mode
                self.state = 'fleeing'
                self.flee_timer = self.max_flee_time
        elif self.state == 'fleeing':
            self.flee(player_rect)
            self.flee_timer -= 1
            if self.flee_timer <= 0:
                self.state = 'patrolling'
                
        # If in a corner, respawn at a random wall
        if self.in_corner():
            self.respawn()
            self.state = 'patrolling'
            self.flee_timer = 0

    def patrol(self):
        target = self.patrol_points[self.current_point]
        dx = target[0] - self.rect.centerx
        dy = target[1] - self.rect.centery
        dist = math.hypot(dx, dy)

        if dist > 0:
            dx /= dist
            dy /= dist
        
        self.rect.x += dx * self.patrol_speed
        self.rect.y += dy * self.patrol_speed

        if distance(self.rect, pygame.Rect(*target, 1, 1)) < 5:
            self.current_point = (self.current_point + 1) % len(self.patrol_points)

        self.boundary_check()

    def flee(self, player_rect):
        dx = self.rect.centerx - player_rect.centerx
        dy = self.rect.centery - player_rect.centery
        dist = math.hypot(dx, dy)

        if dist > 0:
            dx /= dist
            dy /= dist
        
        self.rect.x += dx * self.flee_speed
        self.rect.y += dy * self.flee_speed

        self.boundary_check()

    def in_corner(self):
        return (
            (self.rect.left < 10 and self.rect.top < 10) or  # Top-left corner
            (self.rect.right > RES[0] - 10 and self.rect.top < 10) or  # Top-right corner
            (self.rect.left < 10 and self.rect.bottom > RES[1] - 10) or  # Bottom-left corner
            (self.rect.right > RES[0] - 10 and self.rect.bottom > RES[1] - 10)  # Bottom-right corner
        )

    def boundary_check(self):
        self.rect.right = min(self.rect.right, RES[0])
        self.rect.left = max(self.rect.left, 0)
        self.rect.top = max(self.rect.top, 0)
        self.rect.bottom = min(self.rect.bottom, RES[1])

# Initialize player
NirmRect = NIRM_IMAGE.get_rect(topleft=(400, 400))
Nspeed = 2
facing_right = True

# Initialize boss
boss = Enemy()

# Stamina
stamina = 20

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    # Player movement
    player_moving = False
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        NirmRect.y -= Nspeed
        player_moving = True
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        if facing_right:
            NIRM_IMAGE = pygame.transform.flip(NIRM_IMAGE, True, False)
            facing_right = False
        NirmRect.x -= Nspeed
        player_moving = True
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        if not facing_right:
            NIRM_IMAGE = pygame.transform.flip(NIRM_IMAGE, True, False)
            facing_right = True
        NirmRect.x += Nspeed
        player_moving = True
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        NirmRect.y += Nspeed
        player_moving = True
    if keys[pygame.K_SPACE]:
        if stamina > 0:
            Nspeed = 11
            stamina -= 4
        else:
            Nspeed = 2
            stamina += 1

    # Keep player in bounds
    NirmRect.clamp_ip(pygame.Rect(0, 0, RES[0], RES[1]))

    # Control the boss
    boss.update(NirmRect)

    # Check if the player has caught the boss
    if distance(NirmRect, boss.rect) < 25:  # Adjusted to allow for some proximity
        running = False

    # Play footsteps sound if player is moving
    play_footsteps(player_moving)

    # Play random bark sound
    play_random_bark()

    # Draw everything
    screen.blit(GRASS, (0, 0))
    screen.blit(boss.image, boss.rect)
    screen.blit(NIRM_IMAGE, NirmRect)
    pygame.display.update()
    clock.tick(60)

pygame.quit()
