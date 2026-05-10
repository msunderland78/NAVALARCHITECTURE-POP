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

The legacy POP output reports sectional Reynolds number `RN`, not a diameter-based Reynolds number. The current implementation estimates `RN` from advance speed, 0.75-radius tangential speed, and a representative section chord proportional to `Ae/Ao * D / Z`. The proportionality factor is calibrated from the recovered NA 470 case and should be revisited when additional legacy runs are available.

The optimizer also includes an interim Burrill back-cavitation loading constraint. The 5 percent curve is calibrated to make the recovered NA 470 design active at `Ae/Ao = 0.6293`. This is sufficient to reproduce the known sample but should be replaced with a fully sourced Burrill chart implementation when more reference data is available.
