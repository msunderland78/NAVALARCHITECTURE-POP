from dataclasses import dataclass


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
