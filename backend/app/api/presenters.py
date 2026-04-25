from __future__ import annotations

from pathlib import Path

from backend.app.schemas.public import (
    ApiIndexData,
    PublicBatchPredictionData,
    PublicAsyncTaskData,
    PublicBenchmarkData,
    PublicCleanupData,
    PublicDashboardSummary,
    PublicDeploymentStatusData,
    PublicFeedbackExportData,
    PublicFeedbackPoolSummary,
    PublicHealthData,
    PublicHistoryItem,
    PublicReviewItemDetail,
    PublicReviewItemSummary,
    PublicRetrainBatchExportData,
    PublicRetrainBatchItemDetail,
    PublicRetrainBatchItemSummary,
    PublicRetrainBatchSummary,
    PublicRetrainCatalogItemDetail,
    PublicRetrainCatalogItemSummary,
    PublicRetrainCatalogSummary,
    PublicHistoryCleanupData,
    PublicHistoryRunDetail,
    PublicHistoryRunSummary,
    PublicModelArtifact,
    PublicModelDescriptor,
    PublicModelInventoryData,
    PublicOnnxExportData,
    PublicPredictionData,
    PublicProjectMetadataData,
    PublicQualityRuleMessages,
    PublicReviewQueueSummary,
    PublicQualityRuleSettingsData,
    PublicStorageArtifactItem,
    PublicStorageStatusData,
    PublicTensorRtExportData,
)
from backend.schemas import (
    BatchPredictionResponse,
    BenchmarkResponse,
    CleanupResponse,
    DashboardSummary,
    DeploymentStatusResponse,
    FeedbackExportResponse,
    FeedbackPoolSummary,
    HealthResponse,
    HistoryRunDetail,
    HistoryRunSummary,
    ModelDescriptor,
    ModelInventoryResponse,
    OnnxExportResponse,
    PredictionResponse,
    ProjectMetadataResponse,
    QualityRuleSettings,
    ReviewItemDetail,
    ReviewItemSummary,
    ReviewQueueSummary,
    RetrainBatchExportResponse,
    RetrainBatchItemDetail,
    RetrainBatchItemSummary,
    RetrainBatchSummary,
    RetrainCatalogItemDetail,
    RetrainCatalogItemSummary,
    RetrainCatalogSummary,
    StorageArtifactItem,
    StorageStatusResponse,
    TensorRtExportResponse,
)


def _artifact_name(path: str) -> str:
    return Path(path).name if path else ""


def present_api_index(payload: dict[str, object]) -> ApiIndexData:
    return ApiIndexData(**payload)


def present_health(payload: HealthResponse) -> PublicHealthData:
    return PublicHealthData(
        status=payload.status,
        active_model_name=payload.active_model_name,
        active_model_type=payload.active_model_type,
        model_exists=payload.model_exists,
        model_loaded=payload.model_loaded,
        active_class_names=payload.active_class_names,
    )


def present_metadata(payload: ProjectMetadataResponse) -> PublicProjectMetadataData:
    return PublicProjectMetadataData(
        project_name=payload.project_name,
        model_exists=payload.model_exists,
        class_names=payload.class_names,
        dataset=payload.dataset,
        highlights=payload.highlights,
    )


def present_model_descriptor(payload: ModelDescriptor) -> PublicModelDescriptor:
    return PublicModelDescriptor(
        id=payload.id,
        name=payload.name,
        type=payload.type,
        size_mb=payload.size_mb,
        source=payload.source,
        is_default=payload.is_default,
        is_active=payload.is_active,
        can_delete=payload.can_delete,
        yaml_name=payload.yaml_name,
        class_names=payload.class_names,
        benchmarked_at=payload.benchmarked_at,
        benchmark_image_size=payload.benchmark_image_size,
        benchmark_confidence_threshold=payload.benchmark_confidence_threshold,
        benchmark_pytorch_average_ms=payload.benchmark_pytorch_average_ms,
        benchmark_onnx_average_ms=payload.benchmark_onnx_average_ms,
        benchmark_speedup_vs_pytorch=payload.benchmark_speedup_vs_pytorch,
        benchmark_tensorrt_average_ms=payload.benchmark_tensorrt_average_ms,
        benchmark_tensorrt_speedup_vs_pytorch=payload.benchmark_tensorrt_speedup_vs_pytorch,
    )


def present_model_inventory(payload: ModelInventoryResponse) -> PublicModelInventoryData:
    return PublicModelInventoryData(
        active_model_id=payload.active_model_id,
        active_model_name=payload.active_model_name,
        active_model_type=payload.active_model_type,
        active_class_names=payload.active_class_names,
        models=[present_model_descriptor(item) for item in payload.models],
    )


def _present_model_artifact(path: str, exists: bool, size_mb: float) -> PublicModelArtifact:
    return PublicModelArtifact(name=_artifact_name(path), exists=exists, size_mb=size_mb)


def present_deployment_status(payload: DeploymentStatusResponse) -> PublicDeploymentStatusData:
    return PublicDeploymentStatusData(
        pytorch=_present_model_artifact(payload.pytorch.path, payload.pytorch.exists, payload.pytorch.size_mb),
        onnx=_present_model_artifact(payload.onnx.path, payload.onnx.exists, payload.onnx.size_mb),
        tensorrt=_present_model_artifact(payload.tensorrt.path, payload.tensorrt.exists, payload.tensorrt.size_mb),
        onnx_dependencies_ready=payload.onnx_dependencies_ready,
        tensorrt_dependencies_ready=payload.tensorrt_dependencies_ready,
        onnxruntime_providers=payload.onnxruntime_providers,
    )


def present_onnx_export(payload: OnnxExportResponse) -> PublicOnnxExportData:
    return PublicOnnxExportData(
        status=payload.status,
        onnx=_present_model_artifact(payload.onnx.path, payload.onnx.exists, payload.onnx.size_mb),
        image_size=payload.image_size,
        message=payload.message,
    )


def present_tensorrt_export(payload: TensorRtExportResponse) -> PublicTensorRtExportData:
    return PublicTensorRtExportData(
        status=payload.status,
        tensorrt=_present_model_artifact(payload.tensorrt.path, payload.tensorrt.exists, payload.tensorrt.size_mb),
        image_size=payload.image_size,
        message=payload.message,
    )


def present_prediction(payload: PredictionResponse) -> PublicPredictionData:
    return PublicPredictionData(
        filename=payload.filename,
        model_name=payload.model_name,
        model_type=payload.model_type,
        quality_rule_applied=payload.quality_rule_applied,
        image_size=payload.image_size,
        confidence_threshold=payload.confidence_threshold,
        detections=payload.detections,
        summary=payload.summary,
        report=payload.report,
        artifact_url=payload.artifact_url,
        history_run_id=payload.history_run_id,
    )


def present_batch_prediction(payload: BatchPredictionResponse) -> PublicBatchPredictionData:
    return PublicBatchPredictionData(
        history_run_id=payload.history_run_id,
        active_model_name=payload.active_model_name,
        active_model_type=payload.active_model_type,
        total_files=payload.total_files,
        successful_files=payload.successful_files,
        failed_files=payload.failed_files,
        total_detections=payload.total_detections,
        status_counts=payload.status_counts,
        results=[present_prediction(item) for item in payload.results],
        failures=payload.failures,
        csv_url=payload.csv_url,
        excel_url=payload.excel_url,
    )


def present_benchmark(payload: BenchmarkResponse) -> PublicBenchmarkData:
    return PublicBenchmarkData(
        filename=payload.filename,
        image_size=payload.image_size,
        confidence_threshold=payload.confidence_threshold,
        engines=payload.engines,
        capabilities=payload.capabilities,
        speedup_vs_pytorch=payload.speedup_vs_pytorch,
        tensorrt_speedup_vs_pytorch=payload.tensorrt_speedup_vs_pytorch,
        notes=payload.notes,
    )


def present_dashboard_summary(payload: DashboardSummary) -> PublicDashboardSummary:
    return PublicDashboardSummary(**payload.model_dump())


def present_history_summary(payload: HistoryRunSummary) -> PublicHistoryRunSummary:
    return PublicHistoryRunSummary(**payload.model_dump())


def present_history_detail(payload: HistoryRunDetail) -> PublicHistoryRunDetail:
    return PublicHistoryRunDetail(
        **payload.model_dump(exclude={"items"}),
        items=[PublicHistoryItem(**item.model_dump()) for item in payload.items],
    )


def present_review_summary(payload: ReviewQueueSummary) -> PublicReviewQueueSummary:
    return PublicReviewQueueSummary(**payload.model_dump())


def present_feedback_pool_summary(payload: FeedbackPoolSummary) -> PublicFeedbackPoolSummary:
    return PublicFeedbackPoolSummary(**payload.model_dump())


def present_retrain_catalog_summary(payload: RetrainCatalogSummary) -> PublicRetrainCatalogSummary:
    return PublicRetrainCatalogSummary(**payload.model_dump())


def present_review_item_summary(payload: ReviewItemSummary) -> PublicReviewItemSummary:
    return PublicReviewItemSummary(**payload.model_dump())


def present_review_item_detail(payload: ReviewItemDetail) -> PublicReviewItemDetail:
    return PublicReviewItemDetail(**payload.model_dump())


def present_retrain_catalog_item_summary(payload: RetrainCatalogItemSummary) -> PublicRetrainCatalogItemSummary:
    return PublicRetrainCatalogItemSummary(**payload.model_dump())


def present_retrain_catalog_item_detail(payload: RetrainCatalogItemDetail) -> PublicRetrainCatalogItemDetail:
    return PublicRetrainCatalogItemDetail(**payload.model_dump())


def present_feedback_export(payload: FeedbackExportResponse) -> PublicFeedbackExportData:
    return PublicFeedbackExportData(**payload.model_dump())


def present_retrain_batch_summary(payload: RetrainBatchSummary) -> PublicRetrainBatchSummary:
    return PublicRetrainBatchSummary(**payload.model_dump())


def present_retrain_batch_item_summary(payload: RetrainBatchItemSummary) -> PublicRetrainBatchItemSummary:
    return PublicRetrainBatchItemSummary(**payload.model_dump())


def present_retrain_batch_item_detail(payload: RetrainBatchItemDetail) -> PublicRetrainBatchItemDetail:
    return PublicRetrainBatchItemDetail(
        **payload.model_dump(exclude={"items"}),
        items=[PublicRetrainCatalogItemSummary(**item.model_dump()) for item in payload.items],
    )


def present_retrain_batch_export(payload: RetrainBatchExportResponse) -> PublicRetrainBatchExportData:
    return PublicRetrainBatchExportData(**payload.model_dump())


def _present_storage_artifact(payload: StorageArtifactItem) -> PublicStorageArtifactItem:
    return PublicStorageArtifactItem(**payload.model_dump())


def present_storage_status(payload: StorageStatusResponse) -> PublicStorageStatusData:
    return PublicStorageStatusData(
        artifact_count=payload.artifact_count,
        artifact_total_size_mb=payload.artifact_total_size_mb,
        artifacts=[_present_storage_artifact(item) for item in payload.artifacts],
        history_available=payload.history_db is not None,
    )


def present_cleanup(payload: CleanupResponse) -> PublicCleanupData:
    return PublicCleanupData(**payload.model_dump())


def present_async_task(payload: dict[str, object]) -> PublicAsyncTaskData:
    return PublicAsyncTaskData(
        id=str(payload["id"]),
        kind=str(payload["kind"]),
        status=str(payload["status"]),
        progress=float(payload.get("progress", 0.0)),
        message=payload.get("message"),
        created_at=str(payload["created_at"]),
        started_at=payload.get("started_at"),
        finished_at=payload.get("finished_at"),
        error_code=payload.get("error_code"),
        error_message=payload.get("error_message"),
        error_details=payload.get("error_details"),
        result_payload=payload.get("result_payload"),
    )


def present_history_cleanup(*, deleted_count: int, deleted_run_ids: list[int]) -> PublicHistoryCleanupData:
    return PublicHistoryCleanupData(deleted_count=deleted_count, deleted_run_ids=deleted_run_ids)


def present_quality_rule_settings(payload: QualityRuleSettings) -> PublicQualityRuleSettingsData:
    return PublicQualityRuleSettingsData(
        enabled=payload.enabled,
        fresh_keywords=payload.fresh_keywords,
        rotten_keywords=payload.rotten_keywords,
        pass_max_rotten_rate=payload.pass_max_rotten_rate,
        warning_max_rotten_rate=payload.warning_max_rotten_rate,
        messages=PublicQualityRuleMessages(**payload.messages.model_dump()),
        updated_at=payload.updated_at,
    )
