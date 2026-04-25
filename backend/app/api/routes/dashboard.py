from fastapi import APIRouter, Query

from backend.app.api.presenters import present_dashboard_summary
from backend.app.core.runtime import runtime
from backend.app.schemas.common import ApiResponse, build_api_response
from backend.app.schemas.public import PublicDashboardSummary


router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=ApiResponse[PublicDashboardSummary], summary="Get dashboard summary")
def get_dashboard_summary(days: int = Query(7, ge=1, le=30)) -> ApiResponse[PublicDashboardSummary]:
    payload = runtime.get_dashboard_summary(days=days)
    return build_api_response(
        present_dashboard_summary(payload),
        message="Dashboard summary fetched.",
        meta={"days": days},
    )
