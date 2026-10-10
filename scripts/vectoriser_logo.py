import sys, subprocess, re, numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage
src, out = sys.argv[1], sys.argv[2]
S = 3  # upscale for smoother edges
im = Image.open(src).convert('RGB')
W, H = im.size
im = im.resize((W*S, H*S), Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.2))
a = np.asarray(im).astype(int)
r, g, b = a[..., 0], a[..., 1], a[..., 2]
orange = (r - b) > 45
orange = ndimage.binary_opening(orange, iterations=1)
# remove tiny specks
lab, n = ndimage.label(orange); sizes = ndimage.sum(orange, lab, range(1, n+1))
orange = np.isin(lab, np.where(sizes > 200*S)[0] + 1)
silhouette = ndimage.binary_fill_holes(ndimage.binary_closing(orange, iterations=8)) | ndimage.binary_fill_holes(orange)
# outer rim: fill bevel highlights near the circle edge
ys, xs = np.nonzero(silhouette[H*S//3:]); ys = ys + H*S//3
cx = (xs.min() + xs.max()) / 2; R = (xs.max() - xs.min()) / 2; cy = ys.max() - R
yy, xx = np.mgrid[:H*S, :W*S]
dist = np.hypot(xx - cx, yy - cy)
ang = ((np.arctan2(yy - cy, xx - cx) + np.pi) / (2*np.pi) * 3600).astype(int) % 3600
rmax = np.zeros(3600); np.maximum.at(rmax, ang[orange], dist[orange])
rmax = ndimage.maximum_filter1d(rmax, 5, mode='wrap')
rim = (dist > rmax[ang] - 19*S) & (dist <= rmax[ang]) & ((yy > 225*S) | (xx < 460*S) | (xx > 790*S))  # keep the gap under the 3R crest
orange = orange | rim
print('circle', cx/S, cy/S, R/S)
# drop thin highlight slivers (white regions that vanish under opening)
holes = silhouette & ~orange
lab, n = ndimage.label(holes)
kept = np.unique(lab[ndimage.binary_opening(holes, iterations=4)])
orange = orange | (holes & ~np.isin(lab, kept[kept > 0]))
def trace(mask, name):
    p = f'{out}/{name}.pbm'
    Image.fromarray((~mask).astype(np.uint8)*255).convert('1').save(p)
    subprocess.run(['potrace', p, '-s', '-o', f'{out}/{name}.svg', '-t', str(40*S), '-a', '1.1', '-O', '0.4', '--flat'], check=True)
    svg = open(f'{out}/{name}.svg').read()
    tr = re.search(r'<g transform="([^"]+)"', svg).group(1)
    paths = ' '.join(re.findall(r' d="([^"]+)"', svg))
    return tr, paths
tw, pw = trace(silhouette, 'white'); to, po = trace(orange, 'orange')
vb = f'0 0 {W*S} {H*S}'
def doc(layers):
    body = ''.join(f'<g transform="{t}"><path fill="{c}" fill-rule="evenodd" d="{d}"/></g>' for t, d, c in layers)
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{W}" height="{H}"><title>3R - Rassemblement des Républicains Réformateurs</title>{body}</svg>\n'
open(f'{out}/logo_3R_vectoriel.svg', 'w').write(doc([(tw, pw, '#FFFFFF'), (to, po, '#FE6501')]))
open(f'{out}/logo_3R_vectoriel_orange.svg', 'w').write(doc([(to, po, '#FE6501')]))  # monochrome, letters transparent
