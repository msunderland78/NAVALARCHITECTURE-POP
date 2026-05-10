import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from pop_core import PopInput, parse_legacy_input, read_legacy_pop_text_bytes, result_payload, run_case


FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"
STATIC_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8"
}


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
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)
        data = json.loads(body.decode("utf-8"))
        case = PopInput.from_dict(data)
        self._json(200, result_payload(case, run_case(case)))

    def _import_pop(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)
        text = read_legacy_pop_text_bytes(body)
        self._json(200, {
            "input": parse_legacy_input(text),
            "warnings": []
        })

    def log_message(self, format, *args):
        return

    def _json(self, status: int, payload: dict):
        data = json.dumps(payload, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

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
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
        return True


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
