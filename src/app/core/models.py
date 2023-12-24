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
    name: str = Field("player_{}".format(uuid4()), alias="User Name")
    color: ColorEnum = ColorEnum.RED
    model_config = ConfigDict(populate_by_name=True, extra="allow")
