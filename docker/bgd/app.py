#!/usr/bin/env python3
"""
bgd-lite: remplaçant minimal de l'app BGD.

Objectifs (alignés sur les manifests publics) :
- écouter sur PORT (défaut 8080)
- répondre sur "/" avec une UI simple dont la couleur dépend de COLOR
- exposer "/healthz" pour probes
- loguer sur stdout (console) pour un rendu "container-friendly"

Modification points (optimisation UI) :
- COLOR: couleur CSS (ex: blue, green, #00ff00, rgb(...))
- BALL_COUNT, BALL_SIZE, SPEED: animation
- TITLE, MESSAGE, BACKGROUND: texte & thème
"""

from __future__ import annotations

import json
import os
import socket
import sys
from datetime import datetime, timezone
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse


def env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, str(default)))
    except ValueError:
        return default


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def pod_ip() -> str:
    explicit = os.environ.get("POD_IP")
    if explicit:
        return explicit
    try:
        return socket.gethostbyname(socket.gethostname())
    except OSError:
        return "unknown"


def build_html() -> bytes:
    color = os.environ.get("COLOR", "blue")
    background = os.environ.get("BACKGROUND", "#0b0f19")  # dark background

    ball_count = env_int("BALL_COUNT", 3)
    ball_size = env_int("BALL_SIZE", 28)   # px

    hostname = socket.gethostname()
    ip_addr = pod_ip()

    # Defensive escaping to keep output safe if env vars are untrusted.
    color_css = escape(color)
    bg_css = escape(background)

    balls = "\n".join(
        '<span class="ball"></span>'
        for _ in range(max(1, min(ball_count, 12)))
    )

    html = f"""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>bgd-lite</title>
  <style>
    :root {{
      --accent: {color_css};
      --bg: {bg_css};
      --ball-size: {ball_size}px;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: radial-gradient(1200px 600px at 20% 20%, rgba(255,255,255,.06), transparent 60%),
                  radial-gradient(1200px 600px at 80% 80%, rgba(255,255,255,.04), transparent 60%),
                  var(--bg);
      color: rgba(255,255,255,.90);
      font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji", "Segoe UI Emoji";
      display: grid;
      place-items: center;
      min-height: 100vh;
      padding: 24px;
    }}
    .card {{
      width: min(720px, 100%);
      border: 1px solid rgba(255,255,255,.10);
      border-radius: 16px;
      background: rgba(255,255,255,.03);
      box-shadow: 0 20px 60px rgba(0,0,0,.45);
      overflow: hidden;
    }}
    .header {{
      padding: 18px 20px;
      border-bottom: 1px solid rgba(255,255,255,.08);
    }}
    .pod-line {{
      margin: 0;
      font-size: 24px;
      letter-spacing: .2px;
      line-height: 1.2;
    }}
    .panel {{
      padding: 22px 20px 26px;
    }}
    .balls {{
      display: flex;
      gap: 12px;
      align-items: center;
      justify-content: flex-start;
      padding-top: 6px;
    }}
    .ball {{
      width: var(--ball-size);
      height: var(--ball-size);
      border-radius: 999px;
      background: var(--accent);
      filter: drop-shadow(0 10px 18px rgba(0,0,0,.6));
    }}
    .footer {{
      padding: 14px 20px;
      font-size: 12px;
      opacity: .72;
      border-top: 1px solid rgba(255,255,255,.08);
      display: flex;
      justify-content: space-between;
      gap: 12px;
      flex-wrap: wrap;
    }}
    code {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      font-size: 12px;
    }}
  </style>
</head>
<body>
  <div class="card">
    <div class="header">
      <h2 class="pod-line">{escape(hostname)} ({escape(ip_addr)})</h2>
    </div>

    <div class="panel">
      <div class="balls" aria-label="balls">
        {balls}
      </div>
    </div>

    <div class="footer">
      <span>Endpoints: <code>/</code>, <code>/healthz</code>, <code>/api/info</code></span>
      <span>bgd-lite</span>
    </div>
  </div>
</body>
</html>
"""
    return html.encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    server_version = "bgd-lite/1.0"
    sys_version = ""

    def log_message(self, fmt: str, *args) -> None:
        # Log format stable, container-friendly, includes timestamp.
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        sys.stdout.write(f"{ts} {self.client_address[0]} {self.command} {self.path} - " + (fmt % args) + "\n")

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlparse(self.path).path

        if path == "/healthz":
            self._send(200, b"ok\n", "text/plain; charset=utf-8")
            return

        if path == "/api/info":
            info = {
                "app": "bgd-lite",
                "time_utc": now_iso(),
                "hostname": socket.gethostname(),
                "color": os.environ.get("COLOR", "blue"),
                "port": int(os.environ.get("PORT", "8080")),
            }
            self._send(200, json.dumps(info, indent=2).encode("utf-8"), "application/json; charset=utf-8")
            return

        if path in ("/", ""):
            self._send(200, build_html(), "text/html; charset=utf-8")
            return

        self._send(404, b"not found\n", "text/plain; charset=utf-8")


def main() -> int:
    host = "0.0.0.0"
    port = env_int("PORT", 8080)

    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f"{now_iso()} bgd-lite starting on http://{host}:{port} (COLOR={os.environ.get('COLOR','blue')})", flush=True)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"{now_iso()} bgd-lite shutting down", flush=True)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
