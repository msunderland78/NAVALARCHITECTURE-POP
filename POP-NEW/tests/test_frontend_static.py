import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class FrontendStaticTests(unittest.TestCase):
    def test_frontend_has_propeller_diagram(self):
        html = (ROOT / "app/frontend/index.html").read_text()

        self.assertIn('id="propeller-diagram"', html)
        self.assertIn('id="curve-chart"', html)
        self.assertIn('data-mode-field="evaluation"', html)
        self.assertIn('data-mode-field="optimization"', html)
        self.assertIn('id="legacy-pop-file"', html)
        self.assertIn('id="download-json"', html)
        self.assertIn('id="download-csv"', html)
        self.assertIn("Propeller Optimization Program", html)

    def test_frontend_does_not_auto_run(self):
        script = (ROOT / "app/frontend/app.js").read_text()

        self.assertNotIn("dispatchEvent", script)
        self.assertNotIn("setInterval", script)
        self.assertNotIn("location.reload", script)

    def test_frontend_posts_legacy_import(self):
        script = (ROOT / "app/frontend/app.js").read_text()

        self.assertIn("/api/import-pop", script)
        self.assertIn("application/octet-stream", script)

    def test_frontend_exports_results(self):
        script = (ROOT / "app/frontend/app.js").read_text()

        self.assertIn("payloadToCsv", script)
        self.assertIn("downloadText", script)
        self.assertIn(".csv", script)


if __name__ == "__main__":
    unittest.main()
