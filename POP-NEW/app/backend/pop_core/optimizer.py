from dataclasses import dataclass, replace

from .models import PopInput
from .solver import DesignEvaluation, evaluate_design_auto_reynolds, passes_burrill_constraint


@dataclass(frozen=True)
class OptimizationResult:
    design: DesignEvaluation
    evaluationCount: int


@dataclass(frozen=True)
class BladeSweepEntry:
    bladeCount: int
    result: OptimizationResult | None
    error: str | None


@dataclass(frozen=True)
class BladeSweepResult:
    best: OptimizationResult
    bestBladeCount: int
    entries: list[BladeSweepEntry]
    evaluationCount: int


DEFAULT_BLADE_SWEEP = (3, 4, 5, 6, 7)


def optimize_design_with_blade_sweep(case: PopInput, blade_counts: tuple[int, ...] = DEFAULT_BLADE_SWEEP) -> BladeSweepResult:
    entries = []
    best = None
    best_z = None
    total = 0
    for z in blade_counts:
        try:
            result = optimize_design(replace(case, bladeCount=z))
            entries.append(BladeSweepEntry(z, result, None))
            total += result.evaluationCount
            if best is None or result.design.openWaterEfficiency > best.design.openWaterEfficiency:
                best = result
                best_z = z
        except ValueError as error:
            entries.append(BladeSweepEntry(z, None, str(error)))
    if best is None:
        raise ValueError("No feasible propeller design found at any blade count")
    return BladeSweepResult(best, best_z, entries, total)


def optimize_design(case: PopInput) -> OptimizationResult:
    diameter_low = case.diameterMinMeters
    diameter_high = case.diameterMaxMeters
    pd_low = 0.5
    pd_high = 1.4
    ae_low = 0.3
    ae_high = 1.05
    best = None
    count = 0
    for size in (9, 9, 9):
        best, count = _search_box(case, diameter_low, diameter_high, pd_low, pd_high, ae_low, ae_high, size, best, count)
        diameter_low, diameter_high = _narrow(best.design.diameterMeters, diameter_low, diameter_high, size)
        pd_low, pd_high = _narrow(best.design.pitchDiameterRatio, pd_low, pd_high, size)
        ae_low, ae_high = _narrow(best.design.expandedAreaRatio, ae_low, ae_high, size)
    return best


def _search_box(case: PopInput, diameter_low: float, diameter_high: float, pd_low: float, pd_high: float, ae_low: float, ae_high: float, size: int, best: OptimizationResult | None, count: int) -> tuple[OptimizationResult, int]:
    for diameter in _linspace(diameter_low, diameter_high, size):
        for pd in _linspace(pd_low, pd_high, size):
            for ae in _linspace(ae_low, ae_high, size):
                count += 1
                result = evaluate_design_auto_reynolds(case, diameter, pd, ae)
                if result.torqueCoefficient <= 0 or result.thrustCoefficient <= 0:
                    continue
                if not passes_burrill_constraint(result, case.burrillBackCavitationPercent):
                    continue
                if best is None or result.openWaterEfficiency > best.design.openWaterEfficiency:
                    best = OptimizationResult(result, count)
    if best is None:
        raise ValueError("No feasible propeller design found")
    return best, count


def _linspace(low: float, high: float, size: int) -> list[float]:
    if size == 1:
        return [(low + high) / 2.0]
    step = (high - low) / (size - 1)
    return [low + i * step for i in range(size)]


def _narrow(center: float, low: float, high: float, size: int) -> tuple[float, float]:
    step = (high - low) / (size - 1)
    return max(low, center - step), min(high, center + step)
