"""Applique les visuels officiels 3R sur les photos de mise en situation (versions « B » vierges).

Chaque surface est décrite par ses quatre coins dans la photo (haut-gauche, haut-droit, bas-droit,
bas-gauche). Le visuel est dessiné en SVG à partir des logos vectoriels officiels, mis en perspective,
puis éclairé comme la surface d'origine et légèrement adouci pour se fondre dans la photo.

Usage : python3 scripts/composer_photos.py [maquettes/photos/sources]
Sortie : maquettes/photos/3R_<code>.jpg
"""
import io, os, re, sys
import cairosvg
import cv2
import numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUT = os.path.join(ROOT, 'maquettes', 'photos')
O, OF, N, B, G, GT = '#FE6501', '#C24A00', '#1D2B4F', '#FFFFFF', '#F4EFEA', '#4A5672'
SERIF, SANS = "'Libre Caslon Text', Georgia, serif", "'Source Sans 3', Arial, sans-serif"
FICHIERS = {'couleur': '01_principal/3R_principal_couleur.svg', 'blanc': '03_blanc/3R_blanc.svg',
            'cimier-orange': '05_miniature/3R_cimier_orange.svg', 'cimier-blanc': '05_miniature/3R_cimier_blanc.svg'}
RATIO = {'couleur': 1.1025, 'blanc': 1.1025, 'cimier-orange': 0.538, 'cimier-blanc': 0.538}


def logo(kind, cx, cy, w):
    """Logo officiel imbriqué (tracés vectoriels), centré en (cx, cy), largeur w."""
    src = open(os.path.join(ROOT, 'assets', 'logos', FICHIERS[kind])).read()
    vb = re.search(r'viewBox="([^"]+)"', src).group(1)
    body = re.sub(r'<title>.*?</title>', '', re.sub(r'^.*?<svg[^>]*>|</svg>\s*$', '', src, flags=re.S))
    h = w * RATIO[kind]
    return f'<svg x="{cx - w / 2}" y="{cy - h / 2}" width="{w}" height="{h}" viewBox="{vb}">{body}</svg>'


def t(x, y, s, size, font=SANS, w=700, fill=N, anchor='start', ls=0, style='normal'):
    return f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" font-weight="{w}" font-style="{style}" fill="{fill}" text-anchor="{anchor}" letter-spacing="{ls}">{s}</text>'


def r(x, y, w, h, fill, extra=''):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" {extra}/>'


def rendu(body, w, h, px):
    """Rend un visuel SVG de w × h unités en image RGBA de px pixels de large."""
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">{body}</svg>'
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=px)
    return np.asarray(Image.open(io.BytesIO(png)).convert('RGBA')).astype(np.float32) / 255


def eclairage(photo, masque):
    """Éclairage de la surface d'origine : plan ajusté sur ses zones claires, normalisé autour de 1."""
    lum = cv2.cvtColor(photo, cv2.COLOR_RGB2GRAY).astype(np.float32)
    ys, xs = np.nonzero(masque)
    v = lum[ys, xs]
    clair = v >= np.percentile(v, 70)
    A = np.c_[np.ones(clair.sum()), xs[clair], ys[clair]]
    coef, *_ = np.linalg.lstsq(A, v[clair], rcond=None)
    H, W = lum.shape
    yy, xx = np.mgrid[:H, :W]
    plan = coef[0] + coef[1] * xx + coef[2] * yy
    # seule la variation de lumière compte : le plan est ramené à 1 en moyenne sur la surface
    return np.clip(plan / np.median(plan[ys, xs]), 0.85, 1.08)


def appliquer(photo, quad, visuel, adoucir=0.7, grain=2.0, opacite=1.0):
    H, W = photo.shape[:2]
    h, w = visuel.shape[:2]
    M = cv2.getPerspectiveTransform(np.float32([[0, 0], [w, 0], [w, h], [0, h]]), np.float32(quad))
    rgba = cv2.warpPerspective(visuel, M, (W, H), flags=cv2.INTER_CUBIC)
    masque = cv2.warpPerspective(np.ones((h, w), np.float32), M, (W, H), flags=cv2.INTER_LINEAR)
    masque = cv2.GaussianBlur(masque, (0, 0), 0.6)
    lum = eclairage(photo, masque > 0.5)
    rgb = rgba[..., :3] * lum[..., None]
    if adoucir:
        rgb = cv2.GaussianBlur(rgb, (0, 0), adoucir)
    rgb = rgb + np.random.default_rng(3).normal(0, grain / 255, rgb.shape).astype(np.float32)
    a = (masque * rgba[..., 3] * opacite)[..., None]
    base = photo.astype(np.float32) / 255
    return (np.clip(base * (1 - a) + rgb * a, 0, 1) * 255).astype(np.uint8)


# ---------- visuels conformes à la charte ----------
def badge(categorie, fond, texte):
    w, h = 105, 148
    return w, h, (r(0, 0, w, h, B) + logo('couleur', w / 2, 34, 38) + t(w / 2, 78, '[Prénom]', 11, SERIF, 700, anchor='middle')
                  + t(w / 2, 92, '[NOM]', 11, SERIF, 700, anchor='middle') + t(w / 2, 104, '[Fédération]', 6, w=400, fill=GT, anchor='middle')
                  + r(0, h - 26, w, 26, fond) + t(w / 2, h - 10, categorie, 7.5, w=700, fill=texte, anchor='middle', ls=1.2))


def totem():
    w, h = 300, 700
    return w, h, (r(0, 0, w, h, N) + r(0, 0, w, 250, B) + logo('couleur', w / 2, 125, 170)
                  + t(28, 360, 'BIENVENUE', 13, w=700, fill=O, ls=3) + t(28, 410, 'Siège', 46, SERIF) .replace(f'fill="{N}"', f'fill="{B}"')
                  + t(28, 462, 'national', 46, SERIF).replace(f'fill="{N}"', f'fill="{B}"') + r(28, 492, 70, 4, O)
                  + t(28, 530, 'Accueil au rez-de-chaussée', 14, w=400, fill=G) + r(0, h - 80, w, 80, O)
                  + t(w / 2, h - 34, '[site-du-parti]', 15, w=700, fill=N, anchor='middle'))


def panneau(texte, sens):
    w, h = 320, 265
    fl = (f'<path d="M232 182 h40 v-16 l34 26 l-34 26 v-16 h-40 Z" fill="{O}"/>' if sens > 0 else
          f'<path d="M88 182 h-40 v-16 l-34 26 l34 26 v-16 h40 Z" fill="{O}"/>')
    lignes = texte.split('|')
    corps = ''.join(t(26 if sens > 0 else 104, 120 + i * 34, s, 28, SERIF, 700) for i, s in enumerate(lignes))
    return w, h, r(0, 0, w, h, B) + logo('cimier-orange', 50, 44, 56) + r(26, 76, 268, 2, O) + corps + fl


def rollup():
    w, h = 85, 200
    return w, h, (r(0, 0, w, h, B) + logo('couleur', w / 2, 34, 42) + t(w / 2, 72, 'Rassemblement des', 5.2, SERIF, anchor='middle')
                  + t(w / 2, 79, 'Républicains Réformateurs', 5.2, SERIF, anchor='middle') + r(0, 90, w, 90, N)
                  + t(8, 118, 'BIENVENUE', 3.6, w=700, fill=O, ls=0.8) + t(8, 132, 'Siège', 11, SERIF).replace(f'fill="{N}"', f'fill="{B}"')
                  + t(8, 144, 'national', 11, SERIF).replace(f'fill="{N}"', f'fill="{B}"') + r(8, 151, 18, 1.2, O)
                  + t(8, 162, 'Accueil et information', 3.8, w=400, fill=G) + r(0, 180, w, 20, O) + t(w / 2, 192, '[site-du-parti]', 4.2, anchor='middle'))


def logo_raster(kind, W):
    """Logo officiel rendu à W pixels de large (rendu ×3 puis réduit, pour des bords nets)."""
    H = W * RATIO[kind]
    img = rendu(logo(kind, W / 2, H / 2, W), W, H, int(round(W * 3)))
    im = Image.fromarray((img * 255).astype(np.uint8)).resize((int(round(W)), int(round(H))), Image.LANCZOS)
    return np.asarray(im).astype(np.float32) / 255


def orange(photo, large=False):
    r, g, b = [photo[..., i].astype(int) for i in range(3)]
    if large:  # inclut les bords adoucis du logo d'origine
        return ((r - b) > 35) & (r > 140)
    return ((r - b) > 90) & (r > 180)


def remplacer(photo, bbox, kind, masque=None, alignement='bas', largeur=None, limite=None, garder_devant=True):
    """Efface un logo redessiné (zone bbox) et pose le logo officiel à sa place.
    masque : pixels du logo d'origine (par défaut, les pixels orange de la zone) ;
    limite : masque des pixels où le nouveau logo a le droit d'apparaître (ex. la toile d'un drapeau)."""
    from scipy import ndimage
    x, y, w, h = bbox
    H, W_img = photo.shape[:2]
    zone = np.zeros((H, W_img), bool)
    zone[max(0, y - 6):y + h + 6, max(0, x - 6):x + w + 6] = True
    if masque is None:
        masque = orange(photo, large=True) & zone
    masque = ndimage.binary_dilation(ndimage.binary_fill_holes(ndimage.binary_closing(masque, iterations=3)), iterations=5) & zone
    lum0 = cv2.cvtColor(photo, cv2.COLOR_RGB2GRAY)
    # chaises, micros devant le logo : seules les grandes zones sombres sont conservées
    devant = ndimage.binary_opening((lum0 < 75) & ~orange(photo, large=True) & zone, iterations=3)
    lab_d, n_d = ndimage.label(devant)
    if n_d and garder_devant:
        tailles = ndimage.sum(devant, lab_d, range(1, n_d + 1))
        devant = np.isin(lab_d, np.where(tailles > 400)[0] + 1)
    else:
        devant = np.zeros_like(devant)
    fond = cv2.cvtColor(cv2.inpaint(cv2.cvtColor(photo, cv2.COLOR_RGB2BGR), (masque & ~devant).astype(np.uint8) * 255, 9, cv2.INPAINT_TELEA), cv2.COLOR_BGR2RGB)
    Wl = largeur or w
    img = logo_raster(kind, Wl)
    hl, wl = img.shape[:2]
    x0 = int(round(x + (w - wl) / 2))
    y0 = int(round(y + h - hl)) if alignement == 'bas' else int(round(y + (h - hl) / 2))
    calque = np.zeros((H, W_img, 4), np.float32)
    ys, xs = slice(max(0, y0), min(H, y0 + hl)), slice(max(0, x0), min(W_img, x0 + wl))
    calque[ys, xs] = img[ys.start - y0:ys.stop - y0, xs.start - x0:xs.stop - x0]
    a = calque[..., 3:4].copy()
    if limite is not None:
        a *= limite[..., None]
    a[devant] = 0
    zone_lum = ndimage.binary_dilation(masque, iterations=8) & ~devant
    lum = eclairage(fond, zone_lum if zone_lum.any() else zone & ~devant)
    rgb = cv2.GaussianBlur(calque[..., :3] * lum[..., None], (0, 0), 0.5)
    base = fond.astype(np.float32) / 255
    return (np.clip(base * (1 - a) + rgb * a, 0, 1) * 255).astype(np.uint8)


def poser(photo, quad, dessin, px=1600, **kw):
    w, h, body = dessin
    return appliquer(photo, quad, rendu(body, w, h, px), **kw)


SCENES = {
    # Badges et accréditations (photo 5) : quatre catégories, coins détectés automatiquement puis vérifiés
    'accreditations': ('5.webp', [
        ([[153, 303], [422, 352], [302, 771], [13, 706]], badge('DÉLÉGUÉ', O, N)),
        ([[496, 355], [763, 405], [667, 832], [375, 770]], badge('PRESSE', N, B)),
        ([[823, 397], [1112, 438], [1047, 884], [731, 834]], badge('INVITÉ', G, N)),
        ([[1184, 438], [1481, 498], [1416, 951], [1101, 875]], badge('ORGANISATION', OF, B)),
    ]),
    # Totem d'accueil et panneaux directionnels (photo 3)
    'totem-accueil': ('3.webp', [
        ([[595, 61], [942, 61], [942, 866], [595, 866]], totem()),
        ([[121, 308], [440, 308], [440, 574], [121, 574]], panneau('Salle du|Conseil', -1)),
        ([[1103, 304], [1422, 302], [1422, 575], [1103, 574]], panneau('Salle|plénière', 1)),
    ]),
    # Roll-ups d'accueil (photo 1) : les deux toiles reçoivent le visuel conforme
    'roll-up': ('1.webp', [
        ([[137, 57], [550, 94], [550, 1168], [131, 1200]], rollup()),
        ([[630, 106], [1005, 89], [1005, 1190], [628, 1164]], rollup()),
    ]),
}


MEDAILLONS_2 = [(537, 35, 201, 247), (296, 282, 69, 84), (572, 291, 64, 81), (828, 297, 58, 77), (1066, 304, 53, 74),
               (439, 407, 67, 83), (703, 411, 61, 79), (949, 414, 57, 76), (1176, 416, 53, 74), (296, 534, 69, 84),
               (574, 533, 63, 80), (830, 532, 58, 77), (1067, 530, 54, 74), (752, 714, 139, 183)]
CIMIERS_2 = [(82, 221, 142, 103), (442, 298, 57, 38), (706, 306, 52, 38), (952, 312, 49, 36), (1178, 317, 44, 35),
             (304, 418, 57, 38), (580, 422, 54, 37), (834, 424, 50, 35), (1073, 426, 46, 34), (1181, 540, 44, 34),
             (956, 542, 47, 36), (708, 544, 50, 36), (444, 545, 56, 38), (307, 676, 54, 38)]


def conference(photo):
    """Conférence de presse (photo 2) : chaque médaillon et chaque cimier redessinés sont remplacés."""
    from scipy import ndimage
    for bb in MEDAILLONS_2:
        x, y, w, h = bb
        photo = remplacer(photo, bb, 'couleur', largeur=w * (1.0 if h > 1.05 * w else 1.0))
    for bb in CIMIERS_2:
        photo = remplacer(photo, bb, 'cimier-orange', alignement='centre')
    # Drapeau : logo blanc sur toile orange, effacé en entier puis remplacé dans la limite de la toile
    toile = orange(photo, large=True)
    toile[:, :1150] = False
    toile[650:, :] = False  # sous la table : bande orange de la nappe, à exclure
    lab, n = ndimage.label(toile)
    k = np.argmax(ndimage.sum(toile, lab, range(1, n + 1))) + 1
    drap = ndimage.binary_fill_holes(ndimage.binary_closing(lab == k, iterations=6))
    # toile reconstituée : moyenne locale des seuls pixels orange francs (convolution normalisée)
    f = photo.astype(np.float32)
    ecart = f[..., 0] - f[..., 2]
    franc = (drap & (ecart > 150)).astype(np.float32)
    flou = lambda a: cv2.GaussianBlur(a, (0, 0), 18)
    poids = flou(franc) + 1e-4
    fond = np.dstack([flou(f[..., i] * franc) / poids for i in range(3)])
    a_refaire = ndimage.binary_erosion(drap, iterations=3) & (ecart < 0.85 * (fond[..., 0] - fond[..., 2]))
    a_refaire = ndimage.binary_dilation(a_refaire, iterations=2) & drap
    ys, xs = np.nonzero(a_refaire & (np.mgrid[:a_refaire.shape[0], :a_refaire.shape[1]][0] > 300))
    f[a_refaire] = fond[a_refaire]
    photo = np.clip(f, 0, 255).astype(np.uint8)
    # logo blanc officiel, centré sur l'ancien emplacement, limité à la toile
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    largeur = min(x1 - x0, 150)
    vide = np.zeros(drap.shape, bool)
    photo = remplacer(photo, (int(x0), int(y0), int(x1 - x0), int(y1 - y0)), 'blanc', masque=vide, largeur=largeur,
                      alignement='centre', limite=ndimage.binary_erosion(drap, iterations=2).astype(np.float32))
    return photo


def signaletique(photo):
    """Totem « Assemblée générale » et panneaux (photo 4)."""
    # cimier 3D découpé au-dessus du totem : remplacé par le cimier officiel, à la même place
    photo = remplacer(photo, (563, 36, 302, 102), 'cimier-orange', largeur=210, garder_devant=False)
    photo = remplacer(photo, (610, 174, 260, 267), 'couleur', largeur=262, garder_devant=False)
    for bb in [(219, 246, 87, 100), (1244, 224, 68, 70), (1249, 465, 67, 69)]:
        photo = remplacer(photo, bb, 'couleur', largeur=bb[2] * 0.98)
    return photo


RETOUCHES = {'conference-de-presse': ('2.webp', conference), 'signaletique-evenement': ('4.webp', signaletique)}


def main(src):
    os.makedirs(OUT, exist_ok=True)
    for code, (fichier, fn) in RETOUCHES.items():
        photo = np.asarray(Image.open(os.path.join(src, fichier)).convert('RGB'))
        Image.fromarray(fn(photo)).save(os.path.join(OUT, f'3R_{code}.jpg'), quality=92)
        print('ok', code)
    for code, (fichier, surfaces) in SCENES.items():
        photo = np.asarray(Image.open(os.path.join(src, fichier)).convert('RGB'))
        for quad, dessin in surfaces:
            photo = poser(photo, quad, dessin)
        Image.fromarray(photo).save(os.path.join(OUT, f'3R_{code}.jpg'), quality=92)
        print('ok', code)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(OUT, 'sources'))
