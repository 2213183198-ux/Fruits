from fastapi import APIRouter, Query

from backend.app.api.presenters import present_history_cleanup, present_history_detail, present_history_summary
from backend.app.core.runtime import runtime
from backend.app.schemas.common import ApiResponse, build_api_response
from backend.app.schemas.public import (
    HistoryCleanupRequestBody,
    PublicHistoryCleanupData,
    PublicHistoryRunDetail,
    PublicHistoryRunSummary,
)


router = APIRouter(prefix="/api/v1/history", tags=["History"])


@router.get("/runs", response_model=ApiResponse[list[PublicHistoryRunSummary]], summary="List history runs")
def list_runs(limit: int = Query(10, ge=1, le=100)) -> ApiResponse[list[PublicHistoryRunSummary]]:
    payload = [present_history_summary(item) for item in runtime.list_history_runs(limit=limit)]
    return build_api_response(payload, message="History runs fetched.", meta={"limit": limit, "count": len(payload)})


@router.get("/runs/{run_id}", response_model=ApiResponse[PublicHistoryRunDetail], summary="Get history run detail")
def get_run(run_id: int) -> ApiResponse[PublicHistoryRunDetail]:
    return build_api_response(present_history_detail(runtime.get_history_run(run_id)), message="History run fetched.")


@router.post("/cleanup", response_model=ApiResponse[PublicHistoryCleanupData], summary="Cleanup history by ids or time range")
def cleanup_history(payload: HistoryCleanupRequestBody) -> ApiResponse[PublicHistoryCleanupData]:
    result = runtime.cleanup_history_runs(
        run_ids=payload.run_ids,
        created_from=payload.created_from,
        created_to=payload.created_to,
        delete_all=payload.delete_all,
    )
    return build_api_response(
        present_history_cleanup(
            deleted_count=int(result["deleted_count"]),
            deleted_run_ids=[int(item) for item in result["deleted_run_ids"]],
        ),
        message="History cleanup completed.",
    )
