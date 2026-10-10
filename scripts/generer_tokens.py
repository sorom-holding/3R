"""Génère les design tokens et les nuanciers de l'identité 3R à partir d'une source unique.

Usage : python3 scripts/generer_tokens.py
Sorties : tokens/tokens.json (format W3C Design Tokens), tokens/tokens.css,
          tokens/3R_couleurs.ase (Adobe), tokens/3R_couleurs.gpl (GIMP, Inkscape)
"""
import json, os, struct

OUT = os.path.join(os.path.dirname(__file__), '..', 'tokens')

COULEURS = [
    # clé, nom, hex, CMJN indicatif, Pantone indicatif, rôle
    ('orange', 'Orange 3R', '#FE6501', (0, 70, 100, 0), '1505 C', 'Couleur signature : logo, aplats, accents'),
    ('bleu-nuit', 'Bleu nuit', '#1D2B4F', (100, 80, 30, 45), '2767 C', "Couleur d'accompagnement : textes, fonds institutionnels"),
    ('blanc', 'Blanc', '#FFFFFF', (0, 0, 0, 0), None, 'Fonds, logo blanc, texte sur bleu nuit'),
    ('gris-chaud', 'Gris chaud', '#F4EFEA', (0, 2, 4, 4), None, 'Fonds de section, papeterie'),
    ('orange-fonce', 'Orange foncé', '#C24A00', (0, 75, 100, 20), '1525 C', 'Texte orange sur fond clair (contraste 4,9 : 1)'),
    ('bleu-nuit-clair', 'Bleu nuit clair', '#2E4170', (90, 70, 20, 25), None, 'Survols, aplats secondaires sur bleu nuit'),
    ('gris-texte', 'Gris texte', '#4A5672', (70, 55, 30, 20), None, 'Texte secondaire, légendes'),
    ('gris-filet', 'Gris filet', '#E4DDD4', (0, 3, 7, 12), None, 'Filets, bordures, séparateurs'),
]

TYPO = {
    'titre': {'famille': 'Libre Caslon Text', 'secours': 'Georgia, "Times New Roman", serif', 'graisses': [400, 700]},
    'texte': {'famille': 'Source Sans 3', 'secours': 'Arial, "Segoe UI", sans-serif', 'graisses': [400, 600, 700]},
}
ECHELLE = {  # taille en px (écran) / pt (impression), interlignage
    'affiche': (64, 1.05), 'h1': (40, 1.1), 'h2': (30, 1.15), 'h3': (22, 1.25),
    'chapeau': (20, 1.4), 'texte': (17, 1.55), 'legende': (14, 1.45), 'surtitre': (13, 1.2),
}
ESPACE = {'1': 4, '2': 8, '3': 12, '4': 16, '5': 24, '6': 32, '7': 48, '8': 64, '9': 96}
RAYON = {'aucun': 0, 'petit': 4, 'moyen': 8, 'pilule': 999}


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def tokens_json():
    t = {'couleur': {}, 'police': {}, 'taille': {}, 'espace': {}, 'rayon': {}}
    for k, nom, hx, cmjn, pms, role in COULEURS:
        t['couleur'][k] = {'$type': 'color', '$value': hx, '$description': role,
                           '$extensions': {'3r': {'nom': nom, 'rvb': rgb(hx), 'cmjn': cmjn, 'pantone': pms}}}
    for k, v in TYPO.items():
        t['police'][k] = {'$type': 'fontFamily', '$value': [v['famille']] + [s.strip().strip('"') for s in v['secours'].split(',')],
                          '$extensions': {'3r': {'graisses': v['graisses']}}}
    for k, (px, lh) in ECHELLE.items():
        t['taille'][k] = {'$type': 'dimension', '$value': f'{px}px', '$extensions': {'3r': {'interlignage': lh}}}
    for k, v in ESPACE.items():
        t['espace'][k] = {'$type': 'dimension', '$value': f'{v}px'}
    for k, v in RAYON.items():
        t['rayon'][k] = {'$type': 'dimension', '$value': f'{v}px'}
    return t


def tokens_css():
    lines = ['/* Design tokens 3R — généré par scripts/generer_tokens.py, ne pas modifier à la main */', ':root {']
    lines += [f'  --3r-{k}: {hx};' for k, _, hx, *_ in COULEURS]
    lines += [f'  --3r-police-{k}: "{v["famille"]}", {v["secours"]};' for k, v in TYPO.items()]
    lines += [f'  --3r-taille-{k}: {px / 16:.4g}rem;' for k, (px, _) in ECHELLE.items()]
    lines += [f'  --3r-interligne-{k}: {lh};' for k, (_, lh) in ECHELLE.items()]
    lines += [f'  --3r-espace-{k}: {v / 16:.4g}rem;' for k, v in ESPACE.items()]
    lines += [f'  --3r-rayon-{k}: {v}px;' for k, v in RAYON.items()]
    return '\n'.join(lines + ['}', ''])


def ase():
    """Adobe Swatch Exchange 1.0, couleurs globales en RVB."""
    blocks = b''
    for _, nom, hx, *_ in COULEURS:
        name = (f'3R {nom}' + '\0').encode('utf-16-be')
        body = struct.pack('>H', len(name) // 2) + name + b'RGB ' + struct.pack('>fff', *(c / 255 for c in rgb(hx))) + struct.pack('>H', 0)
        blocks += struct.pack('>HI', 0x0001, len(body)) + body
    return b'ASEF' + struct.pack('>HHI', 1, 0, len(COULEURS)) + blocks


def gpl():
    out = ['GIMP Palette', 'Name: 3R Rassemblement des Républicains Réformateurs', 'Columns: 4', '#']
    out += [f'{r:3d} {g:3d} {b:3d}\t{nom} {hx}' for _, nom, hx, *_ in COULEURS for r, g, b in [rgb(hx)]]
    return '\n'.join(out) + '\n'


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    json.dump(tokens_json(), open(f'{OUT}/tokens.json', 'w'), ensure_ascii=False, indent=2)
    open(f'{OUT}/tokens.css', 'w').write(tokens_css())
    open(f'{OUT}/3R_couleurs.ase', 'wb').write(ase())
    open(f'{OUT}/3R_couleurs.gpl', 'w').write(gpl())
