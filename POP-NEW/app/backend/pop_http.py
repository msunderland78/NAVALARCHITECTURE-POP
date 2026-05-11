import argparse
import json
from json import JSONDecodeError
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from pop_core import NoFeasibleDesignError, PopInput, parse_legacy_input, read_legacy_pop_text_bytes, result_payload, run_case


FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"
MAX_RUN_BYTES = 16384
MAX_IMPORT_BYTES = 1048576
STATIC_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8"
}
SECURITY_HEADERS = {
    "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'",
    "Referrer-Policy": "no-referrer",
    "X-Content-Type-Options": "nosniff"
}


class RequestTooLarge(ValueError):
    pass


class PopHttpHandler(BaseHTTPRequestHandler):
    server_version = "POPHTTP/0.1"

    def do_GET(self):
        if self.path == "/health":
            self._json(200, {"status": "ok"})
            return
        if self.path == "/api/sample":
            self._json(200, sample_case())
            return
        if self._static():
            return
        self._json(404, {"error": "not_found"})

    def do_POST(self):
        if self.path == "/api/run":
            self._run_case()
            return
        if self.path == "/api/import-pop":
            self._import_pop()
            return
        else:
            self._json(404, {"error": "not_found"})
            return

    def _run_case(self):
        try:
            data = self._json_body(MAX_RUN_BYTES)
            case = PopInput.from_dict(data)
            result = run_case(case)
        except RequestTooLarge as error:
            self._json(413, {"error": "request_too_large", "message": str(error)})
            return
        except NoFeasibleDesignError as error:
            self._json(400, {
                "error": "no_feasible_design",
                "message": str(error),
                "hints": error.hints,
                "nearest": error.nearest
            })
            return
        except ValueError as error:
            self._json(400, {"error": "invalid_input", "message": str(error)})
            return
        self._json(200, result_payload(case, result))

    def _import_pop(self):
        try:
            body = self._body(MAX_IMPORT_BYTES)
            text = read_legacy_pop_text_bytes(body)
            self._json(200, {
                "input": parse_legacy_input(text),
                "warnings": []
            })
        except RequestTooLarge as error:
            self._json(413, {"error": "request_too_large", "message": str(error)})
        except ValueError as error:
            self._json(400, {"error": "invalid_input", "message": str(error)})

    def log_message(self, format, *args):
        return

    def _json(self, status: int, payload: dict):
        data = json.dumps(payload, allow_nan=False, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self._security_headers()
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _json_body(self, max_bytes: int):
        body = self._body(max_bytes)
        try:
            return json.loads(body.decode("utf-8"), parse_constant=_reject_json_constant)
        except (UnicodeDecodeError, JSONDecodeError, ValueError) as error:
            raise ValueError("request body must be valid JSON") from error

    def _body(self, max_bytes: int) -> bytes:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError as error:
            raise ValueError("Content-Length must be an integer") from error
        if length < 0:
            raise ValueError("Content-Length must not be negative")
        if length > max_bytes:
            raise RequestTooLarge(f"request body must be {max_bytes} bytes or fewer")
        return self.rfile.read(length)

    def _static(self) -> bool:
        path = self.path.split("?", 1)[0]
        if path == "/":
            filename = "index.html"
        else:
            filename = path.lstrip("/")
        target = (FRONTEND_DIR / filename).resolve()
        if FRONTEND_DIR not in target.parents and target != FRONTEND_DIR:
            return False
        if not target.is_file():
            return False
        data = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", STATIC_TYPES.get(target.suffix, "application/octet-stream"))
        self.send_header("Cache-Control", "no-store")
        self._security_headers()
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
        return True

    def _security_headers(self):
        for name, value in SECURITY_HEADERS.items():
            self.send_header(name, value)


def _reject_json_constant(value: str):
    raise ValueError(f"{value} is not valid JSON")


def sample_case() -> dict:
    return {
        "projectName": "NA 470 Coursepack Example",
        "runId": "test 1.0",
        "mode": "evaluation",
        "series": "wageningen_b",
        "pitchType": "fixed",
        "bladeCount": 4,
        "initialExpandedAreaRatio": 0.75,
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
            "kinematicViscosityM2S": 0.00000118831
        },
        "burrillBackCavitationPercent": 5
    }


def build_server(host: str, port: int) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), PopHttpHandler)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    server = build_server(args.host, args.port)
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
