import json
import unittest
from pathlib import Path

import numpy as np

from pop_core import wageningen_kq, wageningen_kq_corrected, wageningen_kq_reynolds_correction, wageningen_kt, wageningen_kt_corrected, wageningen_kt_reynolds_correction


ROOT = Path(__file__).resolve().parents[1]


class WageningenTests(unittest.TestCase):
    def test_coefficient_table_sizes(self):
        from pop_core.wageningen import KT_TERMS, KQ_TERMS

        self.assertEqual(len(KT_TERMS), 39)
        self.assertEqual(len(KQ_TERMS), 47)

    def test_landmark_coefficients_match_published_values(self):
        # Spot-check coefficients from Bernitsas, Ray, Kinley (1981), Tables I and II.
        # If any of these drift, the polynomial has been retabled and the
        # provenance doc must be updated to match.
        from pop_core.wageningen import KT_TERMS, KQ_TERMS

        kt_index = {(t.j_power, t.pd_power, t.aeao_power, t.blade_power): t.coefficient for t in KT_TERMS}
        kq_index = {(t.j_power, t.pd_power, t.aeao_power, t.blade_power): t.coefficient for t in KQ_TERMS}

        landmark_kt = {
            (0, 0, 0, 0): 0.00880496,
            (1, 0, 0, 0): -0.204554,
            (0, 1, 0, 0): 0.166351,
            (0, 2, 0, 0): 0.158114,
            (0, 0, 0, 2): -0.000606848,
        }
        landmark_kq = {
            (0, 0, 0, 0): 0.00379368,
            (2, 0, 0, 0): 0.00886523,
            (1, 1, 0, 0): -0.032241,
            (0, 6, 1, 1): -0.00142121,
            (1, 6, 2, 2): 0.0000554194,
        }
        for exponents, value in landmark_kt.items():
            self.assertAlmostEqual(kt_index[exponents], value, places=8, msg=f"KT[{exponents}]")
        for exponents, value in landmark_kq.items():
            self.assertAlmostEqual(kq_index[exponents], value, places=8, msg=f"KQ[{exponents}]")

    def test_na470_base_polynomial_point(self):
        case = json.loads((ROOT / "tests/fixtures/na470-coursepack.input.json").read_text())
        expected = json.loads((ROOT / "tests/golden/na470-coursepack.output.json").read_text())["results"]

        kt = wageningen_kt(
            expected["advanceCoefficient"],
            expected["pitchDiameterRatio"],
            expected["expandedAreaRatio"],
            case["bladeCount"]
        )
        kq = wageningen_kq(
            expected["advanceCoefficient"],
            expected["pitchDiameterRatio"],
            expected["expandedAreaRatio"],
            case["bladeCount"]
        )

        self.assertAlmostEqual(kt, expected["thrustCoefficient"], delta=0.003)
        self.assertAlmostEqual(kq, 0.023198, delta=0.000001)

    def test_na470_reynolds_correction(self):
        case = json.loads((ROOT / "tests/fixtures/na470-coursepack.input.json").read_text())
        expected = json.loads((ROOT / "tests/golden/na470-coursepack.output.json").read_text())["results"]
        j = expected["advanceCoefficient"]
        pd = expected["pitchDiameterRatio"]
        aeao = expected["expandedAreaRatio"]
        blade_count = case["bladeCount"]
        rn = expected["reynoldsNumber"]

        self.assertAlmostEqual(wageningen_kt_reynolds_correction(j, pd, aeao, blade_count, rn), 0.00067, delta=0.00001)
        self.assertAlmostEqual(wageningen_kq_reynolds_correction(j, pd, aeao, blade_count, rn), -0.00115, delta=0.00001)

    def test_na470_corrected_golden_point(self):
        case = json.loads((ROOT / "tests/fixtures/na470-coursepack.input.json").read_text())
        expected = json.loads((ROOT / "tests/golden/na470-coursepack.output.json").read_text())["results"]
        j = expected["advanceCoefficient"]
        pd = expected["pitchDiameterRatio"]
        aeao = expected["expandedAreaRatio"]
        blade_count = case["bladeCount"]
        rn = expected["reynoldsNumber"]

        self.assertAlmostEqual(wageningen_kt_corrected(j, pd, aeao, blade_count, rn), expected["thrustCoefficient"], delta=0.0001)
        self.assertAlmostEqual(wageningen_kq_corrected(j, pd, aeao, blade_count, rn), expected["torqueCoefficient"], delta=0.00001)


    def test_polynomial_accepts_array_inputs_and_matches_scalar(self):
        j_arr = np.array([0.4, 0.5408, 0.7])
        pd_arr = np.array([0.7, 0.8171, 0.9])
        ae_arr = np.array([0.55, 0.6293, 0.7])
        z_arr = np.array([4, 4, 4])
        rn_arr = np.array([3.0e7, 3.68e7, 4.0e7])

        batch_kt = wageningen_kt_corrected(j_arr, pd_arr, ae_arr, z_arr, rn_arr)
        batch_kq = wageningen_kq_corrected(j_arr, pd_arr, ae_arr, z_arr, rn_arr)

        for i in range(3):
            scalar_kt = wageningen_kt_corrected(float(j_arr[i]), float(pd_arr[i]), float(ae_arr[i]), int(z_arr[i]), float(rn_arr[i]))
            scalar_kq = wageningen_kq_corrected(float(j_arr[i]), float(pd_arr[i]), float(ae_arr[i]), int(z_arr[i]), float(rn_arr[i]))
            self.assertAlmostEqual(float(batch_kt[i]), scalar_kt, places=12)
            self.assertAlmostEqual(float(batch_kq[i]), scalar_kq, places=12)

    def test_scalar_call_returns_python_float(self):
        kt = wageningen_kt(0.5, 0.9, 0.65, 4)
        self.assertIsInstance(kt, float)


if __name__ == "__main__":
    unittest.main()
