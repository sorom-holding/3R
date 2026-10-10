# 3R — Rassemblement des Républicains Réformateurs

Identité visuelle et charte graphique du parti **3R**.

## Contenu

| Dossier | Contenu |
|---|---|
| `assets/logos/` | Logo officiel en relief (`00_officiel_3D`) et déclinaisons en aplats : principal, monochromes, blanc, fonds foncés, cimier « 3R » (miniature), avatars, favicons. SVG, PDF vectoriel, PNG transparents 512 à 4 096 px. |
| `assets/polices/` | Libre Caslon Text et Source Sans 3 (TTF bureautique, WOFF2 web, licences SIL OFL). |
| `tokens/` | Design tokens (`tokens.json` au format W3C, `tokens.css`), nuanciers Adobe (`.ase`) et GIMP/Inkscape (`.gpl`). |
| `modeles/word/` | Papier à en-tête, communiqué officiel, note d'information, procès-verbal, rapport d'activité. |
| `modeles/powerpoint/` | Modèle de présentation 16:9 (6 dispositions, thème 3R). |
| `modeles/impression/` | Carte de visite, carte de membre, badge, enveloppes DL et C4, chemise : sources SVG modifiables et BAT PDF (fond perdu 3 mm, traits de coupe). |
| `modeles/signature-email/` | Signature e-mail HTML. |
| `maquettes/` | 42 maquettes PNG : événementiel, textiles et objets, signalétique, communication numérique. |
| `charte/` | Charte graphique PDF (A4 paysage). |
| `site/` | Plateforme web de consultation (HTML, CSS, JavaScript sans dépendance). |
| `docs/` | Analyse technique du logo, décisions validées, captures de contrôle. |
| `scripts/` | Générateurs de tous les fichiers ci-dessus. |

## Statut du logo

- **Officiel** : `assets/logos/00_officiel_3D/` (fichiers fournis par le parti, image 1 254 px).
- **Validé** : la version en aplats et le cimier seul sont des adaptations techniques fidèles, validées par le parti. Aucune version horizontale n'est autorisée. Voir `docs/decisions.md`.

## Régénérer les fichiers

Prérequis : Python 3 (numpy, scipy, pillow, cairosvg, pypdf), potrace, Node.js (docx, pptxgenjs, playwright-core), LibreOffice, Poppler.

```bash
python3 scripts/generer_logos.py            # déclinaisons du logo
python3 scripts/generer_tokens.py           # tokens et nuanciers
node scripts/generer_modeles_word.js        # modèles Word
node scripts/generer_modele_powerpoint.js   # modèle PowerPoint
python3 scripts/generer_impression.py       # documents à imprimer
python3 scripts/construire_site.py          # plateforme web (site/fichiers, site/js/donnees.js)
node scripts/exporter.js                    # maquettes PNG, charte PDF, captures
python3 scripts/construire_site.py          # recopie les exports dans la plateforme
```

`site/fichiers/` et `site/js/donnees.js` sont générés et ne sont pas versionnés.
