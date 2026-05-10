import json
import unittest
from pathlib import Path

from pop_core import PopInput, evaluate_design, solve_advance_coefficient_for_thrust


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


if __name__ == "__main__":
    unittest.main()
