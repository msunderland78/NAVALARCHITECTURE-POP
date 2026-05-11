import json
import unittest
from pathlib import Path

from pop_core import NoFeasibleDesignError, PopInput, optimize_design, optimize_design_with_blade_sweep


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

    def test_infeasible_case_raises_with_hints_and_nearest(self):
        case = PopInput.from_dict({
            "projectName": "infeasible",
            "runId": "x",
            "mode": "optimization",
            "series": "wageningen_b",
            "pitchType": "fixed",
            "bladeCount": 4,
            "initialExpandedAreaRatio": 0.75,
            "initialPitchDiameterRatio": 1.0,
            "initialDiameterMeters": 0.55,
            "diameterMinMeters": 0.5,
            "diameterMaxMeters": 0.6,
            "requiredThrustKn": 5000.0,
            "shipSpeedKnots": 5.0,
            "wakeFraction": 0.0,
            "shaftDepthMeters": 0.5,
            "water": {"kind": "salt_15c", "densityKgM3": 1025.87, "kinematicViscosityM2S": 1.18831e-6},
            "burrillBackCavitationPercent": 5
        })

        with self.assertRaises(NoFeasibleDesignError) as ctx:
            optimize_design_with_blade_sweep(case)

        error = ctx.exception
        self.assertTrue(error.hints, "hints should not be empty")
        self.assertIsInstance(error.nearest, dict)
        self.assertIn("burrillLoading", error.nearest)
        self.assertIn("burrillAllowable", error.nearest)
        combined = " ".join(error.hints).lower()
        self.assertIn("burrill", combined)

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
