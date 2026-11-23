"""
Read volume fractions off the two Fluent contour screenshots of 29 June 2026
(media/fluent-water-fraction-2026-06-29.jpg and media/fluent-air-fraction-2026-06-29.jpg).

The solution files behind them were not kept, so the colours are all that is left of the
result. Each pixel's colour is matched to the nearest colour on the screenshot's own colour bar,
which runs linearly from 0 (bottom) to 1 (top). With two phases the water and air fractions add
up to one, so the two screenshots can be checked against each other.

The positions below were measured on the screenshots: the corner where the two straight edges
meet (the rotation axis), the outer radius and the hub radius in pixels, and the colour bar box.
"""
import numpy as np
from PIL import Image

SHOTS = {
    'air':   {'file': 'media/fluent-air-fraction-2026-06-29.jpg', 'corner': (715.0, 703.0),
              'R': 560.5, 'hub': 56.0, 'bar': (285, 316, 349, 619)},
    'water': {'file': 'media/fluent-water-fraction-2026-06-29.jpg', 'corner': (639.0, 697.0),
              'R': 597.0, 'hub': 59.5, 'bar': (180, 213, 320, 609),
              'mask': lambda x, y: (x > 1195) & (y > 680)},     # a snipping-tool thumbnail
}


def load(name, root='.'):
    s = SHOTS[name]
    return np.asarray(Image.open(f'{root}/{s["file"]}').convert('RGB')).astype(float)


def colour_bar(img, box):
    """Mean colour of each row of the colour bar, and its value (1 at the top, 0 at the bottom)."""
    x0, x1, y0, y1 = box
    cols = img[y0:y1 + 1, x0:x1 + 1].mean(axis=1)
    vals = np.linspace(1.0, 0.0, len(cols))
    return cols, vals


def to_value(rgb, cols, vals):
    """Nearest colour-bar entry for each pixel colour (N x 3)."""
    d = ((rgb[:, None, :] - cols[None, :, :]) ** 2).sum(-1)
    i = d.argmin(1)
    return vals[i], np.sqrt(d[np.arange(len(i)), i])


def sample(name, rr, tt, root='.'):
    """Value at radius fractions rr (r/R) and angles tt (degrees), arrays of the same shape.
    Returns (values, colour distance, valid mask)."""
    s = SHOTS[name]
    img = load(name, root)
    cols, vals = colour_bar(img, s['bar'])
    x0, y0 = s['corner']
    x = x0 + rr * s['R'] * np.cos(np.radians(tt))
    y = y0 - rr * s['R'] * np.sin(np.radians(tt))
    xi, yi = np.rint(x).astype(int), np.rint(y).astype(int)
    rgb = img[yi.ravel(), xi.ravel()]
    v, dist = to_value(rgb, cols, vals)
    ok = np.ones(v.shape, bool)
    if 'mask' in s:
        ok &= ~s['mask'](xi.ravel(), yi.ravel())
    return v.reshape(rr.shape), dist.reshape(rr.shape), ok.reshape(rr.shape)


def water_field(n_r=180, n_t=181, root='.'):
    """Water volume fraction on a polar grid, from the air screenshot (1 - air) and from the
    water screenshot, plus the grid. r runs from just outside the hub to just inside the rim."""
    hub = SHOTS['air']['hub'] / SHOTS['air']['R']
    r = np.linspace(hub + 0.012, 0.992, n_r)
    t = np.linspace(1.2, 89.4, n_t)                # clear of the light line Fluent draws on the bottom edge
    RR, TT = np.meshgrid(r, t, indexing='ij')
    air, d_air, _ = sample('air', RR, TT, root)
    water, d_w, ok_w = sample('water', RR, TT, root)
    return r, t, 1.0 - air, water, ok_w, (d_air, d_w)


if __name__ == '__main__':
    r, t, w_from_air, w_direct, ok, (da, dw) = water_field()
    diff = (w_from_air - w_direct)[ok]
    print(f'grid {w_from_air.shape}; colour distance to the bar: median {np.median(da):.1f} and '
          f'{np.median(dw):.1f} (of 441 max)')
    print(f'water fraction from the air shot minus the water shot: mean {diff.mean():+.3f}, '
          f'rms {np.sqrt((diff ** 2).mean()):.3f}, 95% within {np.percentile(np.abs(diff), 95):.3f}')
    prof = w_from_air.mean(axis=1)
    for f in (0.15, 0.3, 0.5, 0.7, 0.85, 0.9, 0.93, 0.95, 0.97, 0.99):
        i = np.argmin(np.abs(r - f))
        print(f'   r/R = {r[i]:.3f}: water fraction (angle-averaged) {prof[i]:.3f}')
