from .core import advance_coefficient, advance_speed_mps, cavitation_number, open_water_efficiency, pitch_meters, required_thrust_newtons, revolutions_per_second, thrust_coefficient
from .legacy_pop import parse_legacy_input, parse_legacy_output, read_legacy_pop_text
from .models import PopInput, Water
from .solver import DesignEvaluation, evaluate_design, solve_advance_coefficient_for_thrust
from .wageningen import wageningen_kq, wageningen_kq_corrected, wageningen_kq_reynolds_correction, wageningen_kt, wageningen_kt_corrected, wageningen_kt_reynolds_correction

__all__ = [
    "PopInput",
    "Water",
    "DesignEvaluation",
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
    "evaluate_design",
    "solve_advance_coefficient_for_thrust",
    "wageningen_kq",
    "wageningen_kq_corrected",
    "wageningen_kq_reynolds_correction",
    "wageningen_kt",
    "wageningen_kt_corrected",
    "wageningen_kt_reynolds_correction"
]
