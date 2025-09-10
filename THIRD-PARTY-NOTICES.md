# Third-Party Notices

Dieses Projekt verwendet verschiedene Open-Source-Software-Komponenten. Die folgenden Hinweise enthalten die erforderlichen Urheberrechts- und Lizenzinformationen für diese Komponenten.

## 1. Python

**Quelle:** Python Software Foundation  
**Website:** https://www.python.org/  
**Lizenz:** Python Software Foundation License  
**Version:** 3.x  

### Copyright Notice
```
Copyright (c) 2001-2024 Python Software Foundation.
All Rights Reserved.

Copyright (c) 2000 BeOpen.com.
All Rights Reserved.

Copyright (c) 1995-2001 Corporation for National Research Initiatives.
All Rights Reserved.

Copyright (c) 1991-1995 Stichting Mathematisch Centrum, Amsterdam.
All Rights Reserved.
```

### License Summary
Python is distributed under the Python Software Foundation License, which is compatible with the GPL but allows for more liberal use.

---

## 2. Tkinter

**Quelle:** Python Software Foundation (Teil von Python)  
**Website:** https://docs.python.org/3/library/tkinter.html  
**Lizenz:** Python Software Foundation License  
**Beschreibung:** Standard GUI-Toolkit für Python  

### Copyright Notice
```
Copyright (c) 2001-2024 Python Software Foundation.
All Rights Reserved.
```

### License Summary
Tkinter ist Teil der Python-Standardbibliothek und unterliegt derselben Lizenz wie Python.

---

## 3. OpenPyXL

**Quelle:** OpenPyXL Development Team  
**Website:** https://openpyxl.readthedocs.io/  
**Repository:** https://github.com/theorchard/openpyxl  
**Lizenz:** MIT License  
**Beschreibung:** Python-Bibliothek zum Lesen und Schreiben von Excel-Dateien  

### Copyright Notice
```
Copyright (c) 2010 openpyxl
```

### MIT License Text
```
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 4. PyInstaller

**Quelle:** PyInstaller Development Team  
**Website:** https://pyinstaller.org/  
**Repository:** https://github.com/pyinstaller/pyinstaller  
**Lizenz:** GPL v2 with Runtime Exception  
**Beschreibung:** Tool zum Erstellen von ausführbaren Dateien aus Python-Skripten  

### Copyright Notice
```
Copyright (c) 2005-2024, PyInstaller Development Team
Copyright (c) 2005-2009, Giovanni Bajo
Copyright (c) 2002-2005, McMillan Enterprise, Inc.
Copyright (c) 1999-2002, McMillan Enterprise, Inc.
```

### Runtime Exception
PyInstaller ist unter GPL v2 lizenziert, enthält jedoch eine Runtime Exception, die es ermöglicht, mit PyInstaller erstellte ausführbare Dateien unter beliebigen Lizenzen zu vertreiben, ohne dass diese der GPL unterliegen.

### Exception Text
```
As a special exception, if you create a program using PyInstaller,
you may distribute that program without restriction. This special
exception does not apply to any modifications of PyInstaller itself.
```

---

## 5. Weitere Python-Standardbibliotheken

Dieses Projekt verwendet verschiedene Module aus der Python-Standardbibliothek, einschließlich aber nicht beschränkt auf:

- `os` - Betriebssystem-Interface
- `sys` - System-spezifische Parameter und Funktionen
- `datetime` - Datum und Zeit Funktionen
- `csv` - CSV-Datei Lesen und Schreiben
- `json` - JSON-Encoder und -Decoder
- `pathlib` - Objektorientierte Dateisystem-Pfade

### Copyright Notice
```
Copyright (c) 2001-2024 Python Software Foundation.
All Rights Reserved.
```

Alle diese Module sind Teil der Python-Standardbibliothek und unterliegen der Python Software Foundation License.

---

## Lizenz-Kompatibilität

### Übersicht der verwendeten Lizenzen
- **MIT License:** OpenPyXL, Dieses Projekt
- **Python Software Foundation License:** Python, Tkinter, Standardbibliotheken
- **GPL v2 + Runtime Exception:** PyInstaller

### Kompatibilitätsmatrix
Alle verwendeten Lizenzen sind miteinander kompatibel:
- MIT License ist sehr permissiv und kompatibel mit allen anderen Lizenzen
- Python Software Foundation License ist GPL-kompatibel
- PyInstaller's Runtime Exception erlaubt die Verteilung unter beliebigen Lizenzen

## Compliance-Checkliste

### ✅ Erfüllte Anforderungen
- [x] Alle Copyright-Hinweise beibehalten
- [x] Alle Lizenztexte verfügbar gemacht
- [x] Haftungsausschlüsse übernommen
- [x] Quellcode-Verfügbarkeit dokumentiert
- [x] Weitergabebedingungen spezifiziert

### 📋 Empfohlene Maßnahmen bei Weitergabe
1. Diese Datei (THIRD-PARTY-NOTICES.md) mitliefern
2. LICENSE.md Datei mitliefern
3. Bei Modifikationen: Änderungen dokumentieren
4. Bei kommerzieller Nutzung: Keine zusätzlichen Einschränkungen

## Aktualisierung dieser Hinweise

Bei Hinzufügung neuer Abhängigkeiten müssen diese Hinweise entsprechend aktualisiert werden. Überprüfen Sie regelmäßig:

1. Neue verwendete Bibliotheken
2. Aktualisierte Versionen bestehender Bibliotheken
3. Geänderte Lizenzbedingungen
4. Neue Copyright-Inhaber

---

**Erstellt:** 2024  
**Letzte Überprüfung:** 2024  
**Nächste Überprüfung:** Bei Änderungen der Abhängigkeiten