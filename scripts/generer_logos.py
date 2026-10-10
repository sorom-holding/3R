"""Génère toutes les déclinaisons du logo 3R à partir de la version en aplats validée.

Entrées : assets/logos/01_principal/3R_principal_couleur.svg (couleur, aplats)
          assets/logos/02_monochrome/3R_mono_orange.svg (une couleur, lettres évidées)
          assets/logos/00_officiel_3D/logo_3R_officiel_3D.png (pour extraire le cimier)
Usage :   python3 scripts/generer_logos.py
Dépendances : numpy, scipy, pillow, cairosvg, potrace (binaire)
"""
import os, re, subprocess, tempfile
import numpy as np
import cairosvg
from PIL import Image, ImageFilter
from scipy import ndimage

ROOT = os.path.join(os.path.dirname(__file__), '..', 'assets', 'logos')
ORANGE, NUIT, NOIR, BLANC = '#FE6501', '#1D2B4F', '#000000', '#FFFFFF'
PNG_SIZES = (512, 1024, 2048, 4096)


def p(*parts):
    path = os.path.join(ROOT, *parts)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def export(svg, folder, name, sizes=PNG_SIZES):
    """Écrit le SVG, un PDF vectoriel et des PNG transparents de plusieurs largeurs."""
    open(p(folder, name + '.svg'), 'w').write(svg)
    cairosvg.svg2pdf(bytestring=svg.encode(), write_to=p(folder, name + '.pdf'))
    for w in sizes:
        cairosvg.svg2png(bytestring=svg.encode(), write_to=p(folder, 'png', f'{name}_{w}px.png'), output_width=w)


def recolor(svg, mapping):
    for a, b in mapping.items():
        svg = svg.replace(f'fill="{a}"', f'fill="{b}"')
    return svg


def trace_crest():
    """Extrait le cimier « 3R » du logo officiel : pixels orange situés hors du médaillon."""
    S = 3
    im = Image.open(p('00_officiel_3D', 'logo_3R_officiel_3D.png')).convert('RGB')
    W, H = im.size
    im = im.resize((W * S, H * S), Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.2))
    a = np.asarray(im).astype(int)
    org = (a[..., 0] - a[..., 2]) > 45
    yy, xx = np.mgrid[:H * S, :W * S]
    # Le cimier « 3R » repose sur un socle courbe, séparé du médaillon par un filet blanc
    # (cercle de rayon ≈ 469 px autour du centre 622 ; 680). On garde ce qui est au-delà du filet,
    # dans la largeur du cimier (x de 466 à 780 px).
    dist = np.hypot(xx - 622 * S, yy - 680 * S)
    crest = org & (dist > 469 * S) & (yy < 235 * S) & (xx > 466 * S) & (xx < 780 * S)
    lab, n = ndimage.label(crest)
    sizes = ndimage.sum(crest, lab, range(1, n + 1))
    crest = np.isin(lab, np.where(sizes > 0.02 * sizes.max())[0] + 1)
    crest = ndimage.binary_opening(crest, iterations=1)
    ys, xs = np.nonzero(crest)
    pad = 6 * S
    crest = crest[ys.min() - pad:ys.max() + pad, xs.min() - pad:xs.max() + pad]
    h, w = crest.shape
    with tempfile.TemporaryDirectory() as d:
        Image.fromarray((~crest).astype(np.uint8) * 255).convert('1').save(f'{d}/c.pbm')
        subprocess.run(['potrace', f'{d}/c.pbm', '-s', '-o', f'{d}/c.svg', '-t', str(20 * S), '-a', '1.1', '-O', '0.4', '--flat'], check=True)
        s = open(f'{d}/c.svg').read()
    tr = re.search(r'<g transform="([^"]+)"', s).group(1)
    paths = ' '.join(re.findall(r' d="([^"]+)"', s))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w // S}" height="{h // S}">'
            f'<title>3R</title><g transform="{tr}"><path fill="{ORANGE}" fill-rule="evenodd" d="{paths}"/></g></svg>\n')


def boxed(inner_svg, bg, size=1024, scale=0.72, radius=0.0, circle=False):
    """Place un SVG centré dans un carré de couleur (avatar, favicon)."""
    vb = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', inner_svg)
    iw, ih = float(vb.group(1)), float(vb.group(2))
    body = re.sub(r'^.*?<svg[^>]*>|</svg>\s*$', '', inner_svg, flags=re.S)
    k = size * scale / max(iw, ih)
    tx, ty = (size - iw * k) / 2, (size - ih * k) / 2
    shape = (f'<circle cx="{size/2}" cy="{size/2}" r="{size/2}" fill="{bg}"/>' if circle else
             f'<rect width="{size}" height="{size}" rx="{size*radius}" fill="{bg}"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}">'
            f'{shape}<g transform="translate({tx:.2f} {ty:.2f}) scale({k:.5f})">{body}</g></svg>\n')


def main():
    couleur = open(p('01_principal', '3R_principal_couleur.svg')).read()
    mono = open(p('02_monochrome', '3R_mono_orange.svg')).read()

    export(couleur, '01_principal', '3R_principal_couleur')
    export(mono, '02_monochrome', '3R_mono_orange')
    export(recolor(mono, {ORANGE: NUIT}), '02_monochrome', '3R_mono_bleu-nuit')
    export(recolor(mono, {ORANGE: NOIR}), '02_monochrome', '3R_mono_noir')
    export(recolor(mono, {ORANGE: BLANC}), '03_blanc', '3R_blanc')
    export(couleur, '04_fonds-fonces', '3R_fond-fonce_couleur')

    crest = trace_crest()
    export(crest, '05_miniature', '3R_cimier_orange')
    export(recolor(crest, {ORANGE: BLANC}), '05_miniature', '3R_cimier_blanc')
    export(recolor(crest, {ORANGE: NUIT}), '05_miniature', '3R_cimier_bleu-nuit')

    # Avatars 1080 × 1080 : le contenu reste dans le cercle de recadrage des réseaux sociaux
    export(boxed(recolor(crest, {ORANGE: BLANC}), ORANGE, 1080, 0.62), '06_avatar', '3R_avatar_cimier_orange', (400, 1080))
    export(boxed(couleur, BLANC, 1080, 0.80), '06_avatar', '3R_avatar_medaillon_blanc', (400, 1080))

    # Favicon : cimier blanc sur carré orange arrondi
    fav = boxed(recolor(crest, {ORANGE: BLANC}), ORANGE, 512, 0.80, radius=0.18)
    open(p('07_favicon', 'favicon.svg'), 'w').write(fav)
    for s, name in [(16, 'favicon-16'), (32, 'favicon-32'), (48, 'favicon-48'), (180, 'apple-touch-icon'), (192, 'icon-192'), (512, 'icon-512')]:
        cairosvg.svg2png(bytestring=fav.encode(), write_to=p('07_favicon', f'{name}.png'), output_width=s)
    big = Image.open(p('07_favicon', 'icon-512.png'))
    big.save(p('07_favicon', 'favicon.ico'), sizes=[(16, 16), (32, 32), (48, 48)])
    open(p('07_favicon', 'site.webmanifest'), 'w').write(
        '{"name":"Rassemblement des Républicains Réformateurs","short_name":"3R",'
        '"icons":[{"src":"icon-192.png","sizes":"192x192","type":"image/png"},'
        '{"src":"icon-512.png","sizes":"512x512","type":"image/png"}],'
        '"theme_color":"#FE6501","background_color":"#FFFFFF","display":"standalone"}\n')


if __name__ == '__main__':
    main()
