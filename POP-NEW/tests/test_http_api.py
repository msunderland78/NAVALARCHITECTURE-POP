import json
import threading
import unittest
import urllib.error
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

    def test_static_assets_include_security_headers(self):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/", timeout=5) as response:
            headers = response.headers

        self.assertIn("default-src 'self'", headers.get("Content-Security-Policy"))
        self.assertEqual(headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(headers.get("Referrer-Policy"), "no-referrer")

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

    def test_run_rejects_invalid_input(self):
        data = sample_case()
        data["shipSpeedKnots"] = 0.0
        request = urllib.request.Request(
            f"http://127.0.0.1:{self.port}/api/run",
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with self.assertRaises(urllib.error.HTTPError) as context:
            urllib.request.urlopen(request, timeout=10)

        payload = json.loads(context.exception.read())
        self.assertEqual(context.exception.code, 400)
        self.assertEqual(payload["error"], "invalid_input")
        self.assertIn("shipSpeedKnots", payload["message"])

    def test_run_rejects_hostile_numeric_types(self):
        probes = [
            ("initialDiameterMeters", "<svg/onload=alert(1)>", "initialDiameterMeters must be a number"),
            ("initialDiameterMeters", None, "initialDiameterMeters must be a number"),
            ("initialDiameterMeters", "1; DROP TABLE pop;", "initialDiameterMeters must be a number"),
            ("bladeCount", True, "bladeCount must be an integer")
        ]
        for field, value, expected in probes:
            with self.subTest(field=field, value=value):
                data = sample_case()
                data[field] = value
                payload = self._post_run_expect_error(data, 400)

                self.assertEqual(payload["error"], "invalid_input")
                self.assertIn(expected, payload["message"])

    def test_run_rejects_malformed_request_shapes(self):
        payload = self._post_raw_expect_error(b"not-json", 400)
        self.assertEqual(payload["error"], "invalid_input")
        self.assertIn("valid JSON", payload["message"])

        payload = self._post_raw_expect_error(b"[]", 400)
        self.assertEqual(payload["error"], "invalid_input")
        self.assertIn("JSON object", payload["message"])

        payload = self._post_raw_expect_error(b'{"initialDiameterMeters": NaN}', 400)
        self.assertEqual(payload["error"], "invalid_input")
        self.assertIn("valid JSON", payload["message"])

    def test_run_rejects_oversized_json_body(self):
        payload = self._post_raw_expect_error(b" " * 17000, 413)

        self.assertEqual(payload["error"], "request_too_large")

    def test_import_rejects_oversized_body(self):
        request = urllib.request.Request(
            f"http://127.0.0.1:{self.port}/api/import-pop",
            data=b"0" * 1048577,
            headers={"Content-Type": "application/octet-stream"},
            method="POST"
        )

        with self.assertRaises(urllib.error.HTTPError) as context:
            urllib.request.urlopen(request, timeout=10)

        payload = json.loads(context.exception.read())
        self.assertEqual(context.exception.code, 413)
        self.assertEqual(payload["error"], "request_too_large")

    def _post_run_expect_error(self, data: dict, status: int) -> dict:
        return self._post_raw_expect_error(json.dumps(data).encode("utf-8"), status)

    def _post_raw_expect_error(self, body: bytes, status: int) -> dict:
        request = urllib.request.Request(
            f"http://127.0.0.1:{self.port}/api/run",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with self.assertRaises(urllib.error.HTTPError) as context:
            urllib.request.urlopen(request, timeout=10)

        self.assertEqual(context.exception.code, status)
        return json.loads(context.exception.read())

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
