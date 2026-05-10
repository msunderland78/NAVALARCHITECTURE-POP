import json
import unittest
from pathlib import Path

from pop_core import parse_legacy_input, parse_legacy_output, read_legacy_pop_text


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parent


class LegacyPopTests(unittest.TestCase):
    def test_parse_legacy_text_to_input(self):
        text = (ROOT / "tests/fixtures/na470-coursepack.legacy-text.txt").read_text()
        expected = json.loads((ROOT / "tests/fixtures/na470-coursepack.input.json").read_text())

        self.assertEqual(parse_legacy_input(text), expected)

    def test_parse_legacy_text_to_output(self):
        text = (ROOT / "tests/fixtures/na470-coursepack.legacy-text.txt").read_text()
        expected = json.loads((ROOT / "tests/golden/na470-coursepack.output.json").read_text())

        self.assertEqual(parse_legacy_output(text), expected["results"])

    def test_read_local_legacy_pop_when_available(self):
        path = PROJECT_ROOT / "POP-OLD/POPout.pop"
        if not path.exists():
            self.skipTest("POP-OLD is not present")

        text = read_legacy_pop_text(path)
        parsed = parse_legacy_output(text)

        self.assertEqual(parsed["diameterMeters"], 4.6)
        self.assertEqual(parsed["optimizationSearchEvaluationCount"], 73)


if __name__ == "__main__":
    unittest.main()
