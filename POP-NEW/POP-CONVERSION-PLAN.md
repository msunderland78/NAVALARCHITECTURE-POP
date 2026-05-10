# POP Conversion Plan

## Executive Summary

The legacy Propeller Optimization Program in `POP-OLD` appears to be a small Win32 MFC graphical shell coupled to a separate Win32 Fortran calculation engine. The correct modernization path is clean reimplementation of the naval architecture calculations and file formats in `POP-NEW`, using the old executables only as investigation inputs and temporary oracle references.

The recommended first product is a web application for Wageningen B-screw fixed-pitch and controllable-pitch preliminary propeller design. The computational core should be implemented in a testable backend module first, then exposed through a browser interface. The final product must not require `POP.EXE`, `POPFTRN.EXE`, the old `.POP` compound-document files, or any Windows runtime.

No obvious hardware-lock or dongle dependency was found in the current artifacts. There are no visible HASP, Sentinel, Rainbow, Wibu, CodeLock, or vendor driver strings/imports in the executables. No `BYPASS` folder is needed at this stage.

## Legacy File Inventory

| File | Size | Type | SHA-256 | Role |
|---|---:|---|---|---|
| `POP.EXE` | 81920 | PE32 Win32 GUI executable | `effcebe1df92a2f4331a682a47b5b9860ca0ed98f8a77ae7e5a0c02a36ed4435` | MFC user interface and document shell |
| `POPFTRN.EXE` | 264192 | PE32 Win32 console executable | `4916b84dc3fa18c4583be28624f2ce409aa659b0c8fbdd779d64212e8e155336` | Fortran numerical engine |
| `POP1.POP` | 9728 | OLE Compound Document | `8a01a465ae0d2b848c0f155f15c7650be47f7c4df74dcde1daacfccc9fe09c63` | Saved sample POP document |
| `POPout.pop` | 12800 | OLE Compound Document | `4e87b676fb23f9ffa0647db3b74727cea752e3b6f712587d52fe3d401095fc38` | Saved sample POP document with output state |
| `fort.9` | 224 | ASCII text with CRLF line endings | `902411cb88f1777df77b9330feaaf2a681aebd693cd0adbf93792b0234824e10` | Fortran diagnostic or scratch output |

## Static Analysis Findings

### `POP.EXE`

`POP.EXE` is a PE32 GUI executable for Intel 80386. It has four sections: `.text`, `.rdata`, `.data`, and `.rsrc`.

Important PE clues:

- Timestamp: July 12, 2000
- Linker: version 6.0
- Subsystem: Windows GUI
- Imports: `MFC42.DLL`, `MSVCRT.dll`, `MSVCIRT.dll`, `KERNEL32.dll`, `USER32.dll`, `GDI32.dll`
- Visible C++/MFC classes: `CPOPDoc`, `CPOPView`, `CPOPGraphView`, `CPOPCntrItem`, `CPOPSrvrItem`
- Version resource: `POP MFC Application`, `POP Application`, version `1, 0, 0, 1`
- UI credit: `POP Interface 1.0 - Visual C++ by Dr. Jun Li`
- Program title: `Propeller Optimization Program (POP-1.5) by M. G. Parsons`

The import table and version data are consistent with Microsoft Visual C++ 6.0 and MFC 4.2.

The GUI contains menus and dialogs for:

- Project name
- Propeller type
- Propeller characteristics
- Operating conditions
- Water properties
- Run and plot commands
- Open, save, print, and OLE document behavior

The executable contains strings for:

- `POPFTRN.exe`
- `Out`
- `POPGR`
- `del Popgr`
- `del Out`
- `POP failed. Please check your input data, or whether you have a POPFTRN.exe file in the folder.`
- `Please first "Run" POP, then "Plot".`

This indicates the MFC shell prepares inputs, deletes old temporary output files, invokes the Fortran executable, reads generated output, and plots graph data from an intermediate file.

### `POPFTRN.EXE`

`POPFTRN.EXE` is a PE32 console executable for Intel 80386. It has four sections: `.text`, `.rdata`, `.data`, and `.idata`.

Important PE clues:

- Timestamp: March 16, 1998
- Linker: version 5.0
- Subsystem: Windows CUI
- Imports: `KERNEL32.dll`
- Static Fortran runtime strings: `DEC Fortran RTL Message Catalog V1.1-14 07-Jan-1997`
- Runtime source paths: `E:\forrtl\build\for_open.c`, `E:\forrtl\build\for_nt_open_proc.c`
- Output file clues: `OUT`, `POPG`, `CONOUT$`, `FORT%d`, `fort.%d`

This is consistent with DEC Visual Fortran or an early Visual Fortran toolchain with a mostly statically linked Fortran runtime.

The executable contains the core engineering text:

- `Wageningen B-Screw Series Propeller Preliminary Design`
- `Oosterveld, M. W. C., and Van Oossanen, P.`
- `"Further Computer-Analyzed Data of the Wageningen B-Screw Series"`
- `Parsons, M. G., "Optimiztion Methods for Use in Computer-Aided Ship Design"`
- `FAILURE TO CONVERGE ON THRUST IN FUNCTN`
- `Eta 0 Reduced by 2% When Controllable Pitch`

The visible outputs include:

- Propeller diameter
- Propeller pitch
- Pitch-diameter ratio
- Expanded area ratio
- Revolutions per minute
- Advance coefficient
- Thrust coefficient
- Torque coefficient
- Open-water efficiency
- Thrust
- Reynolds number
- Cavitation number
- Optimization search evaluation count

### `.POP` Files

Both `.POP` files are OLE Compound Document files. The visible OLE stream names are:

- `Root Entry`
- `Contents`

`POP1.POP` also includes a temporary stream name:

- `emp\~DFFD25.tmp`

The content appears to be MFC serialized document state rather than a simple plain-text input file. Printable strings contain both user input and saved output report text.

Recovered sample input values:

- Project name: `NA 470 Coursepack Example`
- Run identification: `test 1.0`
- Run type: optimization
- Propeller series: Wageningen B-screw series
- Pitch type: fixed-pitch propeller
- Number of blades: `4`
- Initial expanded area ratio `Ae/Ao`: `0.750`
- Initial pitch-diameter ratio `P/Dp`: `1.000`
- Initial propeller diameter `Dp`: `4.57 m`
- Required thrust: `444.822100 kN`
- Ship speed: `11.840 knots`
- Wake fraction: `0.0000`
- Shaft depth below waterline: `4.39 m`
- Water: salt water at 15 degrees Celsius
- Density: `1025.870 kg/m^3`
- Kinematic viscosity: `1.188310e-006 m^2/s`
- Burrill back cavitation constraint: `5%`
- Minimum diameter constraint: `2.00 m`
- Maximum diameter constraint: `4.60 m`

Recovered sample output values:

- Propeller diameter: `4.60 m`
- Propeller pitch: `3.76 m`
- Pitch-diameter ratio: `0.8171`
- Expanded area ratio: `0.6293`
- RPM: `147.07`
- Advance coefficient `J`: `0.5408`
- Thrust coefficient `KT`: `0.1615`
- Torque coefficient `KQ`: `0.02205`
- Open-water efficiency `Eta 0`: `0.631`
- Propeller thrust: `444.8 kN`
- Reynolds number: `0.368E+08`
- Cavitation number `Sigma`: `0.4339`
- Optimization search evaluation count: `73`

### `fort.9`

`fort.9` contains:

```text
 ***RESET RK=   2048.00***
 ***RESET RK=   4096.00***
 ***RESET RK=   8192.00***
 ***RESET RK=  16384.00***
 ***RESET RK=  32768.00***
 ***RESET RK=  65536.00***
 ***RESET RK= 131072.00***
 ***RESET RK= 262144.00***
```

This is likely a diagnostic trace from the optimizer, not a required user-facing output. `RK` appears to be an internal search scale, penalty, or step-control parameter reset during optimization.

## Inferred Legacy Architecture

The legacy application likely follows this flow:

1. `POP.EXE` launches as an MFC/OLE document application.
2. The user enters project, propeller, operating, water, and run options through dialogs.
3. `POP.EXE` serializes document state into an MFC `Contents` stream when saving `.POP` files.
4. On run, `POP.EXE` removes stale `Out` and `Popgr` files.
5. `POP.EXE` writes or passes input data to `POPFTRN.EXE`.
6. `POP.EXE` invokes `POPFTRN.EXE` through the C runtime `system` call.
7. `POPFTRN.EXE` performs the Wageningen B-screw calculation and optimization.
8. `POPFTRN.EXE` writes a report to `Out`.
9. `POPFTRN.EXE` writes plot data to `POPG` or `POPGR`.
10. `POP.EXE` reads the report into the document and enables plotting.

Windows case-insensitivity probably hid differences between `POPG`, `POPGR`, `Popgr`, and `Out`. A Linux reimplementation must avoid case-dependent temporary file names and use explicit structured data instead.

## Hardware Lock Assessment

No current evidence indicates a hardware dongle or software license lock.

Checked indicators:

- No visible `HASP`, `Sentinel`, `Rainbow`, `Wibu`, `CodeLock`, `Aladdin`, or `SafeNet` strings.
- No visible lock-driver DLL imports.
- `POP.EXE` imports standard MFC, C runtime, Win32 user, and GDI libraries.
- `POPFTRN.EXE` imports only `KERNEL32.dll`; the Fortran runtime appears statically linked.
- The observed failure string points to missing `POPFTRN.exe` or invalid input, not license failure.

Conversion action:

- Do not create a `BYPASS` folder now.
- If later artifacts reveal a lock, isolate lock research in root-level `BYPASS` and keep production code independent of that work.
- The final web application must use its own ordinary deployment authorization, not the legacy lock model.

## Reimplementation Scope

### Version 1 Scope

Implement the behavior proven by the current files:

- Wageningen B-screw series
- Fixed-pitch propeller
- Controllable-pitch or controllable-reversible pitch adjustment where confirmed
- Optimization run
- Evaluation run if input-output behavior can be verified
- Salt water at 15 degrees Celsius
- Fresh water at 15 degrees Celsius
- User-entered water density and viscosity
- Burrill back cavitation constraint at 5 percent and 10 percent
- Diameter lower and upper constraints
- Result tables and propeller characteristic plots

### Deferred Scope

The GUI lists `Gawn series` and `Ducted propellers`, but the Fortran strings found so far only prove Wageningen B-screw behavior. Treat Gawn and ducted propeller support as unimplemented until additional binaries, source, documentation, or verified outputs are found.

Printing, OLE embedding, and native `.POP` binary save fidelity should not be recreated as primary product behavior. Modern JSON import/export and PDF/CSV export are better replacements.

## Computational Model To Rebuild

The computational core should be rebuilt around explicit engineering equations and published Wageningen B-series coefficients.

Core variables:

- `Z`: blade count
- `AeAo`: expanded area ratio
- `PD`: pitch-diameter ratio
- `D`: propeller diameter in meters
- `P`: propeller pitch in meters
- `T`: required thrust in newtons
- `Vk`: ship speed in knots
- `Va`: advance speed in meters per second
- `w`: wake fraction
- `rho`: water density
- `nu`: kinematic viscosity
- `n`: shaft revolutions per second
- `rpm`: shaft revolutions per minute
- `J`: advance coefficient
- `KT`: thrust coefficient
- `KQ`: torque coefficient
- `eta0`: open-water efficiency
- `RN`: Reynolds number
- `sigma`: cavitation number

Standard relationships to implement and test:

- `Va = Vk * 0.514444 * (1 - w)`
- `J = Va / (n * D)`
- `KT = T / (rho * n^2 * D^4)`
- `KQ = Q / (rho * n^2 * D^5)`
- `eta0 = J * KT / (2 * pi * KQ)`
- `P = PD * D`

The Wageningen B-series model should evaluate `KT` and `KQ` as polynomial functions of `J`, `P/D`, `Ae/Ao`, and blade count using Oosterveld and Van Oossanen coefficient tables. Coefficients should come from a traceable source or recovered program data, then be locked down in tests.

The cavitation constraint should be rebuilt from the Burrill back-cavitation criterion used by the legacy program. The exact implementation must be verified against the sample output where `sigma = 0.4339` and the accepted back cavitation limit is 5 percent.

The controllable-pitch adjustment must apply the legacy behavior visible in strings: `Eta 0 Reduced by 2% When Controllable Pitch`.

## Optimization Strategy

The production optimizer should be deterministic and constrained.

Recommended implementation:

1. Normalize inputs and validate physical ranges.
2. For a candidate design, solve `n` or `J` so predicted thrust equals required thrust.
3. Compute `KT`, `KQ`, `eta0`, `RN`, `sigma`, cavitation status, and bounds status.
4. Optimize for maximum open-water efficiency subject to:
   - thrust convergence
   - diameter lower bound
   - diameter upper bound
   - blade count range
   - `Ae/Ao` allowed range
   - `P/D` allowed range
   - cavitation constraint
5. Use a repeatable bounded search over `D`, `P/D`, and `Ae/Ao`.
6. Emit the same rounded outputs as legacy POP for regression comparison.

For matching the legacy program, create an oracle phase that records how the old executable changes evaluation count, convergence status, and optimum variables. For production quality, exact replication of the old search path is less important than matching the final engineering result within agreed tolerances.

Recommended tolerances for the first golden case:

- `D`: within `0.01 m`
- `P`: within `0.01 m`
- `P/D`: within `0.001`
- `Ae/Ao`: within `0.001`
- `rpm`: within `0.1 rpm`
- `J`: within `0.001`
- `KT`: within `0.001`
- `KQ`: within `0.0001`
- `eta0`: within `0.002`
- `RN`: within `1 percent`
- `sigma`: within `0.002`

## Data Format Strategy

### New Native Format

Use a structured JSON format as the native save format in `POP-NEW`.

Suggested schema:

```json
{
  "projectName": "NA 470 Coursepack Example",
  "runId": "test 1.0",
  "mode": "optimization",
  "series": "wageningen_b",
  "pitchType": "fixed",
  "bladeCount": 4,
  "initialAeAo": 0.75,
  "initialPitchDiameterRatio": 1.0,
  "initialDiameterMeters": 4.57,
  "diameterMinMeters": 2.0,
  "diameterMaxMeters": 4.6,
  "requiredThrustKn": 444.8221,
  "shipSpeedKnots": 11.84,
  "wakeFraction": 0.0,
  "shaftDepthMeters": 4.39,
  "water": {
    "kind": "salt_15c",
    "densityKgM3": 1025.87,
    "kinematicViscosityM2S": 1.18831e-6
  },
  "burrillBackCavitationPercent": 5
}
```

### Legacy `.POP` Import

Implement `.POP` import as a compatibility feature, not as the internal model.

Plan:

1. Use an OLE Compound File reader to locate the `Contents` stream.
2. Extract known printable fields by label.
3. Recover binary fields only after mapping the MFC serialization layout.
4. Convert imported state into the new JSON schema.
5. Store warnings for fields that cannot be recovered.
6. Do not write legacy `.POP` files unless there is a demonstrated user need.

The current sample files prove enough labels for a practical best-effort importer.

## Web Application Architecture

Recommended structure inside `POP-NEW`:

```text
POP-NEW/
  POP-CONVERSION-PLAN.md
  PROJECT_BRIEF.md
  analysis/
    legacy-inventory.md
    string-findings.md
    file-format-notes.md
  app/
    frontend/
    backend/
    nginx/
    docker-compose.yml
  tests/
    fixtures/
    golden/
```

Recommended first implementation:

- Backend: Python calculation package with FastAPI endpoint
- Frontend: React or plain TypeScript interface
- Plotting: browser-side charting from structured result arrays
- Deployment: containerized backend and static frontend behind NGINX
- Tests: backend unit tests and golden-output regression tests

Python is the best first target because the calculation recovery work will be faster and easier to audit. After formulas are stable, the core can be ported to Rust or WebAssembly if single-binary or browser-only deployment becomes important.

## User Interface Replacement

The modern interface should preserve the engineering workflow, not the Windows dialog structure.

Primary screens:

- Project/run setup
- Propeller definition
- Operating conditions
- Water properties
- Optimization constraints
- Calculation results
- Characteristic curves
- Import/export

Expected controls:

- Series selector
- Pitch type selector
- Blade count input
- `Ae/Ao`, `P/D`, and `D` numeric inputs
- Required thrust, speed, wake fraction, and shaft depth inputs
- Water preset selector
- Density and viscosity inputs for custom water
- Cavitation limit selector
- Diameter min/max controls for optimization
- Run mode selector for optimization or evaluation

Results should show:

- Input verification table
- Optimal design results table
- Warnings and convergence status
- Open-water curves for selected design
- Export to JSON, CSV, and PDF

## Oracle and Test Plan

Do not execute legacy binaries as part of the production application.

Use legacy behavior only during recovery:

1. Preserve file hashes.
2. Record all strings and static-analysis notes in `POP-NEW/analysis`.
3. Build one golden fixture from `POP1.POP` and `POPout.pop`.
4. If Wine is available, run `POPFTRN.EXE` in an isolated working directory to confirm file protocol and produce fresh `Out` and `POPG` artifacts.
5. Compare fresh oracle output against the saved sample strings.
6. Add tests around the new calculation core.
7. Stop depending on the legacy executable once formula tests match.

Because no hardware lock was detected, oracle harnesses can live under `POP-NEW/tests` or `POP-NEW/analysis`. If a later lock appears, all lock-specific support work must move to root-level `BYPASS`.

Minimum golden test:

| Field | Expected |
|---|---:|
| `D` | `4.60 m` |
| `P` | `3.76 m` |
| `P/D` | `0.8171` |
| `Ae/Ao` | `0.6293` |
| `rpm` | `147.07` |
| `J` | `0.5408` |
| `KT` | `0.1615` |
| `KQ` | `0.02205` |
| `eta0` | `0.631` |
| `T` | `444.8 kN` |
| `RN` | `0.368E+08` |
| `sigma` | `0.4339` |

## Work Phases

### Phase 1: Evidence Preservation

Deliverables:

- `POP-NEW/analysis/legacy-inventory.md`
- Static analysis notes for `POP.EXE` and `POPFTRN.EXE`
- Extracted UI labels and output labels
- Golden sample JSON converted from `POP1.POP`
- Golden expected output JSON converted from `POPout.pop`

Exit criteria:

- No production work depends on `POP-OLD`
- All known legacy input and output values are captured in reproducible text files

### Phase 2: Calculation Core

Deliverables:

- Pure calculation module
- Wageningen B-series `KT` and `KQ` evaluator
- Thrust solver
- Cavitation calculator
- Reynolds number calculator
- Fixed-pitch and controllable-pitch branches
- Optimization and evaluation modes

Exit criteria:

- Golden sample matches within tolerance
- Invalid physical inputs fail validation before calculation
- Calculation module has no web or UI dependency

### Phase 3: Legacy Import

Deliverables:

- `.POP` reader for OLE `Contents` stream
- Field extraction for known labels
- Converter from legacy fields to new JSON schema
- Import tests for `POP1.POP` and `POPout.pop`

Exit criteria:

- Current sample `.POP` files can be converted to the native JSON input format
- Import warnings are explicit for unsupported fields

### Phase 4: Web Interface

Deliverables:

- Browser UI for entering inputs
- Input verification view
- Run button
- Results table
- Plot view for characteristic curves
- JSON import/export
- CSV/PDF export if required

Exit criteria:

- The NA 470 sample can be entered or imported and produces the expected result
- The UI does not require Windows, Wine, OLE, or legacy executables

### Phase 5: Container Deployment

Deliverables:

- Dockerfile for backend
- Frontend build pipeline
- NGINX config
- `docker-compose.yml`
- Deployment README

Exit criteria:

- Application runs on Ubuntu Linux behind NGINX
- No `POP-OLD` files are copied into the production image
- Health check and basic smoke test pass

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Wageningen coefficient transcription errors | Wrong engineering output | Source coefficients from a traceable reference and lock with regression tests |
| Burrill cavitation implementation mismatch | Different feasible design region | Use legacy golden case and additional hand cases to calibrate |
| Optimizer mismatch | Different but valid optimum | Match engineering output tolerances first; match legacy evaluation count only if required |
| `.POP` MFC serialization ambiguity | Incomplete legacy import | Use label-based extraction first; keep native JSON as product format |
| Gawn/ducted UI strings without algorithm evidence | Scope creep | Defer until a verified source or executable behavior is available |
| Windows temporary-file assumptions | Failed Linux behavior | Replace temp files with structured in-memory calculations and API responses |
| Old executable hidden side effects | Incorrect oracle assumptions | Run any oracle work in isolated scratch directories only |

## Recommended Immediate Next Steps

1. Create `POP-NEW/analysis` and record static analysis outputs in markdown.
2. Convert the recovered NA 470 sample input to `POP-NEW/tests/fixtures/na470-coursepack.input.json`.
3. Convert the recovered sample output to `POP-NEW/tests/golden/na470-coursepack.output.json`.
4. Implement the calculation core with the published Wageningen B-series polynomial coefficients.
5. Add the golden regression test before building the web UI.
6. Build the frontend only after the backend calculation result is stable.

## Final Conversion Decision

Do not wrap the legacy Windows application for production.

Use `POP.EXE` and `POPFTRN.EXE` only to understand workflow and generate oracle comparisons. The production application should be a clean Linux-native web application with a documented data model, tested numerical core, and browser-based UI.
