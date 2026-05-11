# POP Web - In-Depth Review and Recommendations

Reviewer: Claude Opus 4.7
Date: 2026-05-11 (review issued); status block last updated 2026-05-11 after the 1.1 work.
Scope: Full review of the Codex-produced web port of the legacy Propeller Optimization Program (POP-1.5).

## Implementation Status

Each section below carries a `Status:` line so the original recommendation text stays intact for context but the current state is visible at a glance.

`Done` items are tagged with the short commit hash that shipped them. `Partial` items have a note describing what was addressed and what is still outstanding. `Open` items have not been touched.

Snapshot:

| Section | Item | Status |
|---|---|---|
| 1 Engineering correctness | 1.1 Reynolds chord factor | Done (`e96f50b`) |
| | 1.2 Burrill chart | Done (`eaee538`) |
| | 1.3 Inconsistent radial reference station | Open (documented, not unified) |
| | 1.4 Controllable-pitch empirical multiplier | Done (`279b06d`) |
| | 1.5 Blade-count sweep | Done (`14e1b2a`) |
| | 1.6 Bisection sanity check | Partial (`aad527c` drops iterations; no sign-change sentinel) |
| 2 Performance | 2.1 NumPy vectorise polynomial | Done (`aad527c`, `d423a85`, `442b8f1`) |
| | 2.2 NGINX serves static files directly | Open |
| 3 Production hardening | 3.1 Non-root container, pinned Python | Done (`6dfd8b0`) |
| | 3.2 Request logging | Open |
| | 3.3 NGINX timeouts, IPv6, rate limit | Done (`cf2aeaa`) |
| | 3.4 CI workflow | Done (`e58e3af`, `d423a85`, `442b8f1`) |
| | 3.5 Dependency manifest | Done (`f8634c1`; numpy added in `aad527c`) |
| 4 Robustness | 4.1 CFB parser bounds checks | Done (`3c70d7e`) |
| | 4.2 Brittle frontend tests | Partial (`3baf3db` de-brittled the one explicitly called out) |
| | 4.3 Optimizer error hints | Done (`4bec65a`) |
| | 4.4 Stale result indicator | Done (`2c8fd9c`) |
| 5 UX polish | 5.1 Result warnings | Done (`7098766`) |
| | 5.2 Imperial unit toggle | Open |
| | 5.3 Client-side validation | Done (`7098766`) |
| | 5.4 Version display in UI | Open |
| | 5.5 Propeller diagram is decorative | Open |
| | 5.6 Print button rename | Done (`7098766`) |
| 6 Documentation | 6.1 Coefficient provenance + landmark tests | Done (`795bb07`) |
| | 6.2 Methodology disclosure in UI | Done (`bdfcfda`) |
| | 6.3 CHANGELOG | Done (`66e647e`) |

Test count: 51 at the start of this round, 88 now. CI is green.

## Summary

Codex did a clean job. All 51 tests pass, the golden NA 470 case reproduces within the published tolerances, the calculation core is cleanly separated from the HTTP layer, OLE Compound File parsing was implemented from scratch (no `olefile` dependency), and input validation is solid against the obvious XSS/injection probes. The product is genuinely usable as a B-series preliminary design tool. What follows is what to change, in roughly the order to do it.

---

## 1. Engineering correctness (highest priority for a naval architecture tool)

These affect the numbers the tool produces and therefore the trust customers can place in it.

### 1.1 The Reynolds-section calibration is a single magic constant
**Status: Done** (`e96f50b`). `SECTION_CHORD_FACTOR` is now `2.073` per Carlton. Reported RN shifts ~6.6% from legacy for the NA 470 case; tests widened accordingly. `analysis/wageningen-b-series-sources.md` carries the citation.
`POP-NEW/app/backend/pop_core/solver.py:9` defines `SECTION_CHORD_FACTOR = 2.21926629468588`, fitted from one legacy case. `analysis/wageningen-b-series-sources.md:39` admits this. For any case far from the NA 470 geometry the corrected `KT`/`KQ` will drift. Replace it with the published representative chord at `0.75R`:

```
c_0.75R = 2.073 * Ae/Ao * D / Z   (Carlton, Marine Propellers and Propulsion)
```

Or the ITTC equivalent. Both put the constant near 2.07-2.08, not 2.22. The 2.22 value is over-fitted to one point. Once the chord formula is sourced from a published reference, lock it in tests against a second hand-computed case and remove the calibration justification from the analysis doc.

### 1.2 The Burrill 5%/10% factors are hand-fit, not Burrill chart values
**Status: Done** (`eaee538`). Digitised 5% and 10% lines from Carlton Figure 9.21 with linear interpolation in sigma and linear blending between curves. Five Burrill unit tests + one cavitation-active integration test added.
`solver.py:88` uses `0.26` at 5% and `0.32` at 10% with linear interpolation. Burrill's published tau_c vs sigma_{0.7R} chart is more nuanced - the factors depend on sigma, not just the cavitation percentage. The current implementation is "calibrated to make the recovered NA 470 design active at Ae/Ao = 0.6293" (per the analysis doc). For real design work this can produce a cavitation pass on geometry that would actually cavitate. Replace with a proper digitized Burrill chart and add a second test case to keep it honest.

### 1.3 Inconsistent radial reference station for sigma vs Burrill vs Reynolds
**Status: Open.** The stations (0.7R for sigma, 0.75R for Burrill and Reynolds) are unchanged from the original code. The provenance doc now records which reference each formula follows, so the inconsistency is documented rather than fixed. A future pass should unify on 0.7R per Burrill's original work and recalibrate any factors that move.
- `core.py:48` cavitation number uses `0.7 * pi * n * D` (0.7R)
- `solver.py:76` Reynolds uses `0.75 * pi * n * D` (0.75R)
- `solver.py:83` Burrill loading uses `0.75 * pi * n * D` (0.75R)

Each station is defensible against a different source, but document which reference is being followed for each formula. Burrill's original work uses 0.7R consistently; if Burrill is switched to 0.7R the factors may need recalibration anyway (see 1.2).

### 1.4 The controllable-pitch 2% reduction is a global multiplier, not a physics model
**Status: Done** (`279b06d`). Non-obvious comment in `core.py` explains the empirical origin; yellow banner in the results panel appears whenever Pitch Type is Controllable. Replacement with a hub-ratio-aware model is recorded as a still-open item in the conversion plan.
`core.py:39` applies `0.98 * eta0`. This matches the legacy string `Eta 0 Reduced by 2% When Controllable Pitch` but it's a crude approximation - real CPP hub losses depend on hub-to-diameter ratio. Document it as "matches POP-1.5 behavior, not a physical model" so a future user does not mistake it for fidelity. Add a banner in the UI when `pitchType=controllable` is selected.

### 1.5 Optimizer doesn't optimize blade count or off-design power balance
**Status: Done for blade count** (`14e1b2a`). Optimizer sweeps Z = 3..7 and returns the global best plus a per-Z table; frontend renders the comparison with the best row highlighted. Off-design power balance (operating at multiple conditions) is not addressed.
Current optimizer only searches over `(D, P/D, Ae/Ao)` with blade count fixed. Legacy POP did the same, so this is conformant - but to be genuinely useful for preliminary design, add an outer loop over `Z in {3,4,5,6,7}` and report the best per-Z table. Cheap and high-value.

### 1.6 Bisection lacks a sanity check
**Status: Partial** (`aad527c`). Iterations dropped from 50 to 20 (precision still 1.5e-6 in J). The sign-change sentinel at the bracket endpoints is not implemented; the optimizer's positive-KT / positive-KQ feasibility mask catches the worst failures but a degenerate case could still fall through with a J pinned at the upper bound.
`solver.py:27` `solve_advance_coefficient_for_thrust` hardcodes `low=0.05, high=1.6` with no check that the function actually changes sign on that interval. If a candidate geometry cannot produce required thrust anywhere in that range, the result is silently `high=1.6` and downstream nonsense - the optimizer's `torqueCoefficient <= 0 or thrustCoefficient <= 0` guard catches the worst, but borderline cases sneak through. Either:
- check `kt_available > kt_required` at `low` and `kt_available < kt_required` at `high`, return a sentinel if not, or
- iterate until `(high - low) < 1e-6` and break early (50 iterations on 1.55-wide interval gives 1e-15 precision, far past Python float; cycles are wasted).

---

## 2. Performance

### 2.1 Optimization takes ~2.3 s in pure Python
**Status: Done** (`aad527c`, `d423a85`, `442b8f1`). Wageningen polynomial, bisection, Reynolds iteration and the optimizer grid search are numpy-vectorised. Bisection iterations dropped from 50 to 20. NA 470 full blade-sweep optimization now completes in ~2.2s (was ~11s). Numpy~=2.2 added as the only runtime dependency.
729 candidates x 3 phases x auto-Reynolds inner loop x bisection x 86-term polynomial. Acceptable but right at the threshold where users start mashing buttons. Two ways down:

- **NumPy-vectorize the polynomial evaluator.** Precompute the four exponent arrays once, vectorize `wageningen_kt/kq` across the entire `(D, P/D, Ae/Ao)` grid in one call. Order-of-magnitude speedup. Adds NumPy to the container (~30 MB), but eliminates the perceived lag.
- **Drop bisection iteration count from 50 to ~25.** Already at machine precision well before that.

### 2.2 NGINX proxies the static files through Python
**Status: Open.** All requests still pass through the Python backend, which then serves the static HTML/JS/CSS. Moving the static assets to an NGINX-served volume mount would remove one hop per asset request. Low priority since the static files are small and cached client-side.
`nginx.conf:13` proxies everything. Move `index.html`, `app.js`, `styles.css` to a volume mount and let nginx serve them directly with proper `Cache-Control` for the assets (the HTML can stay `no-store`). Lowers Python's load and lets nginx do what nginx is good at.

---

## 3. Production hardening

### 3.1 Docker container runs as root, doesn't pin Python
**Status: Done** (`6dfd8b0`). Pinned `python:3.12.8-slim`. Unprivileged `pop` user (uid/gid 10001). `USER pop:pop`, `--chown` on COPYs, `PYTHONDONTWRITEBYTECODE` + `PYTHONUNBUFFERED`. Smoke-tested locally.
`POP-NEW/app/backend/Dockerfile:1` uses `python:3.12-slim` (a moving tag) and never creates an unprivileged user. Add:

```dockerfile
FROM python:3.12.8-slim
RUN useradd --create-home --uid 10001 pop
USER pop
```

Pin the version, pin the base image digest for supply-chain hardening.

### 3.2 No request logging at all
**Status: Open.** `pop_http.py` still overrides `log_message` to nothing. NGINX access logs catch the proxy traffic but the Python backend produces no audit trail for invalid input, no-feasible-design rejections, or unexpected exceptions. A future pass should route via Python's `logging` module to stdout so Docker captures it.
`pop_http.py:80` `log_message` is overridden to return nothing. No audit trail for who hit what endpoint with what. For a single-user tool that's fine; the moment this is on the internet, at least error-level access logs to a file or stdout via Python's `logging` module are required. Nginx access logs will help, but they do not see backend exceptions.

### 3.3 No NGINX timeouts, IPv6, or hardening directives
**Status: Done** (`cf2aeaa`). `server_tokens off`, `listen [::]:80`, `proxy_connect_timeout 5s`, `proxy_send_timeout 30s`, `proxy_read_timeout 60s`, and a `limit_req` zone scoped to `/api/run` (10/min with burst 5). Verified live: server header stripped, 429 returned after burst.
`nginx.conf` is minimal. Add at minimum:

```
server_tokens off;
listen [::]:80;
proxy_read_timeout 30s;
proxy_connect_timeout 5s;
```

A rate-limit zone for `/api/run` (the only CPU-burning endpoint) would make abuse harder if this is ever exposed publicly.

### 3.4 No CI
**Status: Done** (`e58e3af`, `d423a85`, `442b8f1`). GitHub Actions workflow runs the test suite and a docker image build on every push and pull request. `permissions: contents: read` limits the workflow's repository access. `pyproject.toml` is set up so `pip install .` is a metadata-only install that just pulls the numpy dependency.
There is no `.github/workflows/`. Add a single workflow that runs `python -m unittest discover` plus a `docker build` check on PRs. The test suite is 9 seconds, basically free.

### 3.5 No requirements/dependency manifest
**Status: Done** (`f8634c1`; numpy declared in `aad527c`). `pyproject.toml` declares `numpy~=2.2`, `.python-version` pins `3.12.8`. The build-system block plus empty packages list makes `pip install .` install dependencies without trying to package the project itself.
The project is admirably stdlib-only, but `pyproject.toml` or even a sentinel `requirements.txt` (empty + comment) helps future maintainers know that's intentional. Same for a `python-version` file.

---

## 4. Robustness gaps

### 4.1 The CFB parser is forgiving of adversarial input
**Status: Done** (`3c70d7e`). 512-byte minimum, `sector_shift` in `[7, 16]`, `mini_sector_shift` in `[6, 12]`, sector offsets bounded against `len(self.data)`, name field capped at 64 bytes, stream-size cap of 64 MB. Six malformed-input unit tests in a new `test_cfb_malformed.py`. Real `POP1.POP`/`POPout.pop` samples still parse cleanly.
`cfb.py` reads file fields without bounds-checking against `len(self.data)`. The 1 MB import limit in `pop_http.py:12` caps damage, but a malformed file with a `start_sector` of `0x0FFFFFFA` could index out-of-bounds. Add a few `assert offset + size <= len(self.data)` guards in `_sector`, `_read_directory_entries`, and `_read_regular_stream`. Add a malformed-input unit test for `cfb.py` - right now it is only tested through the two real samples.

### 4.2 Frontend tests are brittle
**Status: Partial** (`3baf3db`). `test_frontend_escapes_rendered_table_values` was the one explicitly called out and is now a semantic probe (it scopes to each `innerHTML` assignment and checks for `escapeHtml(name)` / `escapeHtml(value)` inside). Other `assertIn` checks against rendered strings (e.g. exact button text, exact warning code names) still use literal substring matching and will need similar treatment if those literals change.
`test_frontend_static.py:69` asserts a specific literal multi-line JS string. Any refactor that changes whitespace breaks the test. Replace the literal-substring check with `assertIn("escapeHtml(name)", script)` style probes. Same applies to the other `assertIn` checks against exact rendered strings.

### 4.3 Optimizer error messages are vague
**Status: Done** (`4bec65a`). `NoFeasibleDesignError` carries a hints list and a `nearest` snapshot (D, P/D, Ae/Ao, RPM, eta, Burrill loading vs allowable, sigma). HTTP layer returns `400 no_feasible_design` with structured `hints` and `nearest` fields; frontend renders the hints as warning rows in the existing Notes panel and the nearest candidate as a comparable info row.
`optimizer.py:43` raises `"No feasible propeller design found"` with no context. Include the active constraint set, the closest infeasible result, and a hint ("relax cavitation limit to 10% or increase diameter range"). Surface those hints in the frontend.

### 4.4 No "stale result" indicator
**Status: Done** (`2c8fd9c`). "Out of date" pill next to the mode chip lights up whenever a previous run exists and the form changes (input event, sample load, `.POP` import). Clears on the next successful run.
After running a case, if an input is changed the result panel keeps showing old numbers with no warning. Add a "results out of date" badge that lights up on `form` `input` events after a successful run, until the user runs again.

---

## 5. UX polish

### 5.1 The result panel doesn't show feasibility/warnings
**Status: Done** (`7098766`). Backend emits a `warnings` array with `level` (warning/info), `code`, and message. Codes: `cavitation_exceeds_limit`, `cavitation_margin_tight`, `low_efficiency`, `high_rpm`/`low_rpm`, `diameter_pinned_min`/`_max`, `pd_at_*_search_bound`, `ae_at_*_search_bound`, `cpp_empirical`. Frontend renders the list under the results header with level-based colouring.
Designs near cavitation, low efficiency, or extreme RPM should get advisory text. The data is already there - `cavitationNumber`, `burrillLoading`, allowable loading - just plumb a `warnings: []` array into the JSON payload and render below the table.

### 5.2 No unit toggle
**Status: Open.** Results are still SI-only. An imperial summary line (feet/inches for D and P, knots/mph for ship speed, lbf for thrust, shaft horsepower) below each result row would help US-coded users without changing the underlying calculation.
US-coded engineers will reach for feet/inches and shaft horsepower. Even a read-only "imperial summary" line below each result row would be welcome. Naval-arch users will say thanks.

### 5.3 Frontend lacks cross-field client-side validation
**Status: Done** (`7098766`). `FIELD_RULES` in `app.js` mirrors the backend validator (blade count, ratio ranges, positives, `D Min <= D Max`, wakeFraction 0-0.9, cavitation 0-100). Invalid fields get a red border and inline message; Run button stays disabled until clean. Re-runs on input, sample load, `.POP` import, and after each successful run.
`Dmin > Dmax`, `bladeCount` out of `[3,7]`, `Ae/Ao` outside Wageningen-valid range - all caught by the backend and shown as a generic error. Mirror the validator's rules client-side and disable the submit button when invalid, with red field highlights.

### 5.4 No version display in the UI
**Status: Open.** README and CHANGELOG name the release as 1.1, but the running app's UI does not display a version string. Easy follow-up: bake a build/commit hash into the container at build time and render it in the footer or behind the Methodology disclosure.
README says 1.0; the app does not say so anywhere. Add a small footer line: `POP for the Web 1.0`. Bake a build/commit hash into the container at build time to know which version a user is running.

### 5.5 The propeller diagram is decorative, not informative
**Status: Open.** Still a stylised SVG of arbitrary blades. Replacing it with an expanded-blade-outline plot against radius (or removing it) is unchanged from the review.
It is a stylized SVG of arbitrary blades. For naval architects this is borderline insulting - they want a polar chart of expanded blade outline against radius, or at minimum a labeled drawing. Replace or remove. The open-water curve plot is the actually-useful visual.

### 5.6 PDF export is "press Ctrl+P"
**Status: Done** (`7098766`). Button now reads "Print" with a tooltip pointing at the browser's Save-as-PDF flow. Server-side PDF generator deferred per the review's recommendation.
Documented, but a one-click button labeled "Print" rather than "PDF" would be more honest. Or implement a real server-side PDF generator (reportlab or weasyprint). The plan doc flags this as an open question - the recommendation is to keep print-to-PDF, rename the button.

---

## 6. Documentation and provenance

### 6.1 Wageningen coefficient provenance is one paragraph
**Status: Done** (`795bb07`). `analysis/wageningen-b-series-sources.md` rewritten with per-table citations: Bernitsas, Ray, Kinley (1981) Tables I/II for KT/KQ, Oosterveld and van Oossanen (1975) for the Reynolds correction, Carlton (2012) for the 0.75R chord and Burrill chart, and the `POPFTRN.EXE` string for the CPP multiplier. Added `test_landmark_coefficients_match_published_values` pinning five KT and five KQ coefficients by exponent key so any retabling trips a test.
`analysis/wageningen-b-series-sources.md:29` says the table is "attributed to Oosterveld and van Oossanen and reproduced in common marine-propulsion references." For an engineering tool, that's hand-waving. Pick the canonical reference (Bernitsas 1981 is already cited), put the page number, and confirm every coefficient against that reference. The 39/47 term split is correct; verify each value to the digit count published.

### 6.2 The "calibrated to one case" caveats should be in the UI, not just analysis docs
**Status: Done** (`bdfcfda`). Methodology disclosure button in the top bar opens an inline panel summarising the calibration sources, Reynolds correction and chord formula, Burrill chart digitisation, optimization scope, CPP empirical reduction, and the calibration-status caveats. Hidden in print so it does not appear on report PDFs.
A non-technical user sees a clean web app and does not read the markdown files. An "About / Methodology" page or a `?` icon next to Reynolds number / Burrill cavitation explaining the calibration status would set expectations honestly.

### 6.3 No CHANGELOG
Add one when version 1.1 is cut.

**Status: Done** (`66e647e`). `POP-NEW/CHANGELOG.md` documents 1.0 and 1.1.

---

## Recommended Priority (original)

Ranked by value-per-effort at review time. All items in this list have shipped.

1. **1.1 + 1.2** (sourced chord formula + sourced Burrill chart) - this is the engineering credibility issue
2. **3.1 + 3.4** (non-root container + CI) - one afternoon, big production-readiness gain
3. **2.1** (NumPy-vectorize the polynomial) - one afternoon, makes optimization feel instant
4. **4.1** (CFB parser bounds checks) - 30 minutes, removes a small attack surface
5. **5.1 + 5.3** (feasibility warnings + client-side validation) - significantly better UX
6. **1.5** (blade-count outer loop) - genuinely useful for preliminary design
7. **6.2** (methodology page) - manages user expectations
8. Everything else

## Still Open After the 1.1 Round

The remaining items, in roughly the same value-per-effort order:

1. **1.3** Unify the radial reference station across `sigma`, Burrill, and Reynolds. Pick 0.7R per Burrill and recalibrate any factor that moves.
2. **1.6** Add a sign-change sanity check on the bisection bracket. The 20-iteration vectorised bisection is correct for well-posed cases; a degenerate case can still pin at the upper bound.
3. **3.2** Wire `pop_http.py` to the Python `logging` module so the backend produces an audit trail to stdout. NGINX access logs already cover the proxy traffic; this is for backend exceptions and rejection paths.
4. **5.2** Imperial unit toggle. A read-only feet/inches/knots/lbf/SHP summary under each result row.
5. **5.4** Display the running version in the UI. Bake commit/version at build time and render it in the footer.
6. **2.2** Move static asset serving to NGINX directly. Low priority since the static files are small and cached client-side.
7. **5.5** Replace or remove the decorative propeller SVG. An expanded-blade-outline plot would be informative; just removing the SVG is also acceptable.
8. **4.2** Walk through the remaining `assertIn` checks in `test_frontend_static.py` and replace any that match exact rendered strings with semantic probes similar to the one fixed in `3baf3db`.

The core decision Codex made - clean Python reimplementation, hand-rolled CFB parser, stdlib-only HTTP server (now plus numpy), vanilla JS frontend, structured input validation - was the right one. The 1.1 round of work hardened the engineering calibration, added the optimization features that were missing, and brought the deployment up to a production baseline. The remaining items are sharpening, not rework.
