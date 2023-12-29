from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


# Enum definitions
class ColorEnum(str, Enum):
    RED = "RED"
    ORANGE = "ORANGE"
    YELLOW = "YELLOW"
    GREEN = "GREEN"
    BLUE = "BLUE"
    INDIGO = "INDIGO"
    VIOLET = "VIOLET"


class ControlPlayerEnum(str, Enum):
    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    SHOOT = "SHOOT"


# Payload models
class Player(BaseModel):
    name: str = Field(f"player_{uuid4()}", alias="User Name")
    color: ColorEnum = ColorEnum.RED
    model_config = ConfigDict(populate_by_name=True, extra="allow")


class ControlPlayer(BaseModel):
    player: Player
    action: ControlPlayerEnum
