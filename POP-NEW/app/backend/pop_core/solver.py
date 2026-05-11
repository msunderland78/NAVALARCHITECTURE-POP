from dataclasses import dataclass
from math import pi, sqrt

import numpy as np

from .core import advance_coefficient, advance_speed_mps, cavitation_number, propeller_open_water_efficiency, required_thrust_newtons, thrust_coefficient
from .models import PopInput
from .wageningen import wageningen_kq_corrected, wageningen_kt_corrected


SECTION_CHORD_FACTOR = 2.073
BISECTION_ITERATIONS = 20


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


@dataclass(frozen=True)
class DesignBatch:
    diameterMeters: np.ndarray
    pitchDiameterRatio: np.ndarray
    expandedAreaRatio: np.ndarray
    rpm: np.ndarray
    advanceCoefficient: np.ndarray
    thrustCoefficient: np.ndarray
    torqueCoefficient: np.ndarray
    openWaterEfficiency: np.ndarray
    reynoldsNumber: np.ndarray
    cavitationNumber: np.ndarray
    burrillLoading: np.ndarray

    def at(self, index: int) -> DesignEvaluation:
        return DesignEvaluation(
            float(self.diameterMeters[index]),
            float(self.pitchDiameterRatio[index]),
            float(self.expandedAreaRatio[index]),
            float(self.rpm[index]),
            float(self.advanceCoefficient[index]),
            float(self.thrustCoefficient[index]),
            float(self.torqueCoefficient[index]),
            float(self.openWaterEfficiency[index]),
            float(self.reynoldsNumber[index]),
            float(self.cavitationNumber[index]),
            float(self.burrillLoading[index])
        )


def solve_advance_coefficient_for_thrust(case: PopInput, diameter_meters: float, pitch_diameter_ratio: float, expanded_area_ratio: float, reynolds_number: float) -> float:
    j = solve_advance_coefficient_for_thrust_batch(
        case,
        np.array([diameter_meters], dtype=np.float64),
        np.array([pitch_diameter_ratio], dtype=np.float64),
        np.array([expanded_area_ratio], dtype=np.float64),
        np.array([case.bladeCount], dtype=np.float64),
        np.array([reynolds_number], dtype=np.float64)
    )
    return float(j[0])


def solve_advance_coefficient_for_thrust_batch(case: PopInput, diameter: np.ndarray, pitch_diameter_ratio: np.ndarray, expanded_area_ratio: np.ndarray, blade_count: np.ndarray, reynolds_number: np.ndarray) -> np.ndarray:
    va = advance_speed_mps(case)
    thrust = required_thrust_newtons(case)
    rho = case.water.densityKgM3
    low = np.full_like(diameter, 0.05)
    high = np.full_like(diameter, 1.6)
    for _ in range(BISECTION_ITERATIONS):
        mid = (low + high) / 2.0
        n = va / (mid * diameter)
        kt_required = thrust / (rho * n ** 2 * diameter ** 4)
        kt_available = wageningen_kt_corrected(mid, pitch_diameter_ratio, expanded_area_ratio, blade_count, reynolds_number)
        condition = kt_available > kt_required
        low = np.where(condition, mid, low)
        high = np.where(condition, high, mid)
    return (low + high) / 2.0


def evaluate_design(case: PopInput, diameter_meters: float, pitch_diameter_ratio: float, expanded_area_ratio: float, reynolds_number: float) -> DesignEvaluation:
    batch = evaluate_designs_batch(
        case,
        np.array([diameter_meters], dtype=np.float64),
        np.array([pitch_diameter_ratio], dtype=np.float64),
        np.array([expanded_area_ratio], dtype=np.float64),
        np.array([case.bladeCount], dtype=np.float64),
        np.array([reynolds_number], dtype=np.float64)
    )
    return batch.at(0)


def evaluate_designs_batch(case: PopInput, diameter: np.ndarray, pitch_diameter_ratio: np.ndarray, expanded_area_ratio: np.ndarray, blade_count: np.ndarray, reynolds_number: np.ndarray) -> DesignBatch:
    va = advance_speed_mps(case)
    thrust = required_thrust_newtons(case)
    rho = case.water.densityKgM3
    j = solve_advance_coefficient_for_thrust_batch(case, diameter, pitch_diameter_ratio, expanded_area_ratio, blade_count, reynolds_number)
    n = va / (j * diameter)
    rpm = n * 60.0
    kt = thrust / (rho * n ** 2 * diameter ** 4)
    kq = wageningen_kq_corrected(j, pitch_diameter_ratio, expanded_area_ratio, blade_count, reynolds_number)
    sigma = _cavitation_number_batch(rho, case.shaftDepthMeters, va, n, diameter)
    loading = _burrill_loading_batch(thrust, rho, va, n, diameter, expanded_area_ratio)
    eta_open = j * kt / (2.0 * pi * kq)
    eta = eta_open * (0.98 if case.pitchType == "controllable" else 1.0)
    return DesignBatch(diameter, pitch_diameter_ratio, expanded_area_ratio, rpm, j, kt, kq, eta, reynolds_number, sigma, loading)


def evaluate_design_auto_reynolds(case: PopInput, diameter_meters: float, pitch_diameter_ratio: float, expanded_area_ratio: float) -> DesignEvaluation:
    batch = evaluate_designs_auto_reynolds_batch(
        case,
        np.array([diameter_meters], dtype=np.float64),
        np.array([pitch_diameter_ratio], dtype=np.float64),
        np.array([expanded_area_ratio], dtype=np.float64),
        np.array([case.bladeCount], dtype=np.float64)
    )
    return batch.at(0)


def evaluate_designs_auto_reynolds_batch(case: PopInput, diameter: np.ndarray, pitch_diameter_ratio: np.ndarray, expanded_area_ratio: np.ndarray, blade_count: np.ndarray) -> DesignBatch:
    reynolds = np.full_like(diameter, 2.0e6)
    batch = evaluate_designs_batch(case, diameter, pitch_diameter_ratio, expanded_area_ratio, blade_count, reynolds)
    for _ in range(4):
        next_reynolds = _estimate_reynolds_batch(case, diameter, expanded_area_ratio, blade_count, batch.advanceCoefficient)
        delta = np.abs(next_reynolds - reynolds) / np.maximum(reynolds, 1.0)
        if np.all(delta < 0.00001):
            return batch
        reynolds = next_reynolds
        batch = evaluate_designs_batch(case, diameter, pitch_diameter_ratio, expanded_area_ratio, blade_count, reynolds)
    return batch


def estimate_reynolds_number(case: PopInput, diameter_meters: float, expanded_area_ratio: float, advance_coefficient_value: float) -> float:
    va = advance_speed_mps(case)
    n = va / (advance_coefficient_value * diameter_meters)
    chord = SECTION_CHORD_FACTOR * expanded_area_ratio * diameter_meters / case.bladeCount
    section_speed = sqrt(va ** 2 + (0.75 * pi * n * diameter_meters) ** 2)
    return section_speed * chord / case.water.kinematicViscosityM2S


def _estimate_reynolds_batch(case: PopInput, diameter: np.ndarray, expanded_area_ratio: np.ndarray, blade_count: np.ndarray, advance_coefficient_value: np.ndarray) -> np.ndarray:
    va = advance_speed_mps(case)
    n = va / (advance_coefficient_value * diameter)
    chord = SECTION_CHORD_FACTOR * expanded_area_ratio * diameter / blade_count
    section_speed = np.sqrt(va ** 2 + (0.75 * pi * n * diameter) ** 2)
    return section_speed * chord / case.water.kinematicViscosityM2S


def burrill_loading(case: PopInput, diameter_meters: float, expanded_area_ratio: float, advance_coefficient_value: float) -> float:
    va = advance_speed_mps(case)
    n = va / (advance_coefficient_value * diameter_meters)
    section_speed = sqrt(va ** 2 + (0.75 * pi * n * diameter_meters) ** 2)
    disk_area = pi * diameter_meters ** 2 / 4.0
    return required_thrust_newtons(case) / (0.5 * case.water.densityKgM3 * section_speed ** 2 * disk_area * expanded_area_ratio)


def _burrill_loading_batch(thrust: float, rho: float, va: float, n: np.ndarray, diameter: np.ndarray, expanded_area_ratio: np.ndarray) -> np.ndarray:
    section_speed = np.sqrt(va ** 2 + (0.75 * pi * n * diameter) ** 2)
    disk_area = pi * diameter ** 2 / 4.0
    return thrust / (0.5 * rho * section_speed ** 2 * disk_area * expanded_area_ratio)


def _cavitation_number_batch(rho: float, shaft_depth: float, va: float, n: np.ndarray, diameter: np.ndarray) -> np.ndarray:
    pressure = 101325.0 + rho * 9.80665 * shaft_depth
    tangential_07 = 0.7 * pi * n * diameter
    return pressure / (0.5 * rho * (va ** 2 + tangential_07 ** 2))


BURRILL_SIGMA = (0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.80, 1.00, 1.50, 2.00, 3.00)
BURRILL_TAUC_5PCT = (0.066, 0.118, 0.155, 0.181, 0.201, 0.218, 0.243, 0.260, 0.286, 0.301, 0.320)
BURRILL_TAUC_10PCT = (0.086, 0.148, 0.188, 0.219, 0.242, 0.260, 0.287, 0.306, 0.336, 0.354, 0.380)

_BURRILL_SIGMA_NP = np.array(BURRILL_SIGMA, dtype=np.float64)
_BURRILL_5_NP = np.array(BURRILL_TAUC_5PCT, dtype=np.float64)
_BURRILL_10_NP = np.array(BURRILL_TAUC_10PCT, dtype=np.float64)


def burrill_allowable_loading(cavitation_number_value, cavitation_percent: int):
    sigma = np.asarray(cavitation_number_value, dtype=np.float64)
    tau5 = np.interp(sigma, _BURRILL_SIGMA_NP, _BURRILL_5_NP)
    tau10 = np.interp(sigma, _BURRILL_SIGMA_NP, _BURRILL_10_NP)
    if cavitation_percent <= 5:
        result = tau5
    elif cavitation_percent >= 10:
        result = tau10
    else:
        result = tau5 + (cavitation_percent - 5) * (tau10 - tau5) / 5.0
    if sigma.ndim == 0:
        return float(result)
    return result


def passes_burrill_constraint(result: DesignEvaluation, cavitation_percent: int) -> bool:
    return result.burrillLoading <= burrill_allowable_loading(result.cavitationNumber, cavitation_percent)
