from dataclasses import dataclass

from .core import propeller_open_water_efficiency, required_thrust_newtons
from .models import PopInput, validate_case
from .optimizer import AE_RANGE, BladeSweepResult, OptimizationResult, PD_RANGE, optimize_design_with_blade_sweep
from .solver import DesignEvaluation, burrill_allowable_loading, evaluate_design_auto_reynolds
from .wageningen import wageningen_kq_corrected, wageningen_kt_corrected


@dataclass(frozen=True)
class PopRunResult:
    mode: str
    design: DesignEvaluation
    bladeCount: int
    evaluationCount: int | None
    bladeSweep: BladeSweepResult | None


def run_case(case: PopInput) -> PopRunResult:
    validate_case(case)
    if case.mode == "optimization":
        sweep = optimize_design_with_blade_sweep(case)
        return PopRunResult(case.mode, sweep.best.design, sweep.bestBladeCount, sweep.evaluationCount, sweep)
    design = evaluate_design_auto_reynolds(
        case,
        case.initialDiameterMeters,
        case.initialPitchDiameterRatio,
        case.initialExpandedAreaRatio
    )
    return PopRunResult(case.mode, design, case.bladeCount, None, None)


def result_payload(case: PopInput, result: PopRunResult) -> dict:
    payload = {
        "projectName": case.projectName,
        "runId": case.runId,
        "mode": result.mode,
        "series": case.series,
        "pitchType": case.pitchType,
        "bladeCount": result.bladeCount,
        "raw": _raw_result(case, result.design, result.evaluationCount),
        "legacyRounded": _legacy_rounded(case, result.design, result.evaluationCount),
        "curves": _curve_data(case, result.design, result.bladeCount),
        "warnings": _warnings(case, result)
    }
    if result.bladeSweep is not None:
        payload["bladeSweep"] = _blade_sweep_payload(result.bladeSweep)
    return payload


def _warnings(case: PopInput, result: PopRunResult) -> list[dict]:
    notes = []
    design = result.design
    allowable = burrill_allowable_loading(design.cavitationNumber, case.burrillBackCavitationPercent)
    if allowable > 0:
        margin = (allowable - design.burrillLoading) / allowable
        if design.burrillLoading > allowable:
            notes.append({"level": "warning", "code": "cavitation_exceeds_limit", "message": f"Burrill loading {design.burrillLoading:.3f} exceeds the {case.burrillBackCavitationPercent}% allowable {allowable:.3f}. Increase Ae/Ao, diameter, or shaft depth."})
        elif margin < 0.10:
            notes.append({"level": "warning", "code": "cavitation_margin_tight", "message": f"Burrill margin only {margin*100:.1f}% below the {case.burrillBackCavitationPercent}% limit. Consider more blade area."})
    if design.openWaterEfficiency < 0.55:
        notes.append({"level": "warning", "code": "low_efficiency", "message": f"Open-water efficiency {design.openWaterEfficiency:.3f} is low. Check loading and J range."})
    if design.rpm > 300:
        notes.append({"level": "info", "code": "high_rpm", "message": f"Shaft RPM {design.rpm:.0f} is high; verify gear ratio and shaft sizing."})
    elif design.rpm < 50:
        notes.append({"level": "info", "code": "low_rpm", "message": f"Shaft RPM {design.rpm:.0f} is unusually low for this thrust."})
    if result.mode == "optimization":
        if abs(design.diameterMeters - case.diameterMaxMeters) / case.diameterMaxMeters < 0.005:
            notes.append({"level": "info", "code": "diameter_pinned_max", "message": "Diameter pinned at the upper bound. A larger maximum diameter may improve efficiency."})
        elif abs(design.diameterMeters - case.diameterMinMeters) / max(case.diameterMaxMeters, 1.0) < 0.005:
            notes.append({"level": "info", "code": "diameter_pinned_min", "message": "Diameter pinned at the lower bound. Consider relaxing the minimum diameter."})
        pd_low, pd_high = PD_RANGE
        if design.pitchDiameterRatio >= pd_high - 0.01:
            notes.append({"level": "info", "code": "pd_at_upper_search_bound", "message": f"P/D pinned at the Wageningen search upper bound ({pd_high}). Optimum may lie outside the validated range."})
        elif design.pitchDiameterRatio <= pd_low + 0.01:
            notes.append({"level": "info", "code": "pd_at_lower_search_bound", "message": f"P/D pinned at the Wageningen search lower bound ({pd_low})."})
        ae_low, ae_high = AE_RANGE
        if design.expandedAreaRatio >= ae_high - 0.01:
            notes.append({"level": "info", "code": "ae_at_upper_search_bound", "message": f"Ae/Ao pinned at the Wageningen search upper bound ({ae_high})."})
        elif design.expandedAreaRatio <= ae_low + 0.01:
            notes.append({"level": "info", "code": "ae_at_lower_search_bound", "message": f"Ae/Ao pinned at the Wageningen search lower bound ({ae_low}). Cavitation may be active."})
    if case.pitchType == "controllable":
        notes.append({"level": "info", "code": "cpp_empirical", "message": "Controllable-pitch efficiency is reduced by 2% as an empirical hub-loss allowance from POP-1.5."})
    return notes


def _blade_sweep_payload(sweep: BladeSweepResult) -> dict:
    return {
        "bestBladeCount": sweep.bestBladeCount,
        "entries": [_blade_sweep_entry(entry) for entry in sweep.entries]
    }


def _blade_sweep_entry(entry) -> dict:
    if entry.result is None:
        return {
            "bladeCount": entry.bladeCount,
            "feasible": False,
            "error": entry.error
        }
    design = entry.result.design
    return {
        "bladeCount": entry.bladeCount,
        "feasible": True,
        "diameterMeters": round(design.diameterMeters, 2),
        "pitchDiameterRatio": round(design.pitchDiameterRatio, 4),
        "expandedAreaRatio": round(design.expandedAreaRatio, 4),
        "rpm": round(design.rpm, 2),
        "openWaterEfficiency": round(design.openWaterEfficiency, 4),
        "cavitationNumber": round(design.cavitationNumber, 4),
        "evaluationCount": entry.result.evaluationCount
    }


def _curve_data(case: PopInput, design: DesignEvaluation, blade_count: int) -> dict:
    rows = []
    for index in range(0, 56):
        j = 0.05 + index * 0.025
        kt = wageningen_kt_corrected(j, design.pitchDiameterRatio, design.expandedAreaRatio, blade_count, design.reynoldsNumber)
        kq = wageningen_kq_corrected(j, design.pitchDiameterRatio, design.expandedAreaRatio, blade_count, design.reynoldsNumber)
        eta = propeller_open_water_efficiency(case, j, kt, kq) if kq > 0 and kt > 0 else 0.0
        rows.append({
            "j": round(j, 4),
            "kt": kt,
            "kq": kq,
            "eta": eta
        })
    return {
        "openWater": rows,
        "point": {
            "j": design.advanceCoefficient,
            "kt": design.thrustCoefficient,
            "kq": design.torqueCoefficient,
            "eta": design.openWaterEfficiency
        }
    }


def _raw_result(case: PopInput, design: DesignEvaluation, evaluation_count: int | None) -> dict:
    return {
        "diameterMeters": design.diameterMeters,
        "pitchMeters": design.diameterMeters * design.pitchDiameterRatio,
        "pitchDiameterRatio": design.pitchDiameterRatio,
        "expandedAreaRatio": design.expandedAreaRatio,
        "rpm": design.rpm,
        "advanceCoefficient": design.advanceCoefficient,
        "thrustCoefficient": design.thrustCoefficient,
        "torqueCoefficient": design.torqueCoefficient,
        "openWaterEfficiency": design.openWaterEfficiency,
        "thrustKn": required_thrust_newtons(case) / 1000.0,
        "reynoldsNumber": design.reynoldsNumber,
        "cavitationNumber": design.cavitationNumber,
        "burrillLoading": design.burrillLoading,
        "optimizationSearchEvaluationCount": evaluation_count
    }


def _legacy_rounded(case: PopInput, design: DesignEvaluation, evaluation_count: int | None) -> dict:
    return {
        "diameterMeters": round(design.diameterMeters, 2),
        "pitchMeters": round(design.diameterMeters * design.pitchDiameterRatio, 2),
        "pitchDiameterRatio": round(design.pitchDiameterRatio, 4),
        "expandedAreaRatio": round(design.expandedAreaRatio, 4),
        "rpm": round(design.rpm, 2),
        "advanceCoefficient": round(design.advanceCoefficient, 4),
        "thrustCoefficient": round(design.thrustCoefficient, 4),
        "torqueCoefficient": round(design.torqueCoefficient, 5),
        "openWaterEfficiency": round(design.openWaterEfficiency, 3),
        "thrustKn": round(required_thrust_newtons(case) / 1000.0, 1),
        "reynoldsNumber": float(f"{design.reynoldsNumber:.3E}"),
        "cavitationNumber": round(design.cavitationNumber, 4),
        "optimizationSearchEvaluationCount": evaluation_count
    }
