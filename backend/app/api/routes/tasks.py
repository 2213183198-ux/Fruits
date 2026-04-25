from fastapi import APIRouter, File, Form, Query, UploadFile

from backend.app.api.presenters import present_async_task
from backend.app.core.runtime import runtime
from backend.app.schemas.common import ApiResponse, build_api_response
from backend.app.schemas.public import PublicAsyncTaskData
from backend.config import settings


router = APIRouter(prefix="/api/v1/tasks", tags=["Tasks"])


@router.get("", response_model=ApiResponse[list[PublicAsyncTaskData]], summary="List async tasks")
def list_tasks(
    limit: int = Query(20, ge=1, le=100),
    kind: str | None = Query(None),
    status: str | None = Query(None),
) -> ApiResponse[list[PublicAsyncTaskData]]:
    payload = [present_async_task(item) for item in runtime.list_tasks(limit=limit, kind=kind, status=status)]
    return build_api_response(payload, message="Tasks fetched.", meta={"limit": limit, "count": len(payload)})


@router.get("/{task_id}", response_model=ApiResponse[PublicAsyncTaskData], summary="Get async task detail")
def get_task(task_id: str) -> ApiResponse[PublicAsyncTaskData]:
    return build_api_response(present_async_task(runtime.get_task(task_id)), message="Task fetched.")


@router.post(
    "/batch-inference",
    response_model=ApiResponse[PublicAsyncTaskData],
    summary="Create a batch inference task",
)
async def create_batch_inference_task(
    files: list[UploadFile] = File(...),
    imgsz: int = Form(settings.default_image_size),
    conf: float = Form(settings.default_confidence),
    save_artifact: bool = Form(True),
    export_csv: bool = Form(True),
    export_excel: bool = Form(True),
) -> ApiResponse[PublicAsyncTaskData]:
    payload = await runtime.create_batch_inference_task(
        files,
        imgsz,
        conf,
        save_artifact,
        export_csv,
        export_excel,
    )
    return build_api_response(present_async_task(payload), message="Batch inference task created.")


@router.post(
    "/benchmark",
    response_model=ApiResponse[PublicAsyncTaskData],
    summary="Create a benchmark task",
)
async def create_benchmark_task(
    file: UploadFile = File(...),
    imgsz: int = Form(settings.default_image_size),
    conf: float = Form(settings.default_confidence),
    runs: int = Form(3),
) -> ApiResponse[PublicAsyncTaskData]:
    payload = await runtime.create_benchmark_task(file, imgsz, conf, runs)
    return build_api_response(present_async_task(payload), message="Benchmark task created.")
