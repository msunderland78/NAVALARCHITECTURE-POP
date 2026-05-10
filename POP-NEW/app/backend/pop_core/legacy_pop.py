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


def parse_legacy_input(text: str) -> dict:
    return {
        "projectName": _project_name(text),
        "runId": _run_id(text),
        "mode": "optimization" if "Optimization Run" in text else "evaluation",
        "series": "wageningen_b",
        "pitchType": "fixed" if "Fixed-Pitch Propeller" in text else "controllable",
        "bladeCount": int(_number_after(text, "Number of Propeller Blades")),
        "initialExpandedAreaRatio": _number_after(text, "Initial Expanded Area Ratio Ae/Ao"),
        "initialPitchDiameterRatio": _number_after(text, "Initial Pitch Diameter Ratio P/Dp"),
        "initialDiameterMeters": _number_after(text, "Initial Propeller Diameter Dp"),
        "diameterMinMeters": _number_after(text, "Minimum Diameter Constriant Dpmin"),
        "diameterMaxMeters": _number_after_any(text, ["Maximum Diameter Constriant Dpmax", "Maximum Diameter Constriant Dpmin"]),
        "requiredThrustKn": _number_after(text, "Required Propeller Thrust"),
        "shipSpeedKnots": _number_after(text, "Ship Speed Vk"),
        "wakeFraction": _number_after(text, "Wake Fraction w"),
        "shaftDepthMeters": _number_after(text, "Depth of Shaft below Waterline"),
        "water": {
            "kind": _water_kind(text),
            "densityKgM3": _number_after(text, "Water Density Rho"),
            "kinematicViscosityM2S": _number_after(text, "Kinematic Viscosity Nu")
        },
        "burrillBackCavitationPercent": int(_number_after(text, "Burrill Back Cavitation Constraint"))
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


def _number_after_any(text: str, labels: list[str]) -> float:
    for label in labels:
        try:
            return _number_after(text, label)
        except ValueError:
            pass
    raise ValueError(f"None of these labels found: {labels}")


def _number_after(text: str, label: str) -> float:
    pattern = re.escape(label) + r"[^\n\r=]*=\s*([-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)"
    matches = re.findall(pattern, text)
    if not matches:
        raise ValueError(f"{label} not found")
    return float(matches[-1])


def _clean_value(value: str) -> str:
    value = value.strip()
    value = re.split(r"\s{2,}|[0-9]?Department|[0-9]?Propeller|[0-9]?Run Identification", value)[0]
    return value.strip()
