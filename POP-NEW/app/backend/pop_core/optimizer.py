from dataclasses import dataclass, replace

import numpy as np

from .models import PopInput
from .solver import DesignEvaluation, burrill_allowable_loading, evaluate_designs_auto_reynolds_batch


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
PD_RANGE = (0.5, 1.4)
AE_RANGE = (0.3, 1.05)
GRID_SIZES = (9, 9, 9)


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
    pd_low, pd_high = PD_RANGE
    ae_low, ae_high = AE_RANGE
    best = None
    count = 0
    for size in GRID_SIZES:
        best, count = _search_box(case, diameter_low, diameter_high, pd_low, pd_high, ae_low, ae_high, size, best, count)
        diameter_low, diameter_high = _narrow(best.design.diameterMeters, diameter_low, diameter_high, size)
        pd_low, pd_high = _narrow(best.design.pitchDiameterRatio, pd_low, pd_high, size)
        ae_low, ae_high = _narrow(best.design.expandedAreaRatio, ae_low, ae_high, size)
    return best


def _search_box(case: PopInput, diameter_low: float, diameter_high: float, pd_low: float, pd_high: float, ae_low: float, ae_high: float, size: int, best: OptimizationResult | None, count: int) -> tuple[OptimizationResult, int]:
    d_grid = np.linspace(diameter_low, diameter_high, size)
    pd_grid = np.linspace(pd_low, pd_high, size)
    ae_grid = np.linspace(ae_low, ae_high, size)
    d_mesh, pd_mesh, ae_mesh = np.meshgrid(d_grid, pd_grid, ae_grid, indexing="ij")
    d_flat = d_mesh.ravel()
    pd_flat = pd_mesh.ravel()
    ae_flat = ae_mesh.ravel()
    z_flat = np.full_like(d_flat, case.bladeCount, dtype=np.float64)

    batch = evaluate_designs_auto_reynolds_batch(case, d_flat, pd_flat, ae_flat, z_flat)
    count += d_flat.size

    allowable = burrill_allowable_loading(batch.cavitationNumber, case.burrillBackCavitationPercent)
    feasible = (
        (batch.thrustCoefficient > 0)
        & (batch.torqueCoefficient > 0)
        & (batch.burrillLoading <= allowable)
    )
    if not np.any(feasible):
        if best is not None:
            return best, count
        raise ValueError("No feasible propeller design found")

    eta = np.where(feasible, batch.openWaterEfficiency, -np.inf)
    idx = int(np.argmax(eta))
    candidate = OptimizationResult(batch.at(idx), count)
    if best is None or candidate.design.openWaterEfficiency > best.design.openWaterEfficiency:
        best = candidate
    return best, count


def _narrow(center: float, low: float, high: float, size: int) -> tuple[float, float]:
    step = (high - low) / (size - 1)
    return max(low, center - step), min(high, center + step)
