// Génère le modèle PowerPoint institutionnel du 3R (16:9, dispositions nommées, thème aux couleurs 3R).
// Usage : node scripts/generer_modele_powerpoint.js
// Sortie : modeles/powerpoint/3R_modele-presentation.pptx
const path = require('path');
const fs = require('fs');
const pptxgen = require('pptxgenjs');
// applyTheme vient de la compétence pptx (PPTX_SKILL) ; sans elle, le thème garde les couleurs Office par défaut.
const applyTheme = process.env.PPTX_SKILL ? require(process.env.PPTX_SKILL + '/scripts/apply_theme.js').applyTheme : async () => {};

const ROOT = path.join(__dirname, '..');
const OUT = path.join(ROOT, 'modeles', 'powerpoint');
const L = (f) => path.join(ROOT, 'assets', 'logos', f);
const LOGO = L('01_principal/png/3R_principal_couleur_1024px.png'); // 1024 × 1128
const LOGO_BLANC = L('03_blanc/png/3R_blanc_1024px.png');
const CIMIER_BLANC = L('05_miniature/png/3R_cimier_blanc_1024px.png'); // 1024 × 552
const CIMIER_ORANGE = L('05_miniature/png/3R_cimier_orange_1024px.png');
const R_LOGO = 1128 / 1024, R_CIMIER = 552 / 1024;

const THEME = {
  name: '3R Rassemblement des Républicains Réformateurs',
  headFontFace: 'Libre Caslon Text', bodyFontFace: 'Source Sans 3',
  colors: { dk1: '1D2B4F', lt1: 'FFFFFF', dk2: '1D2B4F', lt2: 'F4EFEA', accent1: 'FE6501', accent2: '1D2B4F', accent3: 'C24A00', accent4: '2E4170', accent5: '4A5672', accent6: 'E4DDD4', hlink: 'C24A00', folHlink: '4A5672' },
};

const pres = new pptxgen();
pres.layout = 'LAYOUT_16x9'; // 10 × 5,625 in
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.author = 'Rassemblement des Républicains Réformateurs';
pres.company = 'Rassemblement des Républicains Réformateurs';
pres.title = 'Modèle de présentation 3R';
const C = pres.SchemeColor;
const W = 10, H = 5.625, M = 0.6;

// Pied commun des dispositions claires : cimier orange + nom, numéro de page
const piedClair = [
  { image: { path: CIMIER_ORANGE, x: M, y: H - 0.42, w: 0.42, h: 0.42 * R_CIMIER } },
  { text: { text: 'Rassemblement des Républicains Réformateurs', options: { x: M + 0.52, y: H - 0.47, w: 5, h: 0.3, fontSize: 9, color: C.accent5, margin: 0 } } },
];
const numero = (color) => ({ x: W - M - 0.6, y: H - 0.47, w: 0.6, h: 0.3, fontSize: 9, color, align: 'right', margin: 0 });

pres.defineSlideMaster({
  title: '3R Titre', background: { color: C.text1 },
  objects: [
    { image: { path: LOGO, x: W - M - 2.2, y: (H - 2.2 * R_LOGO) / 2, w: 2.2, h: 2.2 * R_LOGO } },
    { placeholder: { options: { name: 'surtitre', type: 'body', x: M, y: 1.35, w: 5.6, h: 0.35, fontSize: 11, bold: true, charSpacing: 3, color: C.accent1, margin: 0 }, text: 'SURTITRE' } },
    { placeholder: { options: { name: 'title', type: 'title', x: M, y: 1.75, w: 5.9, h: 1.6, fontSize: 38, bold: true, color: C.background1, align: 'left', valign: 'top', margin: 0, fontFace: THEME.headFontFace }, text: 'Titre de la présentation' } },
    { placeholder: { options: { name: 'sous-titre', type: 'body', x: M, y: 3.5, w: 5.6, h: 0.7, fontSize: 14, color: C.background2, margin: 0 }, text: 'Instance · lieu · date' } },
  ],
});
pres.defineSlideMaster({
  title: '3R Intercalaire', background: { color: C.accent1 },
  objects: [
    { image: { path: LOGO_BLANC, x: W - M - 1.5, y: M, w: 1.5, h: 1.5 * R_LOGO } },
    { placeholder: { options: { name: 'numero', type: 'body', x: M, y: 1.7, w: 2, h: 0.9, fontSize: 54, bold: true, color: C.text1, margin: 0, fontFace: THEME.headFontFace }, text: '01' } },
    { placeholder: { options: { name: 'title', type: 'title', x: M, y: 2.65, w: 6.4, h: 1.4, fontSize: 34, bold: true, color: C.text1, align: 'left', valign: 'top', margin: 0, fontFace: THEME.headFontFace }, text: 'Titre de la partie' } },
  ],
});
pres.defineSlideMaster({
  title: '3R Titre seul', background: { color: C.background1 },
  objects: [
    ...piedClair,
    { placeholder: { options: { name: 'title', type: 'title', x: M, y: 0.4, w: W - 2 * M, h: 0.75, fontSize: 26, bold: true, color: C.text1, align: 'left', valign: 'middle', margin: 0, fontFace: THEME.headFontFace }, text: 'Titre de la diapositive' } },
  ],
  slideNumber: numero(C.accent5),
});
pres.defineSlideMaster({
  title: '3R Titre et texte', background: { color: C.background1 },
  objects: [
    ...piedClair,
    { placeholder: { options: { name: 'title', type: 'title', x: M, y: 0.4, w: W - 2 * M, h: 0.75, fontSize: 26, bold: true, color: C.text1, align: 'left', valign: 'middle', margin: 0, fontFace: THEME.headFontFace }, text: 'Titre de la diapositive' } },
    { placeholder: { options: { name: 'body', type: 'body', x: M, y: 1.35, w: W - 2 * M, h: 3.4, fontSize: 16, color: C.text1, valign: 'top', margin: 0, paraSpaceAfter: 8 }, text: 'Texte' } },
  ],
  slideNumber: numero(C.accent5),
});
pres.defineSlideMaster({
  title: '3R Citation', background: { color: C.background2 },
  objects: [
    ...piedClair,
    { text: { text: '«', options: { x: M - 0.05, y: 0.55, w: 1, h: 1, fontSize: 80, color: C.accent1, fontFace: THEME.headFontFace, margin: 0 } } },
    { placeholder: { options: { name: 'citation', type: 'body', x: M, y: 1.45, w: 7.6, h: 2.2, fontSize: 26, italic: true, color: C.text1, valign: 'top', margin: 0, fontFace: THEME.headFontFace }, text: 'Citation' } },
    { placeholder: { options: { name: 'auteur', type: 'body', x: M, y: 3.85, w: 7.6, h: 0.5, fontSize: 13, bold: true, color: C.accent3, margin: 0 }, text: 'Prénom NOM, fonction' } },
  ],
  slideNumber: numero(C.accent5),
});
pres.defineSlideMaster({
  title: '3R Fin', background: { color: C.text1 },
  objects: [
    { image: { path: LOGO, x: (W - 1.9) / 2, y: 0.55, w: 1.9, h: 1.9 * R_LOGO } },
    { placeholder: { options: { name: 'title', type: 'title', x: M, y: 2.85, w: W - 2 * M, h: 0.7, fontSize: 28, bold: true, color: C.background1, align: 'center', margin: 0, fontFace: THEME.headFontFace }, text: 'Merci de votre attention' } },
    { placeholder: { options: { name: 'contact', type: 'body', x: M, y: 3.65, w: W - 2 * M, h: 0.9, fontSize: 13, color: C.background2, align: 'center', margin: 0 }, text: 'Contact' } },
  ],
});

const notes = (s, txt) => s.addNotes(txt);

// --- Diapositives d'exemple (une par disposition) ---
pres.addSection({ title: 'Ouverture' });
let s = pres.addSlide({ masterName: '3R Titre', sectionTitle: 'Ouverture' });
s.addText('RÉUNION INSTITUTIONNELLE', { placeholder: 'surtitre' });
s.addText('[Titre de la présentation]', { placeholder: 'title' });
s.addText('[Instance] · [Lieu] · [Date]', { placeholder: 'sous-titre' });
notes(s, 'Diapositive de titre : fond bleu nuit, médaillon couleur à droite. Remplacer les textes entre crochets.');

s = pres.addSlide({ masterName: '3R Titre et texte', sectionTitle: 'Ouverture' });
s.addText('Ordre du jour', { placeholder: 'title' });
s.addText([
  { text: '[Ouverture de la séance]', options: { bullet: { type: 'number' }, breakLine: true } },
  { text: '[Point n° 2]', options: { bullet: { type: 'number' }, breakLine: true } },
  { text: '[Point n° 3]', options: { bullet: { type: 'number' }, breakLine: true } },
  { text: 'Questions diverses', options: { bullet: { type: 'number' } } },
], { placeholder: 'body' });

pres.addSection({ title: 'Partie 1' });
s = pres.addSlide({ masterName: '3R Intercalaire', sectionTitle: 'Partie 1' });
s.addText('01', { placeholder: 'numero' });
s.addText('[Titre de la partie]', { placeholder: 'title' });
notes(s, 'Intercalaire : fond orange, texte bleu nuit (contraste 4,7 : 1), logo blanc.');

s = pres.addSlide({ masterName: '3R Titre seul', sectionTitle: 'Partie 1' });
s.addText('Chiffres clés', { placeholder: 'title' });
const kpi = [['[000]', 'adhérents'], ['[00]', 'fédérations'], ['[000]', 'réunions'], ['[00]', 'élus']];
const kw = (W - 2 * M - 3 * 0.3) / 4;
kpi.forEach(([n, l], i) => {
  const x = M + i * (kw + 0.3);
  s.addShape(pres.shapes.RECTANGLE, { x, y: 1.6, w: kw, h: 1.9, fill: { color: C.background2 }, line: { type: 'none' }, objectName: `kpi-fond-${i + 1}` });
  s.addText(n, { x: x + 0.2, y: 1.8, w: kw - 0.4, h: 0.9, fontSize: 40, bold: true, color: C.accent3, fontFace: THEME.headFontFace, margin: 0, isTextBox: true, objectName: `kpi-valeur-${i + 1}` });
  s.addText(l, { x: x + 0.2, y: 2.75, w: kw - 0.4, h: 0.4, fontSize: 14, color: C.accent5, margin: 0, isTextBox: true, objectName: `kpi-libelle-${i + 1}` });
});
s.addText('[Source et date des chiffres]', { x: M, y: 3.75, w: 6, h: 0.3, fontSize: 10, color: C.accent5, margin: 0, isTextBox: true });

s = pres.addSlide({ masterName: '3R Titre seul', sectionTitle: 'Partie 1' });
s.addText('Deux colonnes', { placeholder: 'title' });
const cw = (W - 2 * M - 0.5) / 2;
[['[Intitulé de gauche]', '[Texte de la colonne de gauche : deux à quatre lignes.]'], ['[Intitulé de droite]', '[Texte de la colonne de droite : deux à quatre lignes.]']].forEach(([t, b], i) => {
  const x = M + i * (cw + 0.5);
  s.addShape(pres.shapes.OVAL, { x, y: 1.45, w: 0.5, h: 0.5, fill: { color: C.accent1 }, line: { type: 'none' }, objectName: `pastille-${i + 1}` });
  s.addText(String(i + 1), { x, y: 1.45, w: 0.5, h: 0.5, fontSize: 16, bold: true, color: C.text1, align: 'center', valign: 'middle', margin: 0, isTextBox: true });
  s.addText(t, { x, y: 2.1, w: cw, h: 0.45, fontSize: 18, bold: true, color: C.text1, fontFace: THEME.headFontFace, margin: 0, isTextBox: true });
  s.addText(b, { x, y: 2.6, w: cw, h: 1.6, fontSize: 15, color: C.text1, valign: 'top', margin: 0, isTextBox: true });
});

s = pres.addSlide({ masterName: '3R Titre seul', sectionTitle: 'Partie 1' });
s.addText('Calendrier', { placeholder: 'title' });
const etapes = ['[Étape 1]', '[Étape 2]', '[Étape 3]', '[Étape 4]'];
const ew = (W - 2 * M) / etapes.length;
s.addShape(pres.shapes.LINE, { x: M + 0.2, y: 2.05, w: W - 2 * M - 0.4, h: 0, line: { color: C.accent6, width: 2 } });
etapes.forEach((e, i) => {
  const x = M + i * ew;
  s.addShape(pres.shapes.OVAL, { x: x + 0.05, y: 1.9, w: 0.3, h: 0.3, fill: { color: i === 0 ? C.accent1 : C.background1 }, line: { color: C.accent1, width: 2 } });
  s.addText('[jj/mm]', { x, y: 1.35, w: ew - 0.2, h: 0.35, fontSize: 12, bold: true, color: C.accent3, margin: 0, isTextBox: true });
  s.addText(e, { x, y: 2.4, w: ew - 0.2, h: 0.4, fontSize: 16, bold: true, color: C.text1, fontFace: THEME.headFontFace, margin: 0, isTextBox: true });
  s.addText('[Description courte]', { x, y: 2.85, w: ew - 0.25, h: 0.8, fontSize: 13, color: C.accent5, valign: 'top', margin: 0, isTextBox: true });
});

s = pres.addSlide({ masterName: '3R Citation', sectionTitle: 'Partie 1' });
s.addText('[Citation du responsable, une à trois lignes.]', { placeholder: 'citation' });
s.addText('[Prénom NOM], [fonction]', { placeholder: 'auteur' });

pres.addSection({ title: 'Clôture' });
s = pres.addSlide({ masterName: '3R Fin', sectionTitle: 'Clôture' });
s.addText('Merci de votre attention', { placeholder: 'title' });
s.addText('[Prénom NOM] · [fonction] · [contact@site-du-parti] · [site-du-parti]', { placeholder: 'contact' });

fs.mkdirSync(OUT, { recursive: true });
const file = path.join(OUT, '3R_modele-presentation.pptx');
pres.writeFile({ fileName: file }).then(() => applyTheme(file, THEME)).then(() => console.log('ok', file));
