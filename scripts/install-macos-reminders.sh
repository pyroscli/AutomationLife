#!/bin/zsh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON="${PYTHON:-/usr/bin/python3}"
LABEL_PREFIX="com.dailyautomation"

mkdir -p "$HOME/Library/LaunchAgents"

install_job() {
  local name="$1"
  local hour="$2"
  local minute="$3"
  local kind="$4"
  local label="${LABEL_PREFIX}.${name}"
  local plist="$HOME/Library/LaunchAgents/${label}.plist"

  cat > "$plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${label}</string>
  <key>WorkingDirectory</key>
  <string>${ROOT}</string>
  <key>ProgramArguments</key>
  <array>
    <string>${PYTHON}</string>
    <string>-m</string>
    <string>daily</string>
    <string>remind</string>
    <string>${kind}</string>
    <string>--send</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>
    <integer>${hour}</integer>
    <key>Minute</key>
    <integer>${minute}</integer>
  </dict>
  <key>StandardOutPath</key>
  <string>${ROOT}/data/${name}.log</string>
  <key>StandardErrorPath</key>
  <string>${ROOT}/data/${name}.err.log</string>
</dict>
</plist>
EOF

  launchctl bootout "gui/$(id -u)/${label}" >/dev/null 2>&1 || true
  launchctl bootstrap "gui/$(id -u)" "$plist"
  echo "Installed ${label} at ${hour}:$(printf '%02d' "$minute")"
}

install_job morning 8 0 morning
install_job night 21 0 night
echo "macOS reminders installed. Your Mac must be awake at those times."
