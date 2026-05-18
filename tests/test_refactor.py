import json
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import frogAuth
from pocs import additional, const, runtime


class JsonHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/v1/status/buildinfo":
            payload = {"status": "success", "data": {"version": "2.52.0"}}
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(payload).encode())
            return
        self.send_response(404)
        self.end_headers()

    def log_message(self, *_):
        return


class RefactorTests(unittest.TestCase):
    def test_normalize_targets_accepts_urls_and_host_ports(self):
        self.assertEqual(
            frogAuth.normalize_targets(["https://example.com/a", "http://example.com:8080", "127.0.0.1:6379", "bad"]),
            ["example.com:443", "example.com:8080", "127.0.0.1:6379"],
        )

    def test_registry_contains_legacy_and_new_components(self):
        names = {check["name"] for check in const.ALL_CHECKS}
        self.assertIn("redis", names)
        self.assertIn("springboot", names)
        self.assertIn("prometheus", names)
        self.assertIn("kubernetes_api", names)
        self.assertGreaterEqual(len(const.all_ports.split(",")), 100)

    def test_low_noise_caps_rates_and_threads(self):
        args = frogAuth.build_parser().parse_args(["linux", "--threads", "100", "--rate", "1000", "--httpx-threads", "300", "--low-noise"])
        frogAuth.apply_low_noise(args)
        self.assertEqual(args.threads, 30)
        self.assertEqual(args.rate, 200)
        self.assertEqual(args.httpx_threads, 80)
        self.assertEqual(args.http_rate, 20)

    def test_prometheus_check_writes_deduped_result(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), JsonHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                output = Path(tmpdir) / "results.txt"
                runtime.configure(output=str(output), timeout=1, append=False)
                target = f"127.0.0.1:{server.server_port}"
                additional.prometheus(target)
                additional.prometheus(target)
                lines = output.read_text(encoding="utf-8").splitlines()
                self.assertEqual(len(lines), 1)
                self.assertIn("prometheus", lines[0])
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    unittest.main()
