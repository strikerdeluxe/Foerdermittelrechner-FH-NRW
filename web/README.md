# Fördermittel-Verteilungsrechner – Web-Version

**Direkt nutzen:** https://strikerdeluxe.github.io/Foerdermittelrechner-FH-NRW/ (passwortgeschützt)

Die Web-Version ist eine einzelne HTML-Datei, die vollständig im Browser läuft. Es gibt keinen Server,
eingegebene Daten werden nicht übertragen. Eingaben bleiben nur im Speicher des jeweiligen Browsers
erhalten, damit sie nach dem Neuladen noch da sind.

## Passwortschutz

Auf GitHub Pages liegt die Anwendung verschlüsselt (AES-256-GCM, Schlüssel per PBKDF2-SHA-256 mit
600.000 Durchläufen aus dem Passwort abgeleitet). Ohne Passwort lässt sich die Seite nicht lesen.
Das Passwort selbst steht weder in der Datei noch im Repository.

- Alle Nutzer verwenden dasselbe Passwort. Wer es nicht mehr haben soll, verliert den Zugang nur durch ein neues Passwort.
- Die verschlüsselte Datei ist öffentlich abrufbar; ein Passwort lässt sich offline durchprobieren. Darum ein langes, nicht naheliegendes Passwort wählen.
- Der Quellcode in diesem Repository ist weiterhin öffentlich. Der Schutz regelt den Zugang zur gehosteten Seite, nicht zum Code.
- „Auf diesem Gerät angemeldet bleiben“ speichert den abgeleiteten Schlüssel im Browser. Im Rechner erscheint dann unten „Auf diesem Gerät abmelden“.

## Funktionen

- Parameter: Gesamtsumme, Mindestbetrag je Kommune, Sockelbetrag in Prozent
- Kommunen eintragen, bearbeiten und löschen (mit Rückgängig)
- Excel-Import (.xlsx) per Auswahl oder Drag & Drop, Import-Vorlage zum Herunterladen
- Ergebnis mit Übersicht, Verteilungsbalken je Kommune und Berechnungsprotokoll je Runde
- Excel-Export im Aufbau der Desktop-Version, Ergebnis als Text in die Zwischenablage

## Gleiche Ergebnisse wie die Desktop-Version

Der Rechenkern ist eine 1:1-Übertragung von `foerdermittel_rechner.py`. Auch die Summation
(paarweise wie in NumPy/pandas) und die Rundung (bei genau 50 Cent zur geraden Zahl) sind nachgebildet.
Dadurch liefert die Web-Version bei gleichen Eingaben bitgenau dieselben Beträge.
Das prüft `npm test`: 38 Fälle (Beispieldaten, Grenzfälle, Zufallsdaten mit bis zu 396 Kommunen) werden
mit dem Python-Original gerechnet und mit der Web-Version verglichen.

Unterschiede zur Desktop-Version:

- Zahlen werden im deutschen Format eingegeben und angezeigt (`500.000` = fünfhunderttausend).
- Im Status „Wert aus Runde 1 (…)“ steht der Betrag im deutschen Format.
- Zusätzliche Hinweise, z. B. wenn die Gesamtsumme nicht für alle Mindestbeträge reicht. Sie ändern keine Beträge.
- Die Import-Kopfzeile wird in den ersten 40 Zeilen gesucht. Daher lassen sich auch exportierte Ergebnisdateien wieder einlesen.

## Dateien

| Datei | Inhalt |
|---|---|
| `index.html` | Quelle der Anwendung (lädt ExcelJS und Schriften beim Öffnen aus dem Netz) |
| `build.mjs` | baut `dist/foerdermittelrechner.html` mit eingebettetem ExcelJS und eingebetteten Schriften; mit `FMR_PASSWORT` zusätzlich die verschlüsselte Fassung |
| `gate.html` | Passwortabfrage, in die `build.mjs` die verschlüsselte Anwendung einsetzt |
| `test/reference.py` | rechnet die Testfälle mit `foerdermittel_rechner.py` |
| `test/compare.mjs` | vergleicht die Web-Version bitgenau mit den Python-Ergebnissen |

## Bauen, prüfen, veröffentlichen

Voraussetzungen: Node.js 18 oder neuer und Python mit den Paketen aus `requirements.txt`.

```bash
cd web
npm ci            # ExcelJS und Schriften (nur für den Build)
npm test          # Vergleich mit der Python-Version
npm run build     # erzeugt dist/foerdermittelrechner.html (ohne Passwort)
```

Die Seite auf GitHub Pages kommt aus dem Branch `gh-pages` (Datei `index.html`). So wird eine neue Version
veröffentlicht, auch um das Passwort zu ändern. Das Leerzeichen am Zeilenanfang hält das Passwort in den
meisten Shells aus dem Verlauf heraus:

```bash
cd web && npm ci
 FMR_PASSWORT='neues Passwort' npm run build    # erzeugt zusätzlich dist/foerdermittelrechner-geschuetzt.html
cd ..
git switch gh-pages
cp web/dist/foerdermittelrechner-geschuetzt.html index.html
git add index.html
git commit -m "feat(web): update web version"
git push
git switch main
```

## Lizenzen

Anwendung: MIT-Lizenz (siehe `LICENSE.md`). Eingebettet in die gebaute Datei:
ExcelJS 4.4.0 (MIT-Lizenz), IBM Plex Sans und IBM Plex Mono sowie Source Serif 4 (SIL Open Font License 1.1).
