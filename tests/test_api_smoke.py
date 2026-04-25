import unittest

try:
    from fastapi.testclient import TestClient
    from backend.app.factory import create_app
except ModuleNotFoundError:  # pragma: no cover - depends on local environment
    TestClient = None
    create_app = None


@unittest.skipIf(TestClient is None or create_app is None, "fastapi is not installed in the current Python environment")
class PublicApiSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(create_app())

    def unwrap_ok(self, path: str):
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200, msg=f"{path} returned {response.status_code}")
        payload = response.json()
        self.assertTrue(payload["success"], msg=f"{path} did not return success=true")
        return payload["data"]

    def test_root_page_is_served(self) -> None:
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers.get("content-type", ""))

    def test_openapi_is_served(self) -> None:
        response = self.client.get("/openapi.json")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("paths", payload)
        self.assertIn("/api/v1/system/health", payload["paths"])
        self.assertIn("/api/v1/models", payload["paths"])
        self.assertIn("/api/v1/retrain/summary", payload["paths"])
        self.assertIn("/api/v1/retrain/batches/summary", payload["paths"])
        self.assertIn("/api/v1/dashboard/summary", payload["paths"])

    def test_api_index_contract(self) -> None:
        data = self.unwrap_ok("/api/v1")
        self.assertIn("service_name", data)
        self.assertEqual(data["api_base_url"], "/api/v1")
        self.assertIn("capabilities", data)
        self.assertIsInstance(data["capabilities"], list)

    def test_health_contract(self) -> None:
        data = self.unwrap_ok("/api/v1/system/health")
        self.assertIn("status", data)
        self.assertIn("active_model_name", data)
        self.assertIn("active_model_type", data)
        self.assertIn("model_loaded", data)
        self.assertIn("active_class_names", data)

    def test_models_contract(self) -> None:
        data = self.unwrap_ok("/api/v1/models")
        self.assertIn("active_model_name", data)
        self.assertIn("active_model_type", data)
        self.assertIn("models", data)
        self.assertIsInstance(data["models"], list)
        if data["models"]:
            model = data["models"][0]
            self.assertIn("id", model)
            self.assertIn("name", model)
            self.assertIn("type", model)
            self.assertIn("class_names", model)

    def test_quality_rules_contract(self) -> None:
        data = self.unwrap_ok("/api/v1/settings/quality-rules")
        self.assertIn("enabled", data)
        self.assertIn("fresh_keywords", data)
        self.assertIn("rotten_keywords", data)
        self.assertIn("messages", data)
        self.assertIn("pass_message", data["messages"])
        self.assertIn("warning_message", data["messages"])
        self.assertIn("critical_message", data["messages"])

    def test_history_contract(self) -> None:
        data = self.unwrap_ok("/api/v1/history/runs")
        self.assertIsInstance(data, list)
        if data:
            item = data[0]
            self.assertIn("id", item)
            self.assertIn("mode", item)
            self.assertIn("created_at", item)

    def test_storage_contract(self) -> None:
        data = self.unwrap_ok("/api/v1/maintenance/storage")
        self.assertIn("artifact_count", data)
        self.assertIn("artifact_total_size_mb", data)
        self.assertIn("artifacts", data)
        self.assertIsInstance(data["artifacts"], list)

    def test_deployment_contract(self) -> None:
        data = self.unwrap_ok("/api/v1/deployment/status")
        self.assertIn("pytorch", data)
        self.assertIn("onnx", data)
        self.assertIn("tensorrt", data)
        self.assertIn("onnx_dependencies_ready", data)
        self.assertIn("tensorrt_dependencies_ready", data)
        self.assertIn("onnxruntime_providers", data)

    def test_dashboard_summary_contract(self) -> None:
        response = self.client.get("/api/v1/dashboard/summary?days=7")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])
        data = payload["data"]
        self.assertIn("total_runs", data)
        self.assertIn("total_samples", data)
        self.assertIn("successful_samples", data)
        self.assertIn("failed_samples", data)
        self.assertIn("success_rate", data)
        self.assertIn("total_detections", data)
        self.assertIn("quality_status_counts", data)
        self.assertIn("mode_sample_counts", data)
        self.assertIn("review_pending_count", data)
        self.assertIn("feedback_queued_count", data)
        self.assertIn("retrain_ready_count", data)
        self.assertIn("recent_daily_stats", data)
        self.assertEqual(payload["meta"]["days"], 7)

    def test_tasks_listing_contract(self) -> None:
        data = self.unwrap_ok("/api/v1/tasks")
        self.assertIsInstance(data, list)

    def test_review_summary_contract(self) -> None:
        data = self.unwrap_ok("/api/v1/review/summary")
        self.assertIn("total", data)
        self.assertIn("pending", data)
        self.assertIn("reviewed", data)
        self.assertIn("feedback", data)
        self.assertIn("false_positive_count", data)
        self.assertIn("missed_detection_count", data)

    def test_feedback_export_contract(self) -> None:
        response = self.client.post("/api/v1/review/feedback/export?mode=single&keyword=demo")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])
        data = payload["data"]
        self.assertIn("export_name", data)
        self.assertIn("export_url", data)
        self.assertIn("item_count", data)

    def test_feedback_pool_summary_contract(self) -> None:
        response = self.client.get("/api/v1/review/feedback/summary?mode=batch&keyword=apple")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])
        data = payload["data"]
        self.assertIn("total", data)
        self.assertIn("false_positive_count", data)
        self.assertIn("missed_detection_count", data)
        self.assertIn("needs_feedback_count", data)
        self.assertIn("single_count", data)
        self.assertIn("batch_count", data)
        self.assertIn("webcam_count", data)
        self.assertIn("artifact_ready_count", data)
        self.assertIn("avg_rotten_rate", data)
        self.assertIn("latest_updated_at", data)
        self.assertEqual(payload["meta"]["mode"], "batch")
        self.assertEqual(payload["meta"]["keyword"], "apple")

    def test_retrain_summary_contract(self) -> None:
        response = self.client.get("/api/v1/retrain/summary?status=ready&mode=single&keyword=pear")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])
        data = payload["data"]
        self.assertIn("total", data)
        self.assertIn("pending", data)
        self.assertIn("ready", data)
        self.assertIn("used", data)
        self.assertIn("false_positive_count", data)
        self.assertIn("missed_detection_count", data)
        self.assertIn("needs_feedback_count", data)
        self.assertIn("latest_updated_at", data)
        self.assertEqual(payload["meta"]["status"], "ready")
        self.assertEqual(payload["meta"]["mode"], "single")
        self.assertEqual(payload["meta"]["keyword"], "pear")

    def test_retrain_items_contract(self) -> None:
        response = self.client.get("/api/v1/retrain/items?limit=10&status=pending&decision=false_positive&mode=batch&keyword=banana")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])
        self.assertIsInstance(payload["data"], list)
        self.assertEqual(payload["meta"]["status"], "pending")
        self.assertEqual(payload["meta"]["decision"], "false_positive")
        self.assertEqual(payload["meta"]["mode"], "batch")
        self.assertEqual(payload["meta"]["keyword"], "banana")

    def test_retrain_batch_summary_contract(self) -> None:
        response = self.client.get("/api/v1/retrain/batches/summary")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])
        data = payload["data"]
        self.assertIn("total", data)
        self.assertIn("draft", data)
        self.assertIn("exported", data)
        self.assertIn("total_items", data)
        self.assertIn("latest_exported_at", data)

    def test_retrain_batches_contract(self) -> None:
        response = self.client.get("/api/v1/retrain/batches?limit=6")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])
        self.assertIsInstance(payload["data"], list)
        self.assertEqual(payload["meta"]["limit"], 6)

    def test_review_items_filter_contract(self) -> None:
        response = self.client.get("/api/v1/review/items?limit=10&queue=all&decision=false_positive&mode=single&keyword=test")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])
        self.assertIsInstance(payload["data"], list)
        self.assertEqual(payload["meta"]["decision"], "false_positive")
        self.assertEqual(payload["meta"]["mode"], "single")
        self.assertEqual(payload["meta"]["keyword"], "test")

    def test_webcam_websocket_ready_message(self) -> None:
        with self.client.websocket_connect("/ws/webcam") as websocket:
            payload = websocket.receive_json()
        self.assertEqual(payload["type"], "ready")
        self.assertIn("timestamp", payload)


if __name__ == "__main__":
    unittest.main()
