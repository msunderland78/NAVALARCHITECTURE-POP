from .core import advance_coefficient, advance_speed_mps, cavitation_number, open_water_efficiency, pitch_meters, required_thrust_newtons, revolutions_per_second, thrust_coefficient
from .legacy_pop import parse_legacy_input, parse_legacy_output, read_legacy_pop_text, read_legacy_pop_text_bytes
from .models import PopInput, Water, validate_case
from .optimizer import OptimizationResult, optimize_design
from .service import PopRunResult, result_payload, run_case
from .solver import DesignEvaluation, burrill_allowable_loading, burrill_loading, estimate_reynolds_number, evaluate_design, evaluate_design_auto_reynolds, passes_burrill_constraint, solve_advance_coefficient_for_thrust
from .wageningen import wageningen_kq, wageningen_kq_corrected, wageningen_kq_reynolds_correction, wageningen_kt, wageningen_kt_corrected, wageningen_kt_reynolds_correction

__all__ = [
    "PopInput",
    "Water",
    "validate_case",
    "DesignEvaluation",
    "OptimizationResult",
    "PopRunResult",
    "advance_coefficient",
    "advance_speed_mps",
    "cavitation_number",
    "open_water_efficiency",
    "pitch_meters",
    "required_thrust_newtons",
    "revolutions_per_second",
    "thrust_coefficient",
    "parse_legacy_input",
    "parse_legacy_output",
    "read_legacy_pop_text",
    "read_legacy_pop_text_bytes",
    "burrill_allowable_loading",
    "burrill_loading",
    "estimate_reynolds_number",
    "evaluate_design",
    "evaluate_design_auto_reynolds",
    "optimize_design",
    "passes_burrill_constraint",
    "result_payload",
    "run_case",
    "solve_advance_coefficient_for_thrust",
    "wageningen_kq",
    "wageningen_kq_corrected",
    "wageningen_kq_reynolds_correction",
    "wageningen_kt",
    "wageningen_kt_corrected",
    "wageningen_kt_reynolds_correction"
]
