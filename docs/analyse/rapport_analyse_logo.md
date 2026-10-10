# Analyse technique du logo 3R — phase 1 (avant production)

Planche annotée : `analyse_geometrique_logo.png`

## 1. Fichiers fournis

| Fichier | Contenu réel |
|---|---|
| `logo_3R_orange_blanc.svg` | Conteneur SVG d'une image PNG 1254 × 1254 px (aucun tracé vectoriel) |
| `logo_3R_orange_blanc.pdf` | Page Inkscape 940,5 × 940,5 pt contenant la même image (96 dpi, aucune police, aucun tracé) |

Conséquence : la définition maximale disponible est de 1254 px, soit environ 10,6 cm imprimés à 300 dpi. Au-delà, il faut une version vectorielle.

## 2. Géométrie (en pixels du fichier source)

- Encombrement : 1016 × 1120 px, rapport largeur : hauteur = 1 : 1,10
- Médaillon : Ø 1016 px, centre (622 ; 680)
- Disque central : rayon 355 px = 0,70 R ; anneau blanc de 11 px ; couronne de texte de 143 px
- Cimier « 3R » : 307 × 146 px (30 % de la largeur, 13 % de la hauteur), centré sur l'axe vertical, posé sur le haut du médaillon
- Unité de protection proposée : x = hauteur du cimier ≈ 1/7 de la largeur du logo

## 3. Couleurs

Une seule teinte (orange) rendue en relief, plus le blanc.

| Zone | Valeur relevée |
|---|---|
| Ombres | #E82100 |
| Médiane des pixels orange | #F75B01 |
| Faces éclairées (aplat) | #FE6501 |
| Reflets | #FD8616 |

## 4. Typographie et symboles

- Cimier « 3R » : lettrage géométrique gras, biseauté, dessiné sur mesure.
- Couronne : « RASSEMBLEMENT • DES RÉPUBLICAINS • RÉFORMATEURS », capitales à empattements, graisse forte, accents corrects ; police non identifiable avec certitude depuis l'image.
- Centre : monogramme de trois R à empattements, fort contraste, jambes en volute, entrelacés.
- Trois points séparateurs dans la couronne.
- Effets : biseaux, ombres portées, reflets, double bordure en relief sur le demi-cercle supérieur.

## 5. Lisibilité

Les lettres de la couronne mesurent environ 7 % de la largeur du logo.

| Largeur du logo | Hauteur des lettres | Verdict |
|---|---|---|
| 30 mm imprimé | ≈ 2,1 mm (≈ 6 pt) | minimum impression |
| 120 px écran | ≈ 8 px | minimum écran |
| 80 px écran | ≈ 5,5 px | illisible |

Les effets 3D ne se reproduisent pas en sérigraphie, broderie, gravure ou impression une couleur : une version en aplats est nécessaire pour ces usages.

## 6. Statut des fichiers

| Statut | Fichiers |
|---|---|
| Officiel (référence) | `assets/logo/logo_3R_orange_blanc.*` (version 3D d'origine) |
| Adaptation technique, à valider | `assets/logo/vectoriel/*` (vectorisation automatique, effets 3D remplacés par des aplats, filet du demi-cercle supérieur régularisé) |
