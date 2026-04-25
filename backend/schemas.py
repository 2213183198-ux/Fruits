from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field, model_validator


class BoundingBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


class DetectionItem(BaseModel):
    class_id: int
    label: str
    confidence: float
    bbox: BoundingBox


class PredictionSummary(BaseModel):
    total_detections: int = Field(ge=0)
    class_counts: Dict[str, int]


class InspectionReport(BaseModel):
    fresh_count: int = Field(ge=0)
    rotten_count: int = Field(ge=0)
    rotten_rate: float = Field(ge=0, le=1)
    status: str
    recommendation: str


class PredictionResponse(BaseModel):
    filename: str
    model_name: str
    model_path: str
    model_type: str
    quality_rule_applied: bool
    image_size: int
    confidence_threshold: float
    detections: List[DetectionItem]
    summary: PredictionSummary
    report: InspectionReport
    artifact_url: Optional[str] = None
    history_run_id: Optional[int] = None


class BatchFailure(BaseModel):
    filename: str
    error: str


class BatchPredictionResponse(BaseModel):
    history_run_id: int
    active_model_name: str
    active_model_type: str
    total_files: int = Field(ge=0)
    successful_files: int = Field(ge=0)
    failed_files: int = Field(ge=0)
    total_detections: int = Field(ge=0)
    status_counts: Dict[str, int]
    results: List[PredictionResponse]
    failures: List[BatchFailure]
    csv_url: Optional[str] = None
    excel_url: Optional[str] = None


class DatasetSummary(BaseModel):
    train_images: int = Field(ge=0)
    val_images: int = Field(ge=0)
    test_images: int = Field(ge=0)
    total_images: int = Field(ge=0)


class TrainingMetrics(BaseModel):
    epochs: int = Field(ge=0)
    precision: float = Field(ge=0)
    recall: float = Field(ge=0)
    map50: float = Field(ge=0)
    map50_95: float = Field(ge=0)


class ProjectMetadataResponse(BaseModel):
    project_name: str
    model_path: str
    model_exists: bool
    model_size_mb: float = Field(ge=0)
    class_names: List[str]
    dataset: DatasetSummary
    metrics: TrainingMetrics
    highlights: List[str]


class ModelArtifact(BaseModel):
    path: str
    exists: bool
    size_mb: float = Field(ge=0)


class DeploymentStatusResponse(BaseModel):
    pytorch: ModelArtifact
    onnx: ModelArtifact
    tensorrt: ModelArtifact
    onnx_dependencies_ready: bool
    tensorrt_dependencies_ready: bool
    onnxruntime_providers: List[str]


class OnnxExportResponse(BaseModel):
    status: str
    onnx: ModelArtifact
    image_size: int = Field(ge=0)
    message: str


class TensorRtExportResponse(BaseModel):
    status: str
    tensorrt: ModelArtifact
    image_size: int = Field(ge=0)
    message: str


class BenchmarkEngineResult(BaseModel):
    engine: str
    runs: int = Field(ge=1)
    average_ms: float = Field(ge=0)
    best_ms: float = Field(ge=0)
    worst_ms: float = Field(ge=0)
    total_detections: int = Field(ge=0)
    class_counts: Dict[str, int]


class BenchmarkEngineCapability(BaseModel):
    engine: str
    implemented: bool
    available: bool
    reason: Optional[str] = None


class BenchmarkResponse(BaseModel):
    filename: str
    image_size: int = Field(ge=0)
    confidence_threshold: float = Field(ge=0, le=1)
    engines: List[BenchmarkEngineResult]
    capabilities: List[BenchmarkEngineCapability] = Field(default_factory=list)
    speedup_vs_pytorch: Optional[float] = None
    tensorrt_speedup_vs_pytorch: Optional[float] = None
    notes: List[str]


class HistoryRunSummary(BaseModel):
    id: int
    mode: str
    created_at: str
    total_files: int = Field(ge=0)
    successful_files: int = Field(ge=0)
    failed_files: int = Field(ge=0)
    total_detections: int = Field(ge=0)
    csv_url: Optional[str] = None
    excel_url: Optional[str] = None


class HistoryItem(BaseModel):
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


class HistoryRunDetail(BaseModel):
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
    items: List[HistoryItem]


class ReviewQueueSummary(BaseModel):
    total: int = Field(ge=0)
    pending: int = Field(ge=0)
    optional: int = Field(ge=0)
    reviewed: int = Field(ge=0)
    feedback: int = Field(ge=0)
    false_positive_count: int = Field(ge=0)
    missed_detection_count: int = Field(ge=0)
    needs_feedback_count: int = Field(ge=0)


class FeedbackPoolSummary(BaseModel):
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


class ReviewItemSummary(BaseModel):
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


class ReviewItemDetail(ReviewItemSummary):
    image_size: int = Field(ge=0)
    confidence_threshold: float = Field(ge=0, le=1)
    review_notes: Optional[str] = None


class RetrainCatalogSummary(BaseModel):
    total: int = Field(ge=0)
    pending: int = Field(ge=0)
    ready: int = Field(ge=0)
    used: int = Field(ge=0)
    false_positive_count: int = Field(ge=0)
    missed_detection_count: int = Field(ge=0)
    needs_feedback_count: int = Field(ge=0)
    latest_updated_at: Optional[str] = None


class RetrainCatalogItemSummary(BaseModel):
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


class RetrainCatalogItemDetail(RetrainCatalogItemSummary):
    recommendation: Optional[str] = None
    error: Optional[str] = None
    review_status: str
    feedback_status: str = "none"
    review_notes: Optional[str] = None
    catalog_notes: Optional[str] = None
    catalog_created_at: str
    annotation_draft: Optional[str] = None


class RetrainCatalogUpsertRequest(BaseModel):
    catalog_status: str = "pending"
    catalog_notes: str = ""
    annotation_draft: Optional[str] = None

    @model_validator(mode="after")
    def validate_status(self) -> "RetrainCatalogUpsertRequest":
        allowed = {"pending", "ready", "used"}
        if self.catalog_status not in allowed:
            raise ValueError(f"catalog_status must be one of: {', '.join(sorted(allowed))}")
        if self.annotation_draft is not None:
            normalized_lines: List[str] = []
            for raw_line in self.annotation_draft.replace("\r\n", "\n").split("\n"):
                line = raw_line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) != 5:
                    raise ValueError("annotation_draft lines must use YOLO format: class x_center y_center width height")
                try:
                    int(parts[0])
                    coords = [float(value) for value in parts[1:]]
                except ValueError as exc:
                    raise ValueError("annotation_draft contains invalid numeric values") from exc
                if any(value < 0 or value > 1 for value in coords):
                    raise ValueError("annotation_draft coordinates must be between 0 and 1")
                normalized_lines.append(
                    f"{int(parts[0])} " + " ".join(f"{value:.6f}".rstrip("0").rstrip(".") for value in coords)
                )
            self.annotation_draft = "\n".join(normalized_lines)
        return self


class RetrainBatchSummary(BaseModel):
    total: int = Field(ge=0)
    draft: int = Field(ge=0)
    exported: int = Field(ge=0)
    total_items: int = Field(ge=0)
    latest_exported_at: Optional[str] = None


class RetrainBatchItemSummary(BaseModel):
    batch_id: int
    batch_name: str
    batch_status: str
    item_count: int = Field(ge=0)
    created_at: str
    updated_at: str
    exported_at: Optional[str] = None
    export_url: Optional[str] = None


class RetrainBatchItemDetail(RetrainBatchItemSummary):
    batch_notes: Optional[str] = None
    export_name: Optional[str] = None
    items: List[RetrainCatalogItemSummary] = Field(default_factory=list)


class RetrainBatchCreateRequest(BaseModel):
    batch_name: str = ""
    batch_notes: str = ""
    item_ids: List[int] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_item_ids(self) -> "RetrainBatchCreateRequest":
        normalized: List[int] = []
        for item_id in self.item_ids:
            try:
                value = int(item_id)
            except (TypeError, ValueError) as exc:
                raise ValueError("item_ids must contain positive integers") from exc
            if value > 0:
                normalized.append(value)
        if not normalized:
            raise ValueError("item_ids must contain at least one positive integer")
        self.item_ids = normalized
        return self


class RetrainBatchExportResponse(BaseModel):
    batch_id: int
    batch_name: str
    export_name: str
    export_url: str
    item_count: int = Field(ge=0)
    exported_at: str
    message: str


class DashboardDailyStat(BaseModel):
    date: str
    run_count: int = Field(ge=0)
    sample_count: int = Field(ge=0)
    detection_count: int = Field(ge=0)
    feedback_count: int = Field(ge=0)
    retrain_count: int = Field(ge=0)


class DashboardSummary(BaseModel):
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
    recent_daily_stats: List[DashboardDailyStat] = Field(default_factory=list)


class FeedbackExportResponse(BaseModel):
    export_name: str
    export_url: str
    item_count: int = Field(ge=0)
    message: str


class ReviewDecisionRequest(BaseModel):
    decision: str
    notes: str = ""
    send_to_feedback: bool = False

    @model_validator(mode="after")
    def validate_decision(self) -> "ReviewDecisionRequest":
        allowed = {"confirm", "false_positive", "missed_detection", "needs_feedback"}
        if self.decision not in allowed:
            raise ValueError(f"decision must be one of: {', '.join(sorted(allowed))}")
        return self


class HealthResponse(BaseModel):
    status: str
    active_model_name: str
    model_path: str
    active_model_type: str
    model_exists: bool
    model_loaded: bool
    active_class_names: List[str] = Field(default_factory=list)


class ModelDescriptor(BaseModel):
    id: str
    name: str
    path: str
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


class ModelInventoryResponse(BaseModel):
    active_model_id: str
    active_model_name: str
    active_model_path: str
    active_model_type: str
    active_class_names: List[str] = Field(default_factory=list)
    models: List[ModelDescriptor]


class ModelUploadResponse(BaseModel):
    message: str
    model: ModelDescriptor


class ActivateModelRequest(BaseModel):
    model_id: str


class ActivateModelResponse(BaseModel):
    active_model_id: str
    active_model_name: str
    active_model_path: str
    active_model_type: str
    active_class_names: List[str] = Field(default_factory=list)
    message: str


class DeleteModelResponse(BaseModel):
    deleted_model_id: str
    deleted_model_name: str
    active_model_id: str
    active_model_name: str
    active_model_type: str
    active_class_names: List[str] = Field(default_factory=list)
    message: str


class StorageArtifactItem(BaseModel):
    name: str
    type: str
    size_mb: float = Field(ge=0)
    download_url: Optional[str] = None


class StorageStatusResponse(BaseModel):
    artifact_count: int = Field(ge=0)
    artifact_total_size_mb: float = Field(ge=0)
    artifacts: List[StorageArtifactItem]
    history_db: Optional[StorageArtifactItem] = None


class CleanupRequest(BaseModel):
    artifact_names: List[str] = Field(default_factory=list)
    delete_all: bool = False
    delete_history: bool = False


class CleanupResponse(BaseModel):
    deleted_files: List[str]
    skipped_files: List[str] = Field(default_factory=list)
    deleted_count: int = Field(ge=0)
    history_cleared: bool
    remaining_count: int = Field(ge=0)


class QualityRuleMessages(BaseModel):
    no_detection: str
    detected_only: str
    pass_message: str
    warning_message: str
    critical_message: str


class QualityRuleSettings(BaseModel):
    enabled: bool = True
    fresh_keywords: List[str] = Field(default_factory=list)
    rotten_keywords: List[str] = Field(default_factory=list)
    pass_max_rotten_rate: float = Field(ge=0, le=1)
    warning_max_rotten_rate: float = Field(ge=0, le=1)
    messages: QualityRuleMessages
    updated_at: Optional[str] = None

    @model_validator(mode="after")
    def validate_thresholds(self) -> "QualityRuleSettings":
        if self.pass_max_rotten_rate > self.warning_max_rotten_rate:
            raise ValueError("pass_max_rotten_rate cannot be greater than warning_max_rotten_rate")
        return self


class QualityRuleSettingsUpdateRequest(BaseModel):
    enabled: bool = True
    fresh_keywords: List[str] = Field(default_factory=list)
    rotten_keywords: List[str] = Field(default_factory=list)
    pass_max_rotten_rate: float = Field(ge=0, le=1)
    warning_max_rotten_rate: float = Field(ge=0, le=1)
    messages: QualityRuleMessages

    @model_validator(mode="after")
    def validate_thresholds(self) -> "QualityRuleSettingsUpdateRequest":
        if self.pass_max_rotten_rate > self.warning_max_rotten_rate:
            raise ValueError("pass_max_rotten_rate cannot be greater than warning_max_rotten_rate")
        return self
