# POP Backend

This package will hold the POP calculation core and API.

The first backend target is a pure Python calculation module with tests against recovered legacy fixtures.

Run a native JSON case from the command line:

```sh
PYTHONPATH=POP-NEW/app/backend python3 POP-NEW/app/backend/run_pop.py POP-NEW/tests/fixtures/na470-coursepack.input.json
```

Run the HTTP API locally:

```sh
PYTHONPATH=POP-NEW/app/backend python3 POP-NEW/app/backend/pop_http.py --host 127.0.0.1 --port 8080
```

Endpoints:

- `GET /health`
- `GET /api/sample`
- `POST /api/run`
