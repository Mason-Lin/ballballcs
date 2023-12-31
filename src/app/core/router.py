import logging

from fastapi import APIRouter, HTTPException, status

from app.core import models
from app.game.run import RUNTIME_DATA

router = APIRouter()
logger = logging.getLogger("uvicorn.access")
logger.setLevel(logging.WARNING)


@router.post("/join")
async def post_foo(player: models.Player):
    if player.name == "reject":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Player name 'reject' is not allowed",
        )
    logging.debug(f"player color: {player.color}")
    return {"greeting": f"Hello Player: {player.name}"}


@router.post("/control")
async def post_control(control: models.GameControl):
    # logging.debug(f"player: {control.player.name}")
    RUNTIME_DATA.append(control)
    return {"control": "done"}
