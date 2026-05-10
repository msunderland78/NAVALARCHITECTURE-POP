from .models import PopInput


KNOT_TO_MPS = 0.514444


def advance_speed_mps(case: PopInput) -> float:
    return case.shipSpeedKnots * KNOT_TO_MPS * (1.0 - case.wakeFraction)


def required_thrust_newtons(case: PopInput) -> float:
    return case.requiredThrustKn * 1000.0


def pitch_meters(diameter_meters: float, pitch_diameter_ratio: float) -> float:
    return diameter_meters * pitch_diameter_ratio
