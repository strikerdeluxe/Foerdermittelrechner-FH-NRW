#!/usr/bin/env bash
# Startet den Fördermittel-Rechner unter Linux.
#
#   ./start.sh            GUI starten
#   ./start.sh --konsole  Konsolen-Version starten
#   ./start.sh --setup    nur die Python-Umgebung einrichten bzw. aktualisieren
#
# Beim ersten Start wird im Projektordner eine virtuelle Python-Umgebung (.venv)
# angelegt und mit den Paketen aus requirements.txt gefüllt. Das dauert einmalig
# etwa eine Minute; danach startet die App sofort.
set -euo pipefail

cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"

PYTHON="${PYTHON:-python3}"
VENV=".venv"
STAMP="$VENV/.requirements-installiert"

fehler() {
    echo "[FEHLER] $*" >&2
    # Beim Start über das Anwendungsmenü gibt es kein Terminal – Hinweis als Benachrichtigung
    if [ ! -t 2 ] && command -v notify-send >/dev/null 2>&1; then
        notify-send "Fördermittel-Rechner" "$*" 2>/dev/null || true
    fi
    exit 1
}

command -v "$PYTHON" >/dev/null 2>&1 \
    || fehler "python3 nicht gefunden. Installieren mit: sudo apt install python3"
"$PYTHON" -c "import tkinter" 2>/dev/null \
    || fehler "Tkinter fehlt. Installieren mit: sudo apt install python3-tk"

# Virtuelle Umgebung anlegen – oder neu anlegen, wenn sie unvollständig ist
# (z. B. nach einem abgebrochenen ersten Start oder einem Python-Update)
if ! "$VENV/bin/python" -m pip --version >/dev/null 2>&1; then
    echo "Richte die Python-Umgebung ein (einmalig) ..."
    rm -rf "$VENV"
    if ! "$PYTHON" -m venv "$VENV" >/dev/null 2>&1; then
        rm -rf "$VENV"
        fehler "Python-venv fehlt. Installieren mit: sudo apt install python3-venv"
    fi
fi

# Pakete installieren, wenn requirements.txt neu ist oder sich geändert hat
if [ ! -f "$STAMP" ] || [ requirements.txt -nt "$STAMP" ]; then
    echo "Installiere die Python-Pakete (pandas, numpy, openpyxl) ..."
    "$VENV/bin/python" -m pip install --disable-pip-version-check -q -r requirements.txt \
        || fehler "Installation der Python-Pakete fehlgeschlagen (Internetverbindung prüfen)"
    touch "$STAMP"
fi

case "${1:-}" in
    --setup)   echo "Python-Umgebung ist eingerichtet." ;;
    --konsole) exec "$VENV/bin/python" foerdermittel_rechner.py ;;
    *)         exec "$VENV/bin/python" foerdermittel_gui.py ;;
esac
