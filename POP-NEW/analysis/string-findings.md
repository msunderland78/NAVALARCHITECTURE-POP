# String Findings

## Product Identity

Recovered identity strings:

- `Propeller Optimization Program (POP-1.5) by M. G. Parsons`
- `POP Interface 1.0 - Visual C++ by Dr. Jun Li`
- `Developed under the COMPASS Project Sponsored by DARPA through Intergraph Federal Systems`
- `University of Michigan`
- `Department of Naval Architecture and Marine Engineering`

## Engineering Sources

Recovered source references:

- `Oosterveld, M. W. C., and Van Oossanen, P.`
- `"Further Computer-Analyzed Data of the Wageningen B-Screw Series"`
- `International Shipbuilding Progress, Vol. 22, No. 251, July, 1975`
- `Parsons, M. G., "Optimiztion Methods for Use in Computer-Aided Ship Design"`
- `First SNAME STAR Symposium, 1975`

## UI Scope

`POP.EXE` exposes user interface labels for:

- Project name
- Propeller type
- Propeller characteristics
- Operating conditions
- Water properties
- Analysis run
- Plot

Propeller choices shown by the GUI:

- Wageningen B-screw series
- Gawn series
- Ducted propellers
- Fixed pitch
- Controllable pitch

Only Wageningen B-screw behavior is currently proven by the Fortran output strings and sample reports.

## Recovered Input Labels

- Project Name
- Run Identification
- Optimization Run
- Evaluation Run
- Number of Propeller Blades
- Initial Expanded Area Ratio Ae/Ao
- Initial Pitch Diameter Ratio P/Dp
- Initial Propeller Diameter Dp
- Burrill Back Cavitation Constraint
- Required Propeller Thrust
- Ship Speed Vk
- Wake Fraction w
- Depth of Shaft below Waterline
- Water Density Rho
- Kinematic Viscosity Nu
- Minimum Diameter Constraint Dpmin
- Maximum Diameter Constraint Dpmax

## Recovered Output Labels

- Propeller Diameter Dp
- Propeller Pitch P
- Pitch Diameter Ratio P/Dp
- Expanded Area Ratio Ae/Ao
- Propeller Revolutions per Minute
- Advance Coefficient J
- Thrust Coefficient KT
- Torque Coefficient KQ
- Propeller Open Water Efficiency Eta 0
- Propeller Thrust
- Reynolds Number RN
- Cavitation Number Sigma
- Optimization Search Evaluation Count

## Runtime and Failure Strings

Useful runtime strings:

- `POPFTRN.exe`
- `Out`
- `POPG`
- `POPGR`
- `del Popgr`
- `del Out`
- `POP failed. Please check your input data, or whether you have a POPFTRN.exe file in the folder.`
- `Please first "Run" POP, then "Plot".`
- `FAILURE TO CONVERGE ON THRUST IN FUNCTN`
- `Eta 0 Reduced by 2% When Controllable Pitch`

## Hardware Lock Strings

No hardware-lock strings were found in the current pass. The current evidence does not justify a `BYPASS` folder.
