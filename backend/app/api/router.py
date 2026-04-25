from fastapi import APIRouter

from backend.app.api.routes.dashboard import router as dashboard_router
from backend.app.api.routes.deployment import router as deployment_router
from backend.app.api.routes.history import router as history_router
from backend.app.api.routes.inference import router as inference_router
from backend.app.api.routes.maintenance import router as maintenance_router
from backend.app.api.routes.models import router as models_router
from backend.app.api.routes.review import router as review_router
from backend.app.api.routes.retrain import router as retrain_router
from backend.app.api.routes.settings import router as settings_router
from backend.app.api.routes.system import router as system_router
from backend.app.api.routes.tasks import router as tasks_router
from backend.app.api.web import router as web_router


api_router = APIRouter()
api_router.include_router(web_router)
api_router.include_router(system_router)
api_router.include_router(models_router)
api_router.include_router(settings_router)
api_router.include_router(inference_router)
api_router.include_router(dashboard_router)
api_router.include_router(deployment_router)
api_router.include_router(history_router)
api_router.include_router(review_router)
api_router.include_router(retrain_router)
api_router.include_router(maintenance_router)
api_router.include_router(tasks_router)
