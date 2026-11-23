# The meshes

Five exports from Pointwise V18.6, all made on Saturday 27 June 2026, and the Pointwise project they
came from. All five hold exactly the same structured grid (the same 41,800 nodes and 41,392
quadrilaterals); only the names and types of the boundaries and cell zones change.

| File | Exported | Cell zones | Boundaries |
|---|---|---|---|
| `We_Love_CFD_101.cas.gz` | 14:21:35 | one, unnamed | `inlet` pressure inlet · `outlet` pressure far-field · `bc-3` wall (casing) · `wall` wall (both straight edges) |
| `We_Love_CFD_102.cas.gz` | 15:03:20 | one, unnamed | `inlet` pressure inlet · `outlet` pressure far-field · `outer_wall` wall · `recirc-out` recirculation outlet (edge at 0°) · `recirculation_inlet` recirculation inlet (edge at 90°) |
| `We_Love_CFD_103.cas.gz` | 15:06:29 | one, unnamed | the same as 102 |
| `We_Love_CFD_104.cas.gz` | 15:09:14 | `porous` (39,601 cells), `wal_fluid` (1,791) | as 102 |
| `We_Love_CFD_105.cas.gz` | 15:14:54 | `porous` (39,601 cells), `wal_fluid` (1,791) | `inlet` velocity inlet · `outlet` pressure outlet · `outer_wall` wall · `interios` interior (both straight edges, 398 faces) |
| `101.pw` | project saved 15:59 | `porous`, `wal_fluid` | `inlet` velocity inlet · `outlet` pressure outlet · `outer wall` wall · `interios` interior |

## The geometry

Units are millimetres. The arcs are centred on (50, 0), not on the origin: the sector runs from the
inlet arc at r = 10 to the casing at r = 50, and from 0° (the edge along y = 0) to 90° (the edge along
x = 50).

- `inlet`: the arc at r = 10, 199 faces, 15.708 mm long.
- `outer_wall`: the arc at r = 50, 199 faces, 78.540 mm long.
- `outlet`: the two 1 mm ends of the gap, r = 49 to 50 at 0° and at 90°, 9 faces each.
- `interios`: the two straight edges from r = 10 to 49, 199 faces each.
- `porous` is everything from r = 10 to 49; `wal_fluid` is the gap from r = 49 to 50, joined to it along
  the interior zone `interior-porous-wal_fluid`.

The spacing is uniform: 0.196 mm between rings in the rotor (199 cells over 39 mm), 0.111 mm in the gap
(9 cells over 1 mm), and 90°/199 = 0.452° between rays.

## Reading them

The `.cas.gz` files are the original ASCII mesh files, gzipped (they unpack byte for byte to what
Pointwise wrote). Fluent reads them as they are: File → Read → Mesh. Scale from millimetres to metres
after reading. In Python:

```
python -m deaerator.mesh mesh/We_Love_CFD_105.cas.gz
```

Despite the `.cas` name, none of the files holds Fluent settings: Pointwise writes the mesh only.
