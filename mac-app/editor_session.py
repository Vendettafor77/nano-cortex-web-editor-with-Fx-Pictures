"""Manage only this editor's Chrome pages and its local HTTP server."""

import json
import os
import re
import signal
import subprocess
import sys
from urllib.error import URLError
from urllib.request import build_opener, ProxyHandler

DEBUG_URL = "http://127.0.0.1:8766"
EDITOR_URL = re.compile(r"http://127\.0\.0\.1:8765/Index%20V3\.0\.html(?:\?v=[0-9a-f]{64})?")
OPENER = build_opener(ProxyHandler({}))


def editor_targets():
    with OPENER.open(DEBUG_URL + "/json/list", timeout=0.5) as response:
        targets = json.load(response)
    return [
        target["id"] for target in targets
        if target.get("type") == "page"
        and EDITOR_URL.fullmatch(target.get("url", ""))
        and re.fullmatch(r"[A-Z0-9]+", target.get("id", ""), re.IGNORECASE)
    ]


def stop_http_server(web_dir):
    listeners = subprocess.run(
        ["/usr/sbin/lsof", "-tiTCP:8765", "-sTCP:LISTEN"],
        capture_output=True, text=True, check=False,
    )
    server_args = f" -m http.server 8765 --bind 127.0.0.1 --directory {web_dir}"
    for pid in listeners.stdout.split():
        if not pid.isdecimal():
            continue
        command = subprocess.run(
            ["/bin/ps", "-ww", "-p", pid, "-o", "command="],
            capture_output=True, text=True, check=False,
        ).stdout.strip()
        if command.endswith(server_args):
            try:
                os.kill(int(pid), signal.SIGTERM)
            except ProcessLookupError:
                pass


def main():
    mode = sys.argv[1]
    try:
        targets = editor_targets()
    except (URLError, TimeoutError, ValueError, TypeError, AttributeError):
        targets = []

    if mode == "--status":
        return 0 if targets else 1
    if mode == "--quit":
        for target in targets:
            try:
                with OPENER.open(DEBUG_URL + "/json/close/" + target, timeout=1):
                    pass
            except (URLError, TimeoutError):
                pass
        stop_http_server(sys.argv[2])
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
