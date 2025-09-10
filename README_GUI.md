# Fördermittel-Verteilungsrechner GUI

Eine benutzerfreundliche grafische Oberfläche für die Berechnung und Verteilung von Fördermitteln an Kommunen.

## 🚀 Schnellstart

### Starten der Anwendung

**Option 1: Über Batch-Datei (empfohlen)**
```
Doppelklick auf: start_gui.bat
```

**Option 2: Über Kommandozeile**
```bash
python foerdermittel_gui.py
```

## 📋 Funktionsübersicht

### 🎯 Hauptfunktionen

- **Intuitive Benutzeroberfläche** mit modernem Design
- **Parameter-Eingabe** für Gesamtsumme, Mindestbetrag und Sockelbetrag
- **Kommunen-Verwaltung** mit Tabelle und CRUD-Funktionen
- **Excel-Import/Export** für einfache Datenübertragung
- **Automatische Berechnung** mit Fortschrittsanzeige
- **Detaillierte Ergebnisanzeige** mit Exportfunktionen
- **Responsive Layout** für verschiedene Bildschirmgrößen

### 🔧 Tastenkürzel

| Tastenkombination | Funktion |
|-------------------|----------|
| `Strg + N` | Neue Kommune hinzufügen |
| `Strg + S` | Excel-Export |
| `Strg + O` | Excel-Import |
| `F5` | Berechnung starten |
| `Entf` | Ausgewählte Kommune löschen |

## 📊 Bedienungsanleitung

### 1. Parameter eingeben (Tab: 📊 Eingabe)

#### Grundparameter
- **Gesamtsumme (€)**: Die zu verteilende Gesamtfördersumme
- **Mindestbetrag (€)**: Mindestbetrag pro Kommune (Standard: 12.500 €)
- **Sockelbetrag (%)**: Prozentsatz des Werts 2019 als Sockelbetrag (Standard: 50%)

### 2. Kommunen verwalten

#### Kommunen hinzufügen
1. **Name**: Name der Kommune eingeben
2. **Wert 2019 (€)**: Förderwert aus dem Jahr 2019
3. **Kinder U3**: Anzahl der Kinder U3 im SGB-II-Bezug
4. Klick auf **➕ Hinzufügen**

#### Kommunen bearbeiten
- **Doppelklick** auf Tabellenzeile oder **✏️ Bearbeiten**-Button
- Werte werden in Eingabefelder geladen
- Nach Änderung erneut **➕ Hinzufügen** klicken

#### Kommunen löschen
- Kommune in Tabelle auswählen
- **🗑️ Löschen**-Button oder **Entf**-Taste

### 3. Daten importieren/exportieren

#### Excel-Import
1. **📁 Excel Import** klicken
2. Excel-Datei auswählen
3. Daten werden automatisch erkannt und importiert

#### Vorlage erstellen
1. **💾 Vorlage erstellen** klicken
2. Speicherort wählen
3. Excel-Vorlage wird erstellt zum Ausfüllen

**Erwartetes Excel-Format:**
| Kommune | Wert 2019 (€) | Kinder U3 im SGB-II-Bezug |
|---------|----------------|----------------------------|
| Stadt A | 50000 | 120 |
| Stadt B | 35000 | 85 |

### 4. Berechnung durchführen (Tab: ⚙️ Berechnung)

1. **🚀 Berechnung starten** klicken
2. Fortschrittsbalken zeigt laufende Berechnung
3. **Berechnungsprotokoll** zeigt Details der iterativen Berechnung
4. Bei Abschluss automatischer Wechsel zu Ergebnissen

### 5. Ergebnisse anzeigen (Tab: 📊 Ergebnisse)

#### Übersicht
- **Gesamtsumme verteilt**: Kontrollsumme der Verteilung
- **Anzahl Kommunen**: Anzahl berücksichtigter Kommunen
- **Durchschnitt pro Kommune**: Durchschnittliche Fördersumme
- **Mindestbetrag**: Verwendeter Mindestbetrag

#### Detailtabelle
Zeigt für jede Kommune:
- **Kommune**: Name
- **Wert 2019**: Ursprünglicher Förderwert
- **Kinder U3**: Anzahl Kinder U3 im SGB-II-Bezug
- **Sockelbetrag**: Berechneter Sockelbetrag (50% von Wert 2019)
- **U3-Anteil**: Anteil basierend auf Kinder U3
- **Zwischensumme**: Sockelbetrag + U3-Anteil
- **Endbetrag**: Finaler Förderbetrag (gerundet)
- **Status**: Berechnungsstatus (OK, Mindestbetrag, etc.)

#### Export-Optionen
- **💾 Excel Export**: Vollständiger Export als formatierte Excel-Datei
- **📋 In Zwischenablage**: Kopiert Ergebnisse als Text

## 🔄 Berechnungslogik

### Iterative Verteilung

1. **Sockelbetrag-Berechnung**: 50% des Werts 2019 pro Kommune
2. **Restbudget-Verteilung**: Verbleibendes Budget nach U3-Kindern
3. **Mindestbetrag-Prüfung**: Kommunen unter Mindestbetrag werden fixiert
4. **Iteration**: Wiederholung bis alle Kommunen den Mindestbetrag erreichen
5. **Rundung**: Finale Beträge auf ganze Euro gerundet
6. **Ausgleich**: Rundungsdifferenz bei Kommune mit höchstem Betrag

### Beispiel-Berechnung

**Ausgangsdaten:**
- Gesamtsumme: 500.000 €
- Mindestbetrag: 12.500 €
- Sockelbetrag: 50%

**Kommune A:**
- Wert 2019: 50.000 € → Sockelbetrag: 25.000 €
- Kinder U3: 120
- U3-Anteil: 120 × Multiplikator
- Endbetrag: Sockelbetrag + U3-Anteil (mind. 12.500 €)

## 🛠️ Technische Anforderungen

### Systemvoraussetzungen
- **Python 3.7+** (empfohlen: Python 3.9+)
- **Windows 10/11** (getestet)

### Python-Bibliotheken
```
pandas>=1.3.0
numpy>=1.21.0
openpyxl>=3.0.9
tkinter (meist vorinstalliert)
```

### Installation der Abhängigkeiten
```bash
pip install pandas numpy openpyxl
```

## 📁 Dateistruktur

```
föder/
├── foerdermittel_rechner.py    # Berechnungslogik (Konsole)
├── foerdermittel_gui.py        # GUI-Anwendung
├── start_gui.bat               # Starter-Batch-Datei
├── README_GUI.md               # Diese Anleitung
└── backup/                     # Backup-Ordner
```

## 🎨 Design-Features

### Moderne Benutzeroberfläche
- **Konsistente Farbgebung** mit professionellem Erscheinungsbild
- **Intuitive Icons** für bessere Orientierung
- **Responsive Layout** passt sich Fenstergröße an
- **Klare Strukturierung** durch Tabs und Karten-Design

### Accessibility-Features
- **Tastaturnavigation** vollständig unterstützt
- **Klare Kontraste** für bessere Lesbarkeit
- **Logische Tab-Reihenfolge** für Screenreader
- **Aussagekräftige Labels** und Tooltips

## 🔍 Fehlerbehebung

### Häufige Probleme

**Problem: "Python wurde nicht gefunden"**
- Lösung: Python installieren von [python.org](https://python.org)
- Sicherstellen, dass Python zum PATH hinzugefügt wurde

**Problem: "Modul 'pandas' nicht gefunden"**
- Lösung: `pip install pandas numpy openpyxl` ausführen

**Problem: GUI startet nicht**
- Lösung: Kommandozeile öffnen und `python foerdermittel_gui.py` ausführen
- Fehlermeldungen beachten und entsprechende Module installieren

**Problem: Excel-Import funktioniert nicht**
- Lösung: Sicherstellen, dass Excel-Datei das korrekte Format hat
- Spalten müssen "Kommune", "Wert 2019 (€)", "Kinder U3 im SGB-II-Bezug" heißen

### Debug-Modus

Für detaillierte Fehlermeldungen:
```bash
python -u foerdermittel_gui.py
```

## 📞 Support

Bei Problemen oder Fragen:
1. README sorgfältig lesen
2. Fehlermeldungen dokumentieren
3. Python- und Bibliotheksversionen prüfen
4. Beispieldaten zum Testen verwenden

## 🔄 Updates und Erweiterungen

### Geplante Features
- **Datenbank-Anbindung** für persistente Speicherung
- **Erweiterte Visualisierungen** mit Diagrammen
- **Batch-Verarbeitung** für mehrere Szenarien
- **PDF-Export** der Ergebnisse

### Anpassungen

Die Anwendung kann einfach erweitert werden:
- **Parameter ändern**: In `foerdermittel_rechner.py`
- **GUI anpassen**: In `foerdermittel_gui.py`
- **Neue Features**: Modulare Struktur ermöglicht einfache Erweiterungen

---

**Version**: 1.0  
**Erstellt**: 2024  
**Lizenz**: Für interne Nutzung  

*Diese GUI-Anwendung basiert auf der bewährten Berechnungslogik des ursprünglichen Konsolen-Rechners und erweitert diese um eine moderne, benutzerfreundliche Oberfläche.*