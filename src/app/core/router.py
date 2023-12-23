import logging

from fastapi import APIRouter, HTTPException, status

from app.core import models

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
