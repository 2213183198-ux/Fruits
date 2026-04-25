from fastapi import APIRouter

from backend.app.api.presenters import present_api_index, present_health, present_metadata
from backend.app.core.runtime import runtime
from backend.app.schemas.common import ApiResponse, build_api_response
from backend.app.schemas.public import ApiIndexData, PublicHealthData, PublicProjectMetadataData


router = APIRouter(prefix="/api/v1", tags=["System"])


@router.get("", response_model=ApiResponse[ApiIndexData], summary="Get API service index")
def get_api_index() -> ApiResponse[ApiIndexData]:
    return build_api_response(present_api_index(runtime.get_api_index()), message="API index fetched.")


@router.get("/system/health", response_model=ApiResponse[PublicHealthData], summary="Get service health")
def get_health() -> ApiResponse[PublicHealthData]:
    return build_api_response(present_health(runtime.get_health()), message="Health status fetched.")


@router.get("/system/metadata", response_model=ApiResponse[PublicProjectMetadataData], summary="Get project metadata")
def get_metadata() -> ApiResponse[PublicProjectMetadataData]:
    return build_api_response(present_metadata(runtime.get_metadata()), message="Project metadata fetched.")
