from dataclasses import dataclass
from math import isfinite


TEXT_LIMIT = 120


@dataclass(frozen=True)
class Water:
    kind: str
    densityKgM3: float
    kinematicViscosityM2S: float


@dataclass(frozen=True)
class PopInput:
    projectName: str
    runId: str
    mode: str
    series: str
    pitchType: str
    bladeCount: int
    initialExpandedAreaRatio: float
    initialPitchDiameterRatio: float
    initialDiameterMeters: float
    diameterMinMeters: float
    diameterMaxMeters: float
    requiredThrustKn: float
    shipSpeedKnots: float
    wakeFraction: float
    shaftDepthMeters: float
    water: Water
    burrillBackCavitationPercent: int

    @classmethod
    def from_dict(cls, values: dict) -> "PopInput":
        if not isinstance(values, dict):
            raise ValueError("input must be a JSON object")
        water = _object(values, "water")
        return cls(
            projectName=_text(values, "projectName"),
            runId=_text(values, "runId"),
            mode=_text(values, "mode"),
            series=_text(values, "series"),
            pitchType=_text(values, "pitchType"),
            bladeCount=_integer(values, "bladeCount"),
            initialExpandedAreaRatio=_number(values, "initialExpandedAreaRatio"),
            initialPitchDiameterRatio=_number(values, "initialPitchDiameterRatio"),
            initialDiameterMeters=_number(values, "initialDiameterMeters"),
            diameterMinMeters=_number(values, "diameterMinMeters"),
            diameterMaxMeters=_number(values, "diameterMaxMeters"),
            requiredThrustKn=_number(values, "requiredThrustKn"),
            shipSpeedKnots=_number(values, "shipSpeedKnots"),
            wakeFraction=_number(values, "wakeFraction"),
            shaftDepthMeters=_number(values, "shaftDepthMeters"),
            water=Water(
                kind=_text(water, "kind"),
                densityKgM3=_number(water, "densityKgM3"),
                kinematicViscosityM2S=_number(water, "kinematicViscosityM2S")
            ),
            burrillBackCavitationPercent=_integer(values, "burrillBackCavitationPercent")
        )


def validate_case(case: PopInput):
    errors = []
    if case.mode not in {"evaluation", "optimization"}:
        errors.append("mode must be evaluation or optimization")
    if case.series != "wageningen_b":
        errors.append("series must be wageningen_b")
    if case.pitchType not in {"fixed", "controllable"}:
        errors.append("pitchType must be fixed or controllable")
    if case.bladeCount < 3 or case.bladeCount > 7:
        errors.append("bladeCount must be between 3 and 7")
    if case.mode == "evaluation":
        _range(errors, "initialExpandedAreaRatio", case.initialExpandedAreaRatio, 0.3, 1.05)
        _range(errors, "initialPitchDiameterRatio", case.initialPitchDiameterRatio, 0.5, 1.4)
        _positive(errors, "initialDiameterMeters", case.initialDiameterMeters)
    if case.mode == "optimization":
        _positive(errors, "diameterMinMeters", case.diameterMinMeters)
        _positive(errors, "diameterMaxMeters", case.diameterMaxMeters)
        if isfinite(case.diameterMinMeters) and isfinite(case.diameterMaxMeters) and case.diameterMinMeters > case.diameterMaxMeters:
            errors.append("diameterMinMeters must be less than or equal to diameterMaxMeters")
    _positive(errors, "requiredThrustKn", case.requiredThrustKn)
    _positive(errors, "shipSpeedKnots", case.shipSpeedKnots)
    _range(errors, "wakeFraction", case.wakeFraction, 0.0, 0.9)
    _range(errors, "shaftDepthMeters", case.shaftDepthMeters, 0.0, float("inf"))
    _positive(errors, "water.densityKgM3", case.water.densityKgM3)
    _positive(errors, "water.kinematicViscosityM2S", case.water.kinematicViscosityM2S)
    _range(errors, "burrillBackCavitationPercent", case.burrillBackCavitationPercent, 0, 100)
    if errors:
        raise ValueError("; ".join(errors))


def _positive(errors: list[str], name: str, value: float):
    if not isfinite(value) or value <= 0:
        errors.append(f"{name} must be greater than zero")


def _range(errors: list[str], name: str, value: float, low: float, high: float):
    if not isfinite(value) or value < low or value > high:
        errors.append(f"{name} must be between {low} and {high}")


def _required(values: dict, name: str):
    if name not in values:
        raise ValueError(f"{name} is required")
    return values[name]


def _object(values: dict, name: str) -> dict:
    value = _required(values, name)
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    return value


def _text(values: dict, name: str) -> str:
    value = _required(values, name)
    if not isinstance(value, str):
        raise ValueError(f"{name} must be text")
    value = value.strip()
    if len(value) > TEXT_LIMIT:
        raise ValueError(f"{name} must be {TEXT_LIMIT} characters or fewer")
    return value


def _number(values: dict, name: str) -> float:
    value = _required(values, name)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number")
    if not isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    return float(value)


def _integer(values: dict, name: str) -> int:
    value = _required(values, name)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")
    return value
