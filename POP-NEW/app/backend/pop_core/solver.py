from dataclasses import dataclass
from math import pi, sqrt

from .core import advance_coefficient, advance_speed_mps, cavitation_number, propeller_open_water_efficiency, required_thrust_newtons, thrust_coefficient
from .models import PopInput
from .wageningen import wageningen_kq_corrected, wageningen_kt_corrected


SECTION_CHORD_FACTOR = 2.073


@dataclass(frozen=True)
class DesignEvaluation:
    diameterMeters: float
    pitchDiameterRatio: float
    expandedAreaRatio: float
    rpm: float
    advanceCoefficient: float
    thrustCoefficient: float
    torqueCoefficient: float
    openWaterEfficiency: float
    reynoldsNumber: float
    cavitationNumber: float
    burrillLoading: float


def solve_advance_coefficient_for_thrust(case: PopInput, diameter_meters: float, pitch_diameter_ratio: float, expanded_area_ratio: float, reynolds_number: float) -> float:
    low = 0.05
    high = 1.6
    for _ in range(50):
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
    sigma = cavitation_number(case.water.densityKgM3, case.shaftDepthMeters, va, n, diameter_meters)
    loading = burrill_loading(case, diameter_meters, expanded_area_ratio, j)
    eta = propeller_open_water_efficiency(case, j, kt, kq)
    return DesignEvaluation(diameter_meters, pitch_diameter_ratio, expanded_area_ratio, rpm, advance_coefficient(va, n, diameter_meters), kt, kq, eta, reynolds_number, sigma, loading)


def evaluate_design_auto_reynolds(case: PopInput, diameter_meters: float, pitch_diameter_ratio: float, expanded_area_ratio: float) -> DesignEvaluation:
    reynolds_number = 2.0e6
    result = None
    for _ in range(5):
        result = evaluate_design(case, diameter_meters, pitch_diameter_ratio, expanded_area_ratio, reynolds_number)
        next_reynolds_number = estimate_reynolds_number(case, diameter_meters, expanded_area_ratio, result.advanceCoefficient)
        if abs(next_reynolds_number - reynolds_number) / max(reynolds_number, 1.0) < 0.00001:
            return evaluate_design(case, diameter_meters, pitch_diameter_ratio, expanded_area_ratio, next_reynolds_number)
        reynolds_number = next_reynolds_number
    return result


def _required_kt_at_j(case: PopInput, diameter_meters: float, j: float) -> float:
    va = advance_speed_mps(case)
    n = va / (j * diameter_meters)
    return thrust_coefficient(required_thrust_newtons(case), case.water.densityKgM3, n, diameter_meters)


def estimate_reynolds_number(case: PopInput, diameter_meters: float, expanded_area_ratio: float, advance_coefficient_value: float) -> float:
    va = advance_speed_mps(case)
    n = va / (advance_coefficient_value * diameter_meters)
    chord = SECTION_CHORD_FACTOR * expanded_area_ratio * diameter_meters / case.bladeCount
    section_speed = sqrt(va ** 2 + (0.75 * pi * n * diameter_meters) ** 2)
    return section_speed * chord / case.water.kinematicViscosityM2S


def burrill_loading(case: PopInput, diameter_meters: float, expanded_area_ratio: float, advance_coefficient_value: float) -> float:
    va = advance_speed_mps(case)
    n = va / (advance_coefficient_value * diameter_meters)
    section_speed = sqrt(va ** 2 + (0.75 * pi * n * diameter_meters) ** 2)
    disk_area = pi * diameter_meters ** 2 / 4.0
    return required_thrust_newtons(case) / (0.5 * case.water.densityKgM3 * section_speed ** 2 * disk_area * expanded_area_ratio)


def burrill_allowable_loading(cavitation_number_value: float, cavitation_percent: int) -> float:
    if cavitation_percent <= 5:
        factor = 0.26
    elif cavitation_percent >= 10:
        factor = 0.32
    else:
        factor = 0.26 + (cavitation_percent - 5) * (0.32 - 0.26) / 5.0
    return factor * cavitation_number_value


def passes_burrill_constraint(result: DesignEvaluation, cavitation_percent: int) -> bool:
    return result.burrillLoading <= burrill_allowable_loading(result.cavitationNumber, cavitation_percent)
