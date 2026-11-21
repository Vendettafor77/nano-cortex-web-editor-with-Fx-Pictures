#!/bin/bash
set -euo pipefail
root=$(cd -- "$(dirname -- "$0")/.." && pwd -P)
app=${1:-"$root/build/Nano Cortex Editor.app"}
if [[ -e "$app" ]]; then
  printf 'Output already exists: %s\n' "$app" >&2
  exit 1
fi
mkdir -p "$(dirname "$app")"
/usr/bin/osacompile -s -o "$app" "$root/mac-app/main.applescript"
resources="$app/Contents/Resources"
mkdir -p "$resources/web"
cp "$root/Index V3.0.html" "$root/LICENSE" "$root/mac-app/LICENSE.nanos-upstream" "$resources/web/"
/usr/bin/ditto "$root/img" "$resources/web/img"
/usr/bin/ditto "$root/fonts" "$resources/web/fonts"
cp "$root/mac-app/"{activate.sh,editor_session.py,main.applescript} "$resources/Scripts/"
cp "$root/mac-app/applet.icns" "$resources/applet.icns"
/usr/bin/plutil -replace CFBundleIdentifier -string com.local.nanocortexeditor "$app/Contents/Info.plist"
/usr/bin/codesign --force --sign - "$app"
/usr/bin/codesign --verify --deep --strict "$app"
printf '%s\n' "$app"
