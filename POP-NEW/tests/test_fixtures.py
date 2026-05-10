import json
import unittest
from pathlib import Path

from pop_core import advance_speed_mps, pitch_meters, required_thrust_newtons, PopInput


ROOT = Path(__file__).resolve().parents[1]


class FixtureTests(unittest.TestCase):
    def test_na470_input_loads(self):
        data = json.loads((ROOT / "tests/fixtures/na470-coursepack.input.json").read_text())
        case = PopInput.from_dict(data)

        self.assertEqual(case.projectName, "NA 470 Coursepack Example")
        self.assertEqual(case.runId, "test 1.0")
        self.assertEqual(case.bladeCount, 4)
        self.assertEqual(case.water.kind, "salt_15c")

    def test_na470_basic_unit_conversions(self):
        data = json.loads((ROOT / "tests/fixtures/na470-coursepack.input.json").read_text())
        case = PopInput.from_dict(data)

        self.assertAlmostEqual(advance_speed_mps(case), 6.09101696)
        self.assertAlmostEqual(required_thrust_newtons(case), 444822.1)
        self.assertAlmostEqual(pitch_meters(4.6, 0.8171), 3.75866)


if __name__ == "__main__":
    unittest.main()
