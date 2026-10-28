// Vergleicht die Schlussrunde „Wert 2026“ der Web-Version bitgenau mit der Python-Referenz.
import fs from 'node:fs';

const html = fs.readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const a = html.indexOf('/*RECHNER-START*/');
const b = html.indexOf('/*RECHNER-END*/');
const Rechner = new Function(html.slice(a, b) + '; return Rechner;')();
const ref = JSON.parse(fs.readFileSync(new URL('./reference_2026.json', import.meta.url), 'utf8'));

const felder = [['Sockelbetrag', 'sockel'], ['U3_Anteil', 'u3'], ['Zwischensumme', 'zwischensumme'],
  ['Endbetrag', 'endbetrag'], ['Endbetrag_vor_Rundung', 'endVorRundung'], ['Erste_Berechnung', 'erste']];
let fehler = 0;
for (const fall of ref.faelle) {
  const erg = Rechner.berechne(fall.kommunen, { gesamtsumme: fall.gesamt, mindestbetrag: fall.mindest, sockelProzent: fall.sockel });
  let ok = true;
  fall.erwartet.forEach((exp, i) => {
    const got = erg.rows[i];
    for (const [py, js] of felder) {
      if (!Object.is(exp[py], got[js]) && !(exp[py] === 0 && got[js] === 0)) {
        ok = false;
        if (fehler++ < 15) console.log(`  ✗ ${fall.titel} / ${exp.Name} / ${py}: py=${exp[py]} js=${got[js]}`);
      }
    }
    const pyStatus = exp.Status.replace(/\(([\d,]+\.\d\d) €\)/, (_, z) => `(${Rechner.eur2(Number(z.replace(/,/g, ''))).replace(' ', ' ')})`);
    if (pyStatus !== got.status || exp.Art !== got.art || exp.Runde !== got.runde) {
      ok = false;
      if (fehler++ < 15) console.log(`  ✗ ${fall.titel} / ${exp.Name}: "${exp.Status}" (${exp.Art}, R${exp.Runde}) vs "${got.status}" (${got.art}, R${got.runde})`);
    }
  });
  const n26 = erg.rows.filter((r) => r.art === 'w2026').length;
  console.log(`${ok ? '✓' : '✗'} ${fall.titel.padEnd(28)} n=${String(fall.kommunen.length).padStart(3)}  auf Wert 2026: ${String(n26).padStart(3)}  Runden=${erg.runden.length}  Hinweise=${erg.hinweise.length}`);
}
console.log(fehler === 0 ? '\nSCHLUSSRUNDE WERT 2026: ALLES IDENTISCH' : `\n${fehler} Abweichungen`);
process.exit(fehler ? 1 : 0);
