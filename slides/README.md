# The slides

[`CFD_EL.pptx`](CFD_EL.pptx) is the presentation we handed in on 30 June 2026, together with a recorded
video in which each of us presented a part. [`CFD_EL.pdf`](CFD_EL.pdf) is the same file converted to PDF
for reading on GitHub. The title is *Numerical Investigation of Flow Through Rotating Porous Blade Using
the Multiple Reference Frame (MRF) Method*.

| Slide | What it covers |
|---|---|
| 1 | title and team |
| 2 | problem definition: an air–water mixture through a rotating porous blade at 1000 rpm |
| 3 | objectives |
| 4 | methodology, in seven steps |
| 5, 6 | the first-cell height |
| 7 | the solver setup and the run plan |
| 8 | the boundaries and cell zones (a table from our report) |
| 9, 10 | boundary and cell-zone conditions |
| 11 | the volume-fraction contours |

The slides are kept exactly as handed in. This is what they get wrong, found in November 2026; the
[main page](../README.md#what-we-checked-in-november-2026) has the detail.

1. **Slide 7: "Density-Based Navier-Stokes (DBNS), Implicit Formulation".** Fluent runs the mixture
   model only with the pressure-based solver, and our session of 27 June was pressure-based.
2. **Slide 7: "Viscous Model: Laminar".** The session of 27 June ran SST k-ω; the model of the final run
   is not recorded.
3. **Slides 9 and 10** describe a model we did not build: outlets on a 270°–360° arc and near the shaft,
   a rotating shaft wall, a sliding interface, and three cell zones, two with mesh motion. Our model is a
   quarter sector with one outlet, periodic edges and two cell zones, turning by frame motion, which is
   what the title's Multiple Reference Frame method means.
4. **Slide 8's table** gives the outer arc as R = 10 mm, the porous zone as 5 to 9 mm and `wal_fluid` as
   an inner core from 0 to 5 mm. In the meshes the casing is at 50 mm, the porous rotor runs from 10 to
   49 mm, and `wal_fluid` is the 1 mm gap at the casing.
5. **Slide 5** leaves the final first-cell height blank ("Δy = mm"); slide 4 says it converged to
   0.0048 mm. No mesh with that spacing survives.
6. **Slide 6** uses Cf = 0.026 / Re^(1/7), a turbulent flat-plate formula, for a run slide 7 calls
   laminar.
7. **Slides 3 and 4** promise a grid-independence study and the separation efficiency at the two
   outlets. Neither is in the slides.
8. **Slide 4** lists the ideal gas law and Sutherland's viscosity among the material properties. Nothing
   we kept confirms that they were used.
