#!/usr/bin/env python3
import http.server
import socketserver
import subprocess
import urllib.parse
import urllib.request
import json
import hashlib
import os

PORT = 20129
WEB_DIR = "/home/pckien/diy-gear-shifter/web_ui"
MAPPINGS_FILE = "/home/pckien/diy-gear-shifter/app_data/gear_mappings.json"
MODELS_FILE = "/home/pckien/diy-gear-shifter/app_data/models.json"

def get_auth_token():
    try:
        mid = open(os.path.expanduser("~/.9router/machine-id")).read().strip()
        cs = open(os.path.expanduser("~/.9router/auth/cli-secret")).read().strip()
        return hashlib.sha256(f"{mid}9r-cli-auth{cs}".encode()).hexdigest()[:16]
    except Exception:
        return ""

def update_codex_combo(model_name):
    token = get_auth_token()
    # Find combo id
    req = urllib.request.Request("http://127.0.0.1:20128/api/combos", headers={"x-9r-cli-token": token})
    try:
        with urllib.request.urlopen(req) as resp:
            combos = json.loads(resp.read().decode())["combos"]
            c = next((x for x in combos if x["name"] == "codex"), None)
            if not c:
                return False
            combo_id = c["id"]
        
        data = json.dumps({"name": "codex", "models": [model_name]}).encode()
        put_req = urllib.request.Request(
            f"http://127.0.0.1:20128/api/combos/{combo_id}",
            data=data,
            headers={"x-9r-cli-token": token, "Content-Type": "application/json"},
            method="PUT"
        )
        with urllib.request.urlopen(put_req) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"Error updating combo: {e}")
        return False

class ShifterHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/shift":
            qs = urllib.parse.parse_qs(parsed.query)
            gear = qs.get("gear", [""])[0]
            if gear:
                # Load current mappings
                try:
                    with open(MAPPINGS_FILE) as f:
                        mappings = json.load(f)
                    target_model = mappings.get(str(gear), {}).get("model")
                    if target_model:
                        update_codex_combo(target_model)
                        try:
                            subprocess.run(["notify-send", "Codex Shifter", f"Đã gài Gear {gear} ➔ {target_model}"], check=False)
                        except Exception:
                            pass
                except Exception as e:
                    print(f"Shift error: {e}")

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"status":"ok"}')
                return

        elif parsed.path == "/api/models":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            if os.path.exists(MODELS_FILE):
                with open(MODELS_FILE, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.wfile.write(b'[]')
            return

        elif parsed.path == "/api/gear_mappings":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            if os.path.exists(MAPPINGS_FILE):
                with open(MAPPINGS_FILE, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.wfile.write(b'{}')
            return

        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/gear_mappings":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body.decode())
                with open(MAPPINGS_FILE, "w") as f:
                    json.dump(data, f, indent=2)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"status":"saved"}')
                return
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())
                return

        self.send_response(404)
        self.end_headers()

def run_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), ShifterHandler) as httpd:
        print(f"Stick Shift backend running on http://127.0.0.1:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()
