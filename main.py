import pygame as py
from sys import exit
from math import *
import math

py.init()

boss = py.image.load("boss1.png")
boss_rect = boss.get_rect(center=(300, 300))

# Constants
HEIGHT = 600
WIDTH = 600
FPS = 120

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Load player image
player1 = py.image.load("normalsmall.png")
playernum = 1
player1_rect = player1.get_rect()
player1_rect.center = (WIDTH // 2, HEIGHT // 2)
right = True

# Load weapon image
weapon = py.image.load("weapon.png")
weapon_rect = weapon.get_rect()
dis_x, dis_y = py.mouse.get_pos()

# Load slash animation
slash1 = py.image.load("slash1.png")
slash2 = py.image.load("slash2.png")
slash_size = (120, 120)
slash1 = py.transform.scale(slash1, slash_size)
slash2 = py.transform.scale(slash2, slash_size)
degs = 0

slashed = False

# Scale the player and weapon images
player_size = (80, 80)  # Adjust player size here
player = py.transform.scale(player1, player_size)
weapon_size = (50, 50)  # Adjust weapon size here
weapon = py.transform.scale(weapon, weapon_size)

# Set up the display
screen = py.display.set_mode((WIDTH, HEIGHT))
clock = py.time.Clock()

bossslash1 = py.image.load("Bossslash1.png")
bossslash2 = py.image.load("Bossslash2.png")

def boss1move():
    global boss_rect, player1_rect, slashed

    # Calculate movement towards player
    dx = player1_rect.centerx - boss_rect.centerx
    dy = player1_rect.centery - boss_rect.centery
    distance = math.hypot(dx, dy)

    if distance > 0:
        boss_rect.x += dx / distance  # Adjust speed as needed
        boss_rect.y += dy / distance  # Adjust speed as needed

def boss1atk():
    global boss_rect, player1_rect, bossslash1, bossslash2, slashed

    # Calculate the distance between boss and player
    dx = boss_rect.centerx - player1_rect.centerx
    dy = boss_rect.centery - player1_rect.centery
    distance = math.hypot(dx, dy)

    if not slashed and distance <= 100:  # Check if the boss can slash
        # Display the slash animation
        
        bossslash1 = py.transform.scale(bossslash1, (100, 100))
        bossslash2 = py.transform.scale(bossslash2, (100, 100))

        angle = atan2(dy, dx)
        angle = degrees(angle)
        angle += 225.3           

        rotated_slash = py.transform.rotate(bossslash1, -angle)
        screen.blit(rotated_slash, player1_rect)
        py.display.flip()
        py.time.delay(100)  # Delay for 100 milliseconds

        rotated_slash = py.transform.rotate(bossslash2, -angle)
        screen.blit(rotated_slash, player1_rect)  # Display slash2 at player's position
        py.display.flip()
        py.time.delay(100)  # Delay for 100 milliseconds

        slashed = True  # Set slashed flag to True
    else:
        slashed = False

def move():
    global player, player1_rect, playernum, right
    keys = py.key.get_pressed()
    move_speed = 2

    if keys[py.K_a]:
        if playernum == 1:  # Only flip the player image if it's the normal image
            player = py.image.load("movesmall.png")  # Change to the moving image
            if right == True:
                player = py.transform.flip(player, True, False)  # Flip the image
                right = False
            playernum = 2
        else:
            player = py.image.load("normalsmall.png")
            playernum = 1
        player1_rect.x -= move_speed
    if keys[py.K_d]:
        player1_rect.x += move_speed
        if playernum == 1:
            player = py.image.load("movesmall.png")  # Change to the moving image
            playernum = 2
            right = True
        else:
            player = py.image.load("normalsmall.png")
            playernum = 1
    if keys[py.K_w]:
        player1_rect.y -= move_speed
        if playernum == 1:
            player = py.image.load("movesmall.png")  # Change to the moving image
            playernum = 2
        else:
            player = py.image.load("normalsmall.png")
            playernum = 1
    if keys[py.K_s]:
        player1_rect.y += move_speed
        if playernum == 1:
            player = py.image.load("movesmall.png")  # Change to the moving image
            playernum = 2
        else:
            player = py.image.load("normalsmall.png")
            playernum = 1

    if not any(keys):  # If no keys are pressed, revert to the normal image
        player = py.image.load("normalsmall.png")
        playernum = 1

    if keys[py.K_a]:
        player = py.transform.flip(player, True, False)

    player1_rect = player.get_rect(center=player1_rect.center)

def update_weapon_position():
    global weapon_rect
    x1, y1 = player1_rect.x + 88, player1_rect.y + 88
    dx = dis_x - x1 + 30
    dy = dis_y - y1 + 40
    rads = atan2(-dy, dx)
    rads %= 2 * pi
    degs = degrees(rads)

    weapon_offset = 120  # Adjust this value to change the distance of the weapon from the player
    weapon_x = x1 + cos(radians(degs)) * weapon_offset
    weapon_y = y1 - sin(radians(degs)) * weapon_offset  # Negative sin because y increases downward

    weapon_rect.center = (weapon_x, weapon_y)
    return degs

def slash_animation():
    global slash1, slash2, weapon_rect, degs

    original_weapon_rect = weapon_rect.copy()  # Store the original weapon position

    dx = dis_x - (player1_rect.centerx)
    dy = dis_y - (player1_rect.centery)
    angle = atan2(dy, dx)
    angle = degrees(angle)
    angle += 45.3           

    rotated_slash = py.transform.rotate(slash1, -angle)
    weapon_rect = rotated_slash.get_rect(center=weapon_rect.center)

    screen.blit(rotated_slash, weapon_rect)
    py.display.flip()
    py.time.delay(100)  # Adjust the delay as needed for animation speed

    rotated_slash = py.transform.rotate(slash2, -angle)
    weapon_rect = rotated_slash.get_rect(center=weapon_rect.center)

    screen.blit(rotated_slash, weapon_rect)
    py.display.flip()
    py.time.delay(100)

    # Restore the original weapon position
    weapon_rect = original_weapon_rect

# Main game loop
running = True
while running:
    clock.tick(FPS)

    # Event handling
    for event in py.event.get():
        if event.type == py.QUIT:
            running = False
        if event.type == py.MOUSEBUTTONDOWN:
            slash_animation()

    # Player movement
    move()

    # Update weapon position
    dis_x, dis_y = py.mouse.get_pos()
    update_weapon_position()

    boss1move()
    boss1atk()

    # Drawing
    screen.fill(WHITE)
    screen.blit(player, player1_rect)
    screen.blit(weapon, weapon_rect)
    screen.blit(boss, boss_rect)  # Draw boss at updated position

    # Update display
    py.display.flip()

# Quit the game
py.quit()
exit()