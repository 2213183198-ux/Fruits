import gc
import json
import shutil
import time
import unittest
import zipfile
from pathlib import Path

from backend.config import settings
from backend.services.history import HistoryService


class RetrainBatchFlowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workspace_temp_root = Path(__file__).resolve().parents[1] / ".tmp-tests"
        self.workspace_temp_root.mkdir(parents=True, exist_ok=True)
        self.case_dir = self.workspace_temp_root / f"case_{time.time_ns()}"
        self.case_dir.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(self.case_dir, ignore_errors=True))
        self.original_artifacts_dir = settings.artifacts_dir
        object.__setattr__(settings, "artifacts_dir", self.case_dir / "artifacts")
        settings.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self.addCleanup(self._restore_artifacts_dir)
        self.service = HistoryService(self.case_dir / "history.db")

    def _restore_artifacts_dir(self) -> None:
        object.__setattr__(settings, "artifacts_dir", self.original_artifacts_dir)

    def tearDown(self) -> None:
        del self.service
        gc.collect()

    def _create_ready_retrain_item(self) -> int:
        (settings.artifacts_dir / "apple-demo.jpg").write_bytes(b"fake-image-bytes")
        run_id = self.service.record_run(
            mode="single",
            image_size=640,
            confidence_threshold=0.25,
            results=[
                {
                    "filename": "apple-demo.jpg",
                    "summary": {"total_detections": 2},
                    "report": {
                        "status": "warning",
                        "rotten_rate": 0.5,
                        "recommendation": "需要人工复核",
                    },
                    "artifact_url": "/artifacts/apple-demo.jpg",
                }
            ],
            failures=[],
            source_model_name="demo-yolo",
            source_model_type="pt",
        )
        item_id = self.service.get_run(run_id)["items"][0]["id"]
        self.service.save_review_decision(
            item_id,
            decision="false_positive",
            notes="检测框偏移",
            send_to_feedback=True,
        )
        self.service.upsert_retrain_catalog_item(
            item_id,
            catalog_status="ready",
            catalog_notes="适合进入下一轮复训",
        )
        return int(item_id)

    def _create_drafted_retrain_item(self) -> int:
        (settings.artifacts_dir / "pear-demo.jpg").write_bytes(b"fake-image-bytes")
        run_id = self.service.record_run(
            mode="single",
            image_size=640,
            confidence_threshold=0.25,
            results=[
                {
                    "filename": "pear-demo.jpg",
                    "summary": {"total_detections": 1},
                    "report": {
                        "status": "warning",
                        "rotten_rate": 0.1,
                        "recommendation": "建议补充框标注",
                    },
                    "artifact_url": "/artifacts/pear-demo.jpg",
                }
            ],
            failures=[],
            source_model_name="demo-yolo",
            source_model_type="pt",
        )
        item_id = self.service.get_run(run_id)["items"][0]["id"]
        self.service.save_review_decision(
            item_id,
            decision="missed_detection",
            notes="漏检样本",
            send_to_feedback=True,
        )
        self.service.upsert_retrain_catalog_item(
            item_id,
            catalog_status="ready",
            catalog_notes="已补充标签草稿，可进入下一轮复训",
            annotation_draft="0 0.5 0.5 0.2 0.2",
        )
        return int(item_id)

    def test_create_and_export_retrain_batch_updates_catalog(self) -> None:
        item_id = self._create_ready_retrain_item()

        created = self.service.create_retrain_batch(
            batch_name="fresh-sort-batch-001",
            batch_notes="第一批用于训练清单导出",
            item_ids=[item_id],
        )
        self.assertEqual(created["batch_name"], "fresh-sort-batch-001")
        self.assertEqual(created["batch_status"], "draft")
        self.assertEqual(created["item_count"], 1)
        self.assertEqual(created["items"][0]["item_id"], item_id)

        export_result = self.service.export_retrain_batch(created["batch_id"])
        self.assertEqual(export_result["batch_name"], "fresh-sort-batch-001")
        self.assertEqual(export_result["item_count"], 1)
        self.assertTrue((settings.artifacts_dir / export_result["export_name"]).exists())
        self.assertTrue(export_result["export_name"].endswith(".zip"))
        self.assertIn("已导出", export_result["message"])

        with zipfile.ZipFile(settings.artifacts_dir / export_result["export_name"]) as archive:
            names = set(archive.namelist())
            self.assertIn("fresh-sort-batch-001/manifest.csv", names)
            self.assertIn("fresh-sort-batch-001/meta.json", names)
            self.assertIn("fresh-sort-batch-001/README.txt", names)
            self.assertIn("fresh-sort-batch-001/annotation_tasks.csv", names)
            self.assertIn("fresh-sort-batch-001/images/0001_apple-demo.jpg", names)
            self.assertIn("fresh-sort-batch-001/labels/0001_apple-demo.txt", names)

            meta = json.loads(archive.read("fresh-sort-batch-001/meta.json").decode("utf-8"))
            self.assertEqual(meta["package_type"], "training_sample_bundle")
            self.assertEqual(meta["item_count"], 1)
            self.assertEqual(meta["image_count"], 1)
            self.assertEqual(meta["label_ready_count"], 1)
            self.assertEqual(meta["label_labeled_count"], 0)
            self.assertEqual(meta["label_empty_count"], 1)
            self.assertEqual(meta["annotation_pending_count"], 0)

            manifest_text = archive.read("fresh-sort-batch-001/manifest.csv").decode("utf-8-sig")
            self.assertIn("label_status", manifest_text)
            self.assertIn("ready_empty", manifest_text)
            self.assertIn("annotation_status", manifest_text)

        batch_detail = self.service.get_retrain_batch(created["batch_id"])
        self.assertEqual(batch_detail["batch_status"], "exported")
        self.assertEqual(batch_detail["item_count"], 1)
        self.assertEqual(batch_detail["export_name"], export_result["export_name"])

        retrain_detail = self.service.get_retrain_catalog_item(item_id)
        self.assertEqual(retrain_detail["catalog_status"], "used")
        self.assertEqual(retrain_detail["batch_name"], "fresh-sort-batch-001")
        self.assertEqual(retrain_detail["batch_status"], "exported")
        self.assertEqual(retrain_detail["batch_export_url"], export_result["export_url"])

        summary = self.service.get_retrain_batch_summary()
        self.assertEqual(summary["total"], 1)
        self.assertEqual(summary["draft"], 0)
        self.assertEqual(summary["exported"], 1)
        self.assertEqual(summary["total_items"], 1)

    def test_export_retrain_batch_includes_annotation_draft_labels(self) -> None:
        item_id = self._create_drafted_retrain_item()

        retrain_detail = self.service.get_retrain_catalog_item(item_id)
        self.assertEqual(retrain_detail["annotation_status"], "drafted")
        self.assertEqual(retrain_detail["annotation_draft"], "0 0.5 0.5 0.2 0.2")
        self.assertTrue(retrain_detail["annotation_updated_at"])

        created = self.service.create_retrain_batch(
            batch_name="fresh-sort-batch-002",
            batch_notes="第二批用于验证标签草稿导出",
            item_ids=[item_id],
        )
        export_result = self.service.export_retrain_batch(created["batch_id"])

        with zipfile.ZipFile(settings.artifacts_dir / export_result["export_name"]) as archive:
            label_text = archive.read("fresh-sort-batch-002/labels/0001_pear-demo.txt").decode("utf-8")
            self.assertEqual(label_text, "0 0.5 0.5 0.2 0.2")

            annotation_tasks_text = archive.read("fresh-sort-batch-002/annotation_tasks.csv").decode("utf-8-sig")
            self.assertIn("annotation_status", annotation_tasks_text)
            self.assertNotIn("pear-demo.jpg", annotation_tasks_text)

            manifest_text = archive.read("fresh-sort-batch-002/manifest.csv").decode("utf-8-sig")
            self.assertIn("ready_labeled", manifest_text)
            self.assertIn("drafted", manifest_text)

            meta = json.loads(archive.read("fresh-sort-batch-002/meta.json").decode("utf-8"))
            self.assertEqual(meta["label_ready_count"], 1)
            self.assertEqual(meta["label_labeled_count"], 1)
            self.assertEqual(meta["label_empty_count"], 0)
            self.assertEqual(meta["annotation_pending_count"], 0)

        exported_detail = self.service.get_retrain_catalog_item(item_id)
        self.assertEqual(exported_detail["catalog_status"], "used")
        self.assertEqual(exported_detail["annotation_status"], "drafted")
        self.assertTrue(exported_detail["annotation_updated_at"])


if __name__ == "__main__":
    unittest.main()
