// Baut die eigenständige Version: eine einzige HTML-Datei ohne externe Abrufe
// (ExcelJS und Schriften eingebettet), z. B. für GitHub Pages, eigenen Server oder Intranet.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

process.chdir(path.dirname(fileURLToPath(import.meta.url)));

const src = fs.readFileSync('index.html', 'utf8');
const [kopf, rumpf] = src.split('<!--BODY-->');
if (!rumpf) throw new Error('Marker <!--BODY--> fehlt');

const font = (pkg, file) => fs.readFileSync(`node_modules/@fontsource/${pkg}/files/${file}`).toString('base64');
const face = (family, weight, pkg, file) =>
  `@font-face{font-family:"${family}";font-style:normal;font-weight:${weight};font-display:swap;src:url(data:font/woff2;base64,${font(pkg, file)}) format("woff2")}`;
const fonts = [
  face('IBM Plex Sans', 400, 'ibm-plex-sans', 'ibm-plex-sans-latin-400-normal.woff2'),
  face('IBM Plex Sans', 500, 'ibm-plex-sans', 'ibm-plex-sans-latin-500-normal.woff2'),
  face('IBM Plex Sans', 600, 'ibm-plex-sans', 'ibm-plex-sans-latin-600-normal.woff2'),
  face('IBM Plex Mono', 400, 'ibm-plex-mono', 'ibm-plex-mono-latin-400-normal.woff2'),
  face('Source Serif 4', 600, 'source-serif-4', 'source-serif-4-latin-600-normal.woff2'),
].join('\n');

const linkRe = /<link id="webfonts"[^>]*>\n?/;
if (!linkRe.test(kopf)) throw new Error('Webfont-Link nicht gefunden');
const kopfNeu = kopf.replace(linkRe, `<!-- Schriften: IBM Plex Sans/Mono (Copyright IBM Corp.), Source Serif 4 (Copyright Adobe), SIL Open Font License 1.1 -->\n<style>\n${fonts}\n</style>\n`);

const lib = fs.readFileSync('node_modules/exceljs/dist/exceljs.min.js', 'utf8');
if (/<\/script/i.test(lib)) throw new Error('Bibliothek enthält </script');
const lizenz = fs.readFileSync('node_modules/exceljs/LICENSE', 'utf8').replace(/\*\//g, '* /');
const libTag = `<script>/*! ExcelJS 4.4.0 – https://github.com/exceljs/exceljs\n${lizenz}*/\n${lib}\n</script>\n`;
const i = rumpf.indexOf('<script>');
if (i < 0) throw new Error('App-Skript nicht gefunden');
const rumpfNeu = rumpf.slice(0, i) + libTag + rumpf.slice(i);

const html = `<!doctype html>
<!-- Fördermittel-Verteilungsrechner, eigenständige Web-Version. © 2025 Marco Benta, MIT-Lizenz.
     Läuft vollständig im Browser, ohne Server und ohne externe Abrufe. -->
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
${kopfNeu}<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}</style>
</head>
<body>
${rumpfNeu}</body>
</html>
`;
fs.mkdirSync('dist', { recursive: true });
fs.writeFileSync('dist/foerdermittelrechner.html', html);
console.log(`web/dist/foerdermittelrechner.html: ${(html.length / 1024).toFixed(0)} KB`);
