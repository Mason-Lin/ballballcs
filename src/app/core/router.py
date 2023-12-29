import logging

from fastapi import APIRouter, HTTPException, status

from app.core import models
from app.game.run import RUNTIME_DATA

router = APIRouter()


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
async def post_control(control: models.ControlPlayer):
    logging.debug(f"player name: {control.player.name}, action: {control.action}")
    if control.player.name == "test":
        RUNTIME_DATA.append(control.model_dump())

    return {"control": "done"}
