#!/bin/bash
# Bascule entre le curseur normal et le curseur "point rouge" (type laser)
STATE_FILE="/tmp/laser-cursor-active"
NORMAL_THEME="Dracula-cursors"
NORMAL_SIZE="25"
LASER_THEME="RedDot"
LASER_SIZE="25"
LASER_INACTIVE_TIMEOUT="0.6" # secondes avant disparition du curseur en mode laser

if [[ -f "$STATE_FILE" ]]; then
    hyprctl setcursor "$NORMAL_THEME" "$NORMAL_SIZE"
    hyprctl keyword cursor:inactive_timeout 0
    rm -f "$STATE_FILE"
else
    hyprctl setcursor "$LASER_THEME" "$LASER_SIZE"
    hyprctl keyword cursor:inactive_timeout "$LASER_INACTIVE_TIMEOUT"
    touch "$STATE_FILE"
fi
