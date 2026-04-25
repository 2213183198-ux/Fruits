from __future__ import annotations

from collections import Counter
from pathlib import Path
from threading import Lock
import time
from typing import Any

from fastapi import UploadFile

from backend.app.core.errors import AppError
from backend.config import settings
from backend.schemas import (
    ActivateModelResponse,
    BatchPredictionResponse,
    BenchmarkResponse,
    CleanupRequest,
    CleanupResponse,
    DashboardSummary,
    DeleteModelResponse,
    DeploymentStatusResponse,
    FeedbackExportResponse,
    FeedbackPoolSummary,
    HealthResponse,
    HistoryRunDetail,
    HistoryRunSummary,
    ModelInventoryResponse,
    ModelUploadResponse,
    OnnxExportResponse,
    PredictionResponse,
    ProjectMetadataResponse,
    QualityRuleSettings,
    QualityRuleSettingsUpdateRequest,
    ReviewDecisionRequest,
    ReviewItemDetail,
    ReviewItemSummary,
    ReviewQueueSummary,
    RetrainBatchCreateRequest,
    RetrainBatchExportResponse,
    RetrainBatchItemDetail,
    RetrainBatchItemSummary,
    RetrainBatchSummary,
    RetrainCatalogItemDetail,
    RetrainCatalogItemSummary,
    RetrainCatalogSummary,
    RetrainCatalogUpsertRequest,
    StorageStatusResponse,
    TensorRtExportResponse,
)
from backend.services.deployment import deployment_service
from backend.services.history import history_service
from backend.services.inference import inference_service
from backend.services.maintenance import MaintenanceService
from backend.services.metadata import get_project_metadata
from backend.services.model_registry import ModelRegistryService
from backend.services.quality_rules import quality_rule_service
from backend.services.tasks import TaskService


SUPPORTED_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


class PlatformRuntime:
    def __init__(self) -> None:
        self.settings = settings
        self.frontend_dir = settings.project_root / "frontend"
        self.index_file = self.frontend_dir / "index.html"
        self.maintenance_service = MaintenanceService(settings.artifacts_dir, settings.history_db_path, history_service)
        self.model_registry_service = ModelRegistryService(
            settings.model_path,
            settings.model_store_dir,
            settings.data_config_path,
        )
        self.history_service = history_service
        self.quality_rule_service = quality_rule_service
        self.inference_service = inference_service
        self.deployment_service = deployment_service
        self.task_service = TaskService(settings.history_db_path, max_workers=settings.background_task_workers)
        self._execution_lock = Lock()
        self.inference_service.set_quality_rule_settings(self.quality_rule_service.get_settings())
        self.sync_active_runtime_targets()

    def get_index_file(self) -> Path:
        if not self.index_file.exists():
            raise AppError(status_code=500, code="frontend_missing", message="前端页面不存在。")
        return self.index_file

    def get_api_index(self) -> dict[str, object]:
        return {
            "service_name": "面向生鲜分拣场景的多模型视觉质检与自动化回流平台 API",
            "api_version": "v1",
            "docs_url": "/docs",
            "redoc_url": "/redoc",
            "openapi_url": "/openapi.json",
            "api_base_url": "/api/v1",
            "capabilities": [
                "模型管理",
                "单图质检",
                "批量质检",
                "部署状态与导出",
                "性能评测",
                "历史记录与清理",
                "人工复核与样本回流",
                "复训目录追踪",
                "训练批次与模型迭代记录",
            ],
        }

    def sync_active_runtime_targets(self) -> dict[str, object]:
        active = self.model_registry_service.get_active_descriptor()
        active_path = Path(active["path"])
        self.inference_service.set_model_path(active_path)
        self.inference_service.set_class_names_override(active.get("class_names", []))
        self.inference_service.set_quality_rule_settings(self.quality_rule_service.get_settings())
        pytorch_path, onnx_path, tensorrt_path = self._resolve_deployment_targets(active_path, str(active["type"]))
        self.deployment_service.set_model_targets(pytorch_path, onnx_path, tensorrt_path)
        return active

    def get_health(self) -> HealthResponse:
        inventory = self.model_registry_service.get_inventory()
        return HealthResponse(
            status="ok",
            active_model_name=inventory["active_model_name"],
            model_path=inventory["active_model_path"],
            active_model_type=inventory["active_model_type"],
            model_exists=Path(inventory["active_model_path"]).exists(),
            model_loaded=self.inference_service.model_loaded,
            active_class_names=inventory["active_class_names"],
        )

    def list_models(self) -> ModelInventoryResponse:
        return ModelInventoryResponse(**self.model_registry_service.get_inventory())

    async def upload_model(self, file: UploadFile, yaml_file: UploadFile | None = None) -> ModelUploadResponse:
        payload = await self._read_required_upload_bytes(file, error_code="model_upload_invalid")
        yaml_payload = None
        yaml_filename = None
        if yaml_file and yaml_file.filename:
            yaml_payload = await yaml_file.read()
            yaml_filename = yaml_file.filename

        try:
            model = self.model_registry_service.save_upload(
                file.filename or "",
                payload,
                yaml_filename=yaml_filename,
                yaml_payload=yaml_payload,
            )
        except ValueError as exc:
            raise AppError(status_code=400, code="model_upload_invalid", message=str(exc)) from exc

        return ModelUploadResponse(message="模型上传成功，请在列表中启用。", model=model)

    def activate_model(self, model_id: str) -> ActivateModelResponse:
        current_inventory = self.model_registry_service.get_inventory()
        previous_model_id = current_inventory["active_model_id"]
        previous_model_path = Path(current_inventory["active_model_path"])
        previous_model_classes = current_inventory["active_class_names"]

        try:
            self.model_registry_service.activate(model_id)
            self.sync_active_runtime_targets()
            self.inference_service.load_model()
        except ValueError as exc:
            raise AppError(status_code=400, code="model_not_found", message=str(exc)) from exc
        except Exception as exc:
            self.model_registry_service.activate(previous_model_id)
            self.inference_service.set_model_path(previous_model_path)
            self.inference_service.set_class_names_override(previous_model_classes)
            fallback_active = self.model_registry_service.get_active_descriptor()
            pytorch_path, onnx_path, tensorrt_path = self._resolve_deployment_targets(previous_model_path, str(fallback_active["type"]))
            self.deployment_service.set_model_targets(pytorch_path, onnx_path, tensorrt_path)
            raise AppError(status_code=400, code="model_activate_failed", message=f"模型启用失败：{exc}") from exc

        inventory = self.model_registry_service.get_inventory()
        return ActivateModelResponse(
            active_model_id=inventory["active_model_id"],
            active_model_name=inventory["active_model_name"],
            active_model_path=inventory["active_model_path"],
            active_model_type=inventory["active_model_type"],
            active_class_names=inventory["active_class_names"],
            message="模型已切换，后续检测任务将使用新模型。",
        )

    def delete_model(self, model_id: str) -> DeleteModelResponse:
        try:
            result = self.model_registry_service.delete(model_id)
            self.sync_active_runtime_targets()
        except ValueError as exc:
            raise AppError(status_code=400, code="model_delete_invalid", message=str(exc)) from exc
        except Exception as exc:
            raise AppError(status_code=500, code="model_delete_failed", message=f"模型删除失败：{exc}") from exc

        return DeleteModelResponse(**result)

    def get_metadata(self) -> ProjectMetadataResponse:
        return ProjectMetadataResponse(**get_project_metadata())

    def get_quality_rule_settings(self) -> QualityRuleSettings:
        return self.quality_rule_service.get_settings()

    def update_quality_rule_settings(self, payload: QualityRuleSettingsUpdateRequest) -> QualityRuleSettings:
        try:
            settings_payload = self.quality_rule_service.update_settings(payload)
        except ValueError as exc:
            raise AppError(status_code=400, code="quality_rule_invalid", message=str(exc)) from exc
        self.inference_service.set_quality_rule_settings(settings_payload)
        return settings_payload

    def get_deployment_status(self) -> DeploymentStatusResponse:
        return DeploymentStatusResponse(**self.deployment_service.get_status())

    def list_history_runs(self, limit: int = 10) -> list[HistoryRunSummary]:
        if limit < 1 or limit > 100:
            raise AppError(status_code=400, code="limit_invalid", message="limit 必须在 1 到 100 之间。")
        return [HistoryRunSummary(**item) for item in self.history_service.list_runs(limit=limit)]

    def get_history_run(self, run_id: int) -> HistoryRunDetail:
        payload = self.history_service.get_run(run_id)
        if payload is None:
            raise AppError(status_code=404, code="history_run_not_found", message="未找到对应历史记录。")
        return HistoryRunDetail(**payload)

    def get_review_summary(self) -> ReviewQueueSummary:
        return ReviewQueueSummary(**self.history_service.get_review_summary())

    def get_feedback_pool_summary(
        self,
        *,
        decision: str | None = None,
        mode: str | None = None,
        keyword: str | None = None,
    ) -> FeedbackPoolSummary:
        try:
            return FeedbackPoolSummary(
                **self.history_service.get_feedback_pool_summary(
                    decision=decision,
                    mode=mode,
                    keyword=keyword,
                )
            )
        except ValueError as exc:
            raise AppError(status_code=400, code="review_queue_invalid", message=str(exc)) from exc

    def list_review_items(
        self,
        *,
        limit: int = 30,
        queue: str = "focus",
        decision: str | None = None,
        mode: str | None = None,
        keyword: str | None = None,
    ) -> list[ReviewItemSummary]:
        if limit < 1 or limit > 100:
            raise AppError(status_code=400, code="limit_invalid", message="limit 必须在 1 到 100 之间。")
        try:
            return [
                ReviewItemSummary(**item)
                for item in self.history_service.list_review_items(
                    limit=limit,
                    queue=queue,
                    decision=decision,
                    mode=mode,
                    keyword=keyword,
                )
            ]
        except ValueError as exc:
            raise AppError(status_code=400, code="review_queue_invalid", message=str(exc)) from exc

    def get_review_item(self, item_id: int) -> ReviewItemDetail:
        payload = self.history_service.get_review_item(item_id)
        if payload is None:
            raise AppError(status_code=404, code="review_item_not_found", message="未找到对应复核样本。")
        return ReviewItemDetail(**payload)

    def save_review_decision(self, item_id: int, payload: ReviewDecisionRequest) -> ReviewItemDetail:
        updated = self.history_service.save_review_decision(
            item_id,
            decision=payload.decision,
            notes=payload.notes,
            send_to_feedback=payload.send_to_feedback,
        )
        if updated is None:
            raise AppError(status_code=404, code="review_item_not_found", message="未找到对应复核样本。")
        return ReviewItemDetail(**updated)

    def export_feedback_manifest(
        self,
        *,
        decision: str | None = None,
        mode: str | None = None,
        keyword: str | None = None,
    ) -> FeedbackExportResponse:
        try:
            return FeedbackExportResponse(
                **self.history_service.export_feedback_manifest(
                    decision=decision,
                    mode=mode,
                    keyword=keyword,
                )
            )
        except ValueError as exc:
            raise AppError(status_code=400, code="review_queue_invalid", message=str(exc)) from exc

    def get_dashboard_summary(self, *, days: int = 7) -> DashboardSummary:
        try:
            return DashboardSummary(**self.history_service.get_dashboard_summary(days=days))
        except ValueError as exc:
            raise AppError(status_code=400, code="dashboard_invalid", message=str(exc)) from exc

    def get_retrain_catalog_summary(
        self,
        *,
        status: str | None = None,
        decision: str | None = None,
        mode: str | None = None,
        keyword: str | None = None,
    ) -> RetrainCatalogSummary:
        try:
            return RetrainCatalogSummary(
                **self.history_service.get_retrain_catalog_summary(
                    status=status,
                    decision=decision,
                    mode=mode,
                    keyword=keyword,
                )
            )
        except ValueError as exc:
            raise AppError(status_code=400, code="retrain_catalog_invalid", message=str(exc)) from exc

    def list_retrain_catalog_items(
        self,
        *,
        limit: int = 50,
        status: str | None = None,
        decision: str | None = None,
        mode: str | None = None,
        keyword: str | None = None,
    ) -> list[RetrainCatalogItemSummary]:
        if limit < 1 or limit > 100:
            raise AppError(status_code=400, code="limit_invalid", message="limit 必须在 1 到 100 之间。")
        try:
            return [
                RetrainCatalogItemSummary(**item)
                for item in self.history_service.list_retrain_catalog_items(
                    limit=limit,
                    status=status,
                    decision=decision,
                    mode=mode,
                    keyword=keyword,
                )
            ]
        except ValueError as exc:
            raise AppError(status_code=400, code="retrain_catalog_invalid", message=str(exc)) from exc

    def get_retrain_catalog_item(self, item_id: int) -> RetrainCatalogItemDetail:
        payload = self.history_service.get_retrain_catalog_item(item_id)
        if payload is None:
            raise AppError(status_code=404, code="retrain_item_not_found", message="未找到对应复训样本。")
        return RetrainCatalogItemDetail(**payload)

    def upsert_retrain_catalog_item(self, item_id: int, payload: RetrainCatalogUpsertRequest) -> RetrainCatalogItemDetail:
        try:
            updated = self.history_service.upsert_retrain_catalog_item(
                item_id,
                catalog_status=payload.catalog_status,
                catalog_notes=payload.catalog_notes,
                annotation_draft=payload.annotation_draft,
            )
        except ValueError as exc:
            raise AppError(status_code=400, code="retrain_catalog_invalid", message=str(exc)) from exc
        if updated is None:
            raise AppError(status_code=404, code="retrain_item_not_found", message="未找到对应复训样本。")
        return RetrainCatalogItemDetail(**updated)

    def get_retrain_batch_summary(self) -> RetrainBatchSummary:
        return RetrainBatchSummary(**self.history_service.get_retrain_batch_summary())

    def list_retrain_batches(self, *, limit: int = 10) -> list[RetrainBatchItemSummary]:
        if limit < 1 or limit > 100:
            raise AppError(status_code=400, code="limit_invalid", message="limit must be between 1 and 100.")
        return [RetrainBatchItemSummary(**item) for item in self.history_service.list_retrain_batches(limit=limit)]

    def get_retrain_batch(self, batch_id: int) -> RetrainBatchItemDetail:
        payload = self.history_service.get_retrain_batch(batch_id)
        if payload is None:
            raise AppError(status_code=404, code="retrain_batch_not_found", message="未找到对应训练批次。")
        return RetrainBatchItemDetail(
            **payload,
            items=[RetrainCatalogItemSummary(**item) for item in payload.get("items", [])],
        )

    def create_retrain_batch(self, payload: RetrainBatchCreateRequest) -> RetrainBatchItemDetail:
        try:
            created = self.history_service.create_retrain_batch(
                batch_name=payload.batch_name,
                batch_notes=payload.batch_notes,
                item_ids=payload.item_ids,
            )
        except ValueError as exc:
            raise AppError(status_code=400, code="retrain_batch_invalid", message=str(exc)) from exc
        return RetrainBatchItemDetail(
            **created,
            items=[RetrainCatalogItemSummary(**item) for item in created.get("items", [])],
        )

    def export_retrain_batch(self, batch_id: int) -> RetrainBatchExportResponse:
        try:
            payload = self.history_service.export_retrain_batch(batch_id)
        except ValueError as exc:
            raise AppError(status_code=400, code="retrain_batch_invalid", message=str(exc)) from exc
        if payload is None:
            raise AppError(status_code=404, code="retrain_batch_not_found", message="未找到对应训练批次。")
        return RetrainBatchExportResponse(**payload)

    def get_storage_status(self) -> StorageStatusResponse:
        return StorageStatusResponse(**self.maintenance_service.get_storage_status())

    def cleanup_storage(self, payload: CleanupRequest) -> CleanupResponse:
        if not payload.delete_all and not payload.artifact_names and not payload.delete_history:
            raise AppError(status_code=400, code="cleanup_invalid", message="至少需要选择文件或勾选清空历史。")
        result = self.maintenance_service.cleanup(
            artifact_names=payload.artifact_names,
            delete_all=payload.delete_all,
            delete_history=payload.delete_history,
        )
        return CleanupResponse(**result)

    def list_tasks(self, *, limit: int = 20, kind: str | None = None, status: str | None = None) -> list[dict[str, Any]]:
        return self.task_service.list_tasks(limit=limit, kind=kind, status=status)

    def get_task(self, task_id: str) -> dict[str, Any]:
        return self.task_service.get_task(task_id)

    def export_onnx(self, imgsz: int) -> OnnxExportResponse:
        self._validate_imgsz(imgsz)
        try:
            return OnnxExportResponse(**self.deployment_service.export_onnx(imgsz=imgsz))
        except FileNotFoundError as exc:
            raise AppError(status_code=500, code="onnx_export_unavailable", message=str(exc)) from exc
        except RuntimeError as exc:
            raise AppError(status_code=500, code="onnx_dependency_missing", message=str(exc)) from exc
        except Exception as exc:
            raise AppError(status_code=500, code="onnx_export_failed", message=f"ONNX 导出失败：{exc}") from exc

    def export_tensorrt(self, imgsz: int) -> TensorRtExportResponse:
        self._validate_imgsz(imgsz)
        try:
            return TensorRtExportResponse(**self.deployment_service.export_tensorrt(imgsz=imgsz))
        except FileNotFoundError as exc:
            raise AppError(status_code=500, code="tensorrt_export_unavailable", message=str(exc)) from exc
        except RuntimeError as exc:
            raise AppError(status_code=500, code="tensorrt_dependency_missing", message=str(exc)) from exc
        except Exception as exc:
            raise AppError(status_code=500, code="tensorrt_export_failed", message=f"TensorRT 导出失败：{exc}") from exc

    async def benchmark(self, file: UploadFile, imgsz: int, conf: float, runs: int) -> BenchmarkResponse:
        payload = await self._read_required_upload_bytes(file, error_code="benchmark_file_invalid", require_image=True)
        self._validate_imgsz(imgsz)
        self._validate_conf(conf)
        self._validate_runs(runs)

        try:
            result = self.deployment_service.benchmark_bytes(
                file_bytes=payload,
                filename=file.filename or "",
                imgsz=imgsz,
                conf=conf,
                runs=runs,
            )
            self._record_active_model_benchmark(result, imgsz=imgsz, conf=conf)
            return BenchmarkResponse(**result)
        except ValueError as exc:
            raise AppError(status_code=400, code="benchmark_invalid", message=str(exc)) from exc
        except FileNotFoundError as exc:
            raise AppError(status_code=500, code="benchmark_model_missing", message=str(exc)) from exc
        except Exception as exc:
            raise AppError(status_code=500, code="benchmark_failed", message=f"Benchmark 执行失败：{exc}") from exc

    async def create_benchmark_task(
        self,
        file: UploadFile,
        imgsz: int,
        conf: float,
        runs: int,
    ) -> dict[str, Any]:
        payload = await self._read_required_upload_bytes(file, error_code="benchmark_file_invalid", require_image=True)
        self._validate_imgsz(imgsz)
        self._validate_conf(conf)
        self._validate_runs(runs)

        filename = file.filename or "benchmark_image"

        def runner(reporter) -> dict[str, Any]:
            reporter.progress(10, message="Benchmark 任务已启动。")
            with self._execution_lock:
                reporter.progress(45, message="正在执行模型基准测试。")
                result = self.deployment_service.benchmark_bytes(
                    file_bytes=payload,
                    filename=filename,
                    imgsz=imgsz,
                    conf=conf,
                    runs=runs,
                )
                self._record_active_model_benchmark(result, imgsz=imgsz, conf=conf)
            reporter.progress(90, message="正在整理 benchmark 输出。")
            return result

        return self.task_service.submit(
            kind="benchmark",
            runner=runner,
            request_payload={
                "filename": filename,
                "imgsz": imgsz,
                "conf": conf,
                "runs": runs,
            },
        )

    async def predict_image(
        self,
        file: UploadFile,
        imgsz: int,
        conf: float,
        save_artifact: bool,
        record_history: bool,
    ) -> PredictionResponse:
        payload = await self._read_required_upload_bytes(file, error_code="image_invalid", require_image=True)
        self._validate_imgsz(imgsz)
        self._validate_conf(conf)

        try:
            result = self.inference_service.predict_bytes(
                file_bytes=payload,
                filename=file.filename or "",
                imgsz=imgsz,
                conf=conf,
                save_artifact=save_artifact,
            )
            if record_history:
                run_id = self.history_service.record_run(
                    mode="single",
                    image_size=imgsz,
                    confidence_threshold=conf,
                    results=[result],
                    failures=[],
                    source_model_name=self.inference_service.get_model_name(),
                    source_model_type=self.inference_service.get_model_type(),
                )
                result["history_run_id"] = run_id
            return PredictionResponse(**result)
        except FileNotFoundError as exc:
            raise AppError(status_code=500, code="model_missing", message=str(exc)) from exc
        except ValueError as exc:
            raise AppError(status_code=400, code="image_invalid", message=str(exc)) from exc
        except Exception as exc:
            raise AppError(status_code=500, code="predict_image_failed", message=f"单图检测失败：{exc}") from exc

    def predict_webcam_frame(self, frame_bytes: bytes, imgsz: int, conf: float) -> PredictionResponse:
        self._validate_imgsz(imgsz)
        self._validate_conf(conf)

        try:
            with self._execution_lock:
                result = self.inference_service.predict_bytes(
                    file_bytes=frame_bytes,
                    filename="webcam.jpg",
                    imgsz=imgsz,
                    conf=conf,
                    save_artifact=False,
                )
            return PredictionResponse(**result)
        except FileNotFoundError as exc:
            raise AppError(status_code=500, code="model_missing", message=str(exc)) from exc
        except ValueError as exc:
            raise AppError(status_code=400, code="image_invalid", message=str(exc)) from exc
        except Exception as exc:
            raise AppError(status_code=500, code="webcam_predict_failed", message=f"摄像头检测失败：{exc}") from exc

    async def predict_batch(
        self,
        files: list[UploadFile],
        imgsz: int,
        conf: float,
        save_artifact: bool,
        export_csv: bool,
        export_excel: bool,
    ) -> BatchPredictionResponse:
        if not files:
            raise AppError(status_code=400, code="batch_empty", message="至少需要上传一张图片。")

        self._validate_imgsz(imgsz)
        self._validate_conf(conf)

        results: list[PredictionResponse] = []
        failures: list[dict[str, str]] = []
        total_detections = 0
        status_counts: Counter[str] = Counter()

        for file in files:
            filename = file.filename or "unnamed_file"
            try:
                self._ensure_supported_image_upload(file)
                payload = await file.read()
                result = self.inference_service.predict_bytes(
                    file_bytes=payload,
                    filename=filename,
                    imgsz=imgsz,
                    conf=conf,
                    save_artifact=save_artifact,
                )
                prediction = PredictionResponse(**result)
                results.append(prediction)
                total_detections += prediction.summary.total_detections
                status_counts[prediction.report.status] += 1
            except Exception as exc:
                failures.append({"filename": filename, "error": str(exc)})

        csv_url = None
        if export_csv and results:
            csv_url = self.inference_service.export_batch_csv([item.model_dump() for item in results])

        excel_url = None
        if export_excel and results:
            excel_url = self.inference_service.export_batch_excel(
                results=[item.model_dump() for item in results],
                failures=failures,
                total_files=len(files),
            )

        run_id = self.history_service.record_run(
            mode="batch",
            image_size=imgsz,
            confidence_threshold=conf,
            results=[item.model_dump() for item in results],
            failures=failures,
            csv_url=csv_url,
            excel_url=excel_url,
            source_model_name=self.inference_service.get_model_name(),
            source_model_type=self.inference_service.get_model_type(),
        )

        return BatchPredictionResponse(
            history_run_id=run_id,
            active_model_name=self.inference_service.get_model_name(),
            active_model_type=self.inference_service.get_model_type(),
            total_files=len(files),
            successful_files=len(results),
            failed_files=len(failures),
            total_detections=total_detections,
            status_counts=dict(sorted(status_counts.items())),
            results=results,
            failures=failures,
            csv_url=csv_url,
            excel_url=excel_url,
        )

    async def create_batch_inference_task(
        self,
        files: list[UploadFile],
        imgsz: int,
        conf: float,
        save_artifact: bool,
        export_csv: bool,
        export_excel: bool,
    ) -> dict[str, Any]:
        if not files:
            raise AppError(status_code=400, code="batch_empty", message="至少需要上传一张图片。")

        self._validate_imgsz(imgsz)
        self._validate_conf(conf)

        buffered_files: list[dict[str, Any]] = []
        for file in files:
            payload = await self._read_required_upload_bytes(file, error_code="image_invalid", require_image=True)
            buffered_files.append(
                {
                    "filename": file.filename or "unnamed_file",
                    "content_type": file.content_type,
                    "payload": payload,
                }
            )

        def runner(reporter) -> dict[str, Any]:
            results: list[PredictionResponse] = []
            failures: list[dict[str, str]] = []
            total_detections = 0
            status_counts: Counter[str] = Counter()
            total_files = len(buffered_files)

            reporter.progress(5, message="批量检测任务已启动。")
            with self._execution_lock:
                for index, item in enumerate(buffered_files, start=1):
                    try:
                        result = self.inference_service.predict_bytes(
                            file_bytes=item["payload"],
                            filename=item["filename"],
                            imgsz=imgsz,
                            conf=conf,
                            save_artifact=save_artifact,
                        )
                        prediction = PredictionResponse(**result)
                        results.append(prediction)
                        total_detections += prediction.summary.total_detections
                        status_counts[prediction.report.status] += 1
                    except Exception as exc:
                        failures.append({"filename": item["filename"], "error": str(exc)})

                    reporter.progress(
                        5 + (index / total_files) * 75,
                        message=f"正在处理第 {index}/{total_files} 个文件。",
                    )

            csv_url = None
            if export_csv and results:
                reporter.progress(84, message="正在生成 CSV 报告。")
                csv_url = self.inference_service.export_batch_csv([entry.model_dump() for entry in results])

            excel_url = None
            if export_excel and results:
                reporter.progress(92, message="正在生成 Excel 报告。")
                excel_url = self.inference_service.export_batch_excel(
                    results=[entry.model_dump() for entry in results],
                    failures=failures,
                    total_files=total_files,
                )

            run_id = self.history_service.record_run(
                mode="batch",
                image_size=imgsz,
                confidence_threshold=conf,
                results=[entry.model_dump() for entry in results],
                failures=failures,
                csv_url=csv_url,
                excel_url=excel_url,
                source_model_name=self.inference_service.get_model_name(),
                source_model_type=self.inference_service.get_model_type(),
            )

            reporter.progress(98, message="正在写入历史记录。")
            return {
                "history_run_id": run_id,
                "active_model_name": self.inference_service.get_model_name(),
                "active_model_type": self.inference_service.get_model_type(),
                "total_files": total_files,
                "successful_files": len(results),
                "failed_files": len(failures),
                "total_detections": total_detections,
                "status_counts": dict(sorted(status_counts.items())),
                "results": [entry.model_dump() for entry in results],
                "failures": failures,
                "csv_url": csv_url,
                "excel_url": excel_url,
            }

        return self.task_service.submit(
            kind="batch_inference",
            runner=runner,
            request_payload={
                "file_count": len(buffered_files),
                "filenames": [item["filename"] for item in buffered_files],
                "imgsz": imgsz,
                "conf": conf,
                "save_artifact": save_artifact,
                "export_csv": export_csv,
                "export_excel": export_excel,
            },
        )

    def cleanup_history_runs(
        self,
        *,
        run_ids: list[int] | None = None,
        created_from: str | None = None,
        created_to: str | None = None,
        delete_all: bool = False,
    ) -> dict[str, Any]:
        deleted_run_ids: list[int] = []

        if delete_all:
            deleted_run_ids = [item.id for item in self.list_history_runs(limit=1000)]
            self.history_service.reset_history()
            return {"deleted_count": len(deleted_run_ids), "deleted_run_ids": deleted_run_ids}

        if run_ids:
            normalized_ids = sorted({int(run_id) for run_id in run_ids if int(run_id) > 0})
            deleted_count = self.history_service.delete_runs(normalized_ids)
            return {"deleted_count": deleted_count, "deleted_run_ids": normalized_ids[:deleted_count] if deleted_count else []}

        if created_from or created_to:
            matched_runs = self.history_service.list_runs(limit=1000)
            matched_ids = [
                int(item["id"])
                for item in matched_runs
                if (created_from is None or item["created_at"] >= created_from)
                and (created_to is None or item["created_at"] <= created_to)
            ]
            deleted_count = self.history_service.delete_runs_by_time_range(
                created_from=created_from,
                created_to=created_to,
            )
            return {"deleted_count": deleted_count, "deleted_run_ids": matched_ids[:deleted_count] if deleted_count else []}

        raise AppError(
            status_code=400,
            code="history_cleanup_invalid",
            message="请提供 run_ids、时间范围，或显式指定 delete_all。",
        )

    def _resolve_deployment_targets(self, active_path: Path, active_type: str) -> tuple[Path | None, Path | None, Path | None]:
        if active_type == "pytorch":
            return active_path, active_path.with_suffix(".onnx"), active_path.with_suffix(".engine")
        if active_type == "onnx":
            sibling_pt = active_path.with_suffix(".pt")
            return (sibling_pt if sibling_pt.exists() else None), active_path, active_path.with_suffix(".engine")
        if active_type == "engine":
            sibling_pt = active_path.with_suffix(".pt")
            sibling_onnx = active_path.with_suffix(".onnx")
            return (
                sibling_pt if sibling_pt.exists() else None,
                sibling_onnx if sibling_onnx.exists() else None,
                active_path,
            )
        return None, None, None

    def _ensure_supported_image_upload(self, file: UploadFile) -> None:
        suffix = Path(file.filename or "").suffix.lower()
        if suffix in SUPPORTED_IMAGE_SUFFIXES:
            return
        if file.content_type and file.content_type.startswith("image/"):
            return
        raise AppError(status_code=400, code="image_invalid", message="只支持图片文件。")

    async def _read_required_upload_bytes(
        self,
        file: UploadFile,
        *,
        error_code: str,
        require_image: bool = False,
    ) -> bytes:
        if not file.filename:
            raise AppError(status_code=400, code=error_code, message="缺少文件名。")
        if require_image:
            self._ensure_supported_image_upload(file)
        payload = await file.read()
        if not payload:
            raise AppError(status_code=400, code=error_code, message="上传的文件为空。")
        return payload

    def _validate_imgsz(self, imgsz: int) -> None:
        if imgsz < 320 or imgsz > 1280:
            raise AppError(status_code=400, code="imgsz_invalid", message="imgsz 必须在 320 到 1280 之间。")

    def _validate_conf(self, conf: float) -> None:
        if conf <= 0 or conf >= 1:
            raise AppError(status_code=400, code="conf_invalid", message="conf 必须在 0 到 1 之间。")

    def _validate_runs(self, runs: int) -> None:
        if runs < 1 or runs > 10:
            raise AppError(status_code=400, code="runs_invalid", message="runs 必须在 1 到 10 之间。")

    def _record_active_model_benchmark(self, result: dict[str, Any], *, imgsz: int, conf: float) -> None:
        active_model = self.model_registry_service.get_active_descriptor()
        self.model_registry_service.update_descriptor_meta(
            active_model["id"],
            {
                "benchmarked_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "benchmark_image_size": imgsz,
                "benchmark_confidence_threshold": conf,
                "benchmark_pytorch_average_ms": next(
                    (engine["average_ms"] for engine in result.get("engines", []) if engine.get("engine") == "pytorch"),
                    None,
                ),
                "benchmark_onnx_average_ms": next(
                    (engine["average_ms"] for engine in result.get("engines", []) if engine.get("engine") == "onnx"),
                    None,
                ),
                "benchmark_tensorrt_average_ms": next(
                    (engine["average_ms"] for engine in result.get("engines", []) if engine.get("engine") == "tensorrt"),
                    None,
                ),
                "benchmark_speedup_vs_pytorch": result.get("speedup_vs_pytorch"),
                "benchmark_tensorrt_speedup_vs_pytorch": result.get("tensorrt_speedup_vs_pytorch"),
            },
        )


runtime = PlatformRuntime()
