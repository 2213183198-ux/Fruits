from fastapi import APIRouter, File, UploadFile

from backend.app.api.presenters import present_model_descriptor, present_model_inventory
from backend.app.core.runtime import runtime
from backend.app.schemas.common import ApiResponse, build_api_response
from backend.app.schemas.public import PublicModelDescriptor, PublicModelInventoryData


router = APIRouter(prefix="/api/v1/models", tags=["Models"])


@router.get("", response_model=ApiResponse[PublicModelInventoryData], summary="List registered models")
def list_models() -> ApiResponse[PublicModelInventoryData]:
    return build_api_response(present_model_inventory(runtime.list_models()), message="Model inventory fetched.")


@router.post("", response_model=ApiResponse[PublicModelDescriptor], summary="Upload a new model")
async def upload_model(
    file: UploadFile = File(...),
    yaml_file: UploadFile | None = File(None),
) -> ApiResponse[PublicModelDescriptor]:
    payload = await runtime.upload_model(file, yaml_file)
    return build_api_response(present_model_descriptor(payload.model), message=payload.message)


@router.post(
    "/{model_id}/activate",
    response_model=ApiResponse[PublicModelInventoryData],
    summary="Activate a model",
)
def activate_model(model_id: str) -> ApiResponse[PublicModelInventoryData]:
    runtime.activate_model(model_id)
    return build_api_response(present_model_inventory(runtime.list_models()), message="Model activated.")


@router.delete(
    "/{model_id}",
    response_model=ApiResponse[PublicModelInventoryData],
    summary="Delete an uploaded model",
)
def delete_model(model_id: str) -> ApiResponse[PublicModelInventoryData]:
    runtime.delete_model(model_id)
    return build_api_response(present_model_inventory(runtime.list_models()), message="Model deleted.")
