import math
import sys
from pathlib import Path

import pygame
from settings import (
    BULLET_LIFETIME,
    BULLET_SCALE,
    BULLET_SPEED,
    ENEMY_SPEED,
    FPS,
    GUN_OFFSET_X,
    GUN_OFFSET_Y,
    HEIGHT,
    PLAYER_SIZE,
    PLAYER_SPEED,
    PLAYER_START_X,
    PLAYER_START_Y,
    SHOOT_COOLDOWN,
    WIDTH,
)

# assets
HERE = Path(__file__).parent.resolve()

pygame.init()

# Creating the window
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BallBallCS")
CLOCK = pygame.time.Clock()

# Load Image
BACKGROUND = pygame.transform.scale(pygame.image.load(HERE / "background" / "background.jpg").convert(), (WIDTH, HEIGHT))
BOUNDARY = pygame.math.Vector2(WIDTH, HEIGHT)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.image.load(HERE / "player" / "player.png").convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, PLAYER_SIZE)
        self.base_player_image = self.image

        self.pos = pos
        self.vec_pos = pygame.math.Vector2(pos)
        self.hitbox_rect = self.base_player_image.get_rect(center=pos)
        self.rect = self.hitbox_rect.copy()

        self.speed = PLAYER_SPEED
        self.shoot = False
        self.shoot_cooldown = 0

        self.health = 100

        self.gun_barrel_offset = pygame.math.Vector2(GUN_OFFSET_X, GUN_OFFSET_Y)

    def player_rotation(self):
        self.mouse_coords = pygame.mouse.get_pos()
        self.x_change_mouse_player = self.mouse_coords[0] - self.hitbox_rect.centerx
        self.y_change_mouse_player = self.mouse_coords[1] - self.hitbox_rect.centery
        self.angle = math.degrees(math.atan2(self.y_change_mouse_player, self.x_change_mouse_player))
        self.image = pygame.transform.rotate(self.base_player_image, -self.angle)
        self.rect = self.image.get_rect(center=self.hitbox_rect.center)

    def user_input(self):
        self.velocity_x = 0
        self.velocity_y = 0

        keys = pygame.key.get_pressed()

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.velocity_y = -self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.velocity_y = self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.velocity_x = self.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.velocity_x = -self.speed

        if self.velocity_x != 0 and self.velocity_y != 0:
            self.velocity_x /= math.sqrt(2)
            self.velocity_y /= math.sqrt(2)

        if pygame.mouse.get_pressed() == (1, 0, 0) or keys[pygame.K_SPACE]:
            self.shoot = True
            self.is_shooting()
        else:
            self.shoot = False

    def is_shooting(self):
        if self.shoot_cooldown == 0:
            self.shoot_cooldown = SHOOT_COOLDOWN
            spawn_bullet_pos = self.pos + self.gun_barrel_offset.rotate(self.angle)
            self.bullet = Bullet(spawn_bullet_pos[0], spawn_bullet_pos[1], self.angle)
            bullet_group.add(self.bullet)
            all_sprites_group.add(self.bullet)

    def move(self):
        new_pos = self.pos + pygame.math.Vector2(self.velocity_x, self.velocity_y)
        if new_pos.x - self.hitbox_rect.width // 2 < 0:
            return
        if new_pos.x + self.hitbox_rect.width // 2 > BOUNDARY.x:
            return
        if new_pos.y - self.hitbox_rect.height // 2 < 0:
            return
        if new_pos.y + self.hitbox_rect.height // 2 > BOUNDARY.y:
            return

        self.pos = new_pos
        self.hitbox_rect.center = self.pos
        self.rect.center = self.hitbox_rect.center

    def update(self):
        self.user_input()
        self.move()
        self.player_rotation()

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.image = pygame.image.load(HERE / "bullet" / "small-red.png").convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, BULLET_SCALE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = BULLET_SPEED
        self.x_vel = math.cos(self.angle * (2 * math.pi / 360)) * self.speed
        self.y_vel = math.sin(self.angle * (2 * math.pi / 360)) * self.speed
        self.bullet_lifetime = BULLET_LIFETIME
        self.spawn_time = pygame.time.get_ticks()

    def bullet_movement(self):
        self.x += self.x_vel
        self.y += self.y_vel

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        if pygame.time.get_ticks() - self.spawn_time > self.bullet_lifetime:
            self.kill()

    def update(self):
        self.bullet_movement()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__(enemy_group, all_sprites_group)
        self.image = pygame.image.load(HERE / "necromancer" / "hunt" / "0.png").convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, 2)

        self.rect = self.image.get_rect()
        self.rect.center = position

        self.direction = pygame.math.Vector2()
        self.velocity = pygame.math.Vector2()
        self.speed = ENEMY_SPEED

        self.position = pygame.math.Vector2(position)

    def hunt_player(self):
        player_vector = pygame.math.Vector2(PLAYER.hitbox_rect.center)
        enemy_vector = pygame.math.Vector2(self.rect.center)
        distance = self.get_vector_distance(player_vector, enemy_vector)

        if distance > 0:
            self.direction = (player_vector - enemy_vector).normalize()
        else:
            self.direction = pygame.math.Vector2()

        self.velocity = self.direction * self.speed
        self.position += self.velocity

        self.rect.centerx = self.position.x
        self.rect.centery = self.position.y

    def get_vector_distance(self, vector_1, vector_2):
        return (vector_1 - vector_2).magnitude()

    def update(self):
        self.hunt_player()


# groups
all_sprites_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

# sprites
PLAYER = Player((PLAYER_START_X, PLAYER_START_Y))
NECROMANCER = Enemy((400, 400))

# add sprites to groups
all_sprites_group.add(PLAYER)

while True:
    key = pygame.key.get_pressed()

    if key[pygame.K_ESCAPE]:
        pygame.quit()
        sys.exit()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    SCREEN.blit(BACKGROUND, (0, 0))
    all_sprites_group.draw(SCREEN)
    all_sprites_group.update()

    # pygame.draw.rect(screen, "red", player.hitbox_rect, width=2)
    # pygame.draw.rect(screen, "yellow", player.rect, width=2)

    pygame.display.update()
    tick = CLOCK.tick(FPS)
