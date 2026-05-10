from dataclasses import dataclass
from math import log10


@dataclass(frozen=True)
class PolynomialTerm:
    coefficient: float
    j_power: int
    pd_power: int
    aeao_power: int
    blade_power: int


KT_TERMS = [
    PolynomialTerm(0.00880496, 0, 0, 0, 0),
    PolynomialTerm(-0.204554, 1, 0, 0, 0),
    PolynomialTerm(0.166351, 0, 1, 0, 0),
    PolynomialTerm(0.158114, 0, 2, 0, 0),
    PolynomialTerm(-0.147581, 2, 0, 1, 0),
    PolynomialTerm(-0.481497, 1, 1, 1, 0),
    PolynomialTerm(0.415437, 0, 2, 1, 0),
    PolynomialTerm(0.0144043, 0, 0, 0, 1),
    PolynomialTerm(-0.0530054, 2, 0, 0, 1),
    PolynomialTerm(0.0143481, 0, 1, 0, 1),
    PolynomialTerm(0.0606826, 1, 1, 0, 1),
    PolynomialTerm(-0.0125894, 0, 0, 1, 1),
    PolynomialTerm(0.0109689, 1, 0, 1, 1),
    PolynomialTerm(-0.133698, 0, 3, 0, 0),
    PolynomialTerm(0.00638407, 0, 6, 0, 0),
    PolynomialTerm(-0.00132718, 2, 6, 0, 0),
    PolynomialTerm(0.168496, 3, 0, 1, 0),
    PolynomialTerm(-0.0507214, 0, 0, 2, 0),
    PolynomialTerm(0.0854559, 2, 0, 2, 0),
    PolynomialTerm(-0.0504475, 3, 0, 2, 0),
    PolynomialTerm(0.010465, 1, 6, 2, 0),
    PolynomialTerm(-0.00648272, 2, 6, 2, 0),
    PolynomialTerm(-0.00841728, 0, 3, 0, 1),
    PolynomialTerm(0.0168424, 1, 3, 0, 1),
    PolynomialTerm(-0.00102296, 3, 3, 0, 1),
    PolynomialTerm(-0.0317791, 0, 3, 1, 1),
    PolynomialTerm(0.018604, 1, 0, 2, 1),
    PolynomialTerm(-0.00410798, 0, 2, 2, 1),
    PolynomialTerm(-0.000606848, 0, 0, 0, 2),
    PolynomialTerm(-0.0049819, 1, 0, 0, 2),
    PolynomialTerm(0.0025983, 2, 0, 0, 2),
    PolynomialTerm(-0.000560528, 3, 0, 0, 2),
    PolynomialTerm(-0.00163652, 1, 2, 0, 2),
    PolynomialTerm(-0.000328787, 1, 6, 0, 2),
    PolynomialTerm(0.000116502, 2, 6, 0, 2),
    PolynomialTerm(0.000690904, 0, 0, 1, 2),
    PolynomialTerm(0.00421749, 0, 3, 1, 2),
    PolynomialTerm(0.0000565229, 3, 6, 1, 2),
    PolynomialTerm(-0.00146564, 0, 3, 2, 2),
]


KQ_TERMS = [
    PolynomialTerm(0.00379368, 0, 0, 0, 0),
    PolynomialTerm(0.00886523, 2, 0, 0, 0),
    PolynomialTerm(-0.032241, 1, 1, 0, 0),
    PolynomialTerm(0.00344778, 0, 2, 0, 0),
    PolynomialTerm(-0.0408811, 0, 1, 1, 0),
    PolynomialTerm(-0.108009, 1, 1, 1, 0),
    PolynomialTerm(-0.0885381, 2, 1, 1, 0),
    PolynomialTerm(0.188561, 0, 2, 1, 0),
    PolynomialTerm(-0.00370871, 1, 0, 0, 1),
    PolynomialTerm(0.00513696, 0, 1, 0, 1),
    PolynomialTerm(0.0209449, 1, 1, 0, 1),
    PolynomialTerm(0.00474319, 2, 1, 0, 1),
    PolynomialTerm(-0.00723408, 2, 0, 1, 1),
    PolynomialTerm(0.00438388, 1, 1, 1, 1),
    PolynomialTerm(-0.0269403, 0, 2, 1, 1),
    PolynomialTerm(0.0558082, 3, 0, 1, 0),
    PolynomialTerm(0.0161886, 0, 3, 1, 0),
    PolynomialTerm(0.00318086, 1, 3, 1, 0),
    PolynomialTerm(0.015896, 0, 0, 2, 0),
    PolynomialTerm(0.0471729, 1, 0, 2, 0),
    PolynomialTerm(0.0196283, 3, 0, 2, 0),
    PolynomialTerm(-0.0502782, 0, 1, 2, 0),
    PolynomialTerm(-0.030055, 3, 1, 2, 0),
    PolynomialTerm(0.0417122, 2, 2, 2, 0),
    PolynomialTerm(-0.0397722, 0, 3, 2, 0),
    PolynomialTerm(-0.00350024, 0, 6, 2, 0),
    PolynomialTerm(-0.0106854, 3, 0, 0, 1),
    PolynomialTerm(0.00110903, 3, 3, 0, 1),
    PolynomialTerm(-0.000313912, 0, 6, 0, 1),
    PolynomialTerm(0.0035985, 3, 0, 1, 1),
    PolynomialTerm(-0.00142121, 0, 6, 1, 1),
    PolynomialTerm(-0.00383637, 1, 0, 2, 1),
    PolynomialTerm(0.0126803, 0, 2, 2, 1),
    PolynomialTerm(-0.00318278, 2, 3, 2, 1),
    PolynomialTerm(0.00334268, 0, 6, 2, 1),
    PolynomialTerm(-0.00183491, 1, 1, 0, 2),
    PolynomialTerm(0.000112451, 3, 2, 0, 2),
    PolynomialTerm(-0.0000297228, 3, 6, 0, 2),
    PolynomialTerm(0.000269551, 1, 0, 1, 2),
    PolynomialTerm(0.00083265, 2, 0, 1, 2),
    PolynomialTerm(0.00155334, 0, 2, 1, 2),
    PolynomialTerm(0.000302683, 0, 6, 1, 2),
    PolynomialTerm(-0.0001843, 0, 0, 2, 2),
    PolynomialTerm(-0.000425399, 0, 3, 2, 2),
    PolynomialTerm(0.0000869243, 3, 3, 2, 2),
    PolynomialTerm(-0.0004659, 0, 6, 2, 2),
    PolynomialTerm(0.0000554194, 1, 6, 2, 2),
]


def wageningen_kt(j: float, pitch_diameter_ratio: float, expanded_area_ratio: float, blade_count: int) -> float:
    return _evaluate(KT_TERMS, j, pitch_diameter_ratio, expanded_area_ratio, blade_count)


def wageningen_kq(j: float, pitch_diameter_ratio: float, expanded_area_ratio: float, blade_count: int) -> float:
    return _evaluate(KQ_TERMS, j, pitch_diameter_ratio, expanded_area_ratio, blade_count)


def wageningen_kt_reynolds_correction(j: float, pitch_diameter_ratio: float, expanded_area_ratio: float, blade_count: int, reynolds_number: float) -> float:
    lr = log10(reynolds_number) - 0.301
    return (
        0.000353485
        - 0.00333758 * expanded_area_ratio * j ** 2
        - 0.00478125 * expanded_area_ratio * pitch_diameter_ratio * j
        + 0.000257792 * lr ** 2 * expanded_area_ratio * j ** 2
        + 0.0000643192 * lr * pitch_diameter_ratio ** 6 * j ** 2
        - 0.0000110636 * lr ** 2 * pitch_diameter_ratio ** 6 * j ** 2
        - 0.0000276305 * lr ** 2 * blade_count * expanded_area_ratio * j ** 2
        + 0.0000954 * lr * blade_count * expanded_area_ratio * pitch_diameter_ratio * j
        + 0.0000032049 * lr * blade_count ** 2 * expanded_area_ratio * pitch_diameter_ratio ** 3 * j
    )


def wageningen_kq_reynolds_correction(j: float, pitch_diameter_ratio: float, expanded_area_ratio: float, blade_count: int, reynolds_number: float) -> float:
    lr = log10(reynolds_number) - 0.301
    return (
        -0.000591412
        + 0.00696898 * pitch_diameter_ratio
        - 0.0000666654 * blade_count * pitch_diameter_ratio ** 6
        + 0.0160818 * expanded_area_ratio ** 2
        - 0.000938091 * lr * pitch_diameter_ratio
        - 0.00059593 * lr * pitch_diameter_ratio ** 2
        + 0.0000782099 * lr ** 2 * pitch_diameter_ratio ** 2
        + 0.0000052199 * lr * blade_count * expanded_area_ratio * j ** 2
        - 0.00000088528 * lr ** 2 * blade_count * expanded_area_ratio * pitch_diameter_ratio * j
        + 0.0000230171 * lr * blade_count * pitch_diameter_ratio ** 6
        - 0.00000184341 * lr ** 2 * blade_count * pitch_diameter_ratio ** 6
        - 0.00400252 * lr * expanded_area_ratio ** 2
        + 0.000220915 * lr ** 2 * expanded_area_ratio ** 2
    )


def wageningen_kt_corrected(j: float, pitch_diameter_ratio: float, expanded_area_ratio: float, blade_count: int, reynolds_number: float) -> float:
    return wageningen_kt(j, pitch_diameter_ratio, expanded_area_ratio, blade_count) + wageningen_kt_reynolds_correction(j, pitch_diameter_ratio, expanded_area_ratio, blade_count, reynolds_number)


def wageningen_kq_corrected(j: float, pitch_diameter_ratio: float, expanded_area_ratio: float, blade_count: int, reynolds_number: float) -> float:
    return wageningen_kq(j, pitch_diameter_ratio, expanded_area_ratio, blade_count) + wageningen_kq_reynolds_correction(j, pitch_diameter_ratio, expanded_area_ratio, blade_count, reynolds_number)


def _evaluate(terms: list[PolynomialTerm], j: float, pitch_diameter_ratio: float, expanded_area_ratio: float, blade_count: int) -> float:
    total = 0.0
    for term in terms:
        total += (
            term.coefficient
            * j ** term.j_power
            * pitch_diameter_ratio ** term.pd_power
            * expanded_area_ratio ** term.aeao_power
            * blade_count ** term.blade_power
        )
    return total
