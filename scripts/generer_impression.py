"""Génère les documents imprimés du 3R : sources SVG modifiables (format fini, en mm)
et PDF prêts à imprimer (fond perdu 3 mm, traits de coupe).

Usage : python3 scripts/generer_impression.py
Sorties : modeles/impression/<document>/{*.svg, *_BAT.pdf}
"""
import os
import re
import cairosvg

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUT = os.path.join(ROOT, 'modeles', 'impression')
ORANGE, ORANGE_F, NUIT, BLANC, GRIS, GRIS_T, FILET = '#FE6501', '#C24A00', '#1D2B4F', '#FFFFFF', '#F4EFEA', '#4A5672', '#E4DDD4'
TITRE, TEXTE = "'Libre Caslon Text', Georgia, serif", "'Source Sans 3', Arial, sans-serif"
LOGO_R = 3363.7 / 3051.0          # hauteur / largeur du médaillon
CIMIER_R = 552 / 1024
BLEED, SLUG = 3, 9                # fond perdu et marge de repérage, en mm


def logo(kind, x, y, w):
    files = {'couleur': '01_principal/3R_principal_couleur.svg', 'blanc': '03_blanc/3R_blanc.svg',
             'cimier-orange': '05_miniature/3R_cimier_orange.svg', 'cimier-blanc': '05_miniature/3R_cimier_blanc.svg'}
    r = CIMIER_R if kind.startswith('cimier') else LOGO_R
    # Logo intégré en SVG imbriqué (tracés vectoriels) : la source reste autonome pour l'imprimeur
    src = open(os.path.join(ROOT, 'assets', 'logos', files[kind])).read()
    vb = re.search(r'viewBox="([^"]+)"', src).group(1)
    body = re.sub(r'^.*?<svg[^>]*>|</svg>\s*$', '', src, flags=re.S)
    body = re.sub(r'<title>.*?</title>', '', body)
    return f'<svg x="{x}" y="{y}" width="{w}" height="{w * r:.2f}" viewBox="{vb}">{body}</svg>'


def txt(x, y, s, size, font=TEXTE, weight=400, fill=NUIT, anchor='start', spacing=0, style='normal'):
    return (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" font-weight="{weight}" font-style="{style}" '
            f'fill="{fill}" text-anchor="{anchor}" letter-spacing="{spacing}">{s}</text>')


def rect(x, y, w, h, fill, extra=''):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" {extra}/>'


def svg_fini(w, h, body, titre):
    """Source modifiable : format fini + fond perdu (le fond déborde de 3 mm)."""
    b = BLEED
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{w + 2 * b}mm" height="{h + 2 * b}mm" viewBox="{-b} {-b} {w + 2 * b} {h + 2 * b}">'
            f'<title>{titre} — format fini {w} × {h} mm, fond perdu {b} mm</title>{body}</svg>\n')


def svg_bat(w, h, body, titre):
    """Épreuve PDF : fond perdu, traits de coupe et légende hors format."""
    b, s = BLEED, SLUG
    W, H = w + 2 * (b + s), h + 2 * (b + s)
    marks = []
    for x in (0, w):
        for y0, y1 in ((-b - s, -b - 1), (h + b + 1, h + b + s)):
            marks.append(f'<line x1="{x}" y1="{y0}" x2="{x}" y2="{y1}"/>')
    for y in (0, h):
        for x0, x1 in ((-b - s, -b - 1), (w + b + 1, w + b + s)):
            marks.append(f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}"/>')
    legende = txt(3, h + b + s - 2, f'3R · {titre} · format fini {w} × {h} mm · fond perdu {b} mm · CMJN : voir charte', 2.2, fill='#000000')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="{-b - s} {-b - s} {W} {H}">'
            f'{rect(-b - s, -b - s, W, H, BLANC)}<svg x="{-b}" y="{-b}" width="{w + 2 * b}" height="{h + 2 * b}" viewBox="{-b} {-b} {w + 2 * b} {h + 2 * b}">{body}</svg>'
            f'<g stroke="#000000" stroke-width="0.15">{"".join(marks)}</g>{legende}</svg>\n')


def produire(dossier, nom, w, h, faces, titre):
    """faces : liste de (suffixe, corps SVG). Écrit un SVG par face et un PDF multipage (BAT)."""
    global OUT_DIR
    OUT_DIR = os.path.join(OUT, dossier)
    os.makedirs(OUT_DIR, exist_ok=True)
    pages = []
    for suffixe, corps_fn in faces:
        body = corps_fn()
        f = f'{nom}_{suffixe}' if suffixe else nom
        open(os.path.join(OUT_DIR, f + '.svg'), 'w').write(svg_fini(w, h, body, titre))
        pdf = os.path.join(OUT_DIR, f'.{f}.pdf')
        cairosvg.svg2pdf(bytestring=svg_bat(w, h, body, f'{titre} {suffixe}'.strip()).encode(), write_to=pdf, url=os.path.join(OUT_DIR, 'x.svg'))
        pages.append(pdf)
    from pypdf import PdfWriter
    wtr = PdfWriter()
    for pg in pages:
        wtr.append(pg)
        os.remove(pg)
    wtr.write(os.path.join(OUT_DIR, f'{nom}_BAT.pdf'))


B = BLEED
PH = {'nom': '[Prénom NOM]', 'fonction': '[Fonction]', 'tel': '+000 00 00 00 00', 'mail': 'prenom.nom@[site-du-parti]', 'adr': 'Siège national · [Adresse], [Ville]', 'site': '[site-du-parti]'}


def carte_visite():
    w, h = 85, 55
    recto = lambda: rect(-B, -B, w + 2 * B, h + 2 * B, ORANGE) + logo('blanc', (w - 26) / 2, (h - 26 * LOGO_R) / 2, 26)
    verso = lambda: (rect(-B, -B, w + 2 * B, h + 2 * B, BLANC) + rect(-B, -B, 4 + B, h + 2 * B, ORANGE)
                     + txt(10, 15, PH['nom'], 5.2, TITRE, 700) + txt(10, 20.5, PH['fonction'].upper(), 2.3, weight=700, fill=ORANGE_F, spacing=0.35)
                     + txt(10, 38, f"T. {PH['tel']}", 2.6, fill=GRIS_T) + txt(10, 42, PH['mail'], 2.6, fill=GRIS_T) + txt(10, 46, PH['adr'], 2.6, fill=GRIS_T)
                     + logo('couleur', w - 6 - 14, 6, 14))
    produire('carte-de-visite', '3R_carte-de-visite', w, h, [('recto', recto), ('verso', verso)], 'Carte de visite')


def carte_membre():
    w, h = 85.6, 54
    recto = lambda: (rect(-B, -B, w + 2 * B, h + 2 * B, BLANC) + rect(-B, -B, 29 + B, h + 2 * B, ORANGE) + logo('blanc', 4.5, (h - 20 * LOGO_R) / 2, 20)
                     + txt(35, 11, "CARTE D'ADHÉRENT · [ANNÉE]", 2.3, weight=700, fill=ORANGE_F, spacing=0.35)
                     + txt(35, 24, '[Prénom]', 4.6, TITRE, 700) + txt(35, 30, '[NOM]', 4.6, TITRE, 700)
                     + txt(35, 44, 'N° [000 000]', 2.6, fill=GRIS_T) + txt(35, 48, 'Fédération [Ville]', 2.6, fill=GRIS_T))
    verso = lambda: (rect(-B, -B, w + 2 * B, h + 2 * B, NUIT) + logo('cimier-orange', 6, 6, 14)
                     + txt(6, 22, 'Rassemblement des Républicains Réformateurs', 3.1, TITRE, 700, BLANC)
                     + txt(6, 28, "Cette carte est personnelle. En cas de perte, contacter le siège national.", 2.2, fill=GRIS)
                     + txt(6, 44, 'Signature du titulaire', 2.2, fill=GRIS) + f'<line x1="6" y1="49" x2="40" y2="49" stroke="{GRIS}" stroke-width="0.2"/>'
                     + txt(w - 6, 49, PH['site'], 2.4, weight=700, fill=ORANGE, anchor='end'))
    produire('carte-de-membre', '3R_carte-de-membre', w, h, [('recto', recto), ('verso', verso)], "Carte d'adhérent")


def badge():
    w, h = 76, 32  # badge nominatif à épingle ou aimant
    corps = lambda: (rect(-B, -B, w + 2 * B, h + 2 * B, BLANC) + rect(-B, h - 6, w + 2 * B, 6 + B, ORANGE) + logo('couleur', 5, 4, 15)
                     + txt(24, 13, '[Prénom NOM]', 4.4, TITRE, 700) + txt(24, 19, '[FONCTION]', 2.3, weight=700, fill=ORANGE_F, spacing=0.35)
                     + txt(w / 2, h - 2.2, 'RASSEMBLEMENT DES RÉPUBLICAINS RÉFORMATEURS', 1.9, weight=700, fill=NUIT, anchor='middle', spacing=0.25))
    produire('badge-nominatif', '3R_badge-nominatif', w, h, [('', corps)], 'Badge nominatif')


def enveloppes():
    for nom, w, h, lw in (('3R_enveloppe-DL', 220, 110, 16), ('3R_enveloppe-C4', 324, 229, 22)):
        corps = lambda w=w, h=h, lw=lw: (rect(-B, -B, w + 2 * B, h + 2 * B, BLANC) + logo('couleur', 12, 10, lw)
                                         + txt(14 + lw, 17, 'Rassemblement des Républicains Réformateurs', 3.6, TITRE, 700)
                                         + txt(14 + lw, 22, PH['adr'], 2.8, fill=GRIS_T)
                                         + rect(-B, h - 4, w + 2 * B, 4 + B, ORANGE))
        produire('enveloppes', nom, w, h, [('', corps)], 'Enveloppe ' + nom.split('-')[-1])


def chemise():
    # Chemise A4 à rabat, à plat : dos (gauche) + face (droite), 2 × 220 × 310 mm. Découpe et rabat : gabarit de l'imprimeur.
    w, h = 440, 310
    face = lambda: (rect(-B, -B, w + 2 * B, h + 2 * B, NUIT)
                    + rect(220, -B, 220 + B, h + 2 * B, NUIT) + logo('couleur', 220 + 20, 24, 46)
                    + txt(240, 200, '[Titre du dossier]', 14, TITRE, 700, BLANC) + txt(240, 212, '[Instance · date]', 6, fill=GRIS)
                    + rect(240, 280, 180, 0.8, ORANGE)
                    + txt(240, 292, 'Rassemblement des Républicains Réformateurs', 5, TITRE, 700, BLANC)
                    + logo('cimier-orange', 20, 24, 24) + txt(20, 280, PH['adr'], 4, fill=GRIS) + txt(20, 287, f"{PH['site']} · T. {PH['tel']}", 4, fill=GRIS)
                    + f'<line x1="220" y1="-3" x2="220" y2="{h + 3}" stroke="{ORANGE}" stroke-width="0.2" stroke-dasharray="2 2" opacity="0.6"/>')
    interieur = lambda: (rect(-B, -B, w + 2 * B, h + 2 * B, GRIS) + logo('cimier-orange', 220 + 160, 250, 32))
    produire('chemise', '3R_chemise-A4', w, h, [('exterieur', face), ('interieur', interieur)], 'Chemise A4 à plat')


if __name__ == '__main__':
    carte_visite(); carte_membre(); badge(); enveloppes(); chemise()
