// Génère les modèles Word institutionnels du 3R (A4, modifiables).
// Usage : node scripts/generer_modeles_word.js
// Sortie : modeles/word/*.docx
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Header, Footer, Table, TableRow, TableCell,
  WidthType, BorderStyle, AlignmentType, ShadingType, PageNumber, TabStopType, LevelFormat,
  HeadingLevel, PageBreak, VerticalAlign, TableOfContents, PositionalTab, PositionalTabAlignment,
  PositionalTabRelativeTo, PositionalTabLeader, LineRuleType,
} = require('docx');

const ROOT = path.join(__dirname, '..');
const OUT = path.join(ROOT, 'modeles', 'word');
const C = { orange: 'FE6501', orangeFonce: 'C24A00', nuit: '1D2B4F', grisTexte: '4A5672', filet: 'E4DDD4', gris: 'F4EFEA', blanc: 'FFFFFF' };
const TITRE = 'Libre Caslon Text';
const TEXTE = 'Source Sans 3';
const LOGO = fs.readFileSync(path.join(ROOT, 'assets/logos/01_principal/png/3R_principal_couleur_512px.png'));
const LOGO_BLANC = fs.readFileSync(path.join(ROOT, 'assets/logos/03_blanc/png/3R_blanc_512px.png'));
const LOGO_RATIO = 564 / 512;
const PAGE_W = 11906, MARGE = 1134, LARGEUR = PAGE_W - 2 * MARGE; // A4, marges 20 mm
const AUCUNE = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
const SANS_BORDURE = { top: AUCUNE, bottom: AUCUNE, left: AUCUNE, right: AUCUNE };
const ADRESSE = 'Siège national · [Adresse] · [Ville] · Tél. [+000 00 00 00 00] · [contact@site-du-parti] · [site-du-parti]';

// ---------- briques communes ----------
const t = (text, o = {}) => new TextRun({ text, font: o.font || TEXTE, size: o.size, bold: o.bold, italics: o.italics, color: o.color || C.nuit, allCaps: o.caps, characterSpacing: o.spacing });
const p = (children, o = {}) => new Paragraph({ children: Array.isArray(children) ? children : [children], spacing: { before: o.before ?? 0, after: o.after ?? 120, line: o.line ?? 276, lineRule: LineRuleType.AUTO }, alignment: o.align, border: o.border, style: o.style, numbering: o.numbering, keepNext: o.keepNext, tabStops: o.tabs, indent: o.indent, shading: o.shading });
const texte = (s, o = {}) => p(t(s, o), o);
const surtitre = (s, o = {}) => p(t(s, { size: 17, bold: true, caps: true, spacing: 40, color: C.orangeFonce }), { after: 60, ...o });
const filetOrange = (after = 240) => p([], { after, border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: C.orange, space: 1 } } });
const logo = (h = 60, blanc = false) => new ImageRun({ type: 'png', data: blanc ? LOGO_BLANC : LOGO, transformation: { width: Math.round(h / LOGO_RATIO), height: h }, altText: { title: 'Logo 3R', description: 'Médaillon du Rassemblement des Républicains Réformateurs', name: 'logo-3R' } });

function cell(children, w, o = {}) {
  return new TableCell({
    children: Array.isArray(children) ? children : [children], width: { size: w, type: WidthType.DXA },
    borders: o.borders || SANS_BORDURE, verticalAlign: o.valign || VerticalAlign.TOP,
    shading: o.fill ? { fill: o.fill, type: ShadingType.CLEAR, color: 'auto' } : undefined,
    margins: o.margins || { top: 60, bottom: 60, left: 100, right: 100 }, columnSpan: o.span,
  });
}
function table(widths, rows, o = {}) {
  return new Table({ width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA }, columnWidths: widths, rows: rows.map((r) => new TableRow({ children: r, tableHeader: o.header && r === rows[0] })) });
}
const grille = { top: { style: BorderStyle.SINGLE, size: 4, color: C.filet }, bottom: { style: BorderStyle.SINGLE, size: 4, color: C.filet }, left: { style: BorderStyle.SINGLE, size: 4, color: C.filet }, right: { style: BorderStyle.SINGLE, size: 4, color: C.filet } };

function entete() {
  return new Header({ children: [
    table([1100, LARGEUR - 1100], [[
      cell(p(logo(58), { after: 0, line: 240 }), 1100, { valign: VerticalAlign.CENTER, margins: { top: 0, bottom: 0, left: 0, right: 0 } }),
      cell([
        p(t('Rassemblement des Républicains Réformateurs', { font: TITRE, bold: true, size: 24 }), { after: 20 }),
        p(t('3R · Siège national', { size: 16, color: C.grisTexte, caps: true, spacing: 30 }), { after: 0 }),
      ], LARGEUR - 1100, { valign: VerticalAlign.CENTER }),
    ]]),
    filetOrange(0),
  ] });
}
function pied() {
  return new Footer({ children: [
    p([
      t(ADRESSE, { size: 15, color: C.grisTexte }),
      new TextRun({ text: '\t', font: TEXTE, size: 15 }),
      new TextRun({ children: [PageNumber.CURRENT], font: TEXTE, size: 15, color: C.grisTexte }),
    ], { after: 0, tabs: [{ type: TabStopType.RIGHT, position: LARGEUR }], border: { top: { style: BorderStyle.SINGLE, size: 4, color: C.filet, space: 6 } } }),
  ] });
}

const styles = {
  default: { document: { run: { font: TEXTE, size: 21, color: C.nuit }, paragraph: { spacing: { after: 120, line: 276, lineRule: LineRuleType.AUTO } } } },
  paragraphStyles: [
    { id: 'Title', name: 'Title', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font: TITRE, size: 44, bold: true, color: C.nuit }, paragraph: { spacing: { before: 0, after: 160, line: 252, lineRule: LineRuleType.AUTO } } },
    { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font: TITRE, size: 32, bold: true, color: C.nuit }, paragraph: { spacing: { before: 360, after: 120 }, keepNext: true, outlineLevel: 0 } },
    { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font: TITRE, size: 26, bold: true, color: C.nuit }, paragraph: { spacing: { before: 240, after: 80 }, keepNext: true, outlineLevel: 1 } },
    { id: 'Heading3', name: 'Heading 3', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font: TEXTE, size: 19, bold: true, color: C.orangeFonce, allCaps: true, characterSpacing: 30 }, paragraph: { spacing: { before: 200, after: 60 }, keepNext: true, outlineLevel: 2 } },
    { id: 'Chapeau', name: 'Chapeau', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font: TITRE, size: 24, italics: true, color: C.nuit }, paragraph: { spacing: { after: 200, line: 300, lineRule: LineRuleType.AUTO } } },
    { id: 'Legende', name: 'Légende 3R', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font: TEXTE, size: 17, color: C.grisTexte }, paragraph: { spacing: { after: 80 } } },
  ],
};
const numbering = { config: [
  { reference: 'puces', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 360, hanging: 240 } }, run: { color: C.orange } } }] },
  { reference: 'ordre', levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 400, hanging: 400 } }, run: { bold: true, color: C.orangeFonce } } }] },
] };
const puce = (s) => new Paragraph({ numbering: { reference: 'puces', level: 0 }, children: [t(s)], spacing: { after: 60 } });
const point = (s) => new Paragraph({ numbering: { reference: 'ordre', level: 0 }, children: [t(s)], spacing: { after: 60 } });
const h1 = (s) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(s)] });
const h2 = (s) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(s)] });
const h3 = (s) => new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun(s)] });
const corps = (n = 2) => Array.from({ length: n }, () => texte('[Texte à rédiger. Phrases courtes, un paragraphe par idée. Le texte courant se compose en Source Sans 3, 10,5 pt, interligne 1,2, en bleu nuit.]'));
const page = { size: { width: PAGE_W, height: 16838 }, margin: { top: 2100, bottom: 1300, left: MARGE, right: MARGE, header: 600, footer: 500 } };

function doc(titreDoc, children, o = {}) {
  return new Document({
    creator: 'Rassemblement des Républicains Réformateurs', title: titreDoc, description: 'Modèle institutionnel 3R', styles, numbering,
    features: { updateFields: !!o.toc },
    sections: o.sections || [{ properties: { page }, headers: { default: entete() }, footers: { default: pied() }, children }],
  });
}
const champs = (paires, wLabel = 1900) => table([wLabel, LARGEUR - wLabel], paires.map(([k, v]) => [
  cell(p(t(k, { size: 17, bold: true, caps: true, spacing: 30, color: C.grisTexte }), { after: 0 }), wLabel, { borders: { ...SANS_BORDURE, bottom: { style: BorderStyle.SINGLE, size: 4, color: C.filet } } }),
  cell(p(t(v), { after: 0 }), LARGEUR - wLabel, { borders: { ...SANS_BORDURE, bottom: { style: BorderStyle.SINGLE, size: 4, color: C.filet } } }),
]));

// ---------- 1. Papier à en-tête ----------
const lettre = doc('Papier à en-tête 3R', [
  texte('[Ville], le [date]', { align: AlignmentType.RIGHT, after: 360 }),
  texte('[Prénom NOM]', { after: 0, indent: { left: 5400 } }), texte('[Fonction]', { after: 0, indent: { left: 5400 } }),
  texte('[Organisation]', { after: 0, indent: { left: 5400 } }), texte('[Adresse]', { after: 0, indent: { left: 5400 } }),
  texte('[Code postal, Ville]', { after: 480, indent: { left: 5400 } }),
  p([t('Réf. : ', { bold: true }), t('[3R/SG/2026/000]')], { after: 40 }),
  p([t('Objet : ', { bold: true }), t('[objet du courrier]')], { after: 360 }),
  texte('Madame, Monsieur,', { after: 200 }),
  ...corps(3),
  texte("Nous vous prions d'agréer, Madame, Monsieur, l'expression de notre haute considération.", { before: 120, after: 600 }),
  texte('[Prénom NOM]', { bold: true, after: 0, indent: { left: 5400 } }),
  texte('[Fonction au sein du 3R]', { color: C.grisTexte, indent: { left: 5400 } }),
]);

// ---------- 2. Communiqué officiel ----------
const communique = doc('Communiqué officiel 3R', [
  surtitre('Communiqué officiel'),
  p([t('N° [000/2026]', { size: 18, color: C.grisTexte }), t('   ·   [Ville], le [date]', { size: 18, color: C.grisTexte })], { after: 240 }),
  new Paragraph({ style: 'Title', children: [new TextRun('[Titre du communiqué, en une ou deux lignes]')] }),
  new Paragraph({ style: 'Chapeau', children: [new TextRun("[Chapeau : l'essentiel de l'information en deux ou trois phrases. Qui, quoi, quand, où.]")] }),
  ...corps(3),
  h3('Citation'),
  p(t('« [Citation du responsable, une à trois phrases.] »', { font: TITRE, italics: true, size: 24 }), { indent: { left: 400 }, border: { left: { style: BorderStyle.SINGLE, size: 18, color: C.orange, space: 12 } }, after: 60 }),
  p(t('[Prénom NOM], [fonction]', { size: 18, color: C.grisTexte }), { indent: { left: 400 }, after: 240 }),
  ...corps(1),
  texte('###', { align: AlignmentType.CENTER, bold: true, color: C.orange, before: 240, after: 240 }),
  table([LARGEUR], [[cell([
    p(t('Contact presse', { size: 17, bold: true, caps: true, spacing: 30, color: C.orangeFonce }), { after: 40 }),
    p(t('[Prénom NOM] · [fonction] · Tél. [+000 00 00 00 00] · [presse@site-du-parti]', { size: 19 }), { after: 0 }),
  ], LARGEUR, { fill: C.gris, margins: { top: 140, bottom: 140, left: 200, right: 200 } })]]),
]);

// ---------- 3. Note d'information ----------
const note = doc("Note d'information 3R", [
  surtitre("Note d'information"),
  new Paragraph({ style: 'Title', children: [new TextRun('[Objet de la note]')] }),
  champs([['De', '[Émetteur, fonction]'], ['À', '[Destinataires]'], ['Copie', '[Personnes en copie]'], ['Date', '[jj/mm/aaaa]'], ['Référence', '[3R/NI/2026/000]'], ['Diffusion', '[Interne · Restreinte · Publique]']]),
  h2('1. Contexte'), ...corps(2),
  h2('2. Points clés'), puce('[Point clé n° 1]'), puce('[Point clé n° 2]'), puce('[Point clé n° 3]'),
  h2('3. Actions demandées'),
  table([600, 5200, 2000, LARGEUR - 7800], [
    ['N°', 'Action', 'Responsable', 'Échéance'].map((s, i) => cell(p(t(s, { size: 17, bold: true, color: C.blanc, caps: true }), { after: 0 }), [600, 5200, 2000, LARGEUR - 7800][i], { fill: C.nuit })),
    ...[1, 2, 3].map((n) => ['' + n, '[Action à mener]', '[Nom]', '[Date]'].map((s, i) => cell(p(t(s), { after: 0 }), [600, 5200, 2000, LARGEUR - 7800][i], { borders: grille }))),
  ], { header: true }),
  h2('4. Pièces jointes'), puce('[Document 1]'), puce('[Document 2]'),
]);

// ---------- 4. Procès-verbal ----------
const W4 = [600, 5038, 1200, 1400, LARGEUR - 8238];
const pv = doc('Procès-verbal 3R', [
  surtitre('Procès-verbal'),
  new Paragraph({ style: 'Title', children: [new TextRun('[Instance] du [date]')] }),
  champs([['Instance', '[Bureau politique · Conseil national · Assemblée générale · Congrès]'], ['Date et heure', '[jj/mm/aaaa], de [hh:mm] à [hh:mm]'], ['Lieu', '[Lieu, ville]'], ['Présidence', '[Prénom NOM, fonction]'], ['Secrétariat', '[Prénom NOM, fonction]'], ['Quorum', '[nombre] membres présents ou représentés sur [nombre] : quorum [atteint / non atteint]']], 2200),
  h2('Présents, représentés, excusés'),
  h3('Présents'), texte('[Liste des membres présents]'),
  h3('Représentés'), texte('[Membre représenté par membre mandataire]'),
  h3('Excusés'), texte('[Liste des membres excusés]'),
  h2('Ordre du jour'), point('[Approbation du procès-verbal de la séance précédente]'), point('[Point n° 2]'), point('[Point n° 3]'), point('Questions diverses'),
  h2('Délibérations'),
  h3('Point 1 · [intitulé]'), ...corps(1),
  h3('Point 2 · [intitulé]'), ...corps(1),
  h2('Relevé des décisions'),
  table(W4, [
    ['N°', 'Décision', 'Pour', 'Contre', 'Abstention'].map((s, i) => cell(p(t(s, { size: 17, bold: true, color: C.blanc, caps: true }), { after: 0 }), W4[i], { fill: C.nuit })),
    ...[1, 2].map((n) => [`D${n}`, '[Texte de la décision]', '[0]', '[0]', '[0]'].map((s, i) => cell(p(t(s), { after: 0, align: i > 1 ? AlignmentType.CENTER : undefined }), W4[i], { borders: grille }))),
  ], { header: true }),
  texte(`L'ordre du jour étant épuisé, la séance est levée à [hh:mm].`, { before: 240, after: 480 }),
  table([LARGEUR / 2, LARGEUR / 2], [[
    cell([texte('Le Président de séance', { bold: true, after: 720 }), texte('[Prénom NOM]', { color: C.grisTexte })], LARGEUR / 2),
    cell([texte('Le Secrétaire de séance', { bold: true, after: 720 }), texte('[Prénom NOM]', { color: C.grisTexte })], LARGEUR / 2),
  ]]),
]);

// ---------- 5. Rapport d'activité ----------
const couverture = [
  p([], { after: 2400 }),
  p(logo(190), { align: AlignmentType.LEFT, after: 600, line: 240 }),
  surtitre("Rapport d'activité"),
  p(t('[Année 2026]', { font: TITRE, bold: true, size: 72 }), { after: 120, line: 240 }),
  p(t('[Sous-titre : fédération, période ou thème]', { font: TITRE, italics: true, size: 30, color: C.grisTexte }), { after: 1600 }),
  filetOrange(120),
  texte('Rassemblement des Républicains Réformateurs', { bold: true, after: 0 }),
  texte('[Instance émettrice] · [Date de publication]', { color: C.grisTexte }),
];
const kpis = (vals) => table(vals.map(() => LARGEUR / vals.length), [vals.map(([n, l]) => cell([
  p(t(n, { font: TITRE, bold: true, size: 44, color: C.orangeFonce }), { after: 0 }),
  p(t(l, { size: 17, color: C.grisTexte }), { after: 0 }),
], LARGEUR / vals.length, { fill: C.gris, margins: { top: 160, bottom: 160, left: 180, right: 120 }, borders: { ...SANS_BORDURE, left: { style: BorderStyle.SINGLE, size: 18, color: C.blanc } } }))]);
const rapport = doc("Rapport d'activité 3R", null, {
  toc: true,
  sections: [
    { properties: { page: { ...page, margin: { ...page.margin, top: 1134 } } }, children: couverture },
    { properties: { page }, headers: { default: entete() }, footers: { default: pied() }, children: [
      new Paragraph({ style: 'Title', children: [new TextRun('Sommaire')] }),
      new TableOfContents('Sommaire', { hyperlink: true, headingStyleRange: '1-2' }),
      p(new PageBreak()),
      h1('Le mot du président'), ...corps(3),
      h1('Chiffres clés'), kpis([['[000]', 'adhérents'], ['[00]', 'fédérations'], ['[000]', 'réunions tenues'], ['[00]', 'élus']]),
      p(t('[Source et date des chiffres]', { size: 17, color: C.grisTexte }), { before: 80 }),
      h1('Activités de l\'année'), h2('Vie du parti'), ...corps(2), h2('Formation des militants'), ...corps(2), h2('Relations institutionnelles'), ...corps(2),
      h1('Fédérations'), ...corps(1),
      h1('Perspectives'), ...corps(2),
    ] },
  ],
});

fs.mkdirSync(OUT, { recursive: true });
const docs = { '3R_papier-en-tete.docx': lettre, '3R_communique-officiel.docx': communique, '3R_note-information.docx': note, '3R_proces-verbal.docx': pv, '3R_rapport-activite.docx': rapport };
Promise.all(Object.entries(docs).map(([f, d]) => Packer.toBuffer(d).then((b) => fs.writeFileSync(path.join(OUT, f), b)))).then(() => console.log('ok', Object.keys(docs).join(', ')));
