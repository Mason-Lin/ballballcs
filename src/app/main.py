import logging

from fastapi import FastAPI

from app.config import get_settings
from app.core import router as core
from app.description import DESCRIPTION
from app.game.run import game_main
from app.health import router as health

config = get_settings()
logging.basicConfig(format="[%(asctime)s][%(filename)s:%(lineno)d] %(levelname)s - %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logging.info({k: v for k, v in config.model_dump().items() if k != "HISTORY"})


app = FastAPI(
    title=config.PROJECT_NAME,
    description=DESCRIPTION,
    version=config.VERSION,
    root_path=config.PATH_PREFIX,
    lifespan=game_main,
)


app.include_router(health.router, tags=["health"])
app.include_router(core.router, tags=["core"], prefix="/core")
