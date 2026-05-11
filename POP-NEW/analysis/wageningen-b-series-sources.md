# Wageningen B-Series Sources

## Polynomial Form

The Wageningen B-screw series open-water characteristics use polynomial regressions for thrust and torque coefficients:

- `KT = sum(C * J^s * (P/D)^t * (Ae/Ao)^u * Z^v)`
- `KQ = sum(C * J^s * (P/D)^t * (Ae/Ao)^u * Z^v)`

The variables are:

- `J`: advance coefficient
- `P/D`: pitch-diameter ratio
- `Ae/Ao`: expanded blade area ratio
- `Z`: number of blades

## Sources Used

Primary project-context source:

- Barnitsas, M. M.; Ray, D.; Kinley, P. `Kt, Kq and Efficiency Curves for the Wageningen B-Series Propellers`. University of Michigan, Department of Naval Architecture and Marine Engineering, Technical Report, May 1, 1981. Deep Blue handle: `https://hdl.handle.net/2027.42/91702`.

Supporting open-access source for the polynomial form:

- Helma, S. `Surprising Behaviour of the Wageningen B-Screw Series Polynomials`. Journal of Marine Science and Engineering, 2020, 8(3), 211. DOI: `10.3390/jmse8030211`.

Coefficient table source note:

The implemented coefficient table is the standard 39-term `KT` and 47-term `KQ` table for Reynolds number `2e6`, attributed to Oosterveld and van Oossanen and reproduced in common marine-propulsion references as table `Coefficients for KT and KQ Polynomials Representing the Wageningen B-Screw Series for a Reynolds Number of 2 x 10^6`.

## Implementation Scope

The current implementation evaluates the base `Rn = 2e6` polynomials and applies the published Reynolds-number correction equations for `KT` and `KQ`.

The recovered POP golden output has `RN = 0.368E+08`, and the correction is required for the `KQ` value to match the legacy result.

## POP Compatibility Notes

The legacy POP output reports sectional Reynolds number `RN`, not a diameter-based Reynolds number. The current implementation estimates `RN` from advance speed, 0.75-radius tangential speed, and a representative section chord proportional to `Ae/Ao * D / Z`. The proportionality factor `SECTION_CHORD_FACTOR = 2.073` follows Carlton, `Marine Propellers and Propulsion`, for the equivalent representative chord at the `0.75R` reference section of a Wageningen B-screw. This is roughly 7 percent lower than the value that would exactly reproduce the legacy `RN = 0.368E+08` for the NA 470 case, so modern results carry a small Reynolds offset relative to legacy POP-1.5. The published constant is preferred because it generalizes to any blade count and `Ae/Ao`, not only the recovered case.

The optimizer uses a digitized Burrill back-cavitation chart for the allowable thrust loading `tau_c` as a function of cavitation number `sigma_0.7R` and back cavitation percentage. Sample digitization points for the 5 percent and 10 percent lines are taken from Carlton, Figure 9.21, with linear interpolation in `sigma` and linear blending between the 5 percent and 10 percent curves for intermediate cavitation percentages. The previous single-point linear calibration is replaced by this table to extend correct behaviour to designs operating at `sigma` values away from the recovered NA 470 point.
