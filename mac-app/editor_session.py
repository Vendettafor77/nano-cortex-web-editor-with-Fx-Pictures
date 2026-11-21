"""Manage only this editor's Chrome pages and its local HTTP server."""

import json
import os
import re
import signal
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import build_opener, ProxyHandler

DEBUG_URL = "http://127.0.0.1:8766"
EDITOR_URL = re.compile(r"http://127\.0\.0\.1:8765/Index%20V3\.0\.html(?:\?v=[0-9a-f]{64})?")
OPENER = build_opener(ProxyHandler({}))


def chrome_targets():
    with OPENER.open(DEBUG_URL + "/json/list", timeout=0.5) as response:
        targets = json.load(response)
    if not isinstance(targets, list) or not all(isinstance(t, dict) for t in targets):
        raise ValueError("Invalid Chrome target list")
    return targets


def editor_targets(targets):
    return [
        target["id"] for target in targets
        if target.get("type") == "page"
        and EDITOR_URL.fullmatch(target.get("url", ""))
        and re.fullmatch(r"[A-Z0-9]+", target.get("id", ""), re.IGNORECASE)
    ]


def listener_pids(port):
    listeners = subprocess.run(
        ["/usr/sbin/lsof", f"-tiTCP:{port}", "-sTCP:LISTEN"],
        capture_output=True, text=True, check=False,
    )
    return {pid for pid in listeners.stdout.split() if pid.isdecimal()}


def process_command(pid):
    return subprocess.run(
        ["/bin/ps", "-ww", "-p", pid, "-o", "command="],
        capture_output=True, text=True, check=False,
    ).stdout.strip()


def dedicated_chrome_pid(profile_dir, chrome_app):
    pids = listener_pids(8766)
    if len(pids) != 1:
        return None
    pid = next(iter(pids))
    command = process_command(pid)
    browser = f"{chrome_app}/Contents/MacOS/Google Chrome"
    if not command.startswith(browser + " "):
        return None
    args = command[len(browser):]
    profile = re.escape(f"--user-data-dir={profile_dir}")
    if re.search(rf"(?:^|\s){profile}(?:\s|$)", args) and re.search(
        r"(?:^|\s)--remote-debugging-port=8766(?:\s|$)", args
    ):
        return pid
    return None


def close_editor_chrome(profile_dir, chrome_app):
    pid = dedicated_chrome_pid(profile_dir, chrome_app)
    if not pid:
        return
    try:
        for target in editor_targets(chrome_targets()):
            with OPENER.open(DEBUG_URL + "/json/close/" + target, timeout=1):
                pass
        # Chrome acknowledges /json/close before the tab has actually gone.
        for _ in range(5):
            remaining = chrome_targets()
            if not editor_targets(remaining):
                break
            time.sleep(0.1)
    except (OSError, URLError, ValueError, TypeError, AttributeError, KeyError):
        return

    # Leave the profile open if it holds any other tab or a Chrome app window.
    if any(t.get("type") in ("page", "tab", "webview", "other") for t in remaining):
        return
    if dedicated_chrome_pid(profile_dir, chrome_app) != pid:
        return
    subprocess.run(
        ["/usr/bin/osascript", "-l", "JavaScript", "-e",
         "ObjC.import('AppKit'); "
         f"var browser = $.NSRunningApplication.runningApplicationWithProcessIdentifier({int(pid)}); "
         "if (browser) browser.terminate;"],
        capture_output=True, check=False,
    )


def stop_http_server(web_dir):
    server_args = f" -m http.server 8765 --bind 127.0.0.1 --directory {web_dir}"
    for pid in listener_pids(8765):
        command = process_command(pid)
        if command.endswith(server_args):
            try:
                os.kill(int(pid), signal.SIGTERM)
            except ProcessLookupError:
                pass


def main():
    mode = sys.argv[1]
    if mode == "--status":
        try:
            return 0 if editor_targets(chrome_targets()) else 1
        except (OSError, URLError, ValueError, TypeError, AttributeError, KeyError):
            return 1
    if mode == "--quit":
        close_editor_chrome(sys.argv[3], sys.argv[4])
        stop_http_server(sys.argv[2])
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
