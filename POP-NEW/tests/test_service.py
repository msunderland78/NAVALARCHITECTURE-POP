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
        self.assertIn("bladeSweep", payload)
        self.assertIn("bladeCount", payload)
        self.assertEqual(payload["bladeCount"], payload["bladeSweep"]["bestBladeCount"])

    def test_blade_sweep_contains_four_blade_result_near_legacy_optimum(self):
        case = PopInput.from_dict(json.loads((ROOT / "tests/fixtures/na470-coursepack.input.json").read_text()))
        payload = result_payload(case, run_case(case))
        sweep = payload["bladeSweep"]
        z4 = next(entry for entry in sweep["entries"] if entry["bladeCount"] == 4)

        self.assertTrue(z4["feasible"])
        self.assertAlmostEqual(z4["diameterMeters"], 4.6, delta=0.02)
        self.assertAlmostEqual(z4["pitchDiameterRatio"], 0.8171, delta=0.02)
        self.assertAlmostEqual(z4["expandedAreaRatio"], 0.6293, delta=0.04)

    def test_payload_includes_warnings_list(self):
        case = PopInput.from_dict(json.loads((ROOT / "tests/fixtures/na470-coursepack.input.json").read_text()))
        payload = result_payload(case, run_case(case))

        self.assertIn("warnings", payload)
        self.assertIsInstance(payload["warnings"], list)
        codes = {w["code"] for w in payload["warnings"]}
        self.assertIn("diameter_pinned_max", codes)
        for warning in payload["warnings"]:
            self.assertIn(warning["level"], {"warning", "info"})
            self.assertIsInstance(warning["message"], str)
            self.assertTrue(warning["message"])

    def test_payload_warns_when_cavitation_exceeds_limit(self):
        data = json.loads((ROOT / "tests/fixtures/na470-coursepack.input.json").read_text())
        data["mode"] = "evaluation"
        data["initialDiameterMeters"] = 3.0
        data["initialPitchDiameterRatio"] = 0.9
        data["initialExpandedAreaRatio"] = 0.35
        case = PopInput.from_dict(data)

        payload = result_payload(case, run_case(case))
        codes = {w["code"] for w in payload["warnings"]}

        self.assertIn("cavitation_exceeds_limit", codes)

    def test_payload_warns_for_controllable_pitch(self):
        data = json.loads((ROOT / "tests/fixtures/na470-coursepack.input.json").read_text())
        data["mode"] = "evaluation"
        data["pitchType"] = "controllable"
        case = PopInput.from_dict(data)

        payload = result_payload(case, run_case(case))
        codes = {w["code"] for w in payload["warnings"]}

        self.assertIn("cpp_empirical", codes)

    def test_blade_sweep_covers_all_five_blade_counts(self):
        case = PopInput.from_dict(json.loads((ROOT / "tests/fixtures/na470-coursepack.input.json").read_text()))
        payload = result_payload(case, run_case(case))
        zs = [entry["bladeCount"] for entry in payload["bladeSweep"]["entries"]]

        self.assertEqual(zs, [3, 4, 5, 6, 7])

    def test_invalid_physical_input_fails_before_calculation(self):
        data = json.loads((ROOT / "tests/fixtures/na470-coursepack.input.json").read_text())
        data["mode"] = "evaluation"
        data["initialDiameterMeters"] = 0.0
        case = PopInput.from_dict(data)

        with self.assertRaisesRegex(ValueError, "initialDiameterMeters"):
            run_case(case)

    def test_non_numeric_input_fails_before_calculation(self):
        data = json.loads((ROOT / "tests/fixtures/na470-coursepack.input.json").read_text())
        data["mode"] = "evaluation"
        data["initialDiameterMeters"] = "<script>alert(1)</script>"

        with self.assertRaisesRegex(ValueError, "initialDiameterMeters must be a number"):
            PopInput.from_dict(data)

    def test_controllable_pitch_curve_uses_reduced_efficiency(self):
        fixed_data = json.loads((ROOT / "tests/fixtures/na470-coursepack.input.json").read_text())
        fixed_data["mode"] = "evaluation"
        controllable_data = dict(fixed_data)
        controllable_data["pitchType"] = "controllable"

        fixed_payload = result_payload(PopInput.from_dict(fixed_data), run_case(PopInput.from_dict(fixed_data)))
        controllable_payload = result_payload(PopInput.from_dict(controllable_data), run_case(PopInput.from_dict(controllable_data)))
        fixed_eta = fixed_payload["curves"]["openWater"][10]["eta"]
        controllable_eta = controllable_payload["curves"]["openWater"][10]["eta"]

        self.assertAlmostEqual(controllable_eta, fixed_eta * 0.98, delta=0.000001)

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
