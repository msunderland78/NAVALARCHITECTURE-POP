# POP Backend

Pure Python calculation core plus a stdlib HTTP API for the POP web application. The calculation modules under `pop_core/` have no UI or HTTP dependency and are independently testable.

## Runtime dependency

`numpy~=2.2` is the only third-party runtime dependency, used to vectorise the Wageningen polynomial and the optimizer's grid search. Install it before running locally:

```sh
python3 -m pip install --user "numpy~=2.2"
```

## Running a single case from the command line

```sh
PYTHONPATH=POP-NEW/app/backend python3 POP-NEW/app/backend/run_pop.py POP-NEW/tests/fixtures/na470-coursepack.input.json
```

Output is a single JSON document on stdout.

## Running the HTTP API locally

```sh
PYTHONPATH=POP-NEW/app/backend python3 POP-NEW/app/backend/pop_http.py --host 127.0.0.1 --port 8080
```

## Endpoints

- `GET  /health` returns `{"status": "ok"}`.
- `GET  /api/sample` returns a representative input case (NA 470 coursepack, evaluation mode).
- `POST /api/run` evaluates a single design or runs the optimizer, depending on `mode`. Body must be JSON; max 16 KB.
- `POST /api/import-pop` accepts a legacy `.POP` OLE Compound File body (max 1 MB) and returns the converted input object.

## Successful `/api/run` response

```json
{
  "projectName": "...",
  "runId": "...",
  "mode": "evaluation" | "optimization",
  "series": "wageningen_b",
  "pitchType": "fixed" | "controllable",
  "bladeCount": <int>,
  "raw": { full-precision design quantities },
  "legacyRounded": { rounded display values },
  "curves": { openWater: [...], point: {...} },
  "warnings": [
    {"level": "warning" | "info", "code": "...", "message": "..."}
  ],
  "bladeSweep": {                  // optimization mode only
    "bestBladeCount": <int>,
    "entries": [ per-Z summary rows ]
  }
}
```

## Failure responses

The HTTP server returns JSON error documents:

- `400  invalid_input` for validation failures and malformed bodies (`message` is the validator error text).
- `400  no_feasible_design` when the optimizer cannot satisfy the constraints. The body includes a `hints` list of human-readable suggestions and a `nearest` snapshot of the closest infeasible candidate (D, P/D, Ae/Ao, RPM, eta, Burrill loading and allowable, cavitation number).
- `413  request_too_large` for oversized bodies.
- `404  not_found` for unknown paths.

## Security headers

Every response carries `Content-Security-Policy`, `Referrer-Policy: no-referrer`, and `X-Content-Type-Options: nosniff`. Static assets are served with `Cache-Control: no-store`.

## Tests

From `POP-NEW`:

```sh
PYTHONPATH=app/backend python3 -m unittest discover -s tests
```
