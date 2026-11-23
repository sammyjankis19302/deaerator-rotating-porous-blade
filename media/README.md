# Screenshots

What we saved from Fluent while we worked, with the time each was taken.

| File | When | What it shows |
|---|---|---|
| [`fluent-porous-zone-porosity-2026-06-27.jpg`](fluent-porous-zone-porosity-2026-06-27.jpg) | 27 June, evening | the `porous` cell zone with frame motion and the porous-zone option on; the porosity being typed in; aluminium as the porous solid |
| [`fluent-session-2026-06-27.jpg`](fluent-session-2026-06-27.jpg) | 27 June, evening | the session title bar (2-D, double precision, pressure-based, mixture, SST k-ω, 8 processes); water and air as materials; the cell zones and boundaries of mesh 105; `interios` being given a new type |
| [`fluent-velocity-inlet-2026-06-27.jpg`](fluent-velocity-inlet-2026-06-27.jpg) | 27 June, evening | the velocity inlet, with turbulence set by 5% intensity and a viscosity ratio of 10 |
| [`fluent-porous-zone-rotation-2026-06-27.jpg`](fluent-porous-zone-rotation-2026-06-27.jpg) | 27 June, evening | the `porous` zone's reference frame: 104.7 rad/s, rotation axis at (0, 0) |
| [`fluent-first-run-diverged-2026-06-27.jpg`](fluent-first-run-diverged-2026-06-27.jpg) | 27 June, 21:27 | the first run: a pressure contour reading `inf` and `-nan(ind)` over the mesh, and floating-point exceptions in the console |
| [`fluent-water-fraction-2026-06-29.jpg`](fluent-water-fraction-2026-06-29.jpg) | 29 June | water volume fraction (phase-1) at t = 0.6 s, with reversed-flow warnings in the console |
| [`fluent-air-fraction-2026-06-29.jpg`](fluent-air-fraction-2026-06-29.jpg) | 29 June | air volume fraction (phase-2) at t = 0.6 s |
| [`slides.png`](slides.png) | | eight of the eleven slides |

The two result screenshots are used as data by [`deaerator/digitize.py`](../deaerator/digitize.py), which
reads the volume fraction back off their colours. They are kept exactly as saved.
