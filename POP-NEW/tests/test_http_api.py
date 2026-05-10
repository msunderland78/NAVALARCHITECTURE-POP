import json
import threading
import unittest
import urllib.request
from pathlib import Path

from pop_http import build_server, sample_case


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parent


class HttpApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = build_server("127.0.0.1", 0)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever)
        cls.thread.daemon = True
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def test_health(self):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/health", timeout=5) as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(json.loads(response.read()), {"status": "ok"})

    def test_serves_frontend(self):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/", timeout=5) as response:
            body = response.read().decode("utf-8")

        self.assertIn("Propeller Optimization Program", body)
        self.assertIn("/app.js", body)

    def test_static_assets_are_not_cached(self):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/app.js", timeout=5) as response:
            cache_control = response.headers.get("Cache-Control")

        self.assertEqual(cache_control, "no-store")

    def test_sample(self):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/api/sample", timeout=5) as response:
            payload = json.loads(response.read())

        self.assertEqual(payload["projectName"], "NA 470 Coursepack Example")
        self.assertEqual(payload["mode"], "evaluation")

    def test_run_evaluation(self):
        data = json.dumps(sample_case()).encode("utf-8")
        request = urllib.request.Request(
            f"http://127.0.0.1:{self.port}/api/run",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(request, timeout=10) as response:
            payload = json.loads(response.read())

        self.assertEqual(payload["runId"], "test 1.0")
        self.assertEqual(payload["mode"], "evaluation")
        self.assertIn("legacyRounded", payload)
        self.assertIn("curves", payload)
        self.assertGreater(payload["legacyRounded"]["rpm"], 0)

    def test_import_pop_when_available(self):
        path = PROJECT_ROOT / "POP-OLD/POP1.POP"
        if not path.exists():
            self.skipTest("POP-OLD is not present")
        request = urllib.request.Request(
            f"http://127.0.0.1:{self.port}/api/import-pop",
            data=path.read_bytes(),
            headers={"Content-Type": "application/octet-stream"},
            method="POST"
        )

        with urllib.request.urlopen(request, timeout=10) as response:
            payload = json.loads(response.read())

        self.assertEqual(payload["input"]["projectName"], "NA 470 Coursepack Example")
        self.assertEqual(payload["input"]["bladeCount"], 4)
        self.assertEqual(payload["input"]["requiredThrustKn"], 444.8221)


if __name__ == "__main__":
    unittest.main()
