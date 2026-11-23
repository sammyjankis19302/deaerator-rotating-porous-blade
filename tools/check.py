"""
Prints every number the README quotes, recomputed from the files in this repository.

  python tools/check.py          (from the repository root)
"""
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
from deaerator import calc, digitize                                          # noqa: E402
from deaerator.mesh import read_mesh, polar, face_zone_geometry                # noqa: E402


def main():
    print('== the five meshes')
    nodes = None
    for k in range(101, 106):
        m = read_mesh(f'mesh/We_Love_CFD_{k}.cas.gz')
        key = np.round(m['nodes'], 9)
        key = key[np.lexsort((key[:, 1], key[:, 0]))]
        same = 'same nodes as 101' if nodes is None or np.allclose(key, nodes) else 'DIFFERENT nodes'
        nodes = key if nodes is None else nodes
        zones = ', '.join(f'{n} ({t})' for z, (t, n) in sorted(m['zones'].items())
                          if not n.startswith('interior-'))
        print(f'{k}: exported {m["exported"]}; {m["n_cells"]} cells; {same}; {zones}')
    m = read_mesh('mesh/We_Love_CFD_105.cas.gz')
    r, th = polar(m['nodes'])
    rings = np.unique(np.round(r, 6))
    print(f'105: r = {r.min():.1f} to {r.max():.1f} mm, {len(rings)} rings, '
          f'{len(np.unique(np.round(th, 6)))} rays; radial spacings {sorted(set(np.round(np.diff(rings), 4)))} mm')
    for z, (a, b) in m['cell_zones'].items():
        print(f'   cell zone {m["zones"][z][1]}: {b - a + 1} cells')
    for z, (t, n) in sorted(m['zones'].items()):
        if z in m['faces'] and (not n.startswith('interior-') or n == 'interior-porous-wal_fluid'):
            g = face_zone_geometry(m, z)
            print(f'   {n:26s} {t:16s} {g["faces"]:4d} faces, r {g["r"][0]:.2f}..{g["r"][1]:.2f} mm, '
                  f'angle {g["theta"][0]:.2f}..{g["theta"][1]:.2f} deg, {g["total"]:.3f} mm long')

    print('\n== the hand calculation')
    c = calc.chain()
    for k, v in c.items():
        print(f'   {k:6s} = {v:.6g}')
    for yp in (1, 5, 30):
        print(f'   first cell for y+ = {yp}: {calc.first_cell(yp, c) * 1e6:.2f} um')
    for y_mm in (1 / 9, 0.0048, 0.02):
        print(f'   y+ of a {y_mm:.4f} mm first cell: {calc.y_plus_of(y_mm * 1e-3, c):.2f}')
    print(f'   laminar boundary layer 5L/sqrt(Re): {calc.laminar_bl_thickness(c) * 1e3:.3f} mm')
    for rr in (0.01, 0.05):
        a = c['omega'] ** 2 * rr
        print(f'   centrifugal acceleration at r = {rr * 1e3:.0f} mm: {a:.1f} m/s^2 = {a / 9.81:.1f} g')
    print(f'   time step for 1 degree of rotation: {60 / 1000 / 360:.4e} s; 10 turns: {10 * 60 / 1000:.2f} s, '
          f'{10 * 360} steps')

    print('\n== the result screenshots')
    for name, s in digitize.SHOTS.items():
        print(f'   {name}: hub / outer radius = {s["hub"] / s["R"]:.3f}')
    rr, tt, w, wd, ok, (da, dw) = digitize.water_field()
    diff = (w - wd)[ok]
    print(f'   water from (1 - air) vs water shot: mean {diff.mean():+.4f}, rms {np.sqrt((diff ** 2).mean()):.4f}')
    prof = w.mean(axis=1)
    core = prof[(rr > 0.2) & (rr < 0.85)]
    print(f'   water fraction for r/R 0.2 to 0.85: mean {core.mean():.3f}, range {core.min():.3f} to {core.max():.3f}')
    half = rr[np.argmax(prof > 0.5)]
    quarter = rr[np.argmax(prof > 0.25)]
    print(f'   angle-averaged water fraction passes 0.25 at r/R = {quarter:.3f} and 0.5 at r/R = {half:.3f} '
          f'({(1 - quarter) * 50:.1f} and {(1 - half) * 50:.1f} mm from the casing if R = 50 mm); '
          f'{prof[-1]:.2f} at r/R = {rr[-1]:.3f}')


if __name__ == '__main__':
    main()
