from fastapi import APIRouter, Query

from backend.app.api.presenters import (
    present_retrain_batch_export,
    present_retrain_batch_item_detail,
    present_retrain_batch_item_summary,
    present_retrain_batch_summary,
    present_retrain_catalog_item_detail,
    present_retrain_catalog_item_summary,
    present_retrain_catalog_summary,
)
from backend.app.core.runtime import runtime
from backend.app.schemas.common import ApiResponse, build_api_response
from backend.app.schemas.public import (
    PublicRetrainBatchExportData,
    PublicRetrainBatchItemDetail,
    PublicRetrainBatchItemSummary,
    PublicRetrainBatchSummary,
    PublicRetrainCatalogItemDetail,
    PublicRetrainCatalogItemSummary,
    PublicRetrainCatalogSummary,
    RetrainBatchCreateRequestBody,
    RetrainCatalogUpsertRequestBody,
)
from backend.schemas import RetrainBatchCreateRequest, RetrainCatalogUpsertRequest


router = APIRouter(prefix="/api/v1/retrain", tags=["Retrain"])


@router.get("/summary", response_model=ApiResponse[PublicRetrainCatalogSummary], summary="Get retrain catalog summary")
def get_retrain_catalog_summary(
    status: str | None = Query(None),
    decision: str | None = Query(None),
    mode: str | None = Query(None),
    keyword: str | None = Query(None),
) -> ApiResponse[PublicRetrainCatalogSummary]:
    payload = runtime.get_retrain_catalog_summary(status=status, decision=decision, mode=mode, keyword=keyword)
    return build_api_response(
        present_retrain_catalog_summary(payload),
        message="Retrain catalog summary fetched.",
        meta={
            "status": status or "all",
            "decision": decision or "all",
            "mode": mode or "all",
            "keyword": keyword or "",
        },
    )


@router.get(
    "/items",
    response_model=ApiResponse[list[PublicRetrainCatalogItemSummary]],
    summary="List retrain catalog items",
)
def list_retrain_catalog_items(
    limit: int = Query(30, ge=1, le=100),
    status: str | None = Query(None),
    decision: str | None = Query(None),
    mode: str | None = Query(None),
    keyword: str | None = Query(None),
) -> ApiResponse[list[PublicRetrainCatalogItemSummary]]:
    payload = [
        present_retrain_catalog_item_summary(item)
        for item in runtime.list_retrain_catalog_items(
            limit=limit,
            status=status,
            decision=decision,
            mode=mode,
            keyword=keyword,
        )
    ]
    return build_api_response(
        payload,
        message="Retrain catalog items fetched.",
        meta={
            "limit": limit,
            "status": status or "all",
            "decision": decision or "all",
            "mode": mode or "all",
            "keyword": keyword or "",
            "count": len(payload),
        },
    )


@router.get(
    "/items/{item_id}",
    response_model=ApiResponse[PublicRetrainCatalogItemDetail],
    summary="Get retrain catalog item detail",
)
def get_retrain_catalog_item(item_id: int) -> ApiResponse[PublicRetrainCatalogItemDetail]:
    return build_api_response(
        present_retrain_catalog_item_detail(runtime.get_retrain_catalog_item(item_id)),
        message="Retrain catalog item fetched.",
    )


@router.post(
    "/items/{item_id}",
    response_model=ApiResponse[PublicRetrainCatalogItemDetail],
    summary="Create or update retrain catalog item",
)
def upsert_retrain_catalog_item(
    item_id: int,
    payload: RetrainCatalogUpsertRequestBody,
) -> ApiResponse[PublicRetrainCatalogItemDetail]:
    updated = runtime.upsert_retrain_catalog_item(
        item_id,
        RetrainCatalogUpsertRequest(
            catalog_status=payload.catalog_status,
            catalog_notes=payload.catalog_notes,
            annotation_draft=payload.annotation_draft,
        ),
    )
    return build_api_response(
        present_retrain_catalog_item_detail(updated),
        message="Retrain catalog item saved.",
    )


@router.get(
    "/batches/summary",
    response_model=ApiResponse[PublicRetrainBatchSummary],
    summary="Get retrain batch summary",
)
def get_retrain_batch_summary() -> ApiResponse[PublicRetrainBatchSummary]:
    return build_api_response(
        present_retrain_batch_summary(runtime.get_retrain_batch_summary()),
        message="Retrain batch summary fetched.",
    )


@router.get(
    "/batches",
    response_model=ApiResponse[list[PublicRetrainBatchItemSummary]],
    summary="List retrain batches",
)
def list_retrain_batches(limit: int = Query(8, ge=1, le=100)) -> ApiResponse[list[PublicRetrainBatchItemSummary]]:
    payload = [present_retrain_batch_item_summary(item) for item in runtime.list_retrain_batches(limit=limit)]
    return build_api_response(
        payload,
        message="Retrain batches fetched.",
        meta={
            "limit": limit,
            "count": len(payload),
        },
    )


@router.post(
    "/batches",
    response_model=ApiResponse[PublicRetrainBatchItemDetail],
    summary="Create retrain batch from selected catalog items",
)
def create_retrain_batch(payload: RetrainBatchCreateRequestBody) -> ApiResponse[PublicRetrainBatchItemDetail]:
    created = runtime.create_retrain_batch(
        RetrainBatchCreateRequest(
            batch_name=payload.batch_name,
            batch_notes=payload.batch_notes,
            item_ids=payload.item_ids,
        )
    )
    return build_api_response(
        present_retrain_batch_item_detail(created),
        message="Retrain batch created.",
    )


@router.get(
    "/batches/{batch_id}",
    response_model=ApiResponse[PublicRetrainBatchItemDetail],
    summary="Get retrain batch detail",
)
def get_retrain_batch(batch_id: int) -> ApiResponse[PublicRetrainBatchItemDetail]:
    return build_api_response(
        present_retrain_batch_item_detail(runtime.get_retrain_batch(batch_id)),
        message="Retrain batch fetched.",
    )


@router.post(
    "/batches/{batch_id}/export",
    response_model=ApiResponse[PublicRetrainBatchExportData],
    summary="Export retrain batch sample package",
)
def export_retrain_batch(batch_id: int) -> ApiResponse[PublicRetrainBatchExportData]:
    payload = runtime.export_retrain_batch(batch_id)
    return build_api_response(
        present_retrain_batch_export(payload),
        message=payload.message,
    )
