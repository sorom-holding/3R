"""Construit la plateforme web de la charte 3R dans site/ :
copie des fichiers téléchargeables, aperçus des modèles, archives ZIP et site/js/donnees.js.

Usage : python3 scripts/construire_site.py
Prérequis : LibreOffice (variable SOFFICE pour un lanceur particulier), pdftoppm, Pillow.
Ordre complet : construire_site.py → node scripts/exporter.js → construire_site.py
"""
import json, os, shutil, subprocess, sys, tempfile, zipfile, glob
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SITE = os.path.join(ROOT, 'site')
FICH = os.path.join(SITE, 'fichiers')
SOFFICE = os.environ.get('SOFFICE', 'soffice')


def copier(src, dst):
    s, d = os.path.join(ROOT, src), os.path.join(FICH, dst)
    if os.path.isdir(d):
        shutil.rmtree(d)
    if os.path.exists(s):
        shutil.copytree(s, d)


def pdf_vers_png(pdf, sortie, page=1, largeur=900):
    with tempfile.TemporaryDirectory() as t:
        subprocess.run(['pdftoppm', '-png', '-r', '110', '-f', str(page), '-l', str(page), pdf, f'{t}/p'], check=True)
        im = Image.open(glob.glob(f'{t}/p*.png')[0]).convert('RGB')
        im.thumbnail((largeur, largeur * 2))
        im.save(sortie, optimize=True)


def apercus():
    out = os.path.join(FICH, 'apercus')
    os.makedirs(out, exist_ok=True)
    items = []
    with tempfile.TemporaryDirectory() as t:
        bureautique = sorted(glob.glob(os.path.join(ROOT, 'modeles/word/*.docx'))) + sorted(glob.glob(os.path.join(ROOT, 'modeles/powerpoint/*.pptx')))
        cmd = SOFFICE.split() + ['--headless', '--convert-to', 'pdf', '--outdir', t] + bureautique
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        infos = {
            '3R_papier-en-tete': ('Papier à en-tête', 'A4 · Word', [['Fichier', 'modeles/word/3R_papier-en-tete.docx'], ['En-tête', 'Médaillon 16 mm, nom du parti en Caslon Bold, filet orange'], ['Pied', 'Adresse du siège, numéro de page']]),
            '3R_communique-officiel': ('Communiqué officiel', 'A4 · Word', [['Fichier', 'modeles/word/3R_communique-officiel.docx'], ['Structure', 'Surtitre, numéro, lieu et date, titre, chapeau, citation, « ### », contact presse']]),
            '3R_note-information': ('Note d’information', 'A4 · Word', [['Fichier', 'modeles/word/3R_note-information.docx'], ['Structure', 'De, À, Copie, Date, Référence, Diffusion ; contexte, points clés, actions, pièces jointes']]),
            '3R_proces-verbal': ('Procès-verbal', 'A4 · Word', [['Fichier', 'modeles/word/3R_proces-verbal.docx'], ['Structure', 'Instance, quorum, présents, ordre du jour, délibérations, relevé des décisions avec votes, signatures']]),
            '3R_rapport-activite': ('Rapport d’activité', 'A4 · Word', [['Fichier', 'modeles/word/3R_rapport-activite.docx'], ['Structure', 'Couverture, sommaire automatique (à mettre à jour dans Word), chiffres clés, chapitres']]),
            '3R_modele-presentation': ('Présentation PowerPoint', '16:9 · PowerPoint', [['Fichier', 'modeles/powerpoint/3R_modele-presentation.pptx'], ['Dispositions', 'Titre, intercalaire, titre seul, titre et texte, citation, fin'], ['Thème', 'Couleurs et polices 3R intégrées au thème']]),
        }
        for pdf in sorted(glob.glob(f'{t}/*.pdf')):
            nom = os.path.splitext(os.path.basename(pdf))[0]
            titre, fmt, specs = infos[nom]
            pdf_vers_png(pdf, os.path.join(out, nom + '.png'))
            items.append({'id': nom, 'titre': titre, 'format': fmt, 'specs': specs, 'image': f'fichiers/apercus/{nom}.png'})
    bat = {
        'carte-de-visite': ('Carte de visite', '85 × 55 mm · recto verso', 'Papier mat 350 g, impression quadri recto verso'),
        'carte-de-membre': ('Carte de membre', '85,6 × 54 mm · recto verso', 'PVC 0,76 mm ou papier 350 g pelliculé, numérotation variable'),
        'badge-nominatif': ('Badge nominatif', '76 × 32 mm', 'Plastique 1 mm, épingle ou aimant'),
        'enveloppes': ('Enveloppes', 'DL 220 × 110 mm · C4 324 × 229 mm', 'Impression sur enveloppes fermées, sans fond perdu au dos'),
        'chemise': ('Chemise à rabats', 'A4 · à plat 440 × 310 mm', 'Carte 350 g, pelliculage mat, découpe selon le gabarit de l’imprimeur'),
    }
    for dossier, (titre, fmt, sup) in bat.items():
        pdfs = sorted(glob.glob(os.path.join(ROOT, 'modeles/impression', dossier, '*_BAT.pdf')))
        for i, pdf in enumerate(pdfs):
            base = os.path.splitext(os.path.basename(pdf))[0]
            pdf_vers_png(pdf, os.path.join(out, base + '.png'))
            items.append({'id': base, 'titre': titre + (f' ({base.split("_")[1].replace("enveloppe-", "")})' if len(pdfs) > 1 else ''), 'format': fmt,
                          'specs': [['Fichier', os.path.relpath(pdf, ROOT)], ['Support', sup], ['Sources', 'SVG modifiables dans le même dossier'], ['Épreuve', 'Fond perdu 3 mm, traits de coupe']],
                          'image': f'fichiers/apercus/{base}.png'})
    items.append({'id': 'signature-email', 'titre': 'Signature e-mail', 'format': 'HTML · Gmail, Outlook', 'image': None,
                  'specs': [['Fichier', 'modeles/signature-email/3R_signature-email.html'], ['Installation', 'Héberger le logo, remplacer les crochets, copier-coller dans le client mail']]})
    items = [i for i in items if i['image']]
    # Photos de mise en situation finalisées (logos officiels posés par scripts/composer_photos.py)
    photos = [
        ('conference-de-presse', 'evenementiel', 'Conférence de presse (photo)', 'Mur médias 3 000 × 2 400 mm · nappe · drapeau', [['Mur médias', 'Grand médaillon et nom du parti, motif alterné médaillon et cimier'], ['Nappe', 'Bleu nuit, médaillon couleur, bande orange'], ['Drapeau', 'Orange, médaillon blanc']]),
        ('signaletique-evenement', 'evenementiel', 'Totem et signalétique d’événement (photo)', 'Totem 800 × 2 000 mm · panneaux A3', [['Totem', 'Cimier découpé en tête, médaillon couleur, intitulé en Libre Caslon blanc'], ['Panneaux', 'Médaillon couleur, intitulé bleu nuit, flèche orange']]),
        ('accreditations', 'evenementiel', 'Badges et accréditations (photo)', 'A6 · 105 × 148 mm', [['Code couleur', 'Délégué orange, presse bleu nuit, invité gris chaud, organisation orange foncé'], ['Tour de cou', 'Ruban 20 mm assorti à la catégorie']]),
        ('totem-accueil', 'evenementiel', 'Totem d’accueil et panneaux (photo)', 'Totem 800 × 2 000 mm · panneaux A3', [['Totem', 'Médaillon couleur sur bandeau blanc, corps bleu nuit, pied orange'], ['Panneaux', 'Fond blanc, cimier orange, flèche du côté de la direction']]),
        ('roll-up', 'evenementiel', 'Roll-ups d’accueil (photo)', '850 × 2 000 mm', [['Haut', 'Médaillon couleur et nom du parti en Libre Caslon'], ['Corps', 'Bleu nuit, intitulé en blanc'], ['Bas', 'Bandeau orange, adresse du site']]),
    ]
    out = os.path.join(FICH, 'maquettes', 'photos')
    for code, cat, titre, fmt, specs in photos:
        if os.path.exists(os.path.join(out, f'3R_{code}.jpg')):
            items.append({'id': 'photo-' + code, 'cat': cat, 'titre': titre, 'format': fmt, 'specs': specs, 'image': f'fichiers/maquettes/photos/3R_{code}.jpg'})
    return items


DESC = {
    '.svg': 'Vectoriel (web, édition)', '.pdf': 'Vectoriel (impression)', '.png': 'Image transparente', '.docx': 'Modèle Word', '.pptx': 'Modèle PowerPoint',
    '.ttf': 'Police bureautique', '.woff2': 'Police web', '.json': 'Design tokens', '.css': 'Variables CSS', '.ase': 'Nuancier Adobe', '.gpl': 'Nuancier GIMP / Inkscape',
    '.html': 'Signature e-mail', '.ico': 'Favicon', '.webmanifest': 'Manifeste web', '.txt': 'Licence', '.zip': 'Archive',
}


def liste(dossier, motif='*', exclure=()):
    base = os.path.join(FICH, dossier)
    fs = sorted(f for f in glob.glob(os.path.join(base, '**', motif), recursive=True) if os.path.isfile(f) and not any(x in f for x in exclure))
    return [{'nom': os.path.basename(f), 'chemin': os.path.relpath(f, SITE), 'taille': os.path.getsize(f), 'desc': DESC.get(os.path.splitext(f)[1], '')} for f in fs]


def archive(nom, dossiers):
    chemin = os.path.join(FICH, 'archives', nom)
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    with zipfile.ZipFile(chemin, 'w', zipfile.ZIP_DEFLATED) as z:
        for d in dossiers:
            for f in glob.glob(os.path.join(FICH, d, '**', '*'), recursive=True):
                if os.path.isfile(f):
                    z.write(f, os.path.join('3R', os.path.relpath(f, FICH)))
    return chemin


def main():
    copier('assets/logos', 'logos')
    copier('assets/polices', 'polices')
    copier('tokens', 'tokens')
    copier('modeles', 'modeles')
    if os.path.isdir(os.path.join(ROOT, 'maquettes')):
        copier('maquettes', 'maquettes')
    os.makedirs(os.path.join(FICH, 'charte'), exist_ok=True)
    charte = os.path.join(ROOT, 'charte', '3R_charte-graphique.pdf')
    if os.path.exists(charte):
        shutil.copy(charte, os.path.join(FICH, 'charte'))
    items = apercus()
    archive('3R_logos.zip', ['logos'])
    archive('3R_modeles.zip', ['modeles'])
    archive('3R_polices-et-couleurs.zip', ['polices', 'tokens'])
    if os.path.isdir(os.path.join(FICH, 'maquettes')):
        archive('3R_maquettes.zip', ['maquettes'])
    archive('3R_identite-complete.zip', ['logos', 'modeles', 'polices', 'tokens', 'maquettes', 'charte'])
    groupes = [
        {'groupe': 'Archives complètes', 'archive': True, 'items': liste('archives')},
        {'groupe': 'Charte graphique PDF', 'items': liste('charte')},
        {'groupe': 'Logos : officiel et principal', 'items': liste('logos/00_officiel_3D') + liste('logos/01_principal')},
        {'groupe': 'Logos : monochromes, blanc, fonds foncés', 'items': liste('logos/02_monochrome', exclure=('_512', '_1024', '_4096')) + liste('logos/03_blanc', exclure=('_512', '_1024', '_4096')) + liste('logos/04_fonds-fonces', exclure=('_512', '_1024', '_4096'))},
        {'groupe': 'Miniature, avatars, favicons', 'items': liste('logos/05_miniature', exclure=('_512', '_1024', '_4096')) + liste('logos/06_avatar') + liste('logos/07_favicon')},
        {'groupe': 'Modèles Word et PowerPoint', 'items': liste('modeles/word') + liste('modeles/powerpoint') + liste('modeles/signature-email')},
        {'groupe': 'Documents à imprimer (BAT et sources SVG)', 'items': liste('modeles/impression')},
        {'groupe': 'Polices', 'items': liste('polices', '*.ttf') + liste('polices', '*.txt')},
        {'groupe': 'Couleurs et design tokens', 'items': liste('tokens')},
        {'groupe': 'Maquettes PNG et photos', 'items': liste('maquettes', exclure=('sources',))},
    ]
    groupes = [g for g in groupes if g['items']]
    donnees = {'apercus': items, 'fichiers': groupes}
    open(os.path.join(SITE, 'js', 'donnees.js'), 'w').write('/* Généré par scripts/construire_site.py */\nwindow.DONNEES_3R = ' + json.dumps(donnees, ensure_ascii=False, indent=1) + ';\n')
    n = sum(len(g['items']) for g in groupes)
    print(f'{len(items)} aperçus, {n} fichiers téléchargeables')


if __name__ == '__main__':
    main()
