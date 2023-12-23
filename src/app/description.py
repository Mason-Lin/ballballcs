from datetime import datetime, timedelta, timezone

from app.config import get_settings

config = get_settings()

DESCRIPTION = f"""
    service: {config.PROJECT_NAME}
    version: {config.VERSION}
    history: {next(iter(config.HISTORY.values()))}
    commit id: {config.SOURCE_VERSION}
    deployed time: {datetime.now(timezone(timedelta(hours=+8))).ctime()}
    """

DESCRIPTION_DICT = {
    "service": config.PROJECT_NAME,
    "version": config.VERSION,
    "commit id": config.SOURCE_VERSION,
    "deployed time": datetime.now(timezone(timedelta(hours=+8))).ctime(),
}
