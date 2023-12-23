from enum import Enum, auto
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


# Enum definitions
class ColorEnum(Enum):
    RED = auto()
    ORANGE = auto()
    YELLOW = auto()
    GREEN = auto()
    BLUE = auto()
    INDIGO = auto()
    VIOLET = auto()


# Payload models
class Player(BaseModel):
    name: str = Field(f"player_{uuid4()}", alias="User Name")
    color: ColorEnum = ColorEnum.RED
    model_config = ConfigDict(populate_by_name=True, extra="allow")
