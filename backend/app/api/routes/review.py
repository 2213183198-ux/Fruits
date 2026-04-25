from fastapi import APIRouter, Query

from backend.app.api.presenters import (
    present_feedback_export,
    present_feedback_pool_summary,
    present_review_item_detail,
    present_review_item_summary,
    present_review_summary,
)
from backend.app.core.runtime import runtime
from backend.app.schemas.common import ApiResponse, build_api_response
from backend.app.schemas.public import (
    PublicFeedbackExportData,
    PublicFeedbackPoolSummary,
    PublicReviewItemDetail,
    PublicReviewItemSummary,
    PublicReviewQueueSummary,
    ReviewDecisionRequestBody,
)
from backend.schemas import ReviewDecisionRequest


router = APIRouter(prefix="/api/v1/review", tags=["Review"])


@router.get("/summary", response_model=ApiResponse[PublicReviewQueueSummary], summary="Get review queue summary")
def get_review_summary() -> ApiResponse[PublicReviewQueueSummary]:
    return build_api_response(
        present_review_summary(runtime.get_review_summary()),
        message="Review summary fetched.",
    )


@router.get(
    "/feedback/summary",
    response_model=ApiResponse[PublicFeedbackPoolSummary],
    summary="Get feedback pool summary",
)
def get_feedback_pool_summary(
    decision: str | None = Query(None),
    mode: str | None = Query(None),
    keyword: str | None = Query(None),
) -> ApiResponse[PublicFeedbackPoolSummary]:
    payload = runtime.get_feedback_pool_summary(decision=decision, mode=mode, keyword=keyword)
    return build_api_response(
        present_feedback_pool_summary(payload),
        message="Feedback pool summary fetched.",
        meta={
            "decision": decision or "all",
            "mode": mode or "all",
            "keyword": keyword or "",
        },
    )


@router.get("/items", response_model=ApiResponse[list[PublicReviewItemSummary]], summary="List review queue items")
def list_review_items(
    limit: int = Query(30, ge=1, le=100),
    queue: str = Query("focus"),
    decision: str | None = Query(None),
    mode: str | None = Query(None),
    keyword: str | None = Query(None),
) -> ApiResponse[list[PublicReviewItemSummary]]:
    payload = [
        present_review_item_summary(item)
        for item in runtime.list_review_items(
            limit=limit,
            queue=queue,
            decision=decision,
            mode=mode,
            keyword=keyword,
        )
    ]
    return build_api_response(
        payload,
        message="Review items fetched.",
        meta={
            "limit": limit,
            "queue": queue,
            "decision": decision or "all",
            "mode": mode or "all",
            "keyword": keyword or "",
            "count": len(payload),
        },
    )


@router.get("/items/{item_id}", response_model=ApiResponse[PublicReviewItemDetail], summary="Get review item detail")
def get_review_item(item_id: int) -> ApiResponse[PublicReviewItemDetail]:
    return build_api_response(
        present_review_item_detail(runtime.get_review_item(item_id)),
        message="Review item fetched.",
    )


@router.post(
    "/items/{item_id}/decision",
    response_model=ApiResponse[PublicReviewItemDetail],
    summary="Save review decision for a history item",
)
def save_review_decision(item_id: int, payload: ReviewDecisionRequestBody) -> ApiResponse[PublicReviewItemDetail]:
    updated = runtime.save_review_decision(
        item_id,
        ReviewDecisionRequest(
            decision=payload.decision,
            notes=payload.notes,
            send_to_feedback=payload.send_to_feedback,
        ),
    )
    return build_api_response(
        present_review_item_detail(updated),
        message="Review decision saved.",
    )


@router.post(
    "/feedback/export",
    response_model=ApiResponse[PublicFeedbackExportData],
    summary="Export feedback queue manifest",
)
def export_feedback_manifest(
    decision: str | None = Query(None),
    mode: str | None = Query(None),
    keyword: str | None = Query(None),
) -> ApiResponse[PublicFeedbackExportData]:
    payload = runtime.export_feedback_manifest(decision=decision, mode=mode, keyword=keyword)
    return build_api_response(
        present_feedback_export(payload),
        message=payload.message,
    )
