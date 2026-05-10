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
        self.assertIn('id="print-report"', html)
        self.assertIn('id="verification-table"', html)
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
        self.assertIn("window.print", script)

    def test_frontend_has_print_styles(self):
        styles = (ROOT / "app/frontend/styles.css").read_text()

        self.assertIn("@media print", styles)
        self.assertIn("size: Letter portrait", styles)
        self.assertIn("margin: 1in", styles)
        self.assertIn("#json-output", styles)
        self.assertIn("max-width: 6.5in", styles)

    def test_frontend_checks_http_error_payloads(self):
        script = (ROOT / "app/frontend/app.js").read_text()

        self.assertIn("readJsonResponse", script)
        self.assertIn("response.ok", script)

    def test_frontend_has_input_verification_view(self):
        script = (ROOT / "app/frontend/app.js").read_text()

        self.assertIn("renderVerification", script)
        self.assertIn("Advance Speed", script)
        self.assertIn("Cavitation Limit", script)

    def test_frontend_escapes_rendered_table_values(self):
        script = (ROOT / "app/frontend/app.js").read_text()

        self.assertIn("resultTable.innerHTML = rows.map(([name, value]) => `<tr><td>${escapeHtml(name)}</td><td>${escapeHtml(value)}</td></tr>`).join(\"\");", script)
        self.assertIn("verificationTable.innerHTML = rows.map(([name, value]) => `<tr><td>${escapeHtml(name)}</td><td>${escapeHtml(value)}</td></tr>`).join(\"\");", script)

    def test_frontend_applies_water_presets(self):
        script = (ROOT / "app/frontend/app.js").read_text()

        self.assertIn("WATER_PRESETS", script)
        self.assertIn("applyWaterPreset", script)
        self.assertIn("markCustomWater", script)


if __name__ == "__main__":
    unittest.main()
