"""Erzeugt Referenzergebnisse mit dem Original-Rechenkern (foerdermittel_rechner.py).

Die Web-Version muss für dieselben Eingaben bitgenau dieselben Werte liefern.
"""
import contextlib
import io
import json
import random
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HIER, '..', '..')))
from foerdermittel_rechner import FoerdermittelRechner  # noqa: E402

BEISPIEL = [
    ("Stadt A", 50000, 120), ("Stadt B", 35000, 85), ("Gemeinde C", 15000, 30),
    ("Gemeinde D", 8000, 15), ("Stadt E", 45000, 95), ("Gemeinde F", 12000, 25),
    ("Stadt G", 60000, 140), ("Gemeinde H", 5000, 8), ("Stadt I", 40000, 75),
    ("Gemeinde J", 18000, 35),
]


def convert_german_number(value):
    """Wörtlich aus FoerdermittelGUI.import_excel (foerdermittel_gui.py)."""
    import pandas as pd
    if pd.isna(value):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    str_val = str(value).strip()
    if not str_val:
        return None
    str_val = str_val.replace('€', '').replace(' ', '')
    if ',' in str_val and '.' in str_val:
        comma_pos = str_val.rfind(',')
        dot_pos = str_val.rfind('.')
        if comma_pos > dot_pos:
            str_val = str_val.replace('.', '').replace(',', '.')
        else:
            parts = str_val.split('.')
            if len(parts) >= 2:
                integer_part = '.'.join(parts[:-1]).replace(',', '')
                decimal_part = parts[-1]
                str_val = f"{integer_part}.{decimal_part}"
            else:
                str_val = str_val.replace(',', '')
    elif ',' in str_val:
        comma_pos = str_val.rfind(',')
        after_comma = str_val[comma_pos+1:]
        if len(after_comma) <= 2 and after_comma.isdigit():
            comma_count = str_val.count(',')
            if comma_count == 1:
                str_val = str_val.replace(',', '.')
            else:
                parts = str_val.split(',')
                if len(parts) >= 2:
                    integer_part = ''.join(parts[:-1])
                    decimal_part = parts[-1]
                    str_val = f"{integer_part}.{decimal_part}"
        else:
            str_val = str_val.replace(',', '')
    try:
        return float(str_val)
    except ValueError:
        return None


def gui_wert(x):
    # Die GUI speichert den Wert als f"{x:,.2f}" in der Tabelle und liest ihn zurück
    return float(f"{x:,.2f}".replace(',', ''))


def gui_kinder_import(x):
    # Beim Excel-Import speichert die GUI Kinder U3 als f"{x:.6f}"
    return float(f"{x:.6f}")


def rechne(kommunen, gesamt, mindest, sockel):
    r = FoerdermittelRechner(gesamt)
    r.mindestbetrag = mindest
    r.sockelbetrag_prozent = sockel
    for name, wert, kinder in kommunen:
        r.kommune_hinzufuegen(name, wert, kinder)
    with contextlib.redirect_stdout(io.StringIO()):
        df = r.berechne_verteilung()
    cols = ['Sockelbetrag', 'U3_Anteil', 'Zwischensumme', 'Endbetrag',
            'Endbetrag_vor_Rundung', 'Erste_Berechnung']
    rows = []
    for _, row in df.iterrows():
        d = {'name': row['Name'], 'status': row['Status'], 'runde': int(row['Runde'])}
        for c in cols:
            d[c] = float(row[c])
        rows.append(d)
    return rows


def zufallsfall(rng, n, kinder_dezimal=False):
    kommunen = []
    for i in range(n):
        groesse = rng.choice(['klein', 'mittel', 'gross'])
        if groesse == 'klein':
            wert = rng.uniform(1000, 14000)
            kinder = rng.uniform(0, 40)
        elif groesse == 'mittel':
            wert = rng.uniform(10000, 60000)
            kinder = rng.uniform(20, 300)
        else:
            wert = rng.uniform(50000, 400000)
            kinder = rng.uniform(200, 4000)
        wert = gui_wert(round(wert, 2))
        kinder = gui_kinder_import(kinder) if kinder_dezimal else float(int(kinder))
        kommunen.append((f"Kommune {i + 1:03d}", wert, kinder))
    summe_wert = sum(k[1] for k in kommunen)
    sockel = rng.choice([0.3, 0.4, 0.5, 0.6])
    gesamt = float(round(summe_wert * rng.uniform(0.8, 1.6)))
    mindest = float(rng.choice([5000, 10000, 12500, 15000, 20000]))
    return kommunen, gesamt, mindest, sockel


def main():
    faelle = []
    faelle.append(('Beispieldaten', [(n, float(w), float(k)) for n, w, k in BEISPIEL], 500000.0, 12500.0, 0.5))
    faelle.append(('Erklaerungsbeispiel', [('Kommune A', 20000.0, 10.0), ('Kommune B', 5000.0, 5.0)], 500000.0, 12500.0, 0.5))
    faelle.append(('Eine Kommune', [('Solo', 12345.67, 12.0)], 100000.0, 12500.0, 0.5))
    faelle.append(('Budget zu klein', [(n, float(w), float(k)) for n, w, k in BEISPIEL], 100000.0, 12500.0, 0.5))
    faelle.append(('Keine U3-Kinder', [('A', 10000.0, 0.0), ('B', 30000.0, 0.0), ('C', 50000.0, 0.0)], 200000.0, 12500.0, 0.5))
    faelle.append(('Sockel 0 Prozent', [(n, float(w), float(k)) for n, w, k in BEISPIEL], 500000.0, 12500.0, 0.0))
    faelle.append(('Sockel 100 Prozent', [(n, float(w), float(k)) for n, w, k in BEISPIEL], 500000.0, 12500.0, 1.0))
    faelle.append(('Gesamtsumme mit Cent', [(n, float(w), float(k)) for n, w, k in BEISPIEL], 500000.5, 12500.0, 0.5))
    faelle.append(('Mindestbetrag 0', [(n, float(w), float(k)) for n, w, k in BEISPIEL], 500000.0, 0.0, 0.5))
    faelle.append(('Sockel 33,3 Prozent', [(n, float(w), float(k)) for n, w, k in BEISPIEL], 487654.0, 14000.0, 33.3 / 100))

    rng = random.Random(20261026)
    for n in [3, 7, 8, 9, 15, 16, 17, 64, 127, 128, 129, 200, 257, 396]:
        for dez in (False, True):
            k, g, m, s = zufallsfall(rng, n, dez)
            faelle.append((f'Zufall n={n} dezimal={dez}', k, g, m, s))

    out = []
    runde1_faelle = 0
    for titel, kommunen, gesamt, mindest, sockel in faelle:
        rows = rechne(kommunen, gesamt, mindest, sockel)
        if any(r['status'].startswith('Wert aus Runde 1') for r in rows):
            runde1_faelle += 1
        out.append({
            'titel': titel, 'gesamt': gesamt, 'mindest': mindest, 'sockel': sockel,
            'kommunen': [{'name': n, 'wert': w, 'kinder': k} for n, w, k in kommunen],
            'erwartet': rows,
        })

    # Formatierung/Rundung wie die GUI (f"{x:.2f}" / f"{x:.6f}")
    werte = [0.125, 0.375, 1000.125, 2.675, 1.005, 0.0078125, 12.0078125, 3.1415926535, 1e-9,
             123456.785, 99.995, 0.5, 1.5, 2.5, 7.0234375]
    for _ in range(3000):
        werte.append(rng.uniform(0, 500000))
        werte.append(rng.randint(0, 100000) / 8)
        werte.append(rng.randint(0, 100000) / 128)
        werte.append(round(rng.uniform(0, 1000), rng.randint(0, 9)))
    fmt = [{'x': x, 'f2': f"{x:.2f}", 'f6': f"{x:.6f}"} for x in werte]

    # Summation wie pandas (Series.sum) für viele Längen
    import pandas as pd
    summen = []
    for n in list(range(0, 300)) + [511, 512, 513, 1000, 1025]:
        werte_s = [rng.uniform(-1000, 100000) * rng.choice([1, 1e-3, 1e3]) for _ in range(n)]
        summen.append({'werte': werte_s, 'summe': float(pd.Series(werte_s, dtype='float64').sum())})

    # Zahlenumwandlung beim Import, Original aus foerdermittel_gui.py
    konvert_in = ['1.000,50', '1,000.50', '35,000', '35,00', '35,5', '1,234,567', '1,234,56', '12.345', '12.5',
                  '€ 1.234,56', '1 234,56', '  42  ', '', 'abc', '1.2.3', '1.000.000,25', '0,125', '7,0',
                  '1,2,3', '−5', '-5', '3e2', '1,000,000.75', '2.5.2019', ',5', '5,', '120', '12,3456']
    konvert = [{'in': s, 'out': convert_german_number(s)} for s in konvert_in]

    json.dump({'faelle': out, 'format': fmt, 'summen': summen, 'konvert': konvert},
              open(os.path.join(HIER, 'reference.json'), 'w'), ensure_ascii=False)
    print(f"{len(out)} Fälle, davon {runde1_faelle} mit 'Wert aus Runde 1'; {len(fmt)} Formatwerte")
    for f in out:
        stati = {}
        for r in f['erwartet']:
            key = r['status'].split(' (')[0]
            stati[key] = stati.get(key, 0) + 1
        print(f"  {f['titel']:<32} {stati}")


if __name__ == '__main__':
    main()
