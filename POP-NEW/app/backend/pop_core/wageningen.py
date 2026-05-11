from dataclasses import dataclass

import numpy as np


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


def _pack(terms: list[PolynomialTerm]):
    coeffs = np.array([t.coefficient for t in terms], dtype=np.float64)
    j_pow = np.array([t.j_power for t in terms], dtype=np.int64)
    pd_pow = np.array([t.pd_power for t in terms], dtype=np.int64)
    ae_pow = np.array([t.aeao_power for t in terms], dtype=np.int64)
    z_pow = np.array([t.blade_power for t in terms], dtype=np.int64)
    return coeffs, j_pow, pd_pow, ae_pow, z_pow


_KT_C, _KT_J, _KT_PD, _KT_AE, _KT_Z = _pack(KT_TERMS)
_KQ_C, _KQ_J, _KQ_PD, _KQ_AE, _KQ_Z = _pack(KQ_TERMS)


def wageningen_kt(j, pitch_diameter_ratio, expanded_area_ratio, blade_count):
    return _polynomial(j, pitch_diameter_ratio, expanded_area_ratio, blade_count, _KT_C, _KT_J, _KT_PD, _KT_AE, _KT_Z)


def wageningen_kq(j, pitch_diameter_ratio, expanded_area_ratio, blade_count):
    return _polynomial(j, pitch_diameter_ratio, expanded_area_ratio, blade_count, _KQ_C, _KQ_J, _KQ_PD, _KQ_AE, _KQ_Z)


def wageningen_kt_reynolds_correction(j, pitch_diameter_ratio, expanded_area_ratio, blade_count, reynolds_number):
    j, pd, ae, z, rn, scalar, shape = _broadcast_inputs(j, pitch_diameter_ratio, expanded_area_ratio, blade_count, reynolds_number)
    lr = np.log10(rn) - 0.301
    value = (
        0.000353485
        - 0.00333758 * ae * j ** 2
        - 0.00478125 * ae * pd * j
        + 0.000257792 * lr ** 2 * ae * j ** 2
        + 0.0000643192 * lr * pd ** 6 * j ** 2
        - 0.0000110636 * lr ** 2 * pd ** 6 * j ** 2
        - 0.0000276305 * lr ** 2 * z * ae * j ** 2
        + 0.0000954 * lr * z * ae * pd * j
        + 0.0000032049 * lr * z ** 2 * ae * pd ** 3 * j
    )
    return _restore_shape(value, scalar, shape)


def wageningen_kq_reynolds_correction(j, pitch_diameter_ratio, expanded_area_ratio, blade_count, reynolds_number):
    j, pd, ae, z, rn, scalar, shape = _broadcast_inputs(j, pitch_diameter_ratio, expanded_area_ratio, blade_count, reynolds_number)
    lr = np.log10(rn) - 0.301
    value = (
        -0.000591412
        + 0.00696898 * pd
        - 0.0000666654 * z * pd ** 6
        + 0.0160818 * ae ** 2
        - 0.000938091 * lr * pd
        - 0.00059593 * lr * pd ** 2
        + 0.0000782099 * lr ** 2 * pd ** 2
        + 0.0000052199 * lr * z * ae * j ** 2
        - 0.00000088528 * lr ** 2 * z * ae * pd * j
        + 0.0000230171 * lr * z * pd ** 6
        - 0.00000184341 * lr ** 2 * z * pd ** 6
        - 0.00400252 * lr * ae ** 2
        + 0.000220915 * lr ** 2 * ae ** 2
    )
    return _restore_shape(value, scalar, shape)


def wageningen_kt_corrected(j, pitch_diameter_ratio, expanded_area_ratio, blade_count, reynolds_number):
    return wageningen_kt(j, pitch_diameter_ratio, expanded_area_ratio, blade_count) + wageningen_kt_reynolds_correction(j, pitch_diameter_ratio, expanded_area_ratio, blade_count, reynolds_number)


def wageningen_kq_corrected(j, pitch_diameter_ratio, expanded_area_ratio, blade_count, reynolds_number):
    return wageningen_kq(j, pitch_diameter_ratio, expanded_area_ratio, blade_count) + wageningen_kq_reynolds_correction(j, pitch_diameter_ratio, expanded_area_ratio, blade_count, reynolds_number)


def _polynomial(j, pd, ae, z, coeffs, j_pow, pd_pow, ae_pow, z_pow):
    j_arr, pd_arr, ae_arr, z_arr, scalar, shape = _broadcast4(j, pd, ae, z)
    contrib = (
        coeffs
        * j_arr[:, None] ** j_pow
        * pd_arr[:, None] ** pd_pow
        * ae_arr[:, None] ** ae_pow
        * z_arr[:, None] ** z_pow
    )
    value = contrib.sum(axis=1)
    return _restore_shape(value, scalar, shape)


def _broadcast4(j, pd, ae, z):
    j_a, pd_a, ae_a, z_a = (np.asarray(x, dtype=np.float64) for x in (j, pd, ae, z))
    scalar = all(arr.ndim == 0 for arr in (j_a, pd_a, ae_a, z_a))
    j_b, pd_b, ae_b, z_b = np.broadcast_arrays(j_a, pd_a, ae_a, z_a)
    shape = j_b.shape
    return j_b.ravel(), pd_b.ravel(), ae_b.ravel(), z_b.ravel(), scalar, shape


def _broadcast_inputs(j, pd, ae, z, rn):
    j_a, pd_a, ae_a, z_a, rn_a = (np.asarray(x, dtype=np.float64) for x in (j, pd, ae, z, rn))
    scalar = all(arr.ndim == 0 for arr in (j_a, pd_a, ae_a, z_a, rn_a))
    j_b, pd_b, ae_b, z_b, rn_b = np.broadcast_arrays(j_a, pd_a, ae_a, z_a, rn_a)
    shape = j_b.shape
    return j_b, pd_b, ae_b, z_b, rn_b, scalar, shape


def _restore_shape(value, scalar, shape):
    arr = np.asarray(value).reshape(shape) if shape else np.asarray(value)
    if scalar:
        return float(arr.item() if arr.shape == () else arr.reshape(-1)[0])
    return arr
