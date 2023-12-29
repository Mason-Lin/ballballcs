# flake8: noqa: E405
# ruff: noqa: F405, F403
# pylint: disable=wildcard-import, unused-wildcard-import, attribute-defined-outside-init
import asyncio
import logging
import math
import sys
from collections import deque
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Union

import pygame
from fastapi import FastAPI

from app.game.settings import *

RUNTIME_DATA = deque()

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
    def __init__(self, who, pos):
        super().__init__()
        self.who = who
        self.image = pygame.image.load(HERE / "player" / "player.png").convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, PLAYER_SIZE)
        self.base_player_image = self.image

        self.position = pos
        self.vec_pos = pygame.math.Vector2(pos)
        self.base_object_rect = self.base_player_image.get_rect(center=pos)
        self.rect = self.base_object_rect.copy()

        self.speed = PLAYER_SPEED
        self.shoot = False
        self.shoot_cooldown = 0

        self.health = 100

        self.gun_barrel_offset = pygame.math.Vector2(GUN_OFFSET_X, GUN_OFFSET_Y)

    def player_rotation(self):
        self.mouse_coords = pygame.mouse.get_pos()
        self.x_change_mouse_player = self.mouse_coords[0] - self.base_object_rect.centerx
        self.y_change_mouse_player = self.mouse_coords[1] - self.base_object_rect.centery
        self.angle = math.degrees(math.atan2(self.y_change_mouse_player, self.x_change_mouse_player))
        self.image = pygame.transform.rotate(self.base_player_image, -self.angle)
        self.rect = self.image.get_rect(center=self.base_object_rect.center)

    def user_input(self):
        self.velocity_x = 0
        self.velocity_y = 0

        if self.who != "you":
            return

        # TODO: key press
        if len(RUNTIME_DATA) > 0 and RUNTIME_DATA[0]["action"] in ("UP", "DOWN", "LEFT", "RIGHT", "SHOOT"):
            control = RUNTIME_DATA.popleft()
            if control["action"] == "UP":
                self.velocity_y = -self.speed
            elif control["action"] == "DOWN":
                self.velocity_y = self.speed
            elif control["action"] == "LEFT":
                self.velocity_x = -self.speed
            elif control["action"] == "RIGHT":
                self.velocity_x = self.speed
            else:
                logging.warning(f"Unknown control: {control}")

            # keys = pygame.key.get_pressed()

            # if keys[pygame.K_w] or keys[pygame.K_UP]:
            #     self.velocity_y = -self.speed
            # if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            #     self.velocity_y = self.speed
            # if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            #     self.velocity_x = self.speed
            # if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            #     self.velocity_x = -self.speed

            if self.velocity_x != 0 and self.velocity_y != 0:
                self.velocity_x /= math.sqrt(2)
                self.velocity_y /= math.sqrt(2)

            # if pygame.mouse.get_pressed() == (1, 0, 0) or keys[pygame.K_SPACE]:
            if control["action"] == "SHOOT":
                self.shoot = True
                self.is_shooting()
            else:
                self.shoot = False

    def is_shooting(self):
        if self.shoot_cooldown == 0:
            self.shoot_cooldown = SHOOT_COOLDOWN
            spawn_bullet_pos = self.position + self.gun_barrel_offset.rotate(self.angle)
            self.bullet = Bullet(spawn_bullet_pos[0], spawn_bullet_pos[1], self.angle)
            bullet_group.add(self.bullet)
            all_sprites_group.add(self.bullet)

    def draw_player_health(self, x, y):
        if self.health > 60:
            color = GREEN
        elif self.health > 30:
            color = YELLOW
        else:
            color = RED
        width = int(self.base_object_rect.width / 2 * self.health / 100)
        pygame.draw.rect(SCREEN, color, (x - 40, y - 45, width, 5))

    def move(self):
        next_x = self.base_object_rect.centerx + self.velocity_x
        next_y = self.base_object_rect.centery + self.velocity_y

        if next_x - self.base_object_rect.width // 2 < 0:
            return
        if next_x + self.base_object_rect.width // 2 > BOUNDARY.x:
            return
        if next_y - self.base_object_rect.height // 2 < 0:
            return
        if next_y + self.base_object_rect.height // 2 > BOUNDARY.y:
            return

        self.position = pygame.math.Vector2(next_x, next_y)
        self.base_object_rect.centerx = next_x
        self.base_object_rect.centery = next_y
        self.rect.center = self.base_object_rect.center
        self.vec_pos = (self.base_object_rect.centerx, self.base_object_rect.centery)

    def check_alive(self):
        if self.health <= 0:
            self.kill()
            return

    def update(self):
        self.draw_player_health(self.position[0], self.position[1])

        self.user_input()
        self.move()
        self.player_rotation()
        self.check_alive()

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

    def bullet_collisions(self):
        hits = pygame.sprite.groupcollide(enemy_group, bullet_group, False, True, hitbox_collide)
        for hit in hits:
            hit.health -= 10
        hits = pygame.sprite.groupcollide(player_group, bullet_group, False, True, hitbox_collide)
        for hit in hits:
            hit.health -= 10

        if self.x < 0 or self.y < 0 or self.x > WIDTH or self.y > HEIGHT:  # screen collisions
            self.kill()

    def update(self):
        self.bullet_movement()
        self.bullet_collisions()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__(enemy_group, all_sprites_group)
        self.image = pygame.image.load(HERE / "necromancer" / "hunt" / "0.png").convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, 2)

        self.rect = self.image.get_rect()
        self.rect.center = position

        self.hitbox_rect = pygame.Rect(0, 0, 75, 100)
        self.base_object_rect = self.hitbox_rect.copy()
        self.base_object_rect.center = self.rect.center

        self.direction = pygame.math.Vector2()
        self.velocity = pygame.math.Vector2()
        self.speed = ENEMY_SPEED

        self.health = 100

        self.position = pygame.math.Vector2(position)

    def check_alive(self):
        if self.health <= 0:
            self.kill()
            return

    def hunt_player(self):
        player_vector = pygame.math.Vector2(PLAYER.base_object_rect.center)
        enemy_vector = pygame.math.Vector2(self.rect.center)
        distance = self.get_vector_distance(player_vector, enemy_vector)

        if distance > 0:
            self.direction = (player_vector - enemy_vector).normalize()
        else:
            self.direction = pygame.math.Vector2()

        self.velocity = self.direction * self.speed
        self.position += self.velocity

        self.base_object_rect.centerx = self.position.x
        self.base_object_rect.centery = self.position.y
        self.rect.center = self.base_object_rect.center
        self.position = (self.base_object_rect.centerx, self.base_object_rect.centery)

    def get_vector_distance(self, vector_1, vector_2):
        return (vector_1 - vector_2).magnitude()

    def update(self):
        self.hunt_player()
        self.check_alive()


def hitbox_collide(sprite1: Union[Enemy, Player], sprite2):
    return sprite1.base_object_rect.colliderect(sprite2.rect)


# groups
all_sprites_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

# sprites
PLAYER = Player("you", (PLAYER_START_X, PLAYER_START_Y))
OTHER_PLAYER = Player("others", (PLAYER_START_X, PLAYER_START_Y))
NECROMANCER = Enemy((400, 400))

# add sprites to groups
all_sprites_group.add(PLAYER)
all_sprites_group.add(OTHER_PLAYER)
player_group.add(OTHER_PLAYER)


async def game_main_loop():
    while True:
        logging.debug("Game Running")

        # DEBUG
        logging.debug("=" * 50)
        logging.debug(PLAYER.position)
        if len(RUNTIME_DATA) > 0:
            control = RUNTIME_DATA[0]
            logging.debug(control)
        # DEBUG

        if len(RUNTIME_DATA) > 0 and RUNTIME_DATA[0]["action"] == "QUIT":
            pygame.quit()

        # key = pygame.key.get_pressed()

        # if key[pygame.K_ESCAPE]:
        #     pygame.quit()
        #     sys.exit()

        # for event in pygame.event.get():
        #     if event.type == pygame.QUIT:
        #         pygame.quit()
        #         sys.exit()

        SCREEN.blit(BACKGROUND, (0, 0))
        all_sprites_group.draw(SCREEN)
        all_sprites_group.update()

        # pygame.draw.rect(screen, "red", player.hitbox_rect, width=2)
        # pygame.draw.rect(screen, "yellow", player.rect, width=2)

        pygame.display.update()
        tick = CLOCK.tick(FPS)

        # FIXME: Use sleep to let service work, should open a standalone process
        await asyncio.sleep(0.25)


@asynccontextmanager
async def game_main(app: FastAPI):
    task = asyncio.create_task(game_main_loop())
    yield
    task.cancel()
