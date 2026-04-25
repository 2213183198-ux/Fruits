from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from backend.schemas import (
    BatchFailure,
    BenchmarkEngineCapability,
    BenchmarkEngineResult,
    DatasetSummary,
    DetectionItem,
    InspectionReport,
    PredictionSummary,
)


class ApiIndexData(BaseModel):
    service_name: str
    api_version: str
    docs_url: str
    redoc_url: str
    openapi_url: str
    api_base_url: str
    capabilities: List[str]


class PublicHealthData(BaseModel):
    status: str
    active_model_name: str
    active_model_type: str
    model_exists: bool
    model_loaded: bool
    active_class_names: List[str] = Field(default_factory=list)


class PublicProjectMetadataData(BaseModel):
    project_name: str
    model_exists: bool
    class_names: List[str] = Field(default_factory=list)
    dataset: DatasetSummary
    highlights: List[str] = Field(default_factory=list)


class PublicModelArtifact(BaseModel):
    name: str
    exists: bool
    size_mb: float = Field(ge=0)


class PublicDeploymentStatusData(BaseModel):
    pytorch: PublicModelArtifact
    onnx: PublicModelArtifact
    tensorrt: PublicModelArtifact
    onnx_dependencies_ready: bool
    tensorrt_dependencies_ready: bool
    onnxruntime_providers: List[str] = Field(default_factory=list)


class PublicOnnxExportData(BaseModel):
    status: str
    onnx: PublicModelArtifact
    image_size: int = Field(ge=0)
    message: str


class PublicTensorRtExportData(BaseModel):
    status: str
    tensorrt: PublicModelArtifact
    image_size: int = Field(ge=0)
    message: str


class PublicBenchmarkData(BaseModel):
    filename: str
    image_size: int = Field(ge=0)
    confidence_threshold: float = Field(ge=0, le=1)
    engines: List[BenchmarkEngineResult]
    capabilities: List[BenchmarkEngineCapability] = Field(default_factory=list)
    speedup_vs_pytorch: Optional[float] = None
    tensorrt_speedup_vs_pytorch: Optional[float] = None
    notes: List[str] = Field(default_factory=list)


class PublicPredictionData(BaseModel):
    filename: str
    model_name: str
    model_type: str
    quality_rule_applied: bool
    image_size: int
    confidence_threshold: float
    detections: List[DetectionItem]
    summary: PredictionSummary
    report: InspectionReport
    artifact_url: Optional[str] = None
    history_run_id: Optional[int] = None


class PublicBatchPredictionData(BaseModel):
    history_run_id: int
    active_model_name: str
    active_model_type: str
    total_files: int = Field(ge=0)
    successful_files: int = Field(ge=0)
    failed_files: int = Field(ge=0)
    total_detections: int = Field(ge=0)
    status_counts: Dict[str, int]
    results: List[PublicPredictionData]
    failures: List[BatchFailure]
    csv_url: Optional[str] = None
    excel_url: Optional[str] = None


class PublicHistoryRunSummary(BaseModel):
    id: int
    mode: str
    created_at: str
    total_files: int = Field(ge=0)
    successful_files: int = Field(ge=0)
    failed_files: int = Field(ge=0)
    total_detections: int = Field(ge=0)
    csv_url: Optional[str] = None
    excel_url: Optional[str] = None


class PublicHistoryItem(BaseModel):
    id: int
    filename: str
    status: str
    total_detections: int = Field(ge=0)
    rotten_rate: float = Field(ge=0, le=1)
    recommendation: Optional[str] = None
    artifact_url: Optional[str] = None
    error: Optional[str] = None
    review_status: str = "optional"
    review_decision: Optional[str] = None
    review_notes: Optional[str] = None
    feedback_status: str = "none"
    review_updated_at: Optional[str] = None


class PublicHistoryRunDetail(BaseModel):
    id: int
    mode: str
    created_at: str
    image_size: int = Field(ge=0)
    confidence_threshold: float = Field(ge=0, le=1)
    total_files: int = Field(ge=0)
    successful_files: int = Field(ge=0)
    failed_files: int = Field(ge=0)
    total_detections: int = Field(ge=0)
    csv_url: Optional[str] = None
    excel_url: Optional[str] = None
    items: List[PublicHistoryItem]


class PublicReviewQueueSummary(BaseModel):
    total: int = Field(ge=0)
    pending: int = Field(ge=0)
    optional: int = Field(ge=0)
    reviewed: int = Field(ge=0)
    feedback: int = Field(ge=0)
    false_positive_count: int = Field(ge=0)
    missed_detection_count: int = Field(ge=0)
    needs_feedback_count: int = Field(ge=0)


class PublicFeedbackPoolSummary(BaseModel):
    total: int = Field(ge=0)
    false_positive_count: int = Field(ge=0)
    missed_detection_count: int = Field(ge=0)
    needs_feedback_count: int = Field(ge=0)
    single_count: int = Field(ge=0)
    batch_count: int = Field(ge=0)
    webcam_count: int = Field(ge=0)
    artifact_ready_count: int = Field(ge=0)
    avg_rotten_rate: float = Field(ge=0, le=1)
    latest_updated_at: Optional[str] = None


class PublicReviewItemSummary(BaseModel):
    item_id: int
    run_id: int
    mode: str
    created_at: str
    filename: str
    source_model_name: Optional[str] = None
    source_model_type: Optional[str] = None
    status: str
    total_detections: int = Field(ge=0)
    rotten_rate: float = Field(ge=0, le=1)
    recommendation: Optional[str] = None
    artifact_url: Optional[str] = None
    error: Optional[str] = None
    review_status: str
    review_decision: Optional[str] = None
    feedback_status: str = "none"
    review_updated_at: Optional[str] = None
    retrain_status: Optional[str] = None
    retrain_updated_at: Optional[str] = None


class PublicReviewItemDetail(PublicReviewItemSummary):
    image_size: int = Field(ge=0)
    confidence_threshold: float = Field(ge=0, le=1)
    review_notes: Optional[str] = None


class PublicRetrainCatalogSummary(BaseModel):
    total: int = Field(ge=0)
    pending: int = Field(ge=0)
    ready: int = Field(ge=0)
    used: int = Field(ge=0)
    false_positive_count: int = Field(ge=0)
    missed_detection_count: int = Field(ge=0)
    needs_feedback_count: int = Field(ge=0)
    latest_updated_at: Optional[str] = None


class PublicRetrainCatalogItemSummary(BaseModel):
    item_id: int
    run_id: int
    mode: str
    source_created_at: str
    filename: str
    source_model_name: Optional[str] = None
    source_model_type: Optional[str] = None
    status: str
    total_detections: int = Field(ge=0)
    rotten_rate: float = Field(ge=0, le=1)
    review_decision: Optional[str] = None
    catalog_status: str
    artifact_url: Optional[str] = None
    catalog_updated_at: str
    batch_id: Optional[int] = None
    batch_name: Optional[str] = None
    batch_status: Optional[str] = None
    batch_export_url: Optional[str] = None
    batch_exported_at: Optional[str] = None
    annotation_status: Optional[str] = None
    annotation_updated_at: Optional[str] = None


class PublicRetrainCatalogItemDetail(PublicRetrainCatalogItemSummary):
    recommendation: Optional[str] = None
    error: Optional[str] = None
    review_status: str
    feedback_status: str = "none"
    review_notes: Optional[str] = None
    catalog_notes: Optional[str] = None
    catalog_created_at: str
    annotation_draft: Optional[str] = None


class PublicFeedbackExportData(BaseModel):
    export_name: str
    export_url: str
    item_count: int = Field(ge=0)
    message: str


class ReviewDecisionRequestBody(BaseModel):
    decision: str
    notes: str = ""
    send_to_feedback: bool = False


class RetrainCatalogUpsertRequestBody(BaseModel):
    catalog_status: str = "pending"
    catalog_notes: str = ""
    annotation_draft: Optional[str] = None


class PublicRetrainBatchSummary(BaseModel):
    total: int = Field(ge=0)
    draft: int = Field(ge=0)
    exported: int = Field(ge=0)
    total_items: int = Field(ge=0)
    latest_exported_at: Optional[str] = None


class PublicRetrainBatchItemSummary(BaseModel):
    batch_id: int
    batch_name: str
    batch_status: str
    item_count: int = Field(ge=0)
    created_at: str
    updated_at: str
    exported_at: Optional[str] = None
    export_url: Optional[str] = None


class PublicRetrainBatchItemDetail(PublicRetrainBatchItemSummary):
    batch_notes: Optional[str] = None
    export_name: Optional[str] = None
    items: List[PublicRetrainCatalogItemSummary] = Field(default_factory=list)


class RetrainBatchCreateRequestBody(BaseModel):
    batch_name: str = ""
    batch_notes: str = ""
    item_ids: List[int] = Field(default_factory=list)


class PublicRetrainBatchExportData(BaseModel):
    batch_id: int
    batch_name: str
    export_name: str
    export_url: str
    item_count: int = Field(ge=0)
    exported_at: str
    message: str


class PublicDashboardDailyStat(BaseModel):
    date: str
    run_count: int = Field(ge=0)
    sample_count: int = Field(ge=0)
    detection_count: int = Field(ge=0)
    feedback_count: int = Field(ge=0)
    retrain_count: int = Field(ge=0)


class PublicDashboardSummary(BaseModel):
    total_runs: int = Field(ge=0)
    total_samples: int = Field(ge=0)
    successful_samples: int = Field(ge=0)
    failed_samples: int = Field(ge=0)
    success_rate: float = Field(ge=0, le=1)
    total_detections: int = Field(ge=0)
    avg_detections_per_run: float = Field(ge=0)
    avg_samples_per_run: float = Field(ge=0)
    latest_run_at: Optional[str] = None
    quality_status_counts: Dict[str, int] = Field(default_factory=dict)
    mode_sample_counts: Dict[str, int] = Field(default_factory=dict)
    review_pending_count: int = Field(ge=0)
    reviewed_count: int = Field(ge=0)
    feedback_queued_count: int = Field(ge=0)
    retrain_pending_count: int = Field(ge=0)
    retrain_ready_count: int = Field(ge=0)
    retrain_used_count: int = Field(ge=0)
    recent_daily_stats: List[PublicDashboardDailyStat] = Field(default_factory=list)


class PublicModelDescriptor(BaseModel):
    id: str
    name: str
    type: str
    size_mb: float = Field(ge=0)
    source: str
    is_default: bool
    is_active: bool
    can_delete: bool = False
    yaml_name: Optional[str] = None
    class_names: List[str] = Field(default_factory=list)
    benchmarked_at: Optional[str] = None
    benchmark_image_size: Optional[int] = None
    benchmark_confidence_threshold: Optional[float] = None
    benchmark_pytorch_average_ms: Optional[float] = None
    benchmark_onnx_average_ms: Optional[float] = None
    benchmark_speedup_vs_pytorch: Optional[float] = None
    benchmark_tensorrt_average_ms: Optional[float] = None
    benchmark_tensorrt_speedup_vs_pytorch: Optional[float] = None


class PublicModelInventoryData(BaseModel):
    active_model_id: str
    active_model_name: str
    active_model_type: str
    active_class_names: List[str] = Field(default_factory=list)
    models: List[PublicModelDescriptor]


class PublicStorageArtifactItem(BaseModel):
    name: str
    type: str
    size_mb: float = Field(ge=0)
    download_url: Optional[str] = None


class PublicStorageStatusData(BaseModel):
    artifact_count: int = Field(ge=0)
    artifact_total_size_mb: float = Field(ge=0)
    artifacts: List[PublicStorageArtifactItem]
    history_available: bool = False


class PublicCleanupData(BaseModel):
    deleted_files: List[str]
    skipped_files: List[str] = Field(default_factory=list)
    deleted_count: int = Field(ge=0)
    history_cleared: bool
    remaining_count: int = Field(ge=0)


class PublicAsyncTaskData(BaseModel):
    id: str
    kind: str
    status: str
    progress: float = Field(ge=0, le=100)
    message: Optional[str] = None
    created_at: str
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    error_details: Dict[str, object] | List[object] | None = None
    result_payload: Dict[str, object] | List[object] | None = None


class HistoryCleanupRequestBody(BaseModel):
    run_ids: List[int] = Field(default_factory=list)
    created_from: Optional[str] = None
    created_to: Optional[str] = None
    delete_all: bool = False


class PublicHistoryCleanupData(BaseModel):
    deleted_count: int = Field(ge=0)
    deleted_run_ids: List[int] = Field(default_factory=list)


class PublicQualityRuleMessages(BaseModel):
    no_detection: str
    detected_only: str
    pass_message: str
    warning_message: str
    critical_message: str


class PublicQualityRuleSettingsData(BaseModel):
    enabled: bool = True
    fresh_keywords: List[str] = Field(default_factory=list)
    rotten_keywords: List[str] = Field(default_factory=list)
    pass_max_rotten_rate: float = Field(ge=0, le=1)
    warning_max_rotten_rate: float = Field(ge=0, le=1)
    messages: PublicQualityRuleMessages
    updated_at: Optional[str] = None


class QualityRuleSettingsUpdateBody(BaseModel):
    enabled: bool = True
    fresh_keywords: List[str] = Field(default_factory=list)
    rotten_keywords: List[str] = Field(default_factory=list)
    pass_max_rotten_rate: float = Field(ge=0, le=1)
    warning_max_rotten_rate: float = Field(ge=0, le=1)
    messages: PublicQualityRuleMessages
