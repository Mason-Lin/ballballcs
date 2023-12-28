# flake8: noqa: E405
# ruff: noqa: F405, F403
# pylint: disable=wildcard-import, unused-wildcard-import, attribute-defined-outside-init

import asyncio
import logging
import sys
from contextlib import asynccontextmanager

import pygame
from fastapi import FastAPI

from app.game.settings import *

# Creating the window
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BallBallCS")
CLOCK = pygame.time.Clock()
pygame.init()


async def game_main_loop():
    while True:
        logging.debug("Game Running")

        key = pygame.key.get_pressed()

        if key[pygame.K_ESCAPE]:
            pygame.quit()
            sys.exit()

        # pygame.draw.rect(SCREEN, "red", player.hitbox_rect, width=2)
        # pygame.draw.rect(screen, "yellow", player.rect, width=2)

        pygame.display.update()
        tick = CLOCK.tick(FPS)


@asynccontextmanager
async def game_main(app: FastAPI):
    task = asyncio.create_task(game_main_loop())
    yield
    task.cancel()
