from fastapi import APIRouter
from app.api.bank_routes import router as bank_router
from app.api.transaction_routes import router as transaction_router
from app.api.mapping_routes import router as mapping_router
from app.api.tally_routes import router as tally_router
from app.api.dashboard_routes import router as dashboard_router
from app.api.report_routes import router as report_router
from app.api.settings_routes import router as settings_router

api_router = APIRouter(prefix="/api")
api_router.include_router(bank_router)
api_router.include_router(transaction_router)
api_router.include_router(mapping_router)
api_router.include_router(tally_router)
api_router.include_router(dashboard_router)
api_router.include_router(report_router)
api_router.include_router(settings_router)

__all__ = ["api_router"]
