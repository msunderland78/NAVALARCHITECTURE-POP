import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from pop_core import PopInput, result_payload, run_case


class PopHttpHandler(BaseHTTPRequestHandler):
    server_version = "POPHTTP/0.1"

    def do_GET(self):
        if self.path == "/health":
            self._json(200, {"status": "ok"})
            return
        if self.path == "/api/sample":
            self._json(200, sample_case())
            return
        self._json(404, {"error": "not_found"})

    def do_POST(self):
        if self.path != "/api/run":
            self._json(404, {"error": "not_found"})
            return
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)
        data = json.loads(body.decode("utf-8"))
        case = PopInput.from_dict(data)
        self._json(200, result_payload(case, run_case(case)))

    def log_message(self, format, *args):
        return

    def _json(self, status: int, payload: dict):
        data = json.dumps(payload, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


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
