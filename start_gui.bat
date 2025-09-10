@echo off
echo Starte Fördermittel-Rechner GUI...
echo.
python foerdermittel_gui.py
if %errorlevel% neq 0 (
    echo.
    echo Fehler beim Starten der Anwendung!
    echo Bitte stellen Sie sicher, dass Python installiert ist.
    echo.
    pause
)