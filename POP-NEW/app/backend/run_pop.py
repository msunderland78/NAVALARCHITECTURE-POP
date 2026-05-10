import json
import sys
from pathlib import Path

from pop_core import PopInput, result_payload, run_case


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: run_pop.py input.json", file=sys.stderr)
        return 2
    case = PopInput.from_dict(json.loads(Path(sys.argv[1]).read_text()))
    print(json.dumps(result_payload(case, run_case(case)), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
