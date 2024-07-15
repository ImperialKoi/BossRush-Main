import pygame
import sys
import math
import random

# Load the player image and block image
circle = pygame.image.load('player.png')
block = pygame.image.load('block.png')

# Load enemy images
enemy_img = pygame.image.load('red.png')
enemy_img2 = pygame.image.load('green.png')
enemy_slash1 = pygame.image.load('enemyslash1.png')
enemy_slash2 = pygame.image.load('enemyslash2.png')
enemy_slash3 = pygame.image.load('enemyslash3.png')

bullet_image = pygame.transform.scale(pygame.image.load('frame1.png'), (40, 20))

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 800
screen_height = 700
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Boss Rush")

bullets = []

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Fonts
font = pygame.font.Font(None, 24)

def rotate(image, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    return rotated_image

class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.image = circle
        self.rect = self.image.get_rect()
        self.rect.topleft = [pos_x, pos_y]

        self.attack_animation = False
        self.sprites = []
        self.sprites.append(pygame.image.load('slash1.png'))
        self.sprites.append(pygame.image.load('slash2.png'))
        self.sprites.append(pygame.image.load('slash3.png'))
        self.current_sprite = 0
        self.speed = 0.15  # Animation speed

        self.block_active = False
        self.block_timer = 0
        self.block_offset = (0, 0)  # Offset from player center

        self.flashing = False
        self.flash_timer = 0

        self.health = 100  # Player health
        self.invulnerable = False

        self.boost_active = False
        self.boost_timer = 0
        self.boost_duration = 0.1  # Duration of the speed boost in seconds
        self.boost_multiplier = 5  # Boost multiplier
        self.boost_cooldown = 3

        self.boost_capacity = 100  # Maximum capacity of the boost bar
        self.boost_amount = 0
        self.last_boost_time = 0
        self.bar_precent = 0

    def attack(self):
        if not self.block_active:  # Only trigger attack animation if block is not active
            self.attack_animation = True

    def update(self):
        if self.attack_animation:
            self.current_sprite += self.speed
            if int(self.current_sprite) >= len(self.sprites):
                self.current_sprite = 0
                self.attack_animation = False

        if self.block_active:
            self.block_timer += 1 / 60  # Assuming 60 FPS

        if self.flashing:
            self.flash_timer += 1 / 60  # Assuming 60 FPS
            if self.flash_timer > 1:  # Flash for 1 second
                self.flashing = False
                self.invulnerable = False

        if self.boost_active:
            self.boost_timer += 1 / 60  # Assuming 60 FPS
            if self.boost_timer >= self.boost_duration:
                self.boost_active = False
                self.speed /= self.boost_multiplier  # Revert to normal speed

        if self.boost_amount < self.boost_capacity and not self.boost_active:
            self.boost_amount += 1 / 60

    def move(self, dx=0, dy=0):
        if self.boost_active:
            dx *= self.boost_multiplier  # Apply boost multiplier to movement
            dy *= self.boost_multiplier  # Apply boost multiplier to movement

        if not self.block_active:
            new_x = self.rect.x + dx
            new_y = self.rect.y + dy
            # Check boundaries
            if 0 <= new_x <= screen_width - self.rect.width:
                self.rect.x = new_x
            if 0 <= new_y <= screen_height - self.rect.height:
                self.rect.y = new_y
        elif self.block_active:
            new_x = self.rect.x + dx * 0.5
            new_y = self.rect.y + dy * 0.5
            # Check boundaries
            if 0 <= new_x <= screen_width - self.rect.width:
                self.rect.x = new_x
            if 0 <= new_y <= screen_height - self.rect.height:
                self.rect.y = new_y

    def boost(self):
        current_time = pygame.time.get_ticks() / 1000  # Convert to seconds
        if current_time - self.last_boost_time >= self.boost_cooldown:
            self.boost_active = True
            self.boost_timer = 0
            self.speed *= self.boost_multiplier  # Increase speed
            self.last_boost_time = current_time
            self.boost_amount = 0  # Reset boost amount when activated

    def draw(self, surface):
        # Draw the player
        if not self.flashing or (int(self.flash_timer * 10) % 2 == 0):  # Flash every 0.1 second
            surface.blit(self.image, self.rect.topleft)

        # Draw the attack animation on top of the player, rotated towards the cursor
        if self.attack_animation:
            rotated_image = pygame.transform.rotate(self.sprites[int(self.current_sprite)], self.angle)
            scaled_image = pygame.transform.scale(rotated_image, (rotated_image.get_width() * 2, rotated_image.get_height() * 2))  # Scale by a factor of 2
            offset_x = 50 * math.cos(math.radians(self.angle))
            offset_y = -50 * math.sin(math.radians(self.angle))
            attack_pos = (self.rect.centerx + offset_x - scaled_image.get_width() / 2,
                          self.rect.centery + offset_y - scaled_image.get_height() / 2)
            surface.blit(scaled_image, attack_pos)

        # Draw the block if active
        if self.block_active:
            block_pos = (self.rect.centerx + self.block_offset[0] - block.get_width() / 2,
                         self.rect.centery + self.block_offset[1] - block.get_height() / 2)
            surface.blit(block, block_pos)

        # Draw player health bar
        pygame.draw.rect(surface, WHITE, (10, screen_height - 30, 100, 20))  # Background
        pygame.draw.rect(surface, RED, (10, screen_height - 30, self.health, 20))  # Health bar

        self.bar_precent = self.boost_amount*33.33333
        if self.bar_precent >= 100:
            pygame.draw.rect(surface, BLUE, (10, screen_height - 60, 100, 20))  # Boost bar
            pygame.draw.rect(surface, WHITE, (10, screen_height - 60, self.boost_capacity, 20), 2)  # Outline
        else:
            pygame.draw.rect(surface, BLUE, (10, screen_height - 60, self.bar_precent, 20))  # Boost bar
            pygame.draw.rect(surface, WHITE, (10, screen_height - 60, self.boost_capacity, 20), 2)  # Outline

    def rotate_towards(self, target_pos):
        rel_x, rel_y = target_pos[0] - self.rect.centerx, target_pos[1] - self.rect.centery
        self.angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)

    def start_flashing(self):
        self.flashing = True
        self.flash_timer = 0
        self.invulnerable = True

    def receive_damage(self):
        self.health -= 33.3  # Reduce health by one-third

class Enemy1(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, target):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.rect.topleft = [pos_x, pos_y]

        self.target = target  # Player to follow
        self.speed = 1  # Half the player's speed

        self.slash_animation = False
        self.sprites = [enemy_slash1, enemy_slash2, enemy_slash3]
        self.current_sprite = 0
        self.slash_speed = 0.15  # Slash animation speed
        self.slash_timer = pygame.time.get_ticks()

        self.paused = False
        self.pause_timer = 0

        self.angle = 0  # Initialize angle

        self.health = 100  # Enemy health

        self.flashing = False
        self.flash_timer = 0
        self.invulnerable = False

    def stun(self):
        self.paused = True
        self.pause_timer = pygame.time.get_ticks()
        self.slash_animation = False  # Stop the current slash animation

    def update(self):
        # Check if the enemy is flashing and update the flash timer
        if self.flashing:
            self.flash_timer += 1 / 60  # Assuming 60 FPS
            if self.flash_timer > 1:  # Flash for 1 second
                self.flashing = False
                self.invulnerable = False

        # Manage stun effect
        if self.paused:
            if pygame.time.get_ticks() - self.pause_timer > 1000:  # 1 second pause
                self.paused = False
            else:
                return  # Early return if still paused

        # Move towards the player
        direction_x, direction_y = self.target.rect.x - self.rect.x, self.target.rect.y - self.rect.y
        distance = math.hypot(direction_x, direction_y)
        if distance > 0:
            direction_x, direction_y = direction_x / distance, direction_y / distance
            self.rect.x += direction_x * self.speed
            self.rect.y += direction_y * self.speed

        # Rotate towards the player
        self.rotate_towards((self.target.rect.centerx, self.target.rect.centery))

        # Slash animation every second
        if pygame.time.get_ticks() - self.slash_timer > 1000:
            self.slash_animation = True
            self.slash_timer = pygame.time.get_ticks()

        if self.slash_animation:
            self.current_sprite += self.slash_speed
            if int(self.current_sprite) >= len(self.sprites):
                self.current_sprite = 0
                self.slash_animation = False

    def draw(self, surface):
        # Draw the enemy
        if not self.flashing or (int(self.flash_timer * 10) % 2 == 0):  # Flash every 0.1 second
            surface.blit(self.image, self.rect.topleft)

        # Draw the slash animation
        if self.slash_animation:
            rotated_image = pygame.transform.rotate(self.sprites[int(self.current_sprite)], self.angle)
            scaled_image = pygame.transform.scale(rotated_image, (rotated_image.get_width() * 2, rotated_image.get_height() * 2))  # Scale by a factor of 2
            offset_x = 50 * math.cos(math.radians(self.angle))
            offset_y = -50 * math.sin(math.radians(self.angle))
            attack_pos = (self.rect.centerx + offset_x - scaled_image.get_width() / 2,
                          self.rect.centery + offset_y - scaled_image.get_height() / 2)
            surface.blit(scaled_image, attack_pos)

        # Draw enemy health bar
        pygame.draw.rect(surface, WHITE, (screen_width - 110, 10, 100, 20))  # Background
        pygame.draw.rect(surface, RED, (screen_width - 110, 10, self.health, 20))  # Health bar

    def rotate_towards(self, target_pos):
        rel_x, rel_y = target_pos[0] - self.rect.centerx, target_pos[1] - self.rect.centery
        self.angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)

    def start_flashing(self):
        self.flashing = True
        self.flash_timer = 0
        self.invulnerable = True

    def receive_damage(self):
        self.health -= 33.3  # Reduce health by 1/3

class Enemy2(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, target):
        super().__init__()
        self.image = enemy_img2
        self.rect = self.image.get_rect()
        self.rect.topleft = [pos_x, pos_y]

        self.target = target  # Player to follow
        self.speed = 1  # Movement speed
        self.phase = "wandering"
        self.wander_timer = 0
        self.wander_target = (random.randint(0, screen_width - self.rect.width),
                              random.randint(0, screen_height - self.rect.height))

        self.angle = 0  # Initialize angle

        self.health = 100  # Enemy health

        self.flashing = False
        self.flash_timer = 0
        self.invulnerable = False

        self.bullet_timer = 0
        self.last_shot_time = pygame.time.get_ticks()

        self.teleport_cooldown = 8000
        self.last_teleport_time = pygame.time.get_ticks()

    def update(self):
        distance_to_player = math.hypot(self.target.rect.x - self.rect.x, self.target.rect.y - self.rect.y)
        self.current_time = pygame.time.get_ticks()

        if self.current_time - self.last_shot_time >= 1000:
            self.shoot()
        
        if distance_to_player < 200:
            self.phase = "running"
        else:
            self.phase = "wandering"

        # Wandering phase
        if self.phase == "wandering":
            self.wander_timer += 1 / 60  # Assuming 60 FPS
            if self.wander_timer >= 2:  # Change direction every 2 seconds
                self.wander_timer = 0
                self.wander_target = (random.randint(0, screen_width - self.rect.width),
                                      random.randint(0, screen_height - self.rect.height))

            # Move towards the wander target
            dx, dy = self.wander_target[0] - self.rect.x, self.wander_target[1] - self.rect.y
            distance = math.hypot(dx, dy)
            if distance > 0:
                dx, dy = dx / distance, dy / distance  # Normalize
                self.rect.x += dx * self.speed
                self.rect.y += dy * self.speed

            if distance > 0:
                dx, dy = dx / distance, dy / distance  # Normalize
                new_x = self.rect.x + dx * self.speed
                new_y = self.rect.y + dy * self.speed
                self.check_boundaries(new_x, new_y)

        # Running phase
        elif self.phase == "running":
            dx, dy = abs(player.rect.x - self.rect.x), abs(player.rect.y - self.rect.y)
            distance = math.hypot(dx, dy)

            if distance > 0:
                dx, dy = dx / distance, dy / distance  # Normalize
                new_x = self.rect.x - dx * self.speed
                new_y = self.rect.y - dy * self.speed
                self.check_boundaries(new_x, new_y)

        if self.current_time - self.last_teleport_time >= self.teleport_cooldown:
            if self.rect.left <= 0:
                self.rect.right = screen_width
                self.last_teleport_time = self.current_time
            elif self.rect.right >= screen_width:
                self.rect.left = 0
                self.last_teleport_time = self.current_time
            if self.rect.top <= 0:
                self.rect.bottom = screen_height
                self.last_teleport_time = self.current_time
            elif self.rect.bottom >= screen_height:
                self.rect.top = 0
                self.last_teleport_time = self.current_time 

        if self.flashing:
            self.flash_timer += 1 / 60  # Assuming 60 FPS
            if self.flash_timer > 1:  # Flash for 1 second
                self.flashing = False
                self.invulnerable = False

        # Update bullet positions
        for bullet in bullets[:]:  # Iterate over a copy of the list
            bullet['x'] += bullet['dx'] * bullet['speed']
            bullet['y'] += bullet['dy'] * bullet['speed']

            # Remove projectiles that have gone off screen
            if bullet['y'] <= 0 or bullet['y'] >= screen_height or bullet['x'] <= 0 or bullet['x'] >= screen_width:
                bullets.remove(bullet)

    def check_boundaries(self, new_x, new_y):
        if new_x < 0 or new_x > screen_width - self.rect.width or new_y < 0 or new_y > screen_height - self.rect.height:
            # Check if teleport cooldown has elapsed
            if self.current_time - self.last_teleport_time >= self.teleport_cooldown:
                # Teleport to the opposite side
                if new_x < 0:
                    self.rect.x = screen_width - self.rect.width
                elif new_x > screen_width - self.rect.width:
                    self.rect.x = 0
                if new_y < 0:
                    self.rect.y = screen_height - self.rect.height
                elif new_y > screen_height - self.rect.height:
                    self.rect.y = 0
                self.last_teleport_time = self.current_time  # Update the last teleport time
            else:
                # Prevent the enemy from moving out of bounds
                if 0 <= new_x <= screen_width - self.rect.width:
                    self.rect.x = new_x
                if 0 <= new_y <= screen_height - self.rect.height:
                    self.rect.y = new_y
        else:
            self.rect.x = new_x
            self.rect.y = new_y

    def draw(self, surface):
        if not self.flashing or (int(self.flash_timer * 10) % 2 == 0):  # Flash every 0.1 second
            surface.blit(self.image, self.rect.topleft)

        pygame.draw.rect(surface, WHITE, (screen_width - 110, 10, 100, 20))  # Background
        pygame.draw.rect(surface, RED, (screen_width - 110, 10, self.health, 20))  # Health bar

    def start_flashing(self):
        self.flashing = True
        self.flash_timer = 0
        self.invulnerable = True

    def receive_damage(self):
        self.health -= 10  # Reduce health by one-third

    def shoot(self):
        # Calculate the direction to the player
        dx = self.target.rect.centerx - self.rect.centerx
        dy = self.target.rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)
        dx /= distance
        dy /= distance

        self.angle = 360 - math.degrees(math.atan2(dy, dx))
        new_projectile = {
            'x': self.rect.centerx,
            'y': self.rect.centery,
            'dx': dx,
            'dy': dy,
            'speed': 5,
            'image': rotate(bullet_image, self.angle)
        }
        bullets.append(new_projectile)

        # Update last shot time
        self.last_shot_time = self.current_time

# Creating the player and enemy
player = Player(200, 200)
enemy1 = Enemy1(100, 100, player)
enemy2 = Enemy2(100, 100, player)

boss1_defeated = False

# Main game loop
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:  # Right mouse button
                player.block_active = True
                player.block_timer = 0
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 3:  # Right mouse button released
                player.block_active = False

            # Trigger attack animation if left mouse button was pressed and block is not active
            if event.button == 1 and not player.block_active:  # Left mouse button
                player.attack()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_e]:
        player.boost()
    if keys[pygame.K_w]:
        player.move(dy=-2)
    if keys[pygame.K_s]:
        player.move(dy=2)
    if keys[pygame.K_a]:
        player.move(dx=-2)
    if keys[pygame.K_d]:
        player.move(dx=2)

    # Rotate towards mouse cursor
    mouse_pos = pygame.mouse.get_pos()
    player.rotate_towards(mouse_pos)

    # Update player and enemy
    player.update()
    if not boss1_defeated:
        enemy1.update()

    if boss1_defeated:
        enemy2.update()

    if enemy1.slash_animation:
        attack_rect = pygame.Rect(enemy1.rect.centerx - 60, enemy1.rect.centery - 60, 120, 120)
        if attack_rect.colliderect(player.rect) and player.flashing == False:
            if not player.flashing:  # Check if the player has not been hit in this frame
                if player.block_active and player.block_timer < 0.35:
                    enemy1.stun()  # Stun the enemy
                elif not player.block_active:
                    player.start_flashing()  # Flash the player if not blocking
                    player.receive_damage()

    # Check for collision between bullet and player
    if len(bullets) > 0:
        for bullet in bullets[:]:  # Iterate over a copy of the list
            bullet_rect = pygame.Rect(bullet['x'], bullet['y'], bullet['image'].get_width(), bullet['image'].get_height())
            
            # Check collision with player
            if bullet_rect.colliderect(player.rect) and not player.flashing:
                if player.block_active:
                    bullets.remove(bullet)
                else:
                    player.start_flashing()  # Flash the player if not blocking
                    player.receive_damage()
                    bullets.remove(bullet)
            
            # Check collision with player attack area
            elif player.attack_animation:
                attack_rect = pygame.Rect(player.rect.centerx - 60, player.rect.centery - 60, 120, 120)
                if bullet_rect.colliderect(attack_rect):
                    # Calculate the direction vector from bullet to player's center
                    dx = player.rect.centerx - bullet['x']
                    dy = player.rect.centery - bullet['y']
                    norm = math.sqrt(dx ** 2 + dy ** 2)
                    
                    if norm != 0:
                        # Normalize the direction vector
                        bullet['dx'] = dx / norm
                        bullet['dy'] = dy / norm
                    else:
                        bullet['dx'] = 0
                        bullet['dy'] = 0
                    
                    bullet['speed'] = 5  # Adjust bullet speed as needed
                    
                    # Reverse the direction vector to reflect the bullet
                    bullet['dx'] *= -1
                    bullet['dy'] *= -1
                    
                    # Update bullet position in the reflected direction
                    bullet['x'] += bullet['dx'] * bullet['speed']
                    bullet['y'] += bullet['dy'] * bullet['speed']
                    
                    # Rotate the bullet image to face the new direction
                    bullet['angle'] = player.angle
                    bullet['image'] = pygame.transform.rotate(bullet_image, bullet['angle'])

                    bullet['reflected'] = True


    # Check for collision between player attack and enemy
    if player.attack_animation:
        attack_rect = pygame.Rect(player.rect.centerx - 60, player.rect.centery - 60, 120, 120)
        if attack_rect.colliderect(enemy1.rect) and enemy1.flashing == False:
            enemy1.start_flashing()
            enemy1.receive_damage()
        if attack_rect.colliderect(enemy2.rect) and enemy2.flashing == False:
            enemy2.start_flashing()
            enemy2.receive_damage()
    
    if len(bullets) > 0:
        for bullet in bullets[:]:  # Iterate over a copy of the list
            bullet_rect = pygame.Rect(bullet['x'], bullet['y'], bullet['image'].get_width(), bullet['image'].get_height())
            if 'reflected' in bullet and bullet['reflected'] and bullet_rect.colliderect(enemy2.rect) and enemy2.flashing == False:
                enemy2.start_flashing()
                enemy2.receive_damage()
                bullets.remove(bullet)

    # Check for game over conditions
    if player.health <= 1:
        running = False

    if enemy1.health <= 1:
        boss1_defeated = True

    # Drawing
    screen.fill((0, 0, 0))
    player.draw(screen)
    if not boss1_defeated:
        enemy1.draw(screen)
    if boss1_defeated:
        enemy2.draw(screen)

    # Draw bullets
    for bullet in bullets:
        screen.blit(bullet['image'], (bullet['x'], bullet['y']))

    pygame.display.flip()
    clock.tick(60)

# Game over
pygame.quit()
sys.exit()
