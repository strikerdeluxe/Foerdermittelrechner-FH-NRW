# Foerdermittel-Rechner

Ein Python-basiertes Tool zur Berechnung und Verteilung von Fördermitteln für Kommunen.

## Features

- **GUI-Version**: Benutzerfreundliche grafische Oberfläche mit Tkinter
- **Excel-Integration**: Import und Export von Excel-Dateien
- **Automatische Berechnung**: Verteilung von Fördermitteln basierend auf verschiedenen Parametern
- **Standalone-Executable**: Fertige EXE-Datei für Windows ohne Python-Installation

## Dateien

- `foerdermittel_gui.py` - Hauptanwendung mit grafischer Benutzeroberfläche
- `foerdermittel_rechner.py` - Ursprüngliche Konsolen-Version
- `rup.xlsx` - Referenzdaten für Berechnungen
- `foerdermittel_beispiel.xlsx` - Beispieldaten
- `dist/Foerdermittel-Rechner.exe` - Fertige Windows-Executable

## Installation

### Für Entwickler
```bash
# Repository klonen
git clone <repository-url>
cd föder

# Python-Abhängigkeiten installieren
pip install pandas openpyxl tkinter

# GUI-Version starten
python foerdermittel_gui.py
```

### Für Endbenutzer
Einfach die `Foerdermittel-Rechner.exe` aus dem `dist/` Ordner herunterladen und ausführen.

## Verwendung

1. Starten Sie die Anwendung
2. Laden Sie Ihre Excel-Datei mit den Kommunendaten
3. Geben Sie die gewünschten Parameter ein
4. Klicken Sie auf "Berechnung starten"
5. Exportieren Sie die Ergebnisse als Excel-Datei

## Build

Um eine neue EXE-Datei zu erstellen:
```bash
pyinstaller --onefile --windowed --name="Foerdermittel-Rechner" foerdermittel_gui.py
```

## Lizenz und rechtliche Hinweise

### Projektlizenz
MIT License - siehe [LICENSE.md](LICENSE.md) für Details.

### Open-Source-Komponenten
Dieses Projekt verwendet verschiedene Open-Source-Bibliotheken. Detaillierte Informationen zu allen verwendeten Komponenten, deren Lizenzen und Copyright-Hinweisen finden Sie in:

- **[LICENSE.md](LICENSE.md)** - Vollständige Lizenz- und Rechtsinformationen
- **[THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md)** - Detaillierte Drittanbieter-Hinweise

### Wichtige Hinweise
- ⚖️ **Haftungsausschluss:** Diese Software dient nur zu Informationszwecken
- 📋 **Keine Rechtsberatung:** Berechnungen ersetzen keine professionelle Beratung
- ✅ **Compliance:** Alle Open-Source-Lizenzen werden eingehalten
- 🔍 **Überprüfung:** Ergebnisse sollten stets von Fachexperten validiert werden