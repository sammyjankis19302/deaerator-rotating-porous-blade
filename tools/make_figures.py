"""
Draws every figure in figures/ from the files in this repository (November 2026).

  python tools/make_figures.py          (from the repository root)

  figures/deaerator-idea.png       what the device does, and how hard it spins
  figures/geometry.png             the quarter sector, its zones and boundaries (mesh 105)
  figures/periodic.png             how one quarter stands for the whole disc
  figures/mesh.png                 the structured grid, whole and zoomed
  figures/mesh-versions.png        the same grid labelled five ways on 27 June
  figures/first-cell-height.png    the hand calculation's y+ line, and the meshes on it
  figures/water-fraction.png       the 29 June result, read off the screenshots
  figures/timeline.png             27 to 30 June 2026
  figures/periodic-water.gif       the result copied round the disc, then turning
"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyArrowPatch, Polygon, Wedge, Circle, Rectangle
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
from deaerator import calc, digitize                     # noqa: E402
from deaerator.mesh import read_mesh, AXIS, polar        # noqa: E402

ORANGE, BLUE, AQUA, YELLOW, PURPLE = '#eb6834', '#2a78d6', '#1baf7a', '#eda100', '#8250df'
INK, MUTED, FAINT = '#1f2328', '#59636e', '#d0d7de'
WATER = LinearSegmentedColormap.from_list('water', ['#f4f8fc', '#9cc3ea', '#2a78d6', '#0b3e7a'])
plt.rcParams.update({'font.size': 10, 'axes.edgecolor': MUTED, 'axes.labelcolor': INK,
                     'xtick.color': MUTED, 'ytick.color': MUTED, 'axes.titlecolor': INK})
R_IN, R_GAP, R_OUT = 10.0, 49.0, 50.0                    # mm, meshes of 27 June


def out(name):
    path = os.path.join(ROOT, 'figures', name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def tidy(ax):
    for sp in ('top', 'right'):
        ax.spines[sp].set_visible(False)
    ax.grid(alpha=0.25)


def arc(r, t0=0.0, t1=90.0, n=200):
    t = np.radians(np.linspace(t0, t1, n))
    return r * np.cos(t), r * np.sin(t)


def pt(r, deg):
    return float(r * np.cos(np.radians(deg))), float(r * np.sin(np.radians(deg)))


def sector_patch(r0, r1, t0=0.0, t1=90.0, **kw):
    return Wedge((0, 0), r1, t0, t1, width=r1 - r0, **kw)


# ── 1. what the device does ──────────────────────────────────────────────────

def deaerator_idea():
    fig = plt.figure(figsize=(14, 5.4))
    a = fig.add_axes([0.01, 0.02, 0.50, 0.86])
    a.set_aspect('equal'); a.axis('off')
    a.set_xlim(-66, 66); a.set_ylim(-74, 64)
    a.add_patch(Circle((0, 0), 52, fc='none', ec=INK, lw=3))                     # casing
    a.add_patch(Wedge((0, 0), 49, 0, 360, width=39, fc='#e8eef5', ec='none'))     # porous rotor
    a.add_patch(Circle((0, 0), 10, fc='white', ec=INK, lw=1.5))                   # hub / inlet
    for k in range(4):
        t = np.radians(90 * k)
        a.plot([10 * np.cos(t), 49 * np.cos(t)], [10 * np.sin(t), 49 * np.sin(t)], color=MUTED, lw=0.8, ls=':')
    rng = np.random.default_rng(3)
    for _ in range(140):
        r = 12 + 35 * rng.random() ** 0.7; t = 2 * np.pi * rng.random()
        a.plot(r * np.cos(t), r * np.sin(t), 'o', ms=2.4, color=BLUE, alpha=0.75)
    for _ in range(45):
        r = 12 + 22 * rng.random(); t = 2 * np.pi * rng.random()
        a.plot(r * np.cos(t), r * np.sin(t), 'o', ms=4.5, mfc='white', mec=MUTED, mew=0.8)
    for t in np.radians([30, 120, 210, 300]):
        a.add_patch(FancyArrowPatch((24 * np.cos(t), 24 * np.sin(t)), (44 * np.cos(t), 44 * np.sin(t)),
                                    arrowstyle='-|>', mutation_scale=14, color=BLUE, lw=2))
    for t in np.radians([75, 165, 255, 345]):
        a.add_patch(FancyArrowPatch((36 * np.cos(t), 36 * np.sin(t)), (17 * np.cos(t), 17 * np.sin(t)),
                                    arrowstyle='-|>', mutation_scale=12, color=MUTED, lw=1.5))
    a.add_patch(FancyArrowPatch((40, 40), (-40, 40), connectionstyle='arc3,rad=0.42', arrowstyle='-|>',
                                mutation_scale=16, color=INK, lw=1.5))
    a.text(0, 59.5, '1000 rpm', ha='center', fontsize=10, color=INK)
    a.text(0, -3.5, 'mixture\nin', ha='center', fontsize=8.5, color=INK, va='center')
    a.text(-64, -57, 'Water (dots) is heavier and is thrown out to the casing; air (circles) is pushed\nback '
           'towards the axis. The porous rotor makes the whole mixture turn with it.', fontsize=9, color=MUTED,
           va='top')
    fig.text(0.02, 0.95, 'A rotating porous blade', fontsize=12, fontweight='bold', color=INK)

    b = fig.add_axes([0.58, 0.14, 0.39, 0.72])
    c = calc.chain()
    r = np.linspace(0, 50, 200)
    g = c['omega'] ** 2 * r * 1e-3 / 9.81
    b.plot(r, g, color=BLUE, lw=2)
    for rr in (10, 50):
        gg = c['omega'] ** 2 * rr * 1e-3 / 9.81
        b.plot(rr, gg, 'o', color=BLUE, ms=7, mec='white', mew=1.5)
        b.annotate(f'r = {rr} mm: {gg:.0f} g', (rr, gg), xytext=(-8, 8) if rr == 50 else (10, -4),
                   textcoords='offset points', ha='right' if rr == 50 else 'left', va='top' if rr == 10 else 'bottom',
                   fontsize=9.5, color=INK)
    b.axvspan(0, 10, color=FAINT, alpha=0.5, lw=0)
    b.text(5, 2, 'hub', ha='center', fontsize=8.5, color=MUTED)
    b.set_xlabel('radius [mm]')
    b.set_ylabel('centrifugal acceleration, ω²r [multiples of g]')
    b.set_title('How hard it spins at 1000 rpm (ω = 104.7 rad/s)', loc='left', fontsize=11, fontweight='bold')
    b.set_xlim(0, 52); b.set_ylim(0, 62)
    tidy(b)
    fig.savefig(out('deaerator-idea.png'), dpi=140)
    plt.close(fig)


# ── 2. the geometry ──────────────────────────────────────────────────────────

def geometry():
    fig = plt.figure(figsize=(13.5, 7.2))
    a = fig.add_axes([0.04, 0.07, 0.56, 0.86])
    a.add_patch(sector_patch(R_IN, R_GAP, fc='#e8eef5', ec='none'))
    a.add_patch(sector_patch(R_GAP, R_OUT, fc='#cfe3f7', ec='none'))
    x, y = arc(R_IN); a.plot(x, y, color=BLUE, lw=3.5)
    x, y = arc(R_OUT); a.plot(x, y, color=INK, lw=3.5)
    x, y = arc(R_GAP); a.plot(x, y, color=MUTED, lw=0.8, ls='--')
    a.plot([R_IN, R_GAP], [0, 0], color=PURPLE, lw=3); a.plot([0, 0], [R_IN, R_GAP], color=PURPLE, lw=3)
    a.plot([R_GAP, R_OUT], [0, 0], color=ORANGE, lw=5); a.plot([0, 0], [R_GAP, R_OUT], color=ORANGE, lw=5)
    a.plot(0, 0, '+', color=INK, ms=12, mew=1.5)
    a.text(1.0, -2.6, 'rotation axis', fontsize=9, color=INK)
    lab = dict(fontsize=10, color=INK)
    a.annotate('inlet  (r = 10 mm)\nvelocity inlet:\n90% water, 10% air', xy=pt(R_IN, 60), xytext=(-22, 12),
               arrowprops=dict(arrowstyle='-', color=BLUE), color=BLUE, fontsize=10)
    a.annotate('outer_wall  (r = 50 mm)\nstationary casing', xy=pt(R_OUT, 40), xytext=(40, 46),
               arrowprops=dict(arrowstyle='-', color=INK), **lab)
    a.text(25, 25, 'porous\nthe rotor, r = 10 to 49 mm,\nturning at 1000 rpm', ha='center', **lab)
    a.annotate('interios: the two straight\nedges, made a periodic pair', xy=(0, 30), xytext=(-21, 33),
               arrowprops=dict(arrowstyle='-', color=PURPLE), color=PURPLE, fontsize=10)
    a.text(30, -3.4, 'interios', ha='center', color=PURPLE, fontsize=9.5)
    a.annotate('outlet: the two 1 mm ends\nof the gap, pressure outlet', xy=(0, 49.5), xytext=(-21, 53),
               arrowprops=dict(arrowstyle='-', color=ORANGE), color=ORANGE, fontsize=10)
    a.set_xlim(-24, 58); a.set_ylim(-7, 58); a.set_aspect('equal')
    a.set_xlabel('x from the axis [mm]'); a.set_ylabel('y [mm]')
    for sp in ('top', 'right'):
        a.spines[sp].set_visible(False)
    a.set_title('The computational domain: a quarter of the disc (mesh We_Love_CFD_105)', loc='left',
                fontsize=11, fontweight='bold')

    b = fig.add_axes([0.64, 0.40, 0.34, 0.50])
    b.add_patch(sector_patch(46.5, R_GAP, 0, 8, fc='#e8eef5', ec='none'))
    b.add_patch(sector_patch(R_GAP, R_OUT, 0, 8, fc='#cfe3f7', ec='none'))
    x, y = arc(R_OUT, 0, 8); b.plot(x, y, color=INK, lw=3)
    x, y = arc(R_GAP, 0, 8); b.plot(x, y, color=MUTED, lw=0.8, ls='--')
    b.plot([46.5, R_GAP], [0, 0], color=PURPLE, lw=3); b.plot([R_GAP, R_OUT], [0, 0], color=ORANGE, lw=5)
    b.annotate('wal_fluid: the gap,\n1 mm, not porous', xy=(49.55, 3.0), xytext=(50.35, 4.6), fontsize=9,
               color=INK, arrowprops=dict(arrowstyle='-', color=MUTED))
    b.text(47.6, 4.5, 'porous', ha='center', fontsize=9, color=INK)
    b.text(49.5, -0.55, 'outlet', ha='center', fontsize=9, color=ORANGE)
    b.text(47.2, -0.55, 'interios', ha='center', fontsize=9, color=PURPLE)
    b.set_xlim(46.3, 52.8); b.set_ylim(-0.9, 6.5); b.set_aspect('equal')
    b.set_title('Close-up where the gap meets the edge', loc='left', fontsize=10, fontweight='bold')
    for sp in ('top', 'right'):
        b.spines[sp].set_visible(False)
    b.tick_params(labelsize=8)
    fig.text(0.64, 0.10, 'Cell zones: porous (39,601 cells) and wal_fluid (1,791 cells).\n'
             'Boundaries: inlet, outer_wall, outlet, interios.\n'
             'Lengths in mm, as in the mesh files; the arcs are centred\n'
             'on (50, 0) in the files, shifted to (0, 0) here.', fontsize=9.5, color=MUTED, va='bottom')
    fig.savefig(out('geometry.png'), dpi=140)
    plt.close(fig)


# ── 3. one quarter for the whole disc ────────────────────────────────────────

def periodic():
    fig, ax = plt.subplots(figsize=(7.6, 7.6))
    for k in range(4):
        t0 = 90 * k
        if k == 0:
            ax.add_patch(sector_patch(R_IN, R_OUT, t0, t0 + 90, fc='#cfe3f7', ec=INK, lw=1.2))
        else:
            ax.add_patch(sector_patch(R_IN, R_OUT, t0, t0 + 90, fc='#f3f6f9', ec=FAINT, lw=1, ls='--'))
            tm = np.radians(t0 + 45)
            ax.text(31 * np.cos(tm), 31 * np.sin(tm), f'copy {k}\n(+{90 * k}°)', ha='center', va='center',
                    color=MUTED, fontsize=9.5)
    ax.text(22, 22, 'the quarter\nwe computed', ha='center', va='center', fontsize=10.5, fontweight='bold', color=INK)
    ax.plot([R_IN, R_OUT], [0, 0], color=PURPLE, lw=3.5)
    ax.plot([0, 0], [R_IN, R_OUT], color=PURPLE, lw=3.5)
    ax.add_patch(FancyArrowPatch((46, 3), (3, 46), connectionstyle='arc3,rad=0.45', arrowstyle='<|-|>',
                                 mutation_scale=16, color=PURPLE, lw=1.6))
    ax.text(43, 43, 'what leaves one straight edge\nenters the other, turned by 90°',
            ha='center', va='center', color=PURPLE, fontsize=9.5)
    ax.text(30, -3.5, 'interios', color=PURPLE, fontsize=9.5, ha='center')
    ax.text(-3.2, 30, 'interios:011', color=PURPLE, fontsize=9.5, ha='center', rotation=90)
    ax.plot(0, 0, '+', color=INK, ms=12, mew=1.5)
    ax.set_xlim(-55, 55); ax.set_ylim(-55, 55); ax.set_aspect('equal'); ax.axis('off')
    ax.set_title('Rotational periodicity: one quarter stands for the whole disc', fontsize=11, fontweight='bold')
    fig.tight_layout()
    fig.savefig(out('periodic.png'), dpi=140)
    plt.close(fig)


# ── 4. the mesh ──────────────────────────────────────────────────────────────

def mesh_lines(msh, keep=None):
    xy = msh['nodes'] - AXIS
    segs = []
    for f in msh['faces'].values():
        segs.append(np.stack([xy[f[:, 0] - 1], xy[f[:, 1] - 1]], axis=1))
    segs = np.concatenate(segs)
    if keep is not None:
        segs = segs[keep(segs)]
    return segs


def mesh_figure():
    msh = read_mesh('mesh/We_Love_CFD_105.cas.gz')
    segs = mesh_lines(msh)
    mid = segs.mean(axis=1)
    rm, tm = np.hypot(*mid.T), np.degrees(np.arctan2(mid[:, 1], mid[:, 0]))
    radial = np.abs(np.hypot(*segs[:, 1].T) - np.hypot(*segs[:, 0].T)) > 1e-6   # segment along a ray
    fig = plt.figure(figsize=(15, 6.2))
    a = fig.add_axes([0.03, 0.08, 0.40, 0.84])
    # every fourth ring and ray in the overview
    ring_idx = np.rint((rm - R_IN) / (39 / 199)).astype(int)
    ray_idx = np.rint(tm / (90 / 199)).astype(int)
    show = np.where(radial, ray_idx % 4 == 0, (ring_idx % 4 == 0) | (rm > R_GAP - 1e-6))
    a.add_collection(LineCollection(segs[show], colors=BLUE, linewidths=0.25))
    a.set_xlim(-2, 52); a.set_ylim(-2, 52); a.set_aspect('equal')
    a.set_title('The whole sector (every 4th grid line)', loc='left', fontsize=11, fontweight='bold')
    a.set_xlabel('x from the axis [mm]'); a.set_ylabel('y [mm]')
    for sp in ('top', 'right'):
        a.spines[sp].set_visible(False)
    a.add_patch(Rectangle((-0.3, 9.0), 3.6, 3.6, fc='none', ec=ORANGE, lw=1.4))
    a.add_patch(Rectangle((46.6, -0.3), 3.8, 3.0, fc='none', ec=ORANGE, lw=1.4))
    a.text(3.8, 12.9, 'A', color=ORANGE, fontweight='bold'); a.text(46.2, 3.0, 'B', color=ORANGE, fontweight='bold')

    b = fig.add_axes([0.47, 0.08, 0.24, 0.84])
    k = (mid[:, 0] > -0.5) & (mid[:, 0] < 3.5) & (mid[:, 1] > 8.8) & (mid[:, 1] < 12.8)
    b.add_collection(LineCollection(segs[k], colors=BLUE, linewidths=0.6))
    x, y = arc(R_IN, 0, 90); b.plot(x, y, color=BLUE, lw=3)
    b.set_xlim(-0.3, 3.3); b.set_ylim(9.0, 12.6); b.set_aspect('equal')
    b.set_title('A: at the inlet, r = 10 mm', loc='left', fontsize=10.5, fontweight='bold')
    b.text(0.15, 9.15, '0.196 mm along the radius,\n0.079 mm along the arc', fontsize=9, color=INK,
           bbox=dict(fc='white', ec='none', alpha=0.9))
    for sp in ('top', 'right'):
        b.spines[sp].set_visible(False)

    c = fig.add_axes([0.75, 0.08, 0.24, 0.84])
    k = (mid[:, 0] > 46.4) & (mid[:, 0] < 50.6) & (mid[:, 1] > -0.4) & (mid[:, 1] < 2.9)
    c.add_collection(LineCollection(segs[k], colors=BLUE, linewidths=0.6))
    c.plot([R_GAP, R_OUT], [0, 0], color=ORANGE, lw=4)
    x, y = arc(R_OUT, 0, 5); c.plot(x, y, color=INK, lw=3)
    c.set_xlim(46.6, 50.4); c.set_ylim(-0.3, 2.7); c.set_aspect('equal')
    c.set_title('B: the gap and an outlet end', loc='left', fontsize=10.5, fontweight='bold')
    c.text(0.0, -0.16, 'Rings 0.196 mm apart in the rotor and\n0.111 mm apart (9 cells) in the gap, so the\n'
           'first cell at the casing is 0.111 mm high:\ny⁺ ≈ 27 by the hand calculation.', transform=c.transAxes,
           fontsize=9, color=INK, va='top')
    for sp in ('top', 'right'):
        c.spines[sp].set_visible(False)
    fig.suptitle('41,392 quadrilaterals: 199 × 199 in the porous rotor and 9 × 199 in the gap, '
                 'uniform spacing, no wall refinement', x=0.03, ha='left', fontsize=10, color=MUTED, y=0.995)
    fig.savefig(out('mesh.png'), dpi=150)
    plt.close(fig)


# ── 5. the same grid, labelled five ways ─────────────────────────────────────

KIND = {'wall': (INK, '-', 3.0), 'pressure-inlet': (BLUE, '-', 3.0), 'velocity-inlet': (BLUE, '-', 3.0),
        'pressure-far-field': (ORANGE, '-', 4.0), 'pressure-outlet': (ORANGE, '-', 4.0),
        'recirculation-outlet': (AQUA, '-', 3.0), 'recirculation-inlet': (AQUA, '--', 3.0),
        'interior': (PURPLE, '-', 3.0)}


def mesh_versions():
    notes = {101: 'the straight edges are walls;\ninlet a pressure inlet;\noutlet a pressure far-field',
             102: 'straight edges become a\nrecirculation outlet and inlet',
             103: 'the same labels, saved again',
             104: 'two cell zones: the porous\nrotor and the 1 mm gap',
             105: 'velocity inlet, pressure outlet;\nstraight edges an interior zone,\nlater made periodic in Fluent'}
    fig, axes = plt.subplots(1, 5, figsize=(16, 4.6))
    for ax, k in zip(axes, range(101, 106)):
        msh = read_mesh(f'mesh/We_Love_CFD_{k}.cas.gz')
        two_zones = len(msh['cell_zones']) == 2
        ax.add_patch(sector_patch(R_IN, R_GAP if two_zones else R_OUT, fc='#e8eef5', ec='none'))
        if two_zones:
            ax.add_patch(sector_patch(R_GAP, R_OUT, fc='#9cc3ea', ec='none'))
        xy = msh['nodes'] - AXIS
        for z, (typ, name) in msh['zones'].items():
            if z not in msh['faces'] or typ not in KIND or (typ == 'interior' and name != 'interios'):
                continue
            col, ls, lw = KIND[typ]
            f = msh['faces'][z]
            seg = np.stack([xy[f[:, 0] - 1], xy[f[:, 1] - 1]], axis=1)
            ax.add_collection(LineCollection(seg, colors=col, linewidths=lw, linestyles=ls))
        ax.set_xlim(-4, 54); ax.set_ylim(-4, 54); ax.set_aspect('equal'); ax.axis('off')
        hh = msh['exported'].split()[0][:5]
        ax.set_title(f'{k}   ·   27 June, {hh}', fontsize=10.5, fontweight='bold')
        ax.text(2, -14, notes[k], fontsize=8.8, color=INK, va='top')
    handles = [plt.Line2D([], [], color=c, ls=ls, lw=lw) for c, ls, lw in
               [KIND['wall'], KIND['pressure-inlet'], KIND['pressure-outlet'], KIND['recirculation-outlet'],
                KIND['interior']]]
    fig.legend(handles, ['wall', 'inlet', 'outlet', 'recirculation pair', 'interior (to be made periodic)'],
               loc='upper center', ncol=5, frameon=False, fontsize=9.5, bbox_to_anchor=(0.5, 0.96))
    fig.suptitle('One grid, labelled five ways in 53 minutes: We_Love_CFD_101 to 105', fontsize=11.5,
                 fontweight='bold', y=1.0)
    fig.tight_layout(rect=(0, 0.0, 1, 0.9))
    fig.subplots_adjust(bottom=0.25)
    fig.savefig(out('mesh-versions.png'), dpi=140)
    plt.close(fig)


# ── 6. first-cell height ─────────────────────────────────────────────────────

def first_cell_height():
    c = calc.chain()
    y = np.logspace(-6.3, -3.3, 200)
    fig, ax = plt.subplots(figsize=(10.5, 5.6))
    ax.loglog(y * 1e3, calc.y_plus_of(y, c), color=INK, lw=1.8)
    marks = [(calc.first_cell(1, c), 'y⁺ = 1: 4.1 μm', BLUE, 'target in the hand calculation'),
             (calc.first_cell(5, c), 'y⁺ = 5: 20 μm', BLUE, ''),
             (calc.first_cell(30, c), 'y⁺ = 30: 123 μm', BLUE, ''),
             (0.0048e-3, '0.0048 mm (slides)', AQUA, ''),
             (0.02e-3, '0.02 mm, the y⁺ ≈ 5 mesh', AQUA, ''),
             (1e-3 / 9, '0.111 mm, the meshes we have', ORANGE, '')]
    for k, (yy, lab, col, _) in enumerate(marks):
        yp = calc.y_plus_of(yy, c)
        ax.plot(yy * 1e3, yp, 'o', color=col, ms=8, mec='white', mew=1.5, zorder=3)
        dx, dy = (10, -14) if col == BLUE else (-12, 9)
        if lab.startswith('0.111'):
            dx, dy = (-12, 8)
        ax.annotate(f'{lab}  (y⁺ = {yp:.1f})' if col != BLUE else lab, (yy * 1e3, yp), xytext=(dx, dy),
                    textcoords='offset points', fontsize=9.3, color=INK, ha='right' if dx < 0 else 'left')
    d = calc.laminar_bl_thickness(c) * 1e3
    ax.axvline(d, color=MUTED, ls='--', lw=1)
    ax.text(d * 0.93, 0.35, f'laminar boundary layer\non the casing, about {d:.2f} mm', ha='right', fontsize=9,
            color=MUTED)
    ax.set_xlabel('height of the first cell at the wall [mm]')
    ax.set_ylabel('y⁺')
    ax.set_title('y⁺ = ρ u_τ y / μ with the hand calculation\'s numbers: u_τ = 0.245 m/s from τ_w = 60 Pa',
                 loc='left', fontsize=11, fontweight='bold')
    ax.set_xlim(4e-4, 0.6); ax.set_ylim(0.1, 150)
    tidy(ax)
    fig.tight_layout()
    fig.savefig(out('first-cell-height.png'), dpi=140)
    plt.close(fig)


# ── 7. the result, read off the screenshots ──────────────────────────────────

def full_disc(field, r, t, n=520, rot=0.0):
    """Paint the quarter field and its three periodic copies on an n x n image (white outside)."""
    s = np.linspace(-1, 1, n)
    X, Y = np.meshgrid(s, -s)
    rr = np.hypot(X, Y)
    th = (np.degrees(np.arctan2(Y, X)) - rot) % 90.0
    ir = np.clip(np.searchsorted(r, rr) , 0, len(r) - 1)
    it = np.clip(np.rint((th - t[0]) / (t[1] - t[0])).astype(int), 0, len(t) - 1)
    img = field[ir, it]
    inside = (rr >= r[0] - 0.004) & (rr <= 1.0)
    return np.where(inside, img, np.nan)


def water_fraction():
    r, t, w, w_direct, ok, _ = digitize.water_field()
    diff = (w - w_direct)[ok]
    prof = w.mean(axis=1)
    fig = plt.figure(figsize=(14, 6.0))
    a = fig.add_axes([0.02, 0.06, 0.40, 0.84])
    img = full_disc(w, r, t)
    a.imshow(img, cmap=WATER, vmin=0, vmax=1, extent=(-1, 1, -1, 1))
    th = np.radians(np.linspace(0, 90, 100))
    a.plot(np.r_[r[0] * np.cos(th), np.cos(th[::-1]), r[0]], np.r_[r[0] * np.sin(th), np.sin(th[::-1]), 0],
           color=ORANGE, lw=1.6)
    a.text(0.47, 0.47, 'computed', color=ORANGE, fontsize=10.5, fontweight='bold', rotation=-45, ha='center',
           va='center')
    a.text(-0.62, -0.66, 'periodic copies', color=MUTED, fontsize=9.5, rotation=-45, ha='center')
    a.set_xlim(-1.05, 1.05); a.set_ylim(-1.05, 1.05); a.axis('off')
    a.set_title('Water volume fraction at t = 0.6 s', loc='left', fontsize=11, fontweight='bold')
    sm = plt.cm.ScalarMappable(cmap=WATER, norm=plt.Normalize(0, 1))
    cb = fig.colorbar(sm, ax=a, fraction=0.04, pad=0.01)
    cb.set_label('water volume fraction')

    b = fig.add_axes([0.53, 0.19, 0.44, 0.68])
    lo, hi = np.percentile(w, 10, axis=1), np.percentile(w, 90, axis=1)
    b.fill_between(r, lo, hi, color=BLUE, alpha=0.18, lw=0, label='middle 80% of angles')
    b.plot(r, prof, color=BLUE, lw=2, label='averaged over the angle')
    b.axhline(0.9, color=MUTED, ls=':', lw=1)
    b.text(0.12, 0.915, 'water fraction at the inlet: 0.9', fontsize=9, color=MUTED)
    half = r[np.argmax(prof > 0.5)]
    b.axvline(half, color=MUTED, ls='--', lw=0.8)
    b.annotate(f'half water at r/R = {half:.3f}\n({(1 - half) * 50:.1f} mm from the casing if R = 50 mm)',
               (half, 0.5), xytext=(-12, 40), textcoords='offset points', ha='right', fontsize=9.3, color=INK,
               arrowprops=dict(arrowstyle='-', color=MUTED, lw=0.8))
    b.set_xlim(0.08, 1.0); b.set_ylim(0, 1.0)
    b.set_xlabel('radius as a fraction of the outer radius, r/R')
    b.set_ylabel('water volume fraction')
    b.set_title('Across the radius: about a fifth water, then the layer on the casing', loc='left',
                fontsize=11, fontweight='bold')
    b.legend(frameon=False, loc='upper left', bbox_to_anchor=(0.0, 0.88), fontsize=9)
    tidy(b)
    fig.text(0.53, 0.012, f'Read off the colours of the two Fluent screenshots of 29 June. The water screenshot\n'
             f'and one minus the air screenshot agree to {np.sqrt((diff ** 2).mean()):.3f} (rms).',
             fontsize=8.8, color=MUTED)
    fig.savefig(out('water-fraction.png'), dpi=140)
    plt.close(fig)
    return r, t, w


def periodic_gif(r, t, w):
    n = 480
    s = np.linspace(-1, 1, n)
    X, Y = np.meshgrid(s, -s)
    TH = np.degrees(np.arctan2(Y, X)) % 360

    def quarter_at(phi):                           # the computed quarter, turned by phi degrees
        f = full_disc(w, r, t, n, rot=phi)
        return np.where(((TH - phi) % 360) < 90, f, np.nan)

    def combine(layers):
        arr = np.full((n, n), np.nan)
        for L in layers:
            arr = np.where(np.isnan(L), arr, L)
        return arr

    def render(arr):
        rgba = WATER(np.nan_to_num(arr, nan=0.0))
        rgba[np.isnan(arr)] = (1, 1, 1, 1)
        return (rgba[..., :3] * 255).astype(np.uint8)

    fig = plt.figure(figsize=(5.6, 6.0), dpi=100)
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.86]); ax.axis('off')
    title = fig.text(0.5, 0.94, '', ha='center', fontsize=12, fontweight='bold', color=INK)
    sub = fig.text(0.5, 0.905, '', ha='center', fontsize=9.5, color=MUTED)
    placed = [quarter_at(0.0)]
    im = ax.imshow(render(placed[0]), extent=(-1, 1, -1, 1))
    th = np.radians(np.linspace(0, 90, 60))
    qx = np.r_[r[0] * np.cos(th), np.cos(th[::-1]), r[0]]
    qy = np.r_[r[0] * np.sin(th), np.sin(th[::-1]), 0]
    outline, = ax.plot(qx, qy, color=ORANGE, lw=1.6)
    ax.set_xlim(-1.03, 1.03); ax.set_ylim(-1.03, 1.03)
    frames = []

    def grab(k=1):
        fig.canvas.draw()
        f = Image.frombuffer('RGBA', fig.canvas.get_width_height(), fig.canvas.buffer_rgba()).convert('RGB')
        frames.extend([f] * k)

    title.set_text('The quarter we computed')
    sub.set_text('water volume fraction at t = 0.6 s, read off the Fluent screenshot')
    grab(14)
    for k in (1, 2, 3):
        title.set_text('Copied round by periodicity')
        sub.set_text(f'copy {k} of 3: the same quarter, turned by {90 * k}°')
        for step in range(1, 11):
            im.set_data(render(combine(placed + [quarter_at(90 * (k - 1) + 9 * step)])))
            grab()
        placed.append(quarter_at(90.0 * k))
        grab(4)
    title.set_text('The whole disc')
    sub.set_text('water thrown out to the casing, air left in the core')
    grab(14)
    sub.set_text('turning with the rotor (1000 rpm, shown very slowly)')
    for step in range(1, 31):
        rot = 3.0 * step
        im.set_data(render(full_disc(w, r, t, n, rot=rot)))
        c, s_ = np.cos(np.radians(rot)), np.sin(np.radians(rot))
        outline.set_data(c * qx - s_ * qy, s_ * qx + c * qy)
        grab()
    plt.close(fig)
    pal = frames[len(frames) // 2].quantize(colors=96, method=Image.Quantize.MEDIANCUT)
    q = []
    for f in frames:
        x = f.quantize(palette=pal, dither=Image.Dither.NONE)
        x.info.clear()
        q.append(x)
    q[0].save(out('periodic-water.gif'), save_all=True, append_images=q[1:], duration=80, loop=0, optimize=True)


# ── 8. timeline ──────────────────────────────────────────────────────────────

def timeline():
    ev = [(0.0, '27 June, 14:21', 'first mesh exported\nfrom Pointwise', 1, BLUE),
          (0.9, '15:14', 'fifth labelling (105):\nporous rotor, gap,\nperiodic edges', -1, BLUE),
          (2.6, 'evening', 'Fluent: mixture model,\nporous zone turning at\n104.7 rad/s', 1, BLUE),
          (3.6, '21:27', 'the first run diverges:\nfloating-point exceptions', -1, ORANGE),
          (6.4, '29 June', 'first cell sized by hand;\na y⁺ ≈ 5 mesh', 1, AQUA),
          (7.4, '16:07', 'volume-fraction contours\nat t = 0.6 s', -1, AQUA),
          (9.6, '30 June', 'slides and a recorded\nvideo presentation\nhanded in', 1, PURPLE),
          (12.6, 'November', 'files recovered,\nchecked and put here', -1, MUTED)]
    fig, ax = plt.subplots(figsize=(14, 3.7))
    ax.plot([-0.4, 10.6], [0, 0], color=MUTED, lw=2)
    ax.plot([11.6, 13.4], [0, 0], color=MUTED, lw=2)
    ax.text(11.1, 0, '···', ha='center', va='center', color=MUTED, fontsize=14)
    for x, when, what, side, col in ev:
        ax.plot(x, 0, 'o', color=col, ms=11, mec='white', mew=2, zorder=3)
        ax.plot([x, x], [0, 0.3 * side], color=col, lw=1.2)
        ax.text(x, 0.36 * side, f'{when}\n{what}', ha='center', va='bottom' if side > 0 else 'top',
                fontsize=9, color=INK, linespacing=1.3)
    ax.set_xlim(-1.4, 14.2); ax.set_ylim(-1.5, 1.5); ax.axis('off')
    fig.tight_layout()
    fig.savefig(out('timeline.png'), dpi=140)
    plt.close(fig)


if __name__ == '__main__':
    deaerator_idea()
    geometry()
    periodic()
    mesh_figure()
    mesh_versions()
    first_cell_height()
    r, t, w = water_fraction()
    periodic_gif(r, t, w)
    timeline()
    print('done')
