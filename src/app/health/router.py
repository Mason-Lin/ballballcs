from fastapi import APIRouter

from app.config import Settings, get_settings

router = APIRouter()
settings: Settings = get_settings()


@router.get("/")
async def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "history": settings.HISTORY,
        "commit id": settings.SOURCE_VERSION,
    }


@router.get("/ping")
async def pong():
    return {"ping": "pong!"}


@router.get("/info")
async def info():
    return {"type": settings.PROJECT_NAME, "typeVer": settings.VERSION, "sourceVer": settings.SOURCE_VERSION}


@router.get("/health")
async def health():
    return {"status": "ok"}
