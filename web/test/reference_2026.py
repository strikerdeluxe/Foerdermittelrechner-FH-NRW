"""Unabhängige Python-Referenz für die Schlussrunde „Wert 2026“ der Web-Version.

Die Routine ist wörtlich aus FoerdermittelRechner.berechne_verteilung übernommen (pandas),
danach folgen Schlussrunde und Rundung nach der vereinbarten Regel:

1. Nach der Routine wird jede Kommune, deren Betrag unter ihrem Wert 2026 liegt,
   genau auf den Wert 2026 festgesetzt.
2. Das übrige Budget wird auf die nicht festgesetzten Kommunen nach demselben Schlüssel
   (Sockelbetrag + Kinder U3 x Multiplikator) neu verteilt. Fällt eine Kommune unter den
   höheren Wert aus Mindestbetrag und Wert 2026, wird sie darauf festgesetzt; wiederholen,
   bis keine Kommune mehr darunter fällt.
3. Rundung auf ganze Euro; der Ausgleich erfolgt bei der Kommune mit dem höchsten Betrag,
   die nicht auf ihren Wert 2026 festgesetzt ist.
"""
import contextlib
import io
import json
import math
import os
import random
import sys

import pandas as pd

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HIER, '..', '..')))
from foerdermittel_rechner import FoerdermittelRechner  # noqa: E402


def berechne_2026(kommunen, gesamtsumme, mindestbetrag, sockel):
    df = pd.DataFrame([{'Name': n, 'Wert_2019': w, 'Kinder_U3': k,
                        'Wert_2026': (float('nan') if w26 is None else w26), 'Status': 'In Berechnung'}
                       for n, w, k, w26 in kommunen])
    df['Sockelbetrag'] = df['Wert_2019'] * sockel
    df['U3_Anteil'] = 0.0
    df['Zwischensumme'] = 0.0
    df['Endbetrag'] = 0.0
    df['Runde'] = 0
    df['Erste_Berechnung'] = 0.0
    df['Art'] = 'offen'

    fixiert = set()
    runde = 0
    abgeschlossen_runden = 0
    while runde < 10:
        runde += 1
        aktive_df = df[~df.index.isin(fixiert)].copy()
        if len(aktive_df) == 0:
            break
        summe_sockel = aktive_df['Sockelbetrag'].sum()
        bereits_fixiert_summe = df[df.index.isin(fixiert)]['Endbetrag'].sum()
        verfuegbares_budget = gesamtsumme - bereits_fixiert_summe
        restbudget = verfuegbares_budget - summe_sockel
        summe_u3 = aktive_df['Kinder_U3'].sum()
        multiplikator = restbudget / summe_u3 if summe_u3 > 0 else 0
        for idx in aktive_df.index:
            df.loc[idx, 'U3_Anteil'] = df.loc[idx, 'Kinder_U3'] * multiplikator
            df.loc[idx, 'Zwischensumme'] = df.loc[idx, 'Sockelbetrag'] + df.loc[idx, 'U3_Anteil']
            df.loc[idx, 'Runde'] = runde
            if runde == 1:
                df.loc[idx, 'Erste_Berechnung'] = df.loc[idx, 'Zwischensumme']
        neue = []
        for idx in aktive_df.index:
            zs = df.loc[idx, 'Zwischensumme']
            if zs < mindestbetrag:
                if runde > 1 and df.loc[idx, 'Erste_Berechnung'] >= mindestbetrag:
                    df.loc[idx, 'Endbetrag'] = df.loc[idx, 'Erste_Berechnung']
                    df.loc[idx, 'Status'] = f'Wert aus Runde 1 ({df.loc[idx, "Erste_Berechnung"]:,.2f} €)'
                    df.loc[idx, 'Art'] = 'runde1'
                else:
                    df.loc[idx, 'Endbetrag'] = mindestbetrag
                    df.loc[idx, 'Status'] = f'Fixiert auf Mindestbetrag (Runde {runde})'
                    df.loc[idx, 'Art'] = 'mindest'
                neue.append(idx)
            else:
                df.loc[idx, 'Endbetrag'] = zs
        fixiert.update(neue)
        abgeschlossen_runden = runde
        if len(neue) == 0:
            for idx in aktive_df.index:
                df.loc[idx, 'Status'] = 'OK'
                df.loc[idx, 'Art'] = 'ok'
            break

    # Schlussrunde Wert 2026
    if df['Wert_2026'].notna().any():
        r2 = abgeschlossen_runden + 1
        neue = []
        for idx in df.index:
            w26 = df.loc[idx, 'Wert_2026']
            if not math.isnan(w26) and df.loc[idx, 'Endbetrag'] < w26:
                df.loc[idx, 'Endbetrag'] = w26
                df.loc[idx, 'Status'] = f'Fixiert auf Wert 2026 (Runde {r2})'
                df.loc[idx, 'Art'] = 'w2026'
                df.loc[idx, 'Runde'] = r2
                neue.append(idx)
        fixiert.update(neue)
        while neue:
            r2 += 1
            aktive_df = df[~df.index.isin(fixiert)].copy()
            if len(aktive_df) == 0:
                break
            summe_sockel = aktive_df['Sockelbetrag'].sum()
            bereits_fixiert_summe = df[df.index.isin(fixiert)]['Endbetrag'].sum()
            restbudget = (gesamtsumme - bereits_fixiert_summe) - summe_sockel
            summe_u3 = aktive_df['Kinder_U3'].sum()
            multiplikator = restbudget / summe_u3 if summe_u3 > 0 else 0
            neue = []
            for idx in aktive_df.index:
                df.loc[idx, 'U3_Anteil'] = df.loc[idx, 'Kinder_U3'] * multiplikator
                df.loc[idx, 'Zwischensumme'] = df.loc[idx, 'Sockelbetrag'] + df.loc[idx, 'U3_Anteil']
                df.loc[idx, 'Runde'] = r2
                w26 = df.loc[idx, 'Wert_2026']
                hat = not math.isnan(w26) and w26 > mindestbetrag
                grenze = w26 if hat else mindestbetrag
                if df.loc[idx, 'Zwischensumme'] < grenze:
                    df.loc[idx, 'Endbetrag'] = grenze
                    df.loc[idx, 'Status'] = f'Fixiert auf Wert 2026 (Runde {r2})' if hat else f'Fixiert auf Mindestbetrag (Runde {r2})'
                    df.loc[idx, 'Art'] = 'w2026' if hat else 'mindest'
                    neue.append(idx)
                else:
                    df.loc[idx, 'Endbetrag'] = df.loc[idx, 'Zwischensumme']
            fixiert.update(neue)

    df['Endbetrag_vor_Rundung'] = df['Endbetrag'].copy()
    df['Endbetrag'] = df['Endbetrag'].round(0)
    differenz = gesamtsumme - df['Endbetrag'].sum()
    if abs(differenz) >= 1:
        pool = df[df['Art'] != 'w2026']
        if len(pool) == 0:
            pool = df
        max_idx = pool['Endbetrag'].idxmax()
        df.loc[max_idx, 'Endbetrag'] += differenz
        if 'Rundungsausgleich' not in df.loc[max_idx, 'Status']:
            df.loc[max_idx, 'Status'] += ' + Rundungsausgleich'
    return df


def original(kommunen, gesamt, mindest, sockel):
    r = FoerdermittelRechner(gesamt)
    r.mindestbetrag = mindest
    r.sockelbetrag_prozent = sockel
    for n, w, k, _ in kommunen:
        r.kommune_hinzufuegen(n, w, k)
    with contextlib.redirect_stdout(io.StringIO()):
        return r.berechne_verteilung()


def main():
    rng = random.Random(2026)
    faelle = []
    beispiel = [('Stadt A', 50000.0, 120.0, 88000.0), ('Stadt B', 35000.0, 85.0, 66500.0), ('Gemeinde C', 15000.0, 30.0, 23000.0),
                ('Gemeinde D', 8000.0, 15.0, 13800.0), ('Stadt E', 45000.0, 95.0, 72000.0), ('Gemeinde F', 12000.0, 25.0, 21000.0),
                ('Stadt G', 60000.0, 140.0, 101000.0), ('Gemeinde H', 5000.0, 8.0, 11000.0), ('Stadt I', 40000.0, 75.0, 60000.0),
                ('Gemeinde J', 18000.0, 35.0, 27500.0)]
    faelle.append(('Beispieldaten Web', beispiel, 500000.0, 12500.0, 0.5))
    faelle.append(('Beispiel ohne 2026', [(n, w, k, None) for n, w, k, _ in beispiel], 500000.0, 12500.0, 0.5))
    faelle.append(('2026 übersteigt Budget', [(n, w, k, w26 * 1.3) for n, w, k, w26 in beispiel], 500000.0, 12500.0, 0.5))
    faelle.append(('Alle exakt auf 2026', [(n, w, k, w26) for n, w, k, w26 in beispiel], float(sum(b[3] for b in beispiel)), 12500.0, 0.5))
    faelle.append(('Wert 2026 unter Mindest', [(n, w, k, 5000.0) for n, w, k, _ in beispiel], 500000.0, 12500.0, 0.5))

    for n in [3, 7, 9, 17, 64, 129, 200, 396]:
        for anteil in (0.5, 1.0):
            kommunen = []
            for i in range(n):
                g = rng.choice(['klein', 'mittel', 'gross'])
                wert = {'klein': rng.uniform(1000, 14000), 'mittel': rng.uniform(10000, 60000), 'gross': rng.uniform(50000, 400000)}[g]
                kinder = {'klein': rng.uniform(0, 40), 'mittel': rng.uniform(20, 300), 'gross': rng.uniform(200, 4000)}[g]
                kommunen.append([f'Kommune {i + 1:03d}', float(f'{wert:.2f}'), float(f'{kinder:.6f}'), None])
            gesamt = float(round(sum(k[1] for k in kommunen) * rng.uniform(0.9, 1.5)))
            mindest = float(rng.choice([5000, 10000, 12500, 15000]))
            sockel = rng.choice([0.3, 0.5, 0.6])
            # Wert 2026 um das Ergebnis der Routine streuen, damit Kommunen darunter fallen
            basis = original([tuple(k) for k in kommunen], gesamt, mindest, sockel)
            for i, k in enumerate(kommunen):
                if rng.random() < anteil:
                    k[3] = float(round(basis.loc[i, 'Endbetrag'] * rng.uniform(0.85, 1.12)))
            faelle.append((f'Zufall n={n} Anteil={anteil}', [tuple(k) for k in kommunen], gesamt, mindest, sockel))

    out = []
    for titel, kommunen, gesamt, mindest, sockel in faelle:
        df = berechne_2026(kommunen, gesamt, mindest, sockel)
        # Plausibilität: Summe exakt, Untergrenzen eingehalten (wenn das Budget reicht)
        grenzen = [max(mindest, w26 if w26 is not None else 0) for _, _, _, w26 in kommunen]
        reicht = sum(grenzen) <= gesamt
        verletzt = sum(1 for i, g in enumerate(grenzen) if df.loc[i, 'Endbetrag'] < g - 1e-9)
        stati = {}
        for s in df['Status']:
            key = s.split(' (')[0]
            stati[key] = stati.get(key, 0) + 1
        print(f"{titel:<28} Summe={df['Endbetrag'].sum():>12,.0f} Soll={gesamt:>12,.0f} "
              f"Untergrenzen {'eingehalten' if verletzt == 0 else f'{verletzt} verletzt'}{'' if reicht else ' (Budget reicht nicht)'}  {stati}")
        if reicht:
            assert verletzt == 0, titel
            assert abs(df['Endbetrag'].sum() - gesamt) < 0.01, titel
        rows = []
        for _, row in df.iterrows():
            rows.append({k: (float(row[k]) if k not in ('Name', 'Status', 'Art', 'Runde') else (int(row[k]) if k == 'Runde' else row[k]))
                         for k in ['Name', 'Status', 'Art', 'Runde', 'Sockelbetrag', 'U3_Anteil', 'Zwischensumme',
                                   'Endbetrag', 'Endbetrag_vor_Rundung', 'Erste_Berechnung']})
        out.append({'titel': titel, 'gesamt': gesamt, 'mindest': mindest, 'sockel': sockel,
                    'kommunen': [{'name': n, 'wert': w, 'kinder': k, 'wert2026': w26} for n, w, k, w26 in kommunen],
                    'erwartet': rows})

    # Ohne Wert 2026 muss das Ergebnis exakt dem Original entsprechen
    ohne = [(n, w, k, None) for n, w, k, _ in beispiel]
    a = berechne_2026(ohne, 500000.0, 12500.0, 0.5)
    b = original(ohne, 500000.0, 12500.0, 0.5)
    assert all(a['Endbetrag'] == b['Endbetrag']) and all(a['Status'] == b['Status'])
    json.dump({'faelle': out}, open(os.path.join(HIER, 'reference_2026.json'), 'w'), ensure_ascii=False)
    print(f'{len(out)} Fälle geschrieben; ohne Wert 2026 identisch mit dem Original.')


if __name__ == '__main__':
    main()
