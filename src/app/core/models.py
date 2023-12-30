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


# Payload models
class Player(BaseModel):
    name: str = Field(f"player_{uuid4()}", alias="User Name")
    color: ColorEnum = ColorEnum.RED
    model_config = ConfigDict(populate_by_name=True, extra="allow")


class GameControl(BaseModel):
    player: Player
    key_pressed: list[bool]
    mouse_coords: tuple[int, int]
    mouse_pressed: tuple[bool, bool, bool]
