@echo off
title Foerdermittel-Verteilungsrechner
color 0A
cls

echo ========================================
echo    FOERDERMITTEL-VERTEILUNGSRECHNER
echo ========================================
echo.

REM Prüfe ob Python installiert ist
python --version >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] Python ist nicht installiert oder nicht im PATH!
    echo.
    echo Bitte installieren Sie Python von https://python.org
    echo Wichtig: Haken bei "Add Python to PATH" setzen!
    echo.
    pause
    exit /b 1
)

echo [OK] Python ist installiert
echo.

REM Prüfe und installiere benötigte Pakete
echo Pruefe benoetigte Pakete...
echo.

pip show pandas >nul 2>&1
if errorlevel 1 (
    echo Installiere pandas...
    pip install pandas
)

pip show openpyxl >nul 2>&1
if errorlevel 1 (
    echo Installiere openpyxl...
    pip install openpyxl
)

pip show numpy >nul 2>&1
if errorlevel 1 (
    echo Installiere numpy...
    pip install numpy
)

echo.
echo [OK] Alle Pakete sind installiert
echo.
echo ========================================
echo.

REM Prüfe ob Python-Datei existiert
if not exist "foerdermittel_rechner.py" (
    echo [FEHLER] Die Datei 'foerdermittel_rechner.py' wurde nicht gefunden!
    echo.
    echo Bitte stellen Sie sicher, dass sich diese Batch-Datei
    echo im gleichen Ordner wie 'foerdermittel_rechner.py' befindet.
    echo.
    pause
    exit /b 1
)

REM Starte das Python-Programm
echo Starte Foerdermittel-Rechner...
echo.
echo ========================================
echo.

python foerdermittel_rechner.py

echo.
echo ========================================
echo.
echo Programm beendet.
echo.
pause