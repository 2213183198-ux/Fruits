import shutil
import time
import unittest
from pathlib import Path

from backend.services.model_registry import ModelRegistryService


class ModelRegistryServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workspace_temp_root = Path(__file__).resolve().parents[1] / ".tmp-tests"
        self.workspace_temp_root.mkdir(parents=True, exist_ok=True)
        self.case_dir = self.workspace_temp_root / f"model_case_{time.time_ns()}"
        self.case_dir.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(self.case_dir, ignore_errors=True))

        self.default_model_path = self.case_dir / "default.pt"
        self.default_model_path.write_bytes(b"default-model")
        self.default_yaml_path = self.case_dir / "data.yaml"
        self.default_yaml_path.write_text("names: [fresh, rotten]\n", encoding="utf-8")
        self.model_store_dir = self.case_dir / "models"

        self.registry = ModelRegistryService(
            self.default_model_path,
            self.model_store_dir,
            self.default_yaml_path,
        )

    def test_save_upload_persists_yaml_and_class_metadata(self) -> None:
        descriptor = self.registry.save_upload(
            "multi-qc-yolo-v3.pt",
            b"trained-model",
            yaml_filename="custom.yaml",
            yaml_payload=b"names: [fresh, rotten]\n",
        )

        self.assertEqual(descriptor["yaml_name"], "multi-qc-yolo-v3.yaml")
        self.assertEqual(descriptor["class_names"], ["fresh", "rotten"])

        inventory = self.registry.get_inventory()
        uploaded = next(item for item in inventory["models"] if item["name"].startswith("multi-qc-yolo-v3"))
        self.assertEqual(uploaded["yaml_name"], "multi-qc-yolo-v3.yaml")
        self.assertEqual(uploaded["class_names"], ["fresh", "rotten"])

    def test_update_descriptor_meta_persists_benchmark_snapshot(self) -> None:
        uploaded = self.registry.save_upload(
            "deploy-candidate.onnx",
            b"onnx-model",
        )

        updated = self.registry.update_descriptor_meta(
            uploaded["id"],
            {
                "benchmarked_at": "2026-04-11 10:00:00",
                "benchmark_image_size": 640,
                "benchmark_confidence_threshold": 0.25,
                "benchmark_pytorch_average_ms": 82.4,
                "benchmark_onnx_average_ms": 41.2,
                "benchmark_speedup_vs_pytorch": 2.0,
            },
        )

        self.assertEqual(updated["benchmarked_at"], "2026-04-11 10:00:00")
        self.assertEqual(updated["benchmark_image_size"], 640)
        self.assertAlmostEqual(updated["benchmark_confidence_threshold"], 0.25)
        self.assertAlmostEqual(updated["benchmark_pytorch_average_ms"], 82.4)
        self.assertAlmostEqual(updated["benchmark_onnx_average_ms"], 41.2)
        self.assertAlmostEqual(updated["benchmark_speedup_vs_pytorch"], 2.0)

        inventory = self.registry.get_inventory()
        persisted = next(item for item in inventory["models"] if item["id"] == uploaded["id"])
        self.assertEqual(persisted["benchmarked_at"], "2026-04-11 10:00:00")
        self.assertEqual(persisted["benchmark_image_size"], 640)
        self.assertAlmostEqual(persisted["benchmark_onnx_average_ms"], 41.2)


if __name__ == "__main__":
    unittest.main()
