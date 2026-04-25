from fastapi import APIRouter, File, Form, UploadFile

from backend.app.api.presenters import present_benchmark, present_deployment_status, present_onnx_export, present_tensorrt_export
from backend.app.core.runtime import runtime
from backend.app.schemas.common import ApiResponse, build_api_response
from backend.app.schemas.public import PublicBenchmarkData, PublicDeploymentStatusData, PublicOnnxExportData, PublicTensorRtExportData
from backend.config import settings


router = APIRouter(prefix="/api/v1/deployment", tags=["Deployment"])


@router.get("/status", response_model=ApiResponse[PublicDeploymentStatusData], summary="Get deployment status")
def get_status() -> ApiResponse[PublicDeploymentStatusData]:
    return build_api_response(
        present_deployment_status(runtime.get_deployment_status()),
        message="Deployment status fetched.",
    )


@router.post("/onnx/export", response_model=ApiResponse[PublicOnnxExportData], summary="Export active model to ONNX")
def export_onnx(imgsz: int = Form(settings.default_image_size)) -> ApiResponse[PublicOnnxExportData]:
    payload = runtime.export_onnx(imgsz)
    return build_api_response(present_onnx_export(payload), message=payload.message)


@router.post("/tensorrt/export", response_model=ApiResponse[PublicTensorRtExportData], summary="Export active model to TensorRT")
def export_tensorrt(imgsz: int = Form(settings.default_image_size)) -> ApiResponse[PublicTensorRtExportData]:
    payload = runtime.export_tensorrt(imgsz)
    return build_api_response(present_tensorrt_export(payload), message=payload.message)


@router.post("/benchmark", response_model=ApiResponse[PublicBenchmarkData], summary="Run model benchmark")
async def benchmark(
    file: UploadFile = File(...),
    imgsz: int = Form(settings.default_image_size),
    conf: float = Form(settings.default_confidence),
    runs: int = Form(3),
) -> ApiResponse[PublicBenchmarkData]:
    payload = await runtime.benchmark(file, imgsz, conf, runs)
    return build_api_response(present_benchmark(payload), message="Benchmark completed.")
