import json
import unittest
from pathlib import Path

import numpy as np

from pop_core import PopInput, estimate_reynolds_number, evaluate_design, evaluate_design_auto_reynolds, passes_burrill_constraint, solve_advance_coefficient_for_thrust
from pop_core.solver import burrill_allowable_loading, evaluate_designs_auto_reynolds_batch


ROOT = Path(__file__).resolve().parents[1]


class SolverTests(unittest.TestCase):
    def test_solve_na470_golden_design(self):
        case = PopInput.from_dict(json.loads((ROOT / "tests/fixtures/na470-coursepack.input.json").read_text()))
        expected = json.loads((ROOT / "tests/golden/na470-coursepack.output.json").read_text())["results"]

        j = solve_advance_coefficient_for_thrust(
            case,
            expected["diameterMeters"],
            expected["pitchDiameterRatio"],
            expected["expandedAreaRatio"],
            expected["reynoldsNumber"]
        )

        self.assertAlmostEqual(j, expected["advanceCoefficient"], delta=0.001)

    def test_evaluate_na470_golden_design(self):
        case = PopInput.from_dict(json.loads((ROOT / "tests/fixtures/na470-coursepack.input.json").read_text()))
        expected = json.loads((ROOT / "tests/golden/na470-coursepack.output.json").read_text())["results"]

        result = evaluate_design(
            case,
            expected["diameterMeters"],
            expected["pitchDiameterRatio"],
            expected["expandedAreaRatio"],
            expected["reynoldsNumber"]
        )

        self.assertAlmostEqual(result.advanceCoefficient, expected["advanceCoefficient"], delta=0.001)
        self.assertAlmostEqual(result.rpm, expected["rpm"], delta=0.2)
        self.assertAlmostEqual(result.thrustCoefficient, expected["thrustCoefficient"], delta=0.001)
        self.assertAlmostEqual(result.torqueCoefficient, expected["torqueCoefficient"], delta=0.0001)

    def test_reynolds_estimate_within_seven_percent_of_legacy(self):
        case = PopInput.from_dict(json.loads((ROOT / "tests/fixtures/na470-coursepack.input.json").read_text()))
        expected = json.loads((ROOT / "tests/golden/na470-coursepack.output.json").read_text())["results"]

        rn = estimate_reynolds_number(
            case,
            expected["diameterMeters"],
            expected["expandedAreaRatio"],
            expected["advanceCoefficient"]
        )

        self.assertLess(abs(rn - expected["reynoldsNumber"]) / expected["reynoldsNumber"], 0.08)

    def test_auto_reynolds_evaluation_matches_golden_design(self):
        case = PopInput.from_dict(json.loads((ROOT / "tests/fixtures/na470-coursepack.input.json").read_text()))
        expected = json.loads((ROOT / "tests/golden/na470-coursepack.output.json").read_text())["results"]

        result = evaluate_design_auto_reynolds(
            case,
            expected["diameterMeters"],
            expected["pitchDiameterRatio"],
            expected["expandedAreaRatio"]
        )

        self.assertLess(abs(result.reynoldsNumber - expected["reynoldsNumber"]) / expected["reynoldsNumber"], 0.08)
        self.assertAlmostEqual(result.advanceCoefficient, expected["advanceCoefficient"], delta=0.001)
        self.assertAlmostEqual(result.rpm, expected["rpm"], delta=0.5)
        self.assertTrue(passes_burrill_constraint(result, case.burrillBackCavitationPercent))

    def test_burrill_chart_returns_table_values_at_node_points(self):
        self.assertAlmostEqual(burrill_allowable_loading(0.10, 5), 0.066, delta=0.001)
        self.assertAlmostEqual(burrill_allowable_loading(0.40, 5), 0.181, delta=0.001)
        self.assertAlmostEqual(burrill_allowable_loading(1.00, 5), 0.260, delta=0.001)
        self.assertAlmostEqual(burrill_allowable_loading(0.40, 10), 0.219, delta=0.001)
        self.assertAlmostEqual(burrill_allowable_loading(1.00, 10), 0.306, delta=0.001)

    def test_burrill_chart_interpolates_between_nodes(self):
        self.assertAlmostEqual(burrill_allowable_loading(0.45, 5), (0.181 + 0.201) / 2.0, delta=0.001)
        self.assertAlmostEqual(burrill_allowable_loading(0.45, 10), (0.219 + 0.242) / 2.0, delta=0.001)

    def test_burrill_chart_blends_between_5_and_10_percent(self):
        five = burrill_allowable_loading(0.50, 5)
        ten = burrill_allowable_loading(0.50, 10)
        self.assertAlmostEqual(burrill_allowable_loading(0.50, 7), five + 0.4 * (ten - five), delta=0.001)

    def test_burrill_chart_clamps_outside_table_bounds(self):
        self.assertEqual(burrill_allowable_loading(0.05, 5), burrill_allowable_loading(0.10, 5))
        self.assertEqual(burrill_allowable_loading(5.00, 5), burrill_allowable_loading(3.00, 5))

    def test_cavitation_active_case_respects_chart_limit(self):
        case = PopInput.from_dict({
            "projectName": "burrill-active",
            "runId": "cav-1",
            "mode": "evaluation",
            "series": "wageningen_b",
            "pitchType": "fixed",
            "bladeCount": 4,
            "initialExpandedAreaRatio": 0.35,
            "initialPitchDiameterRatio": 0.9,
            "initialDiameterMeters": 3.0,
            "diameterMinMeters": 2.0,
            "diameterMaxMeters": 4.0,
            "requiredThrustKn": 400.0,
            "shipSpeedKnots": 12.0,
            "wakeFraction": 0.0,
            "shaftDepthMeters": 2.0,
            "water": {"kind": "salt_15c", "densityKgM3": 1025.87, "kinematicViscosityM2S": 0.00000118831},
            "burrillBackCavitationPercent": 5
        })
        result = evaluate_design_auto_reynolds(case, 3.0, 0.9, 0.35)
        allowable = burrill_allowable_loading(result.cavitationNumber, 5)
        self.assertGreater(result.burrillLoading, allowable)
        self.assertFalse(passes_burrill_constraint(result, 5))

    def test_controllable_pitch_reduces_efficiency_by_two_percent(self):
        fixed_data = json.loads((ROOT / "tests/fixtures/na470-coursepack.input.json").read_text())
        fixed_data["mode"] = "evaluation"
        fixed_case = PopInput.from_dict(fixed_data)
        controllable_data = dict(fixed_data)
        controllable_data["pitchType"] = "controllable"
        controllable_case = PopInput.from_dict(controllable_data)

        fixed = evaluate_design_auto_reynolds(
            fixed_case,
            fixed_case.initialDiameterMeters,
            fixed_case.initialPitchDiameterRatio,
            fixed_case.initialExpandedAreaRatio
        )
        controllable = evaluate_design_auto_reynolds(
            controllable_case,
            controllable_case.initialDiameterMeters,
            controllable_case.initialPitchDiameterRatio,
            controllable_case.initialExpandedAreaRatio
        )

        self.assertAlmostEqual(controllable.openWaterEfficiency, fixed.openWaterEfficiency * 0.98, delta=0.000001)


    def test_batch_auto_reynolds_matches_scalar_evaluations(self):
        case = PopInput.from_dict(json.loads((ROOT / "tests/fixtures/na470-coursepack.input.json").read_text()))
        d = np.array([3.5, 4.0, 4.6])
        pd = np.array([0.75, 0.8171, 0.9])
        ae = np.array([0.55, 0.6293, 0.75])
        z = np.full(3, 4.0)

        batch = evaluate_designs_auto_reynolds_batch(case, d, pd, ae, z)

        for i in range(3):
            scalar = evaluate_design_auto_reynolds(case, float(d[i]), float(pd[i]), float(ae[i]))
            self.assertAlmostEqual(scalar.openWaterEfficiency, float(batch.openWaterEfficiency[i]), places=8)
            self.assertAlmostEqual(scalar.advanceCoefficient, float(batch.advanceCoefficient[i]), places=8)
            self.assertAlmostEqual(scalar.thrustCoefficient, float(batch.thrustCoefficient[i]), places=8)
            self.assertAlmostEqual(scalar.torqueCoefficient, float(batch.torqueCoefficient[i]), places=8)

    def test_burrill_chart_accepts_numpy_array(self):
        sigma = np.array([0.1, 0.4, 1.0])
        result = burrill_allowable_loading(sigma, 5)
        self.assertEqual(result.shape, (3,))
        self.assertAlmostEqual(float(result[0]), 0.066, delta=0.001)
        self.assertAlmostEqual(float(result[1]), 0.181, delta=0.001)
        self.assertAlmostEqual(float(result[2]), 0.260, delta=0.001)


if __name__ == "__main__":
    unittest.main()
