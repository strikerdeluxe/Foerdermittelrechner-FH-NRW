# Open-Source Compliance Checkliste

Diese Datei dient als Compliance-Leitfaden für die Einhaltung aller Open-Source-Lizenzanforderungen des Foerdermittel-Rechner Projekts.

## 📋 Compliance-Status

### ✅ Erfüllte Anforderungen

#### Lizenzbedingungen
- [x] **MIT License Text** - Vollständig in LICENSE.md enthalten
- [x] **Python Software Foundation License** - Referenziert und verlinkt
- [x] **GPL v2 + Runtime Exception** - Dokumentiert für PyInstaller
- [x] **Alle Lizenztexte verfügbar** - In LICENSE.md und THIRD-PARTY-NOTICES.md

#### Urheberrechtshinweise
- [x] **Projekt Copyright** - Copyright (c) 2024 Foerdermittel-Rechner
- [x] **Python Copyright** - Python Software Foundation Hinweise
- [x] **OpenPyXL Copyright** - Copyright (c) 2010 openpyxl
- [x] **PyInstaller Copyright** - PyInstaller Development Team Hinweise
- [x] **Alle Copyright-Hinweise beibehalten** - In allen relevanten Dateien

#### Haftungsausschlüsse
- [x] **Allgemeiner Haftungsausschluss** - MIT License Disclaimer
- [x] **Software "AS IS" Klausel** - In LICENSE.md enthalten
- [x] **Spezifischer Haftungsausschluss** - Für Fördermittelberechnungen
- [x] **Keine Gewährleistung** - Explizit dokumentiert

#### Weitergabebedingungen
- [x] **MIT License Bedingungen** - Copyright-Hinweis und Lizenz beibehalten
- [x] **Freie Nutzung und Modifikation** - Erlaubt unter MIT License
- [x] **Kommerzielle Nutzung** - Explizit erlaubt
- [x] **Sublizenzierung** - Unter MIT License möglich

#### Quellcode-Verfügbarkeit
- [x] **Projektquellcode** - Alle .py Dateien verfügbar
- [x] **Abhängigkeiten-Quellcode** - Links zu Repositories dokumentiert
- [x] **Keine Copyleft-Verpflichtungen** - PyInstaller Runtime Exception
- [x] **Build-Anweisungen** - In README.md dokumentiert

#### Dokumentation
- [x] **LICENSE.md** - Vollständige Lizenzinformationen
- [x] **THIRD-PARTY-NOTICES.md** - Drittanbieter-Komponenten
- [x] **README.md** - Lizenzverweise und Hinweise
- [x] **COMPLIANCE.md** - Diese Compliance-Checkliste

## 🔍 Detaillierte Compliance-Überprüfung

### 1. MIT License Compliance (Projekt + OpenPyXL)

**Anforderungen:**
- ✅ Copyright-Hinweis beibehalten
- ✅ Lizenztext mitliefern
- ✅ Haftungsausschluss übernehmen

**Erfüllung:**
- Copyright-Hinweise in LICENSE.md
- Vollständiger MIT License Text in LICENSE.md
- Haftungsausschluss in deutscher und englischer Sprache

### 2. Python Software Foundation License Compliance

**Anforderungen:**
- ✅ Copyright-Hinweise der PSF beibehalten
- ✅ Lizenzreferenz bereitstellen
- ✅ Keine zusätzlichen Einschränkungen

**Erfüllung:**
- PSF Copyright-Hinweise in THIRD-PARTY-NOTICES.md
- Link zur vollständigen PSF License
- Keine Einschränkungen der Python-Nutzung

### 3. PyInstaller GPL v2 + Runtime Exception Compliance

**Anforderungen:**
- ✅ Runtime Exception dokumentieren
- ✅ Keine Copyleft-Verpflichtungen für Executable
- ✅ PyInstaller Copyright beibehalten

**Erfüllung:**
- Runtime Exception explizit dokumentiert
- Executable kann unter MIT License vertrieben werden
- PyInstaller Copyright-Hinweise enthalten

## 📦 Verteilungs-Compliance

### Bei Source Code Distribution
**Erforderliche Dateien:**
- ✅ LICENSE.md
- ✅ THIRD-PARTY-NOTICES.md
- ✅ README.md (mit Lizenzverweisen)
- ✅ Alle .py Quelldateien

### Bei Binary Distribution (EXE)
**Erforderliche Dateien:**
- ✅ LICENSE.md
- ✅ THIRD-PARTY-NOTICES.md
- ✅ README.md
- ✅ Foerdermittel-Rechner.exe

**Hinweis:** Dank PyInstaller Runtime Exception keine Verpflichtung zur Quellcode-Bereitstellung bei Binary Distribution.

## 🚀 Deployment-Checkliste

### Vor der Veröffentlichung
- [ ] Alle Lizenzdateien aktuell?
- [ ] Neue Abhängigkeiten dokumentiert?
- [ ] Copyright-Jahre aktualisiert?
- [ ] Compliance-Status überprüft?

### Bei GitHub Upload
- [ ] LICENSE.md im Repository-Root
- [ ] THIRD-PARTY-NOTICES.md verfügbar
- [ ] README.md mit Lizenzverweisen
- [ ] Repository-Lizenz auf "MIT" gesetzt

### Bei Release-Erstellung
- [ ] Alle Compliance-Dateien in Release enthalten
- [ ] Release Notes mit Lizenzhinweisen
- [ ] Download-Hinweise für rechtliche Dokumente

## ⚠️ Wichtige Hinweise für Nutzer

### Für Entwickler
1. **Bei Modifikationen:** Copyright-Hinweise beibehalten
2. **Bei Weitergabe:** Alle Lizenzdateien mitliefern
3. **Bei neuen Abhängigkeiten:** Compliance-Dokumentation aktualisieren
4. **Bei kommerzieller Nutzung:** Keine zusätzlichen Einschränkungen

### Für Endnutzer
1. **Nutzung:** Frei für private und kommerzielle Zwecke
2. **Haftung:** Keine Gewährleistung für Berechnungsergebnisse
3. **Beratung:** Software ersetzt keine professionelle Rechtsberatung
4. **Überprüfung:** Ergebnisse eigenverantwortlich validieren

## 🔄 Wartung und Updates

### Regelmäßige Überprüfungen
- **Monatlich:** Neue Abhängigkeiten prüfen
- **Bei Updates:** Lizenzänderungen überprüfen
- **Jährlich:** Copyright-Jahre aktualisieren
- **Bei Releases:** Vollständige Compliance-Prüfung

### Aktualisierungsprozess
1. Neue Abhängigkeiten identifizieren
2. Lizenzen der neuen Komponenten prüfen
3. THIRD-PARTY-NOTICES.md aktualisieren
4. LICENSE.md bei Bedarf erweitern
5. Diese Compliance-Checkliste aktualisieren

## 📞 Kontakt bei Compliance-Fragen

Bei Fragen zur Open-Source-Compliance oder zu Lizenzangelegenheiten:

- **Projekt-Repository:** [Wird bei GitHub-Upload ergänzt]
- **Issues:** Für öffentliche Compliance-Diskussionen
- **Rechtliche Anfragen:** [Kontakt wird bei Bedarf ergänzt]

---

**Status:** ✅ Vollständig Compliant  
**Letzte Überprüfung:** 2024  
**Nächste Überprüfung:** Bei Änderungen der Abhängigkeiten  
**Version:** 1.0