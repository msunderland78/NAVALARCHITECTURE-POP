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
        self.assertIn("Propeller Optimization Program", html)

    def test_frontend_does_not_auto_run(self):
        script = (ROOT / "app/frontend/app.js").read_text()

        self.assertNotIn("dispatchEvent", script)
        self.assertNotIn("setInterval", script)
        self.assertNotIn("location.reload", script)


if __name__ == "__main__":
    unittest.main()
