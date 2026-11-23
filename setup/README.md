# Rebuilding the Fluent case

The Fluent case and data files of our runs were not kept. This page puts together what we do know,
from the screenshots of 27 June, from our slides and from the meshes, so that the case can be set up
again from [`mesh/We_Love_CFD_105.cas.gz`](../mesh). Each setting says where it comes from.

Sources: **[S]** screenshots of 27 June in [`media/`](../media) · **[P]** our slides · **[M]** the mesh files

## What we know

| Setting | Value | Source |
|---|---|---|
| Fluent version | 2024 R1 | the result screenshots |
| Space | 2-D, double precision | [S] title bar |
| Solver | pressure-based | [S] title bar (the slides' "density-based" cannot run the mixture model) |
| Multiphase | mixture, 2 phases: water (primary, `water-liquid`), air (secondary) | [S] materials, [P] |
| Mixture options | slip velocity on, body force on | [P] |
| Viscous model | laminar in the slides; SST k-ω in the session of 27 June | [P], [S] |
| Cell zone `porous` | frame motion (rotating reference frame), 104.7 rad/s = 1000 rpm, about z; porous zone on | [S] |
| Porous resistance | viscous resistance 1.8 × 10¹¹ m⁻² | [P] |
| Porous solid, heat transfer | aluminium, equilibrium thermal model (the defaults) | [S] |
| Cell zone `wal_fluid` | the 1 mm gap, not porous; stationary, as far as we can tell | [M], [P] |
| `inlet` | velocity inlet; 90% water, 10% air by volume; turbulence 5% intensity, viscosity ratio 10 (27 June) | [P], [S] |
| `outlet` | pressure outlet, the two 1 mm ends of the gap | [M] |
| `outer_wall` | stationary wall, no slip | [M], [P] |
| `interios` | split into its two edges and made a rotational periodic pair (`interios`, `interios:011`) | [M], the table on slide 8 |
| Steady start | 5,000 iterations: 1,500 first-order upwind, then 3,500 second-order upwind | [P] |
| Transient | time step 1.6667 × 10⁻⁴ s (1° of rotation), 3,600 steps, 0.6 s | [P] |

## What we don't know

The inlet velocity, the porosity value, the initial condition, the outlet's backflow settings, the
turbulence model of the final run, and the final mesh (which had a smaller hub and a finer first cell
than the files here).

## Steps

1. **Read the mesh.** File → Read → Mesh, `We_Love_CFD_105.cas.gz`. Then Domain → Mesh → Scale, with
   the mesh created in millimetres.
2. **Put the axis where the arcs are centred.** In the file the arcs are centred on (50, 0) mm. Either
   translate the mesh by (−0.05, 0) m (Domain → Mesh → Transform → Translate), or use (0.05, 0) m as the
   rotation-axis origin in step 4. The screenshots of 27 June show the origin left at (0, 0), which only
   works if the mesh was moved first.
3. **Models.** Pressure-based solver. Multiphase → Mixture with two phases, water primary and air
   secondary, with slip velocity and body force switched on. Viscous model as you choose (see above).
4. **Cell zones.** `porous`: tick Frame Motion, 104.72 rad/s about the z axis through the arcs' centre;
   tick Porous Zone and set the viscous resistance to 1.8 × 10¹¹ m⁻² in both directions. `wal_fluid`:
   no motion.
5. **Periodic edges.** `interios` holds both straight edges. Separate it into two zones (Domain → Zones
   → Separate → Faces, by angle: the edges are at right angles), then join the two with the text
   command `mesh/modify-zones/make-periodic`, answering that the periodicity is rotational. Fluent takes
   the rotation axis from the cell zone next to the boundary, which is why step 4 comes first.
6. **Boundaries.** `inlet`: velocity inlet, with the air volume fraction 0.1 on the air phase.
   `outlet`: pressure outlet at zero gauge pressure. `outer_wall`: stationary wall.
7. **Run.** Steady first, 1,500 iterations with first-order upwinding and 3,500 with second-order, then
   transient with a time step of 1.6667 × 10⁻⁴ s for 3,600 steps.

With frame motion the mesh itself does not turn, so a time step tied to 1° of rotation is a habit from
sliding-mesh runs rather than a requirement. It does no harm.
