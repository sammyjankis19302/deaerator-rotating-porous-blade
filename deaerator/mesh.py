"""
Reader for the 2-D ASCII Fluent mesh files that Pointwise wrote for this project
(mesh/We_Love_CFD_101.cas.gz ... 105.cas.gz). They hold the mesh only: nodes, faces, cells
and zone names. Fluent settings were never saved into them.

Sections used
  (10 (zone first last type 2) (x y ...))      node coordinates
  (13 (zone first last bc-type face-type) (...)) faces: node0 node1 cell-left cell-right (hex)
  (12 (zone first last type elem-type))          cell ranges per cell zone
  (45 (zone type name) ())                       zone types and names

The geometry is a quarter annulus. Its arcs are centred on (50, 0) in the file's units,
which are millimetres (the outer arc is r = 50, matching the 0.05 m in the hand calculation).

Usage:  python -m deaerator.mesh mesh/We_Love_CFD_105.cas.gz
"""
import gzip
import re
import sys

import numpy as np

AXIS = np.array([50.0, 0.0])           # centre of the arcs, mm


def _open(path):
    if str(path).endswith('.gz'):
        return gzip.open(path, 'rt', errors='replace')
    return open(path, 'r', errors='replace')


def read_mesh(path):
    """Return a dict with nodes (N x 2, mm), faces {zone: (M x 4) int array, 1-based node and
    cell numbers}, zones {id: (type, name)}, cell_zones {id: (first, last)}, and the header."""
    with _open(path) as fh:
        txt = fh.read()
    out = {'zones': {}, 'faces': {}, 'cell_zones': {}}
    for m in re.finditer(r'\(45 \((\d+) ([\w-]+) ([\w:-]+)\)', txt):
        out['zones'][int(m.group(1))] = (m.group(2), m.group(3))
    m = re.search(r'\(10 \(([0-9a-fA-F]+) ([0-9a-fA-F]+) ([0-9a-fA-F]+) [0-9a-fA-F]+ 2\)\s*\(', txt)
    if m is None:
        raise ValueError(f'{path}: no 2-D node section found')
    s, e = m.end(), txt.index(')', m.end())
    out['nodes'] = np.array(txt[s:e].split(), dtype=float).reshape(-1, 2)
    for m in re.finditer(r'\(13 \(([0-9a-fA-F]+) ([0-9a-fA-F]+) ([0-9a-fA-F]+) ([0-9a-fA-F]+) '
                         r'([0-9a-fA-F]+)\)\s*\(', txt):
        zone = int(m.group(1), 16)
        if zone == 0:
            continue
        s, e = m.end(), txt.index(')', m.end())
        out['faces'][zone] = np.array([int(t, 16) for t in txt[s:e].split()],
                                      dtype=np.int64).reshape(-1, 4)
    for m in re.finditer(r'\(12 \(([0-9a-fA-F]+) ([0-9a-fA-F]+) ([0-9a-fA-F]+) ([0-9a-fA-F]+) '
                         r'([0-9a-fA-F]+)\)', txt):
        zone = int(m.group(1), 16)
        if zone:
            out['cell_zones'][zone] = (int(m.group(2), 16), int(m.group(3), 16))
    hdr = re.search(r'\(0 "(\d\d:\d\d:\d\d\s+\w+ \w+ \d+ \d{4})"\)', txt)
    out['exported'] = ' '.join(hdr.group(1).split()) if hdr else ''
    out['n_cells'] = int(re.search(r'Total Number of Cells : (\d+)', txt).group(1))
    return out


def polar(xy):
    """Radius (mm) and angle (degrees) about the arcs' centre."""
    d = np.atleast_2d(xy) - AXIS
    return np.hypot(d[:, 0], d[:, 1]), np.degrees(np.arctan2(d[:, 1], d[:, 0]))


def face_zone_geometry(msh, zone):
    """Radius and angle ranges, face lengths and total length of one face zone."""
    f = msh['faces'][zone]
    xy = msh['nodes']
    a, b = xy[f[:, 0] - 1], xy[f[:, 1] - 1]
    r, th = polar(0.5 * (a + b))
    L = np.hypot(*(b - a).T)
    return {'faces': len(f), 'r': (r.min(), r.max()), 'theta': (th.min(), th.max()),
            'length': (L.min(), L.max()), 'total': L.sum()}


def cell_centres(msh):
    """Approximate cell centres (mean of the face midpoints around each cell) and cell sizes."""
    xy = msh['nodes']
    n = msh['n_cells']
    acc = np.zeros((n, 2)); cnt = np.zeros(n)
    for f in msh['faces'].values():
        mid = 0.5 * (xy[f[:, 0] - 1] + xy[f[:, 1] - 1])
        for col in (2, 3):
            c = f[:, col]
            ok = c > 0
            np.add.at(acc, c[ok] - 1, mid[ok]); np.add.at(cnt, c[ok] - 1, 1)
    return acc / cnt[:, None]


def audit(path):
    msh = read_mesh(path)
    xy = msh['nodes']
    r, _ = polar(xy)
    rows = []
    for z, (typ, name) in sorted(msh['zones'].items()):
        if z in msh['faces'] and not name.startswith('interior-') and name != 'interior-unspecified':
            g = face_zone_geometry(msh, z)
            rows.append((name, typ, g))
    return msh, r, rows


if __name__ == '__main__':
    for p in sys.argv[1:]:
        msh, r, rows = audit(p)
        print(f'{p}: exported {msh["exported"]}, {len(msh["nodes"])} nodes, {msh["n_cells"]} cells, '
              f'r = {r.min():.3f} to {r.max():.3f} mm')
        for z, (a, b) in msh['cell_zones'].items():
            print(f'   cell zone {msh["zones"][z][1]:12s} {b - a + 1:6d} cells')
        for name, typ, g in rows:
            print(f'   {name:22s} {typ:22s} {g["faces"]:4d} faces  r {g["r"][0]:6.2f}..{g["r"][1]:6.2f}  '
                  f'theta {g["theta"][0]:6.2f}..{g["theta"][1]:6.2f}  length {g["total"]:.3f} mm')
