# POP Web - In-Depth Review and Recommendations

Reviewer: Claude Opus 4.7
Date: 2026-05-11
Scope: Full review of the Codex-produced web port of the legacy Propeller Optimization Program (POP-1.5).

## Summary

Codex did a clean job. All 51 tests pass, the golden NA 470 case reproduces within the published tolerances, the calculation core is cleanly separated from the HTTP layer, OLE Compound File parsing was implemented from scratch (no `olefile` dependency), and input validation is solid against the obvious XSS/injection probes. The product is genuinely usable as a B-series preliminary design tool. What follows is what to change, in roughly the order to do it.

---

## 1. Engineering correctness (highest priority for a naval architecture tool)

These affect the numbers the tool produces and therefore the trust customers can place in it.

### 1.1 The Reynolds-section calibration is a single magic constant
`POP-NEW/app/backend/pop_core/solver.py:9` defines `SECTION_CHORD_FACTOR = 2.21926629468588`, fitted from one legacy case. `analysis/wageningen-b-series-sources.md:39` admits this. For any case far from the NA 470 geometry the corrected `KT`/`KQ` will drift. Replace it with the published representative chord at `0.75R`:

```
c_0.75R = 2.073 * Ae/Ao * D / Z   (Carlton, Marine Propellers and Propulsion)
```

Or the ITTC equivalent. Both put the constant near 2.07-2.08, not 2.22. The 2.22 value is over-fitted to one point. Once the chord formula is sourced from a published reference, lock it in tests against a second hand-computed case and remove the calibration justification from the analysis doc.

### 1.2 The Burrill 5%/10% factors are hand-fit, not Burrill chart values
`solver.py:88` uses `0.26` at 5% and `0.32` at 10% with linear interpolation. Burrill's published tau_c vs sigma_{0.7R} chart is more nuanced - the factors depend on sigma, not just the cavitation percentage. The current implementation is "calibrated to make the recovered NA 470 design active at Ae/Ao = 0.6293" (per the analysis doc). For real design work this can produce a cavitation pass on geometry that would actually cavitate. Replace with a proper digitized Burrill chart and add a second test case to keep it honest.

### 1.3 Inconsistent radial reference station for sigma vs Burrill vs Reynolds
- `core.py:48` cavitation number uses `0.7 * pi * n * D` (0.7R)
- `solver.py:76` Reynolds uses `0.75 * pi * n * D` (0.75R)
- `solver.py:83` Burrill loading uses `0.75 * pi * n * D` (0.75R)

Each station is defensible against a different source, but document which reference is being followed for each formula. Burrill's original work uses 0.7R consistently; if Burrill is switched to 0.7R the factors may need recalibration anyway (see 1.2).

### 1.4 The controllable-pitch 2% reduction is a global multiplier, not a physics model
`core.py:39` applies `0.98 * eta0`. This matches the legacy string `Eta 0 Reduced by 2% When Controllable Pitch` but it's a crude approximation - real CPP hub losses depend on hub-to-diameter ratio. Document it as "matches POP-1.5 behavior, not a physical model" so a future user does not mistake it for fidelity. Add a banner in the UI when `pitchType=controllable` is selected.

### 1.5 Optimizer doesn't optimize blade count or off-design power balance
Current optimizer only searches over `(D, P/D, Ae/Ao)` with blade count fixed. Legacy POP did the same, so this is conformant - but to be genuinely useful for preliminary design, add an outer loop over `Z in {3,4,5,6,7}` and report the best per-Z table. Cheap and high-value.

### 1.6 Bisection lacks a sanity check
`solver.py:27` `solve_advance_coefficient_for_thrust` hardcodes `low=0.05, high=1.6` with no check that the function actually changes sign on that interval. If a candidate geometry cannot produce required thrust anywhere in that range, the result is silently `high=1.6` and downstream nonsense - the optimizer's `torqueCoefficient <= 0 or thrustCoefficient <= 0` guard catches the worst, but borderline cases sneak through. Either:
- check `kt_available > kt_required` at `low` and `kt_available < kt_required` at `high`, return a sentinel if not, or
- iterate until `(high - low) < 1e-6` and break early (50 iterations on 1.55-wide interval gives 1e-15 precision, far past Python float; cycles are wasted).

---

## 2. Performance

### 2.1 Optimization takes ~2.3 s in pure Python
729 candidates x 3 phases x auto-Reynolds inner loop x bisection x 86-term polynomial. Acceptable but right at the threshold where users start mashing buttons. Two ways down:

- **NumPy-vectorize the polynomial evaluator.** Precompute the four exponent arrays once, vectorize `wageningen_kt/kq` across the entire `(D, P/D, Ae/Ao)` grid in one call. Order-of-magnitude speedup. Adds NumPy to the container (~30 MB), but eliminates the perceived lag.
- **Drop bisection iteration count from 50 to ~25.** Already at machine precision well before that.

### 2.2 NGINX proxies the static files through Python
`nginx.conf:13` proxies everything. Move `index.html`, `app.js`, `styles.css` to a volume mount and let nginx serve them directly with proper `Cache-Control` for the assets (the HTML can stay `no-store`). Lowers Python's load and lets nginx do what nginx is good at.

---

## 3. Production hardening

### 3.1 Docker container runs as root, doesn't pin Python
`POP-NEW/app/backend/Dockerfile:1` uses `python:3.12-slim` (a moving tag) and never creates an unprivileged user. Add:

```dockerfile
FROM python:3.12.8-slim
RUN useradd --create-home --uid 10001 pop
USER pop
```

Pin the version, pin the base image digest for supply-chain hardening.

### 3.2 No request logging at all
`pop_http.py:80` `log_message` is overridden to return nothing. No audit trail for who hit what endpoint with what. For a single-user tool that's fine; the moment this is on the internet, at least error-level access logs to a file or stdout via Python's `logging` module are required. Nginx access logs will help, but they do not see backend exceptions.

### 3.3 No NGINX timeouts, IPv6, or hardening directives
`nginx.conf` is minimal. Add at minimum:

```
server_tokens off;
listen [::]:80;
proxy_read_timeout 30s;
proxy_connect_timeout 5s;
```

A rate-limit zone for `/api/run` (the only CPU-burning endpoint) would make abuse harder if this is ever exposed publicly.

### 3.4 No CI
There is no `.github/workflows/`. Add a single workflow that runs `python -m unittest discover` plus a `docker build` check on PRs. The test suite is 9 seconds, basically free.

### 3.5 No requirements/dependency manifest
The project is admirably stdlib-only, but `pyproject.toml` or even a sentinel `requirements.txt` (empty + comment) helps future maintainers know that's intentional. Same for a `python-version` file.

---

## 4. Robustness gaps

### 4.1 The CFB parser is forgiving of adversarial input
`cfb.py` reads file fields without bounds-checking against `len(self.data)`. The 1 MB import limit in `pop_http.py:12` caps damage, but a malformed file with a `start_sector` of `0x0FFFFFFA` could index out-of-bounds. Add a few `assert offset + size <= len(self.data)` guards in `_sector`, `_read_directory_entries`, and `_read_regular_stream`. Add a malformed-input unit test for `cfb.py` - right now it is only tested through the two real samples.

### 4.2 Frontend tests are brittle
`test_frontend_static.py:69` asserts a specific literal multi-line JS string. Any refactor that changes whitespace breaks the test. Replace the literal-substring check with `assertIn("escapeHtml(name)", script)` style probes. Same applies to the other `assertIn` checks against exact rendered strings.

### 4.3 Optimizer error messages are vague
`optimizer.py:43` raises `"No feasible propeller design found"` with no context. Include the active constraint set, the closest infeasible result, and a hint ("relax cavitation limit to 10% or increase diameter range"). Surface those hints in the frontend.

### 4.4 No "stale result" indicator
After running a case, if an input is changed the result panel keeps showing old numbers with no warning. Add a "results out of date" badge that lights up on `form` `input` events after a successful run, until the user runs again.

---

## 5. UX polish

### 5.1 The result panel doesn't show feasibility/warnings
Designs near cavitation, low efficiency, or extreme RPM should get advisory text. The data is already there - `cavitationNumber`, `burrillLoading`, allowable loading - just plumb a `warnings: []` array into the JSON payload and render below the table.

### 5.2 No unit toggle
US-coded engineers will reach for feet/inches and shaft horsepower. Even a read-only "imperial summary" line below each result row would be welcome. Naval-arch users will say thanks.

### 5.3 Frontend lacks cross-field client-side validation
`Dmin > Dmax`, `bladeCount` out of `[3,7]`, `Ae/Ao` outside Wageningen-valid range - all caught by the backend and shown as a generic error. Mirror the validator's rules client-side and disable the submit button when invalid, with red field highlights.

### 5.4 No version display in the UI
README says 1.0; the app does not say so anywhere. Add a small footer line: `POP for the Web 1.0`. Bake a build/commit hash into the container at build time to know which version a user is running.

### 5.5 The propeller diagram is decorative, not informative
It is a stylized SVG of arbitrary blades. For naval architects this is borderline insulting - they want a polar chart of expanded blade outline against radius, or at minimum a labeled drawing. Replace or remove. The open-water curve plot is the actually-useful visual.

### 5.6 PDF export is "press Ctrl+P"
Documented, but a one-click button labeled "Print" rather than "PDF" would be more honest. Or implement a real server-side PDF generator (reportlab or weasyprint). The plan doc flags this as an open question - the recommendation is to keep print-to-PDF, rename the button.

---

## 6. Documentation and provenance

### 6.1 Wageningen coefficient provenance is one paragraph
`analysis/wageningen-b-series-sources.md:29` says the table is "attributed to Oosterveld and van Oossanen and reproduced in common marine-propulsion references." For an engineering tool, that's hand-waving. Pick the canonical reference (Bernitsas 1981 is already cited), put the page number, and confirm every coefficient against that reference. The 39/47 term split is correct; verify each value to the digit count published.

### 6.2 The "calibrated to one case" caveats should be in the UI, not just analysis docs
A non-technical user sees a clean web app and does not read the markdown files. An "About / Methodology" page or a `?` icon next to Reynolds number / Burrill cavitation explaining the calibration status would set expectations honestly.

### 6.3 No CHANGELOG
Add one when version 1.1 is cut.

---

## Recommended Priority

Ranked by value-per-effort:

1. **1.1 + 1.2** (sourced chord formula + sourced Burrill chart) - this is the engineering credibility issue
2. **3.1 + 3.4** (non-root container + CI) - one afternoon, big production-readiness gain
3. **2.1** (NumPy-vectorize the polynomial) - one afternoon, makes optimization feel instant
4. **4.1** (CFB parser bounds checks) - 30 minutes, removes a small attack surface
5. **5.1 + 5.3** (feasibility warnings + client-side validation) - significantly better UX
6. **1.5** (blade-count outer loop) - genuinely useful for preliminary design
7. **6.2** (methodology page) - manages user expectations
8. Everything else

The core decision Codex made - clean Python reimplementation, hand-rolled CFB parser, stdlib-only HTTP server, vanilla JS frontend, structured input validation - was the right one. The recommendations above are sharpening, not rework.
