/* Plateforme de la charte 3R : rendu des listes, comparateur, galeries, visionneuse, téléchargements. */
(function () {
  const D = window.DONNEES_3R || { fichiers: [], apercus: [] };
  const M = window.MAQUETTES_3R || [];
  const $ = (s, el = document) => el.querySelector(s);
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const F = 'fichiers/logos/';

  /* Versions du logo */
  const VERSIONS = [
    ['Officiel en relief', 'officiel', F + '00_officiel_3D/logo_3R_officiel_3D.png', '#FFFFFF', 'Référence de la marque. Écran et impression jusqu’à 10 cm.', ['00_officiel_3D/logo_3R_officiel_3D.png', '00_officiel_3D/logo_3R_officiel_3D.pdf']],
    ['Principal en aplats', 'valide', F + '01_principal/3R_principal_couleur.svg', '#FFFFFF', 'Version technique : impression, web, broderie.', ['01_principal/3R_principal_couleur.svg', '01_principal/3R_principal_couleur.pdf', '01_principal/png/3R_principal_couleur_2048px.png']],
    ['Fonds foncés', 'valide', F + '04_fonds-fonces/3R_fond-fonce_couleur.svg', '#1D2B4F', 'Sur bleu nuit ou photo sombre.', ['04_fonds-fonces/3R_fond-fonce_couleur.svg', '04_fonds-fonces/3R_fond-fonce_couleur.pdf']],
    ['Blanc', 'valide', F + '03_blanc/3R_blanc.svg', '#FE6501', 'Sur orange ou fond coloré.', ['03_blanc/3R_blanc.svg', '03_blanc/3R_blanc.pdf', '03_blanc/png/3R_blanc_2048px.png']],
    ['Monochrome orange', 'valide', F + '02_monochrome/3R_mono_orange.svg', '#F4EFEA', 'Sérigraphie ou gravure une encre.', ['02_monochrome/3R_mono_orange.svg', '02_monochrome/3R_mono_orange.pdf']],
    ['Monochrome bleu nuit', 'valide', F + '02_monochrome/3R_mono_bleu-nuit.svg', '#FFFFFF', 'Documents une couleur.', ['02_monochrome/3R_mono_bleu-nuit.svg', '02_monochrome/3R_mono_bleu-nuit.pdf']],
    ['Monochrome noir', 'valide', F + '02_monochrome/3R_mono_noir.svg', '#FFFFFF', 'Presse noir et blanc, tampons.', ['02_monochrome/3R_mono_noir.svg', '02_monochrome/3R_mono_noir.pdf']],
    ['Miniature : cimier 3R', 'valide', F + '05_miniature/3R_cimier_orange.svg', '#FFFFFF', 'Sous 30 mm ou 120 px. Orange, blanc ou bleu nuit.', ['05_miniature/3R_cimier_orange.svg', '05_miniature/3R_cimier_blanc.svg', '05_miniature/3R_cimier_bleu-nuit.svg']],
  ];
  const ext = (p) => p.split('.').pop().toUpperCase();
  $('#versions').innerHTML = VERSIONS.map(([nom, st, img, bg, desc, fs]) => `<article class="version-carte"><div class="scene" style="background:${bg}"><img src="${img}" alt="${esc(nom)}"></div><div class="info"><span class="statut ${st}">${st === 'officiel' ? 'Officiel' : 'Validé'}</span><h4>${esc(nom)}</h4><p class="small">${esc(desc)}</p><div class="liens">${fs.map((f) => `<a class="btn-fichier" href="${F + f}" download>${ext(f)}${f.includes('_2048') ? ' 2048' : ''}${f.includes('cimier_') ? ' ' + f.split('cimier_')[1].split('.')[0] : ''}</a>`).join('')}</div></div></article>`).join('');

  /* Comparateur : variante × fond, avec verdict selon les règles */
  const VAR = { couleur: ['Couleur', F + '01_principal/3R_principal_couleur.svg'], blanc: ['Blanc', F + '03_blanc/3R_blanc.svg'], orange: ['Orange', F + '02_monochrome/3R_mono_orange.svg'], nuit: ['Bleu nuit', F + '02_monochrome/3R_mono_bleu-nuit.svg'], noir: ['Noir', F + '02_monochrome/3R_mono_noir.svg'], cimier: ['Cimier orange', F + '05_miniature/3R_cimier_orange.svg'] };
  const FONDS = { blanc: ['Blanc', '#FFFFFF'], gris: ['Gris chaud', '#F4EFEA'], orange: ['Orange', '#FE6501'], nuit: ['Bleu nuit', '#1D2B4F'], noir: ['Noir', '#111111'] };
  const OK = { couleur: ['blanc', 'gris', 'nuit', 'noir'], blanc: ['orange', 'nuit', 'noir'], orange: ['blanc', 'gris', 'nuit'], nuit: ['blanc', 'gris'], noir: ['blanc', 'gris'], cimier: ['blanc', 'gris', 'nuit'] };
  const RAISON = { 'couleur-orange': 'Le médaillon orange disparaît sur un fond orange : utiliser le logo blanc.', 'blanc-blanc': 'Logo blanc invisible sur fond clair.', 'blanc-gris': 'Contraste insuffisant.', 'orange-orange': 'Logo invisible.', 'orange-noir': 'Préférer le logo couleur sur fond noir.', 'nuit-nuit': 'Logo invisible.', 'nuit-orange': 'Bleu sur orange : utiliser le logo blanc.', 'nuit-noir': 'Contraste insuffisant.', 'noir-orange': 'Le noir n’est pas une couleur de l’identité sur orange.', 'noir-nuit': 'Contraste insuffisant.', 'noir-noir': 'Logo invisible.', 'cimier-orange': 'Utiliser le cimier blanc sur orange.', 'cimier-noir': 'Préférer le cimier blanc sur noir.' };
  let etat = { v: 'couleur', f: 'blanc' };
  const boutons = (id, src, cle, pastille) => { $(id).innerHTML = Object.entries(src).map(([k, [nom, col]]) => `<button type="button" data-k="${k}" aria-pressed="${etat[cle] === k}">${pastille ? `<span class="pastille" style="background:${col}"></span>` : ''}${esc(nom)}</button>`).join(''); $(id).addEventListener('click', (e) => { const b = e.target.closest('button'); if (!b) return; etat[cle] = b.dataset.k; majComp(); }); };
  function majComp() {
    document.querySelectorAll('#comp-variante button').forEach((b) => b.setAttribute('aria-pressed', b.dataset.k === etat.v));
    document.querySelectorAll('#comp-fond button').forEach((b) => b.setAttribute('aria-pressed', b.dataset.k === etat.f));
    $('#comp-scene').style.background = FONDS[etat.f][1];
    $('#comp-img').src = VAR[etat.v][1];
    const ok = OK[etat.v].includes(etat.f), v = $('#comp-verdict');
    v.className = 'verdict ' + (ok ? 'ok' : 'ko');
    v.textContent = ok ? '✓ Combinaison autorisée' : '✕ Combinaison interdite. ' + (RAISON[etat.v + '-' + etat.f] || '');
  }
  boutons('#comp-variante', VAR, 'v'); boutons('#comp-fond', FONDS, 'f', true); majComp();

  /* Interdits */
  const INTERDITS = [['Déformer', 'transform:scaleX(1.45)', 'Toujours conserver les proportions.'], ['Recolorer', 'filter:hue-rotate(170deg) saturate(1.3)', 'Seules les versions de la charte existent.'], ['Ajouter une ombre', 'filter:drop-shadow(8px 10px 5px rgba(0,0,0,.55))', 'Pas d’ombre, de contour ni de relief ajouté.'], ['Incliner', 'transform:rotate(-20deg)', 'Le médaillon reste droit, cimier en haut.'], ['Fond chargé', 'BUSY', 'Poser le logo sur un aplat uni.'], ['Recadrer', 'transform:translate(32%,30%) scale(1.5)', 'Le médaillon n’est jamais coupé.'], ['Isoler le monogramme', 'CLIP', 'Le disque RRR seul n’est pas autorisé.'], ['Composer à l’horizontale', 'HORIZ', 'Aucune version horizontale n’est validée.']];
  $('#interdits').innerHTML = INTERDITS.map(([t, st, d]) => {
    let inner = `<img src="${F}01_principal/3R_principal_couleur.svg" alt="" style="${st}">`, bg = '';
    if (st === 'BUSY') { inner = `<img src="${F}01_principal/3R_principal_couleur.svg" alt="">`; bg = 'background:repeating-linear-gradient(45deg,#FE6501 0 12px,#FFB27F 12px 24px,#1D2B4F 24px 36px)'; }
    if (st === 'CLIP') inner = `<img src="${F}01_principal/3R_principal_couleur.svg" alt="" style="clip-path:circle(31% at 50% 53%);transform:scale(1.6)">`;
    if (st === 'HORIZ') inner = `<div style="display:flex;align-items:center;gap:6px;width:86%"><img src="${F}01_principal/3R_principal_couleur.svg" alt="" style="width:38%"><span style="font:700 12px var(--3r-police-titre);line-height:1.15">Rassemblement des Républicains Réformateurs</span></div>`;
    return `<figure class="interdit" style="margin:0"><div class="scene" style="${bg}">${inner}</div><b>✕ ${esc(t)}</b><span>${esc(d)}</span></figure>`;
  }).join('');

  /* Nuancier */
  const COUL = [['Orange 3R', '#FE6501', '254 · 101 · 1', '0 · 70 · 100 · 0', '≈ 1505 C', 'Couleur signature', '#1D2B4F'], ['Bleu nuit', '#1D2B4F', '29 · 43 · 79', '100 · 80 · 30 · 45', '≈ 2767 C', 'Textes, fonds institutionnels', '#FFFFFF'], ['Blanc', '#FFFFFF', '255 · 255 · 255', '0 · 0 · 0 · 0', '—', 'Fonds, logo blanc', '#1D2B4F'], ['Gris chaud', '#F4EFEA', '244 · 239 · 234', '0 · 2 · 4 · 4', '—', 'Fonds de section', '#1D2B4F'], ['Orange foncé', '#C24A00', '194 · 74 · 0', '0 · 75 · 100 · 20', '≈ 1525 C', 'Texte orange sur fond clair', '#FFFFFF'], ['Bleu nuit clair', '#2E4170', '46 · 65 · 112', '90 · 70 · 20 · 25', '—', 'Survols, aplats secondaires', '#FFFFFF'], ['Gris texte', '#4A5672', '74 · 86 · 114', '70 · 55 · 30 · 20', '—', 'Texte secondaire', '#FFFFFF'], ['Gris filet', '#E4DDD4', '228 · 221 · 212', '0 · 3 · 7 · 12', '—', 'Filets, bordures', '#1D2B4F']];
  $('#nuancier').innerHTML = COUL.map(([n, hex, rvb, cmjn, pms, role, fg]) => `<article class="teinte"><div class="puce" style="background:${hex};color:${fg};${hex === '#FFFFFF' ? 'border-bottom:1px solid #E4DDD4' : ''}">${n}</div><dl><dt>HEX</dt><dd>${hex}</dd><dt>RVB</dt><dd>${rvb}</dd><dt>CMJN</dt><dd>${cmjn}</dd><dt>Pantone</dt><dd>${pms}</dd></dl><p class="role">${role}</p><button class="copier" type="button" data-hex="${hex}">Copier ${hex}</button></article>`).join('');
  $('#nuancier').addEventListener('click', (e) => {
    const b = e.target.closest('.copier'); if (!b) return;
    const hex = b.dataset.hex, lbl = 'Copier ' + hex, fin = (t) => { b.textContent = t; setTimeout(() => (b.textContent = lbl), 1500); };
    try { navigator.clipboard.writeText(hex).then(() => fin('Copié ✓'), () => fin(hex)); } catch (_) { fin(hex); }
  });

  /* Galeries */
  const apercuPapeterie = D.apercus.map((a) => ({ cat: a.cat || 'papeterie', id: a.id, titre: a.titre, format: a.format, specs: a.specs, image: a.image }));
  const tout = [...apercuPapeterie, ...M];
  const visuel = (m) => (m.image ? `<img src="${m.image}" alt="">` : m.dessin());
  document.querySelectorAll('[data-galerie]').forEach((g) => {
    const items = tout.filter((m) => m.cat === g.dataset.galerie);
    g.innerHTML = items.map((m) => `<button type="button" class="maquette" data-id="${m.cat}:${m.id}" id="maquette-${m.id}"><div class="apercu">${visuel(m)}</div><h4>${esc(m.titre)}</h4><span class="format">${esc(m.format)}</span><dl class="specs specs-print">${(m.specs || []).map(([k, v]) => `<dt>${esc(k)}</dt><dd>${esc(v)}</dd>`).join('')}</dl></button>`).join('');
  });
  const vis = $('#visionneuse');
  let retour = null;
  document.addEventListener('click', (e) => {
    const b = e.target.closest('.maquette'); if (!b) return;
    const m = tout.find((x) => `${x.cat}:${x.id}` === b.dataset.id); if (!m) return;
    retour = b;
    $('#v-image').innerHTML = visuel(m); $('#v-titre').textContent = m.titre; $('#v-format').textContent = m.format;
    $('#v-specs').innerHTML = (m.specs || []).map(([k, v]) => `<dt>${esc(k)}</dt><dd>${esc(v)}</dd>`).join('');
    $('#v-png').innerHTML = m.image ? '' : `<a class="btn-fichier" href="fichiers/maquettes/${m.cat}/3R_${m.id}.png" download>Télécharger la maquette (PNG)</a>`;
    vis.hidden = false; $('#v-fermer').focus();
  });
  const fermer = () => { vis.hidden = true; if (retour) retour.focus(); };
  $('#v-fermer').addEventListener('click', fermer);
  vis.addEventListener('click', (e) => { if (e.target === vis) fermer(); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && !vis.hidden) fermer(); });

  /* Téléchargements */
  const poids = (o) => (o > 1048576 ? (o / 1048576).toFixed(1).replace('.', ',') + ' Mo' : Math.max(1, Math.round(o / 1024)) + ' Ko');
  $('#fichiers').innerHTML = D.fichiers.length ? D.fichiers.map((g) => `<div class="groupe ${g.archive ? 'archive' : ''}"><h3>${esc(g.groupe)}</h3><ul>${g.items.map((f) => `<li><a href="${f.chemin}" download><span class="ext">${esc(f.chemin.split('.').pop().toUpperCase())}</span><span class="nom">${esc(f.nom)}<span class="desc">${esc(f.desc || '')}</span></span><span class="poids">${poids(f.taille)}</span></a></li>`).join('')}</ul></div>`).join('') : '<p class="small">La liste des fichiers est générée par scripts/construire_site.py.</p>';

  /* Navigation : section active, menu mobile */
  const liens = [...document.querySelectorAll('.nav a')];
  const nav = $('#nav'), mb = $('.menu-btn');
  mb.addEventListener('click', () => { const o = nav.classList.toggle('ouvert'); mb.setAttribute('aria-expanded', o); });
  nav.addEventListener('click', (e) => { if (e.target.closest('a')) { nav.classList.remove('ouvert'); mb.setAttribute('aria-expanded', 'false'); } });
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((es) => es.forEach((en) => { if (en.isIntersecting) liens.forEach((a) => a.classList.toggle('actif', a.getAttribute('href') === '#' + en.target.id)); }), { rootMargin: '-40% 0px -55% 0px' });
    document.querySelectorAll('main > section').forEach((s) => io.observe(s));
  }
})();
