from dataclasses import dataclass
from math import isfinite


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
        return cls(
            projectName=values["projectName"],
            runId=values["runId"],
            mode=values["mode"],
            series=values["series"],
            pitchType=values["pitchType"],
            bladeCount=values["bladeCount"],
            initialExpandedAreaRatio=values["initialExpandedAreaRatio"],
            initialPitchDiameterRatio=values["initialPitchDiameterRatio"],
            initialDiameterMeters=values["initialDiameterMeters"],
            diameterMinMeters=values["diameterMinMeters"],
            diameterMaxMeters=values["diameterMaxMeters"],
            requiredThrustKn=values["requiredThrustKn"],
            shipSpeedKnots=values["shipSpeedKnots"],
            wakeFraction=values["wakeFraction"],
            shaftDepthMeters=values["shaftDepthMeters"],
            water=Water(**values["water"]),
            burrillBackCavitationPercent=values["burrillBackCavitationPercent"]
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
