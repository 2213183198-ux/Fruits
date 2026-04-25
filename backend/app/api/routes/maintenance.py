from fastapi import APIRouter

from backend.app.api.presenters import present_cleanup, present_storage_status
from backend.app.core.runtime import runtime
from backend.app.schemas.common import ApiResponse, build_api_response
from backend.app.schemas.public import PublicCleanupData, PublicStorageStatusData
from backend.schemas import CleanupRequest


router = APIRouter(prefix="/api/v1/maintenance", tags=["Maintenance"])


@router.get("/storage", response_model=ApiResponse[PublicStorageStatusData], summary="Get storage status")
def get_storage_status() -> ApiResponse[PublicStorageStatusData]:
    return build_api_response(present_storage_status(runtime.get_storage_status()), message="Storage status fetched.")


@router.post("/cleanup", response_model=ApiResponse[PublicCleanupData], summary="Cleanup generated files or history")
def cleanup_storage(payload: CleanupRequest) -> ApiResponse[PublicCleanupData]:
    result = runtime.cleanup_storage(payload)
    return build_api_response(present_cleanup(result), message="Cleanup completed.")
