import json
import unittest
from pathlib import Path

from pop_core import advance_coefficient, advance_speed_mps, cavitation_number, open_water_efficiency, required_thrust_newtons, revolutions_per_second, thrust_coefficient, PopInput


ROOT = Path(__file__).resolve().parents[1]


class CoreRelationshipTests(unittest.TestCase):
    def test_golden_output_is_physically_consistent(self):
        case_data = json.loads((ROOT / "tests/fixtures/na470-coursepack.input.json").read_text())
        output_data = json.loads((ROOT / "tests/golden/na470-coursepack.output.json").read_text())["results"]
        case = PopInput.from_dict(case_data)

        va = advance_speed_mps(case)
        n = revolutions_per_second(output_data["rpm"])
        j = advance_coefficient(va, n, output_data["diameterMeters"])
        kt = thrust_coefficient(required_thrust_newtons(case), case.water.densityKgM3, n, output_data["diameterMeters"])
        eta = open_water_efficiency(output_data["advanceCoefficient"], output_data["thrustCoefficient"], output_data["torqueCoefficient"])
        sigma = cavitation_number(case.water.densityKgM3, case.shaftDepthMeters, va, n, output_data["diameterMeters"])

        self.assertAlmostEqual(j, output_data["advanceCoefficient"], delta=0.001)
        self.assertAlmostEqual(kt, output_data["thrustCoefficient"], delta=0.001)
        self.assertAlmostEqual(eta, output_data["openWaterEfficiency"], delta=0.002)
        self.assertAlmostEqual(sigma, output_data["cavitationNumber"], delta=0.006)


if __name__ == "__main__":
    unittest.main()
