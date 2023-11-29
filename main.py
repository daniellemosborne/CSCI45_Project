import pygame
import random
from pygame.locals import *

pygame.init()

clock = pygame.time.Clock()
fps = 30

screen_width = 664
screen_height = 736
ground_height = 665

points = 0
high_score = 0

# game title
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Swamp Run')

# loading fonts
button_font_path = 'game/what.ttf'
button_font = pygame.font.Font(button_font_path, 36)

# speed of scrolling ground
scroll_ground = 0
scroll_speed = 4

# start button and positioning
start_button = pygame.image.load('game/start_button.png')
button_rect = start_button.get_rect(center=(screen_width // 2, screen_height // 2))

# setting up background and scrolling ground
background = pygame.image.load('game/swamp_bg.png')
ground = pygame.image.load('game/swamp_ground.png')

class Troll(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0 # controls the speed of animation
        for num in range(1, 5):
            img = pygame.image.load(f'game/troll{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.initial_y = y  # Store initial y position for reference
        self.on_ground = False
        self.velocity_y = 0  # Y velocity for jumping
        self.jump_power = -15  # Initial strength of the jump
        self.jump_time = 0  # Duration of the jump
        self.max_jump_time = 15  # Maximum duration of the jump
        self.gravity = 1.2  # Adjust to control gravity effect
        self.mask = pygame.mask.from_surface(self.image)
        self.successful_jump = False

    def update(self, scroll):
        # animation update
        self.counter += 1
        troll_cooldown = 6

        if self.counter > troll_cooldown:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.images):
                self.index = 0
        self.image = self.images[self.index]

        # movement update
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            self.rect.x += 13  # Change this value for speed adjustment

        # gravity (jumping)
        if not self.on_ground:
            self.velocity_y += self.gravity  # Gravity effect
            self.rect.y += self.velocity_y
            if self.rect.y >= ground_height - self.rect.height:
                self.rect.y = ground_height - self.rect.height
                self.velocity_y = 0
                self.on_ground = True
                self.jump_power = -15  # Reset jump power when troll touches the ground

        # move troll guy along with the scrolling ground
        self.rect.x -= scroll

    def jump(self):
        # Start the jump when spacebar is pressed
        if self.on_ground:
            self.on_ground = False

        # Increase the jump power based on jump duration
        if self.jump_time < self.max_jump_time:
            self.velocity_y = self.jump_power + (self.jump_time / 2)
            self.jump_time += 1
        else:
            self.jump_time = 0
            self.jump_power = -15  # Reset jump power after reaching max jump duration

    def collide_boulder(self, boulder):
        return self.rect.colliderect(boulder.rect)

class Boulder(pygame.sprite.Sprite):
    def __init__(self, x, y, is_large=False):
        pygame.sprite.Sprite.__init__(self)
        # adding larger boulder
        if is_large:
            self.original_image = pygame.image.load('game/boulder_large.png')
        else:
            self.original_image = pygame.image.load('game/boulder.png')
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.topleft = [x, y]
        self.initial_x = x  # Store initial x position for reference
        self.angle = 0  # Initial angle for rotation

        # creating a mask for the irregular shape of boulder
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, scroll):
        # simulate rolling boulder towards troll
        self.rect.x -= 8  # Adjust this value for speed adjustment
        if self.rect.right < 0:  # Reset the boulder's position if it goes off-screen
            self.rect.x = self.initial_x

        # rotate the boulder image gradually to simulate rolling
        self.angle += 5  # Adjust this value to control the rotation speed
        rotated_image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = rotated_image.get_rect(center=self.rect.center)
        self.image = rotated_image

        # update the mask
        self.mask = pygame.mask.from_surface(self.image)

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('game/coin.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = [x, y]
        self.mask = pygame.mask.from_surface(self.image)

# define coin creation
def create_coin():
    x = screen_width + random.randint(100, 300)  # Random x-coordinate within visible area
    y = 600  # Fixed y-coordinate
    return Coin(x, y)

# boulder creation
max_boulders = 1
active_boulders = 0
boulder_creating = False

def create_new_boulder():
    global last_boulder_time, boulder_creating, active_boulders  # Store the last time a boulder was created
    current_time = pygame.time.get_ticks()
    if current_time - last_boulder_time > 7000 and active_boulders < max_boulders:  # Create a new boulder every 7 secs
        if not boulder_creating:
            is_large = random.choice([True, False])
            if is_large:
                new_boulder = Boulder(650, 485, is_large)
            else:
                new_boulder = Boulder(650, 561, is_large)
            boulder_group.add(new_boulder)
            last_boulder_time = current_time  # Update the last boulder creation time
            boulder_creating = True
            active_boulders += 1

def remove_offscreen_boulders():
    global active_boulders
    for boulder in boulder_group:
        if boulder.rect.right < 0:
            boulder_group.remove(boulder)
            active_boulders -= 1

# group creation and object instances

# boulders
boulder_group = pygame.sprite.Group()
rolling_boulder = Boulder(650, 561)  # Place the boulder outside the left edge
boulder_group.add(rolling_boulder)

# troll character
troll_group = pygame.sprite.Group()
running = Troll(100, 400)
troll_group.add(running)

# coins
coin_group = pygame.sprite.Group()

run = True
game_over = False
game_started = False

last_boulder_time = pygame.time.get_ticks()
boulder_creating = False

screen.blit(background, (0,0))
screen.blit(ground, (0,0))

# game loop
while run:

    clock.tick(fps)

    create_new_boulder()
    remove_offscreen_boulders()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                running.jump()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if button_rect.collidepoint(mouse_pos):
                game_started = True

    if game_started:

        # update troll guy and boulders
        troll_group.update(scroll_speed)
        boulder_group.update(scroll_speed)

        # check for collisions with boulders
        for boulder in boulder_group:
            if pygame.sprite.collide_mask(running, boulder):
                game_over = True  # Collision detected based on masks, end the game

        # collecting coins
        for coin in coin_group:
            if pygame.sprite.collide_mask(running, coin):
                coin_group.remove(coin)
                points += 10  # Increase points when Shrek collects a coin

        # checking for high score
        if points > high_score:
            high_score = points

        # limit on coins
        if len(coin_group) < 3:
            new_coin = create_coin()
            coin_group.add(new_coin)

        for coin in coin_group:
            coin.rect.x -= scroll_speed

        screen.blit(background, (0, 0))
        troll_group.draw(screen)
        coin_group.draw(screen)
        boulder_group.draw(screen)

        screen.blit(ground, (scroll_ground, 1))

        # display points
        points_text = button_font.render(f"Points {points}", True, (255, 255, 255))
        screen.blit(points_text, (screen_width - 155, 20))

        screen.blit(ground, (scroll_ground, 1))
        scroll_ground -= scroll_speed
        if abs(scroll_ground) > 35:
            scroll_ground = 0

        if game_over:
            # display game over
            font = pygame.font.Font(button_font_path, 48)
            text = font.render("GAME OVER!", True, (79, 114, 42))
            screen.blit(text, (210, screen_height / 2))
            pygame.display.flip()

            # display high score
            text_surface = font.render(f"HIGH SCORE: {high_score}", True, (79, 114, 42))
            screen.blit(text_surface, (190, screen_height / 2.35))
            pygame.display.flip()

            # delay the window closing
            pygame.time.delay(6000)
            run = False  # exit the game loop

    if not game_started:
        screen.blit(start_button, button_rect)

    pygame.display.update()

pygame.quit()

