import json
import unittest
from pathlib import Path

from pop_core import PopInput, estimate_reynolds_number, evaluate_design, evaluate_design_auto_reynolds, passes_burrill_constraint, solve_advance_coefficient_for_thrust


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

    def test_reynolds_estimate_matches_golden_case(self):
        case = PopInput.from_dict(json.loads((ROOT / "tests/fixtures/na470-coursepack.input.json").read_text()))
        expected = json.loads((ROOT / "tests/golden/na470-coursepack.output.json").read_text())["results"]

        rn = estimate_reynolds_number(
            case,
            expected["diameterMeters"],
            expected["expandedAreaRatio"],
            expected["advanceCoefficient"]
        )

        self.assertAlmostEqual(rn, expected["reynoldsNumber"], delta=1000.0)

    def test_auto_reynolds_evaluation_matches_golden_design(self):
        case = PopInput.from_dict(json.loads((ROOT / "tests/fixtures/na470-coursepack.input.json").read_text()))
        expected = json.loads((ROOT / "tests/golden/na470-coursepack.output.json").read_text())["results"]

        result = evaluate_design_auto_reynolds(
            case,
            expected["diameterMeters"],
            expected["pitchDiameterRatio"],
            expected["expandedAreaRatio"]
        )

        self.assertAlmostEqual(result.reynoldsNumber, expected["reynoldsNumber"], delta=20000.0)
        self.assertAlmostEqual(result.advanceCoefficient, expected["advanceCoefficient"], delta=0.001)
        self.assertAlmostEqual(result.rpm, expected["rpm"], delta=0.2)
        self.assertTrue(passes_burrill_constraint(result, case.burrillBackCavitationPercent))


if __name__ == "__main__":
    unittest.main()
