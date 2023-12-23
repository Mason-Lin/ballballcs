import json
import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


def get_history() -> dict:
    history_folder = Path(__file__).parent
    history_path = history_folder / "history.json"
    return json.loads(history_path.read_text())


class Settings(BaseSettings):
    # local run loads environment variables from load.env; online run loads real environment variables
    PROJECT_NAME: str = os.environ.get("PROJECT_NAME", "DummyProject")
    PATH_PREFIX: str = "/"
    HISTORY: dict = get_history()
    VERSION: str = next(iter(HISTORY.keys()))
    VOLUME: Path = Path(os.environ.get("VOLUME_MOUNT_PATH", "/data"))
    LOG_FOLDER: Path = VOLUME / "log"
    SOURCE_VERSION: str = "local"


@lru_cache
def get_settings() -> Settings:
    return Settings()
