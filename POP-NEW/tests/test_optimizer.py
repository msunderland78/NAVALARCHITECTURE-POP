import json
import unittest
from pathlib import Path

from pop_core import PopInput, optimize_design, optimize_design_with_blade_sweep


ROOT = Path(__file__).resolve().parents[1]


class OptimizerTests(unittest.TestCase):
    def test_optimize_na470_case(self):
        case = PopInput.from_dict(json.loads((ROOT / "tests/fixtures/na470-coursepack.input.json").read_text()))
        expected = json.loads((ROOT / "tests/golden/na470-coursepack.output.json").read_text())["results"]

        result = optimize_design(case)
        design = result.design

        self.assertAlmostEqual(design.diameterMeters, expected["diameterMeters"], delta=0.02)
        self.assertAlmostEqual(design.pitchDiameterRatio, expected["pitchDiameterRatio"], delta=0.02)
        self.assertAlmostEqual(design.expandedAreaRatio, expected["expandedAreaRatio"], delta=0.03)
        self.assertAlmostEqual(design.rpm, expected["rpm"], delta=3.0)
        self.assertGreater(result.evaluationCount, 0)

    def test_blade_sweep_returns_all_blade_counts_and_global_best(self):
        case = PopInput.from_dict(json.loads((ROOT / "tests/fixtures/na470-coursepack.input.json").read_text()))

        sweep = optimize_design_with_blade_sweep(case)

        self.assertEqual([entry.bladeCount for entry in sweep.entries], [3, 4, 5, 6, 7])
        for entry in sweep.entries:
            self.assertTrue(entry.result is not None)
        feasible_etas = [entry.result.design.openWaterEfficiency for entry in sweep.entries]
        self.assertEqual(sweep.best.design.openWaterEfficiency, max(feasible_etas))
        self.assertIn(sweep.bestBladeCount, [3, 4, 5, 6, 7])


if __name__ == "__main__":
    unittest.main()
