// Exporte depuis la plateforme web : maquettes PNG (maquettes/<catégorie>/), charte PDF (charte/)
// et captures de contrôle. Le site doit être construit (scripts/construire_site.py).
// Usage : node scripts/exporter.js   (CHROMIUM=/chemin/vers/chrome si besoin)
const { chromium } = require('playwright-core');
const http = require('http');
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const SITE = path.join(ROOT, 'site');
const TYPES = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.svg': 'image/svg+xml', '.png': 'image/png', '.woff2': 'font/woff2', '.ico': 'image/x-icon', '.json': 'application/json', '.pdf': 'application/pdf' };

const serveur = http.createServer((req, res) => {
  const p = path.join(SITE, decodeURIComponent(req.url.split('?')[0]).replace(/\/$/, '/index.html'));
  if (!p.startsWith(SITE) || !fs.existsSync(p)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': TYPES[path.extname(p)] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(res);
});

(async () => {
  await new Promise((r) => serveur.listen(0, r));
  const url = `http://127.0.0.1:${serveur.address().port}/`;
  const b = await chromium.launch({ executablePath: process.env.CHROMIUM || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const page = await b.newPage({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: 2 });
  const erreurs = [];
  page.on('pageerror', (e) => erreurs.push(e.message));
  page.on('requestfailed', (r) => erreurs.push('échec ' + r.url()));
  page.on('response', (r) => { if (r.status() >= 400) erreurs.push(r.status() + ' ' + r.url()); });
  await page.goto(url, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);

  // 1. Maquettes PNG (largeur 2 400 px)
  const liste = await page.evaluate(() => window.MAQUETTES_3R.map((m) => ({ cat: m.cat, id: m.id })));
  for (const { cat, id } of liste) {
    await page.evaluate(({ cat, id }) => {
      const m = window.MAQUETTES_3R.find((x) => x.cat === cat && x.id === id);
      let el = document.getElementById('export-zone');
      if (!el) { el = document.createElement('div'); el.id = 'export-zone'; el.style.cssText = 'position:fixed;left:0;top:0;width:1200px;z-index:99;background:#fff'; document.body.appendChild(el); }
      el.innerHTML = m.dessin();
      el.firstElementChild.style.cssText = 'display:block;width:1200px;height:auto';
    }, { cat, id });
    await page.waitForLoadState('networkidle');
    const dir = path.join(ROOT, 'maquettes', cat);
    fs.mkdirSync(dir, { recursive: true });
    await page.locator('#export-zone svg').screenshot({ path: path.join(dir, `3R_${id}.png`) });
  }
  await page.evaluate(() => document.getElementById('export-zone').remove());
  console.log(`${liste.length} maquettes exportées`);

  // 2. Charte PDF (A4 paysage, mise en page d'impression)
  fs.mkdirSync(path.join(ROOT, 'charte'), { recursive: true });
  await page.emulateMedia({ media: 'print' });
  await page.pdf({ path: path.join(ROOT, 'charte', '3R_charte-graphique.pdf'), format: 'A4', landscape: true, printBackground: true, preferCSSPageSize: true,
    displayHeaderFooter: true, headerTemplate: '<span></span>', footerTemplate: '<div style="width:100%;font:8px Arial;color:#4A5672;padding:0 16mm;display:flex;justify-content:space-between"><span>3R · Charte graphique · version 1.0</span><span class="pageNumber"></span></div>' });
  await page.emulateMedia({ media: 'screen' });
  console.log('charte PDF générée');

  // 3. Captures de contrôle (bureau et téléphone)
  const ctrl = path.join(ROOT, 'docs', 'captures');
  fs.mkdirSync(ctrl, { recursive: true });
  await page.screenshot({ path: path.join(ctrl, 'bureau_haut.png') });
  const tel = await b.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 });
  await tel.goto(url, { waitUntil: 'networkidle' });
  await tel.screenshot({ path: path.join(ctrl, 'telephone_haut.png') });
  const debord = await tel.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  console.log('débordement horizontal téléphone :', debord, 'px');
  console.log(erreurs.length ? 'ERREURS :\n' + [...new Set(erreurs)].join('\n') : 'aucune erreur de chargement');
  await b.close();
  serveur.close();
})().catch((e) => { console.error(e); process.exit(1); });
