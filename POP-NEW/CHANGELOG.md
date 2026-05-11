# Changelog

All notable changes to POP for the Web are listed here. The original review and rationale for the 1.1 changes are captured in `CLAUDE-REVIEW-PLAN.md`.

## 1.1 - 2026-05-11

### Engineering correctness
- Section chord factor for Reynolds estimate now follows Carlton's published `0.75R` representative chord (`2.073`). The previous single-case fit is removed. Reported RN shifts about 7% from legacy POP-1.5 for the NA 470 case.
- Burrill back-cavitation allowable loading replaced with a digitised lookup of the 5% and 10% lines from Carlton (2012) Figure 9.21. Linear interpolation in sigma, linear blending between curves for intermediate cavitation percentages.
- Controllable-pitch 0.98 efficiency multiplier is preserved but documented and surfaced as an empirical hub-loss allowance from POP-1.5, not a physical model.
- Optimization mode sweeps blade count Z = 3..7 and reports the global best plus a per-Z table.

### Performance
- Wageningen polynomial, bisection, Reynolds iteration, and the optimizer grid search are vectorised with numpy. Bisection iterations dropped from 50 to 20 (still 1.5e-6 precision in J). Full blade-sweep optimization on the NA 470 case dropped from ~11s to ~2s. Full unit test suite from ~60s to ~12s.

### Product hardening
- Container pins `python:3.12.8-slim` and runs as the unprivileged `pop` user (uid 10001). PYTHONDONTWRITEBYTECODE and PYTHONUNBUFFERED enabled.
- NGINX adds `server_tokens off`, IPv6 listen, proxy timeouts (5s connect, 30s send, 60s read), and a `limit_req` zone for `/api/run` (10/min, burst 5).
- GitHub Actions CI workflow runs the test suite and a docker image build on every push and pull request.
- `pyproject.toml` and `.python-version` declare runtime dependencies (numpy~=2.2) and pin the Python interpreter.

### Robustness
- CFB legacy parser bounds-checked: 512-byte minimum, sector_shift range, sector offsets bounded against EOF, name-field cap, stream-size cap. Six malformed-input tests added.
- Optimizer no-feasible failures now raise a structured error with hints and the closest infeasible candidate's numbers; HTTP layer surfaces these as `400 no_feasible_design`.

### UX
- Results panel shows a Notes list (cavitation margin, low efficiency, extreme RPM, boundary-pinned designs, CPP empirical reduction).
- Client-side validation mirrors the backend validator; invalid fields highlight in red, Run button stays disabled until clean.
- "Out of date" badge appears when inputs change after a successful run.
- Per-Z comparison table renders below the main result in Optimization mode.
- "PDF" button relabelled to "Print" with a tooltip pointing at browser Save-as-PDF.
- New Methodology disclosure in the top bar summarises the calibration sources (Bernitsas 1981, Oosterveld and van Oossanen 1975, Carlton 2012).

### Documentation
- `analysis/wageningen-b-series-sources.md` rewritten with per-table citations (Bernitsas Tables I and II, Oosterveld and van Oossanen for the Reynolds correction, Carlton for the chord factor and Burrill chart, POPFTRN.EXE string for the CPP multiplier).
- Landmark coefficient verification test added so retabling can never be silent.

### Test count
- 88 unit and integration tests passing locally and on GitHub Actions.

## 1.0 - 2026-05-10

- Initial public release. Clean reimplementation of POP-1.5 as a containerised Python + vanilla JS web application based on the Wageningen B-series polynomial, with legacy `.POP` import.
