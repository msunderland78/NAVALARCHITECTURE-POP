import json
import unittest
from pathlib import Path

from pop_core import PopInput, optimize_design


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


if __name__ == "__main__":
    unittest.main()
