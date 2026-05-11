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

        for context_node in ("resultTable", "verificationTable"):
            assignment = self._innerhtml_assignment(script, context_node)
            self.assertIn("escapeHtml(name)", assignment, f"{context_node} should escape the cell label")
            self.assertIn("escapeHtml(value)", assignment, f"{context_node} should escape the cell value")
        self.assertNotIn("resultTable.innerHTML = `<", script)
        self.assertNotIn("verificationTable.innerHTML = `<", script)

    @staticmethod
    def _innerhtml_assignment(script: str, node_name: str) -> str:
        marker = f"{node_name}.innerHTML"
        index = script.find(marker)
        if index < 0:
            return ""
        end = script.find(";", index)
        return script[index:end if end >= 0 else len(script)]

    def test_frontend_applies_water_presets(self):
        script = (ROOT / "app/frontend/app.js").read_text()

        self.assertIn("WATER_PRESETS", script)
        self.assertIn("applyWaterPreset", script)
        self.assertIn("markCustomWater", script)

    def test_frontend_renders_warnings_section(self):
        html = (ROOT / "app/frontend/index.html").read_text()
        script = (ROOT / "app/frontend/app.js").read_text()
        styles = (ROOT / "app/frontend/styles.css").read_text()

        self.assertIn('id="warnings-section"', html)
        self.assertIn('id="warnings-list"', html)
        self.assertIn("renderWarnings", script)
        self.assertIn("level-warning", styles)
        self.assertIn("level-info", styles)

    def test_frontend_has_client_side_validation(self):
        script = (ROOT / "app/frontend/app.js").read_text()
        styles = (ROOT / "app/frontend/styles.css").read_text()

        self.assertIn("FIELD_RULES", script)
        self.assertIn("collectValidationErrors", script)
        self.assertIn("applyFieldErrors", script)
        self.assertIn("validateForm", script)
        self.assertIn("runButton.disabled", script)
        self.assertIn("input.invalid", styles)
        self.assertIn(".field-error", styles)

    def test_frontend_renders_run_error_hints(self):
        script = (ROOT / "app/frontend/app.js").read_text()

        self.assertIn("renderRunError", script)
        self.assertIn('"no_feasible_design"', script)
        self.assertIn("error.hints", script)
        self.assertIn("error.nearest", script)

    def test_frontend_has_methodology_panel(self):
        html = (ROOT / "app/frontend/index.html").read_text()
        script = (ROOT / "app/frontend/app.js").read_text()
        styles = (ROOT / "app/frontend/styles.css").read_text()

        self.assertIn('id="methodology-panel"', html)
        self.assertIn('id="methodology-button"', html)
        self.assertIn("Bernitsas", html)
        self.assertIn("Carlton", html)
        self.assertIn("setMethodologyOpen", script)
        self.assertIn(".methodology-panel", styles)

    def test_frontend_has_stale_result_indicator(self):
        html = (ROOT / "app/frontend/index.html").read_text()
        script = (ROOT / "app/frontend/app.js").read_text()
        styles = (ROOT / "app/frontend/styles.css").read_text()

        self.assertIn('id="stale-badge"', html)
        self.assertIn("setStale(true)", script)
        self.assertIn("setStale(false)", script)
        self.assertIn(".stale-badge", styles)

    def test_print_button_uses_print_label(self):
        html = (ROOT / "app/frontend/index.html").read_text()
        script = (ROOT / "app/frontend/app.js").read_text()

        self.assertIn(">Print<", html)
        self.assertNotIn(">PDF<", html)
        self.assertIn("Print Ready", script)
        self.assertNotIn("PDF Ready", script)

    def test_frontend_renders_blade_sweep_table(self):
        html = (ROOT / "app/frontend/index.html").read_text()
        script = (ROOT / "app/frontend/app.js").read_text()
        styles = (ROOT / "app/frontend/styles.css").read_text()

        self.assertIn('id="blade-sweep-section"', html)
        self.assertIn('id="blade-sweep-body"', html)
        self.assertIn("renderBladeSweep", script)
        self.assertIn(".blade-sweep", styles)
        self.assertIn("best-row", styles)

    def test_frontend_has_controllable_pitch_banner(self):
        html = (ROOT / "app/frontend/index.html").read_text()
        script = (ROOT / "app/frontend/app.js").read_text()
        styles = (ROOT / "app/frontend/styles.css").read_text()

        self.assertIn('id="cpp-banner"', html)
        self.assertIn("empirical hub-loss", html)
        self.assertIn("updateCppBanner", script)
        self.assertIn(".cpp-banner", styles)


if __name__ == "__main__":
    unittest.main()
