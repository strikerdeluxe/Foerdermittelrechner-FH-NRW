// Vergleicht den JavaScript-Rechenkern bitgenau mit den Python-Referenzergebnissen.
import fs from 'node:fs';

const html = fs.readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const a = html.indexOf('/*RECHNER-START*/');
const b = html.indexOf('/*RECHNER-END*/');
const Rechner = new Function(html.slice(a, b) + '; return Rechner;')();
const ref = JSON.parse(fs.readFileSync(new URL('./reference.json', import.meta.url), 'utf8'));

let fehler = 0;
const felder = [['Sockelbetrag', 'sockel'], ['U3_Anteil', 'u3'], ['Zwischensumme', 'zwischensumme'],
  ['Endbetrag', 'endbetrag'], ['Endbetrag_vor_Rundung', 'endVorRundung'], ['Erste_Berechnung', 'erste']];

for (const fall of ref.faelle) {
  const erg = Rechner.berechne(fall.kommunen, { gesamtsumme: fall.gesamt, mindestbetrag: fall.mindest, sockelProzent: fall.sockel });
  let ok = true;
  fall.erwartet.forEach((exp, i) => {
    const got = erg.rows[i];
    for (const [py, js] of felder) {
      if (!Object.is(exp[py], got[js]) && !(exp[py] === 0 && got[js] === 0)) {
        ok = false;
        if (fehler < 15) console.log(`  ✗ ${fall.titel} / ${exp.name} / ${py}: py=${exp[py]} js=${got[js]}`);
        fehler++;
      }
    }
    // Status: Python formatiert Beträge englisch, die Web-Version deutsch
    const pyStatus = exp.status.replace(/\(([\d,]+\.\d\d) €\)/, (_, z) => `(${Rechner.eur2(Number(z.replace(/,/g, ''))).replace('\u00a0', ' ')})`);
    if (pyStatus !== got.status) { ok = false; fehler++; console.log(`  ✗ Status ${fall.titel} / ${exp.name}: "${exp.status}" vs "${got.status}"`); }
    if (exp.runde !== got.runde) { ok = false; fehler++; console.log(`  ✗ Runde ${fall.titel} / ${exp.name}`); }
  });
  const summe = Rechner.npSum(erg.rows.map((r) => r.endbetrag));
  console.log(`${ok ? '✓' : '✗'} ${fall.titel.padEnd(30)} n=${String(fall.kommunen.length).padStart(3)}  Runden=${erg.runden.length}  Summe=${summe}  Hinweise=${erg.hinweise.length}`);
}

let fmtFehler = 0;
for (const f of ref.format) {
  if (Rechner.pyFixed(f.x, 2) !== f.f2) { if (fmtFehler++ < 10) console.log(`  ✗ .2f ${f.x}: py=${f.f2} js=${Rechner.pyFixed(f.x, 2)}`); }
  if (Rechner.pyFixed(f.x, 6) !== f.f6) { if (fmtFehler++ < 10) console.log(`  ✗ .6f ${f.x}: py=${f.f6} js=${Rechner.pyFixed(f.x, 6)}`); }
}
console.log(`Formatierung: ${ref.format.length * 2 - fmtFehler}/${ref.format.length * 2} identisch`);

if (ref.summen) {
  let sf = 0;
  for (const s of ref.summen) if (!Object.is(Rechner.npSum(s.werte), s.summe)) sf++;
  console.log(`Summen (NumPy/pandas): ${ref.summen.length - sf}/${ref.summen.length} identisch`);
  fehler += sf;
}
if (ref.konvert) {
  let kf = 0;
  for (const k of ref.konvert) {
    const got = Rechner.convertGermanNumber(k.in);
    if (!(got === k.out || (got === null && k.out === null))) { kf++; console.log(`  ✗ convert ${JSON.stringify(k.in)}: py=${k.out} js=${got}`); }
  }
  console.log(`Zahlenumwandlung Import: ${ref.konvert.length - kf}/${ref.konvert.length} identisch`);
  fehler += kf;
}
console.log(fehler + fmtFehler === 0 ? '\nALLES IDENTISCH' : `\n${fehler + fmtFehler} Abweichungen`);
process.exit(fehler + fmtFehler ? 1 : 0);
