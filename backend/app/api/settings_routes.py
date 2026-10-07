from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.config.settings import settings

router = APIRouter(prefix="/settings", tags=["Settings"])

class SettingsUpdateRequest(BaseModel):
    tally_host: Optional[str] = None
    tally_port: Optional[int] = None
    tally_company: Optional[str] = None
    tally_simulation_mode: Optional[bool] = None
    default_bank_ledger: Optional[str] = None
    auto_approve_threshold: Optional[float] = None
    log_level: Optional[str] = None

@router.get("")
def get_settings():
    return {
        "tally_host": settings.TALLY_HOST,
        "tally_port": settings.TALLY_PORT,
        "tally_company": settings.TALLY_COMPANY,
        "tally_simulation_mode": settings.TALLY_SIMULATION_MODE,
        "default_bank_ledger": settings.DEFAULT_BANK_LEDGER,
        "auto_approve_threshold": settings.AUTO_APPROVE_THRESHOLD,
        "log_level": settings.LOG_LEVEL,
        "upload_dir": settings.UPLOAD_DIR,
        "database_url": settings.DATABASE_URL
    }

@router.put("")
def update_settings(req: SettingsUpdateRequest):
    if req.tally_host is not None:
        settings.TALLY_HOST = req.tally_host
    if req.tally_port is not None:
        settings.TALLY_PORT = req.tally_port
    if req.tally_company is not None:
        settings.TALLY_COMPANY = req.tally_company
    if req.tally_simulation_mode is not None:
        settings.TALLY_SIMULATION_MODE = req.tally_simulation_mode
    if req.default_bank_ledger is not None:
        settings.DEFAULT_BANK_LEDGER = req.default_bank_ledger
    if req.auto_approve_threshold is not None:
        settings.AUTO_APPROVE_THRESHOLD = req.auto_approve_threshold
    if req.log_level is not None:
        settings.LOG_LEVEL = req.log_level

    return {
        "success": True,
        "message": "Settings updated successfully.",
        "settings": get_settings()
    }
