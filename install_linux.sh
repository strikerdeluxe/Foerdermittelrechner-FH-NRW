#!/usr/bin/env bash
# Richtet den Fördermittel-Rechner unter Linux ein:
#   1. prüft die nötigen Systempakete
#   2. legt die Python-Umgebung an (über start.sh --setup)
#   3. trägt die App ins Anwendungsmenü ein
#
#   ./install_linux.sh              einrichten (kann jederzeit wiederholt werden)
#   ./install_linux.sh --entfernen  Menüeintrag wieder entfernen
set -euo pipefail

APP_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"
DESKTOP_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
DESKTOP_FILE="$DESKTOP_DIR/foerdermittelrechner.desktop"

if [ "${1:-}" = "--entfernen" ]; then
    rm -f "$DESKTOP_FILE"
    update-desktop-database "$DESKTOP_DIR" >/dev/null 2>&1 || true
    echo "Menüeintrag entfernt. (Der Projektordner bleibt unverändert.)"
    exit 0
fi

# 1. Systempakete prüfen und alle fehlenden auf einmal nennen
PYTHON="${PYTHON:-python3}"
fehlend=()
if command -v "$PYTHON" >/dev/null 2>&1; then
    "$PYTHON" -c "import tkinter" 2>/dev/null || fehlend+=(python3-tk)
    "$PYTHON" -c "import ensurepip" 2>/dev/null || fehlend+=(python3-venv)
else
    fehlend+=(python3 python3-tk python3-venv)
fi
if [ ${#fehlend[@]} -gt 0 ]; then
    echo "Es fehlen noch Systempakete. Bitte zuerst ausführen:"
    echo
    echo "    sudo apt install ${fehlend[*]}"
    echo
    echo "Danach dieses Skript erneut starten."
    exit 1
fi

# 2. Python-Umgebung
"$APP_DIR/start.sh" --setup

# 3. Eintrag im Anwendungsmenü
mkdir -p "$DESKTOP_DIR"
cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=Fördermittel-Rechner
Comment=Fördermittel nach Sockelbetrag und U3-Kindern auf Kommunen verteilen
Exec="$APP_DIR/start.sh"
Path=$APP_DIR
Icon=$APP_DIR/assets/icon.png
Terminal=false
Categories=Office;Finance;
Keywords=Fördermittel;Kommunen;Verteilung;Frühe Hilfen;
StartupWMClass=Foerdermittelrechner
EOF
update-desktop-database "$DESKTOP_DIR" >/dev/null 2>&1 || true

echo
echo "Fertig! Der Fördermittel-Rechner steht jetzt im Anwendungsmenü."
echo "Alternativ im Terminal starten mit:  $APP_DIR/start.sh"
