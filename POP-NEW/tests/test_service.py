import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from pop_core import PopInput, result_payload, run_case


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parent


class ServiceTests(unittest.TestCase):
    def test_result_payload_shape(self):
        case = PopInput.from_dict(json.loads((ROOT / "tests/fixtures/na470-coursepack.input.json").read_text()))
        payload = result_payload(case, run_case(case))

        self.assertEqual(payload["projectName"], "NA 470 Coursepack Example")
        self.assertEqual(payload["mode"], "optimization")
        self.assertEqual(payload["series"], "wageningen_b")
        self.assertIn("raw", payload)
        self.assertIn("legacyRounded", payload)
        self.assertIn("curves", payload)
        self.assertIn("openWater", payload["curves"])
        self.assertGreater(len(payload["curves"]["openWater"]), 20)
        self.assertAlmostEqual(payload["legacyRounded"]["diameterMeters"], 4.6, delta=0.02)
        self.assertAlmostEqual(payload["legacyRounded"]["pitchDiameterRatio"], 0.8171, delta=0.02)
        self.assertAlmostEqual(payload["legacyRounded"]["expandedAreaRatio"], 0.6293, delta=0.03)

    def test_invalid_physical_input_fails_before_calculation(self):
        data = json.loads((ROOT / "tests/fixtures/na470-coursepack.input.json").read_text())
        data["mode"] = "evaluation"
        data["initialDiameterMeters"] = 0.0
        case = PopInput.from_dict(data)

        with self.assertRaisesRegex(ValueError, "initialDiameterMeters"):
            run_case(case)

    def test_cli_outputs_json(self):
        data = json.loads((ROOT / "tests/fixtures/na470-coursepack.input.json").read_text())
        data["mode"] = "evaluation"
        temp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        temp.write(json.dumps(data))
        temp.close()
        command = [
            sys.executable,
            str(ROOT / "app/backend/run_pop.py"),
            temp.name
        ]
        try:
            completed = subprocess.run(
                command,
                cwd=PROJECT_ROOT,
                env={"PYTHONPATH": str(ROOT / "app/backend")},
                check=True,
                capture_output=True,
                text=True
            )
        finally:
            Path(temp.name).unlink(missing_ok=True)

        payload = json.loads(completed.stdout)
        self.assertEqual(payload["runId"], "test 1.0")
        self.assertEqual(payload["mode"], "evaluation")
        self.assertIn("legacyRounded", payload)


if __name__ == "__main__":
    unittest.main()
