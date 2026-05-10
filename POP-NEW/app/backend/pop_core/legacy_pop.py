import re
from pathlib import Path

from .cfb import CfbFile


def extract_printable_text(data: bytes) -> str:
    chars = []
    for value in data:
        if value in (9, 10, 13) or 32 <= value <= 126:
            chars.append(chr(value))
        else:
            chars.append("\n")
    text = "".join(chars)
    text = re.sub(r"\n{2,}", "\n", text)
    return text


def read_legacy_pop_text(path: Path) -> str:
    cfb = CfbFile.from_path(path)
    return extract_printable_text(cfb.read_stream("Contents"))


def read_legacy_pop_text_bytes(data: bytes) -> str:
    cfb = CfbFile(data)
    return extract_printable_text(cfb.read_stream("Contents"))


def parse_legacy_input(text: str) -> dict:
    return {
        "projectName": _project_name(text),
        "runId": _run_id(text),
        "mode": "optimization" if "Optimization Run" in text else "evaluation",
        "series": "wageningen_b",
        "pitchType": "fixed" if "Fixed-Pitch Propeller" in text else "controllable",
        "bladeCount": int(_number_after(text, "Number of Propeller Blades", first=True)),
        "initialExpandedAreaRatio": _number_after(text, "Initial Expanded Area Ratio Ae/Ao", first=True),
        "initialPitchDiameterRatio": _number_after(text, "Initial Pitch Diameter Ratio P/Dp", first=True),
        "initialDiameterMeters": _number_after(text, "Initial Propeller Diameter Dp", first=True),
        "diameterMinMeters": _number_after(text, "Minimum Diameter Constriant Dpmin", first=True),
        "diameterMaxMeters": _number_after_any(text, ["Maximum Diameter Constriant Dpmax", "Maximum Diameter Constriant Dpmin"], first=True),
        "requiredThrustKn": _number_after(text, "Required Propeller Thrust", first=True),
        "shipSpeedKnots": _number_after(text, "Ship Speed Vk", first=True),
        "wakeFraction": _number_after(text, "Wake Fraction w", first=True),
        "shaftDepthMeters": _number_after(text, "Depth of Shaft below Waterline", first=True),
        "water": {
            "kind": _water_kind(text),
            "densityKgM3": _number_after(text, "Water Density Rho", first=True),
            "kinematicViscosityM2S": _number_after(text, "Kinematic Viscosity Nu", first=True)
        },
        "burrillBackCavitationPercent": int(_number_after(text, "Burrill Back Cavitation Constraint", first=True))
    }


def parse_legacy_output(text: str) -> dict:
    return {
        "diameterMeters": _number_after(text, "Propeller Diameter Dp"),
        "pitchMeters": _number_after(text, "Propeller Pitch P"),
        "pitchDiameterRatio": _number_after(text, "Pitch Diameter Ratio P/Dp"),
        "expandedAreaRatio": _number_after(text, "Expanded Area Ratio Ae/Ao"),
        "rpm": _number_after(text, "Propeller Revolutions per Minute"),
        "advanceCoefficient": _number_after(text, "Advance Coefficient J"),
        "thrustCoefficient": _number_after(text, "Thrust Coefficient KT"),
        "torqueCoefficient": _number_after(text, "Torque Coefficient KQ"),
        "openWaterEfficiency": _number_after(text, "Propeller Open Water Efficiency Eta 0"),
        "thrustKn": _number_after(text, "Propeller Thrust"),
        "reynoldsNumber": _number_after(text, "Reynolds Number RN"),
        "cavitationNumber": _number_after(text, "Cavitation Number Sigma"),
        "optimizationSearchEvaluationCount": int(_number_after(text, "Optimization Search Evaluation Count"))
    }


def _project_name(text: str) -> str:
    match = re.search(r"Project Name:\s*([^\n\r]+)", text)
    if match:
        return _clean_value(match.group(1))
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines[0]


def _run_id(text: str) -> str:
    match = re.search(r"Run Identification:\s*([^\n\r]+)", text)
    if match:
        return _clean_value(match.group(1))
    raise ValueError("Run Identification not found")


def _water_kind(text: str) -> str:
    if "Salt Water at 15 degrees Celsius" in text or "salt@15C" in text:
        return "salt_15c"
    if "Fresh Water at 15 degrees Celsius" in text or "Fresh@15C" in text:
        return "fresh_15c"
    return "custom"


def _number_after_any(text: str, labels: list[str], first: bool = False) -> float:
    for label in labels:
        try:
            return _number_after(text, label, first=first)
        except ValueError:
            pass
    raise ValueError(f"None of these labels found: {labels}")


def _number_after(text: str, label: str, first: bool = False) -> float:
    pattern = re.escape(label) + r"[^\n\r=]*=\s*([-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)"
    matches = re.findall(pattern, text)
    if not matches:
        raise ValueError(f"{label} not found")
    return float(matches[0] if first else matches[-1])


def _clean_value(value: str) -> str:
    value = value.strip()
    value = re.split(r"\s{2,}|\d? Department|\d? Propeller|\d? Run Identification|[0-9]?Department|[0-9]?Propeller|[0-9]?Run Identification", value)[0]
    value = re.sub(r"(?<=[A-Za-z)])\d+$", "", value)
    return value.strip()
