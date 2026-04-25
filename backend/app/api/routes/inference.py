from fastapi import APIRouter, File, Form, UploadFile

from backend.app.api.presenters import present_batch_prediction, present_prediction
from backend.app.core.runtime import runtime
from backend.app.schemas.common import ApiResponse, build_api_response
from backend.app.schemas.public import PublicBatchPredictionData, PublicPredictionData
from backend.config import settings


router = APIRouter(prefix="/api/v1/inference", tags=["Inference"])


@router.post("/image", response_model=ApiResponse[PublicPredictionData], summary="Run single image inference")
async def predict_image(
    file: UploadFile = File(...),
    imgsz: int = Form(settings.default_image_size),
    conf: float = Form(settings.default_confidence),
    save_artifact: bool = Form(True),
    record_history: bool = Form(True),
) -> ApiResponse[PublicPredictionData]:
    payload = await runtime.predict_image(file, imgsz, conf, save_artifact, record_history)
    return build_api_response(present_prediction(payload), message="Single image inference completed.")


@router.post("/batch", response_model=ApiResponse[PublicBatchPredictionData], summary="Run batch image inference")
async def predict_batch(
    files: list[UploadFile] = File(...),
    imgsz: int = Form(settings.default_image_size),
    conf: float = Form(settings.default_confidence),
    save_artifact: bool = Form(True),
    export_csv: bool = Form(True),
    export_excel: bool = Form(True),
) -> ApiResponse[PublicBatchPredictionData]:
    payload = await runtime.predict_batch(files, imgsz, conf, save_artifact, export_csv, export_excel)
    return build_api_response(present_batch_prediction(payload), message="Batch inference completed.")
