#!/bin/bash
SCRIPT_DIR=$(cd -- "$(dirname -- "$0")" && pwd -P) || exit 1
WEB_DIR=$(cd -- "$SCRIPT_DIR/../web" && pwd -P) || exit 1
PROFILE_DIR="$HOME/.NanoCortexChromeProfile"
CHROME_APP="/Applications/Google Chrome.app"

PYTHON=$(command -v python3) || exit 1
for candidate in /opt/homebrew/bin/python3 /usr/local/bin/python3; do
  if [ -x "$candidate" ]; then PYTHON="$candidate"; break; fi
done
if [ "$#" -gt 0 ]; then
  exec "$PYTHON" "$SCRIPT_DIR/editor_session.py" "$1" "$WEB_DIR" "$PROFILE_DIR" "$CHROME_APP"
fi

if [ ! -d "$CHROME_APP" ]; then
  echo "Google Chrome is required at $CHROME_APP." >&2
  exit 1
fi

EDITOR_SHA=$(/usr/bin/shasum -a 256 "$WEB_DIR/Index V3.0.html") || exit 1
EDITOR_URL="http://127.0.0.1:8765/Index%20V3.0.html?v=${EDITOR_SHA%% *}"

if ! /usr/sbin/lsof -tiTCP:8765 -sTCP:LISTEN >/dev/null 2>&1; then
  "$PYTHON" -m http.server 8765 --bind 127.0.0.1 --directory "$WEB_DIR" </dev/null >/dev/null 2>&1 &
fi
for i in {1..15}; do
  /usr/bin/curl --noproxy '*' -fsSI --max-time 0.5 "$EDITOR_URL" >/dev/null 2>&1 && break
  sleep 0.2
done
if ! /usr/bin/curl --noproxy '*' -fsSI --max-time 1 "$EDITOR_URL" >/dev/null 2>&1; then
  echo "The local editor page could not be served on port 8765." >&2
  exit 1
fi

if ! "$PYTHON" "$SCRIPT_DIR/editor_session.py" --status; then
  /usr/bin/open -na "$CHROME_APP" --args \
    --user-data-dir="$PROFILE_DIR" \
    --no-first-run \
    --no-default-browser-check \
    --disable-breakpad \
    --disable-sync \
    --disable-background-mode \
    --disable-background-networking \
    --enable-features=WebBluetoothNewPermissionsBackend \
    --remote-debugging-port=8766 \
    --app="$EDITOR_URL" || exit 1
  for i in {1..20}; do
    sleep 0.2
    "$PYTHON" "$SCRIPT_DIR/editor_session.py" --status && break
  done
fi

# Raise the dedicated editor window on Dock reopen.
if "$PYTHON" "$SCRIPT_DIR/editor_session.py" --status; then
  PID=$(/usr/sbin/lsof -tiTCP:8766 -sTCP:LISTEN | head -n 1)
  if [[ "$PID" =~ ^[0-9]+$ ]]; then
    /usr/bin/osascript -l JavaScript -e "ObjC.import('AppKit'); var app = $.NSRunningApplication.runningApplicationWithProcessIdentifier($PID); if (app) app.activateWithOptions(3);" >/dev/null 2>&1 || true
  fi
fi
