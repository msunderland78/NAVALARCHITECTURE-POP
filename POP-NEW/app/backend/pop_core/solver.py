from dataclasses import dataclass

from .core import advance_coefficient, advance_speed_mps, required_thrust_newtons, revolutions_per_second, thrust_coefficient
from .models import PopInput
from .wageningen import wageningen_kq_corrected, wageningen_kt_corrected


@dataclass(frozen=True)
class DesignEvaluation:
    diameterMeters: float
    pitchDiameterRatio: float
    expandedAreaRatio: float
    rpm: float
    advanceCoefficient: float
    thrustCoefficient: float
    torqueCoefficient: float


def solve_advance_coefficient_for_thrust(case: PopInput, diameter_meters: float, pitch_diameter_ratio: float, expanded_area_ratio: float, reynolds_number: float) -> float:
    low = 0.05
    high = 1.6
    for _ in range(80):
        mid = (low + high) / 2.0
        kt_required = _required_kt_at_j(case, diameter_meters, mid)
        kt_available = wageningen_kt_corrected(mid, pitch_diameter_ratio, expanded_area_ratio, case.bladeCount, reynolds_number)
        if kt_available > kt_required:
            low = mid
        else:
            high = mid
    return (low + high) / 2.0


def evaluate_design(case: PopInput, diameter_meters: float, pitch_diameter_ratio: float, expanded_area_ratio: float, reynolds_number: float) -> DesignEvaluation:
    j = solve_advance_coefficient_for_thrust(case, diameter_meters, pitch_diameter_ratio, expanded_area_ratio, reynolds_number)
    va = advance_speed_mps(case)
    n = va / (j * diameter_meters)
    rpm = n * 60.0
    kt = thrust_coefficient(required_thrust_newtons(case), case.water.densityKgM3, n, diameter_meters)
    kq = wageningen_kq_corrected(j, pitch_diameter_ratio, expanded_area_ratio, case.bladeCount, reynolds_number)
    return DesignEvaluation(diameter_meters, pitch_diameter_ratio, expanded_area_ratio, rpm, advance_coefficient(va, n, diameter_meters), kt, kq)


def _required_kt_at_j(case: PopInput, diameter_meters: float, j: float) -> float:
    va = advance_speed_mps(case)
    n = va / (j * diameter_meters)
    return thrust_coefficient(required_thrust_newtons(case), case.water.densityKgM3, n, diameter_meters)
