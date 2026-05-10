import json
import unittest
from pathlib import Path

from pop_core import wageningen_kq, wageningen_kq_corrected, wageningen_kq_reynolds_correction, wageningen_kt, wageningen_kt_corrected, wageningen_kt_reynolds_correction


ROOT = Path(__file__).resolve().parents[1]


class WageningenTests(unittest.TestCase):
    def test_coefficient_table_sizes(self):
        from pop_core.wageningen import KT_TERMS, KQ_TERMS

        self.assertEqual(len(KT_TERMS), 39)
        self.assertEqual(len(KQ_TERMS), 47)

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


if __name__ == "__main__":
    unittest.main()
