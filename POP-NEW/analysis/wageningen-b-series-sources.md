# Wageningen B-Series Sources and Coefficient Provenance

## Polynomial Form

The Wageningen B-screw series open-water characteristics use polynomial regressions for thrust and torque coefficients at a reference Reynolds number `RN_ref = 2 x 10^6`:

- `KT(J, P/D, Ae/Ao, Z; RN_ref) = sum_n  C_n * J^s_n * (P/D)^t_n * (Ae/Ao)^u_n * Z^v_n`
- `KQ(J, P/D, Ae/Ao, Z; RN_ref) = sum_n  D_n * J^s_n * (P/D)^t_n * (Ae/Ao)^u_n * Z^v_n`

Variables:

- `J`: advance coefficient
- `P/D`: pitch-diameter ratio
- `Ae/Ao`: expanded blade area ratio
- `Z`: number of blades

Reynolds-number correction at `RN != RN_ref` is applied as a separate polynomial in `log10(RN) - log10(2e6)`, see "Reynolds correction" below.

## Coefficient Table Provenance

The base 39-term `KT` table and 47-term `KQ` table currently in `app/backend/pop_core/wageningen.py` are reproduced from:

> Bernitsas, M. M.; Ray, D.; Kinley, P. *Kt, Kq and Efficiency Curves for the Wageningen B-Series Propellers*. University of Michigan, Department of Naval Architecture and Marine Engineering, Report No. 237, May 1981. Deep Blue handle: <https://hdl.handle.net/2027.42/91702>.

Specifically, the implementation uses:

- The 39-row `Coefficients for KT_BP polynomial representing the Wageningen B-Screw Series at Reynolds number 2 x 10^6` table (Bernitsas 1981, Table I).
- The 47-row `Coefficients for KQ_BP polynomial representing the Wageningen B-Screw Series at Reynolds number 2 x 10^6` table (Bernitsas 1981, Table II).

Bernitsas reproduces the tables originally published by:

> Oosterveld, M. W. C.; van Oossanen, P. *Further Computer-Analyzed Data of the Wageningen B-Screw Series*. International Shipbuilding Progress, Vol. 22, No. 251, July 1975.

The Bernitsas reproduction is preferred because it is the version cited in the legacy POP `POPFTRN.EXE` strings, it is openly accessible through Deep Blue, and its formatting groups the polynomial exponents into well-defined columns that map directly to the code tables.

A useful cross-check on the polynomial form (not the coefficients) is:

> Helma, S. *Surprising Behaviour of the Wageningen B-Screw Series Polynomials*. Journal of Marine Science and Engineering, 2020, 8(3), 211. DOI: <https://doi.org/10.3390/jmse8030211>.

Helma documents conditioning concerns at the edges of the valid `J`, `P/D`, `Ae/Ao`, `Z` domain. The implementation does not extrapolate beyond Bernitsas' published domain.

## Published Precision

Bernitsas reports each coefficient to six significant figures. The Python tables in `wageningen.py` are entered at the same precision. The polynomial sum is evaluated in `float64`, so the eighth significant figure of the final `KT`/`KQ` is dominated by accumulated rounding, not by the table precision.

## Reynolds Correction

The `KT` and `KQ` Reynolds corrections in `wageningen.py` follow:

> Oosterveld and van Oossanen, *Further Computer-Analyzed Data of the Wageningen B-Screw Series*, 1975, equations for `delta KT` and `delta KQ` as a function of `log10(RN) - 0.301`.

The constant `0.301` is the published offset `log10(RN_ref) - 6 = log10(2 x 10^6) - 6`, so `log10(RN) - 0.301` equals `log10(RN / 2 x 10^6)`. The implementation uses the constant verbatim from the publication to keep the formula transcription auditable.

At the NA 470 sample point (`J = 0.5408`, `P/D = 0.8171`, `Ae/Ao = 0.6293`, `Z = 4`, `RN = 3.68 x 10^7`) the correction is `delta KT ~= 0.000670` and `delta KQ ~= -0.001150`. These two numbers are pinned in `test_wageningen.py::test_na470_reynolds_correction` so transcription errors cannot drift the correction silently.

## Reference Section Chord and Reynolds Estimate

The legacy POP output reports a sectional Reynolds number `RN`, not a diameter-based Reynolds number. The current implementation estimates `RN` from advance speed, the `0.75R` tangential speed, and a representative section chord:

`c_0.75R = SECTION_CHORD_FACTOR * Ae/Ao * D / Z`,  with `SECTION_CHORD_FACTOR = 2.073`.

The `2.073` constant is taken from:

> Carlton, J. S. *Marine Propellers and Propulsion*, 3rd ed., Butterworth-Heinemann, 2012. Section on Wageningen B-Series geometry.

This generalises to any `Z` and `Ae/Ao`. The previous single-case fit (`2.21926629...`) reproduced the legacy `RN = 0.368E+08` exactly but had no generality. The Carlton value puts modern `RN` about 7 percent below the legacy report for the NA 470 case.

## Burrill Back-Cavitation Chart

`burrill_allowable_loading(sigma, percent)` looks up the allowable thrust loading coefficient `tau_c` against `sigma_0.7R` from a digitised version of:

> Carlton, J. S. *Marine Propellers and Propulsion*, Figure 9.21 (Burrill back-cavitation diagram).

Digitised points for the 5 percent and 10 percent back cavitation lines are listed at the top of `app/backend/pop_core/solver.py` as `BURRILL_SIGMA`, `BURRILL_TAUC_5PCT`, `BURRILL_TAUC_10PCT`. Interpolation is linear in `sigma`; intermediate cavitation percentages are linearly blended between the two lines. The previous linear single-point calibration is replaced by this table so the constraint stays correct for designs operating at `sigma` values away from the recovered NA 470 point.

## Controllable-Pitch Efficiency Adjustment

The legacy POP-1.5 program multiplies the computed open-water efficiency by `0.98` when controllable-pitch is selected, per the `POPFTRN.EXE` string:

> `Eta 0 Reduced by 2% When Controllable Pitch`

The implementation preserves this behaviour, but it is empirical, not a physical CPP hub-loss model. Real CPP hub losses depend on hub-to-diameter ratio and blade root section; for production work a hub-specific loss model should replace this 2 percent flat reduction.

## Optimization Approach

In optimization mode the implementation:

1. Sweeps `Z` in `{3, 4, 5, 6, 7}`.
2. For each `Z`, runs a three-phase grid search over `(D, P/D, Ae/Ao)` of 9 x 9 x 9 candidates per phase, with the bounds narrowed around the previous-phase best.
3. At every candidate, solves `J` such that predicted thrust equals required thrust using a bisection on `[0.05, 1.6]` with 20 iterations (precision `~ 1.5 x 10^-6` in `J`, well past the 1 x 10^-3 engineering tolerance).
4. Computes `KT`, `KQ`, `eta_0`, sectional Reynolds, cavitation number and Burrill loading at the converged `J`.
5. Rejects candidates that fail positive-thrust or the Burrill constraint.
6. Reports both the global best (across all `Z`) and the per-`Z` optimum.

Legacy POP-1.5 only optimised over `(D, P/D, Ae/Ao)` at the user-selected `Z`. The per-Z table makes early-stage blade count selection an output of the calculation rather than a separate user decision.

## Verification Tests

The implementation is locked against transcription error by the following tests in `tests/`:

- `test_wageningen.test_coefficient_table_sizes` confirms the 39 and 47 term counts.
- `test_wageningen.test_landmark_coefficients_match_published_values` (added with this provenance update) pins specific landmark `KT` and `KQ` coefficient values that should never change without a deliberate retable.
- `test_wageningen.test_na470_reynolds_correction` pins the Reynolds correction at the NA 470 sample point.
- `test_wageningen.test_na470_corrected_golden_point` confirms the corrected `KT` and `KQ` reproduce the recovered POP-1.5 numbers to four significant figures.
- `test_solver.test_burrill_chart_returns_table_values_at_node_points` pins each digitised Burrill chart node.

Anyone touching the coefficient or chart tables must update these tests in the same commit.
