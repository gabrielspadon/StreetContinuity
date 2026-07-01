# StreetContinuity

Primal-to-dual street network with Intersection Continuity
Negotiation (ICN) and Hierarchical ICN (H-ICN).

![A street network and its dual representation](images/sc-test.png)

*A real-world street network and its dual. On the left, the primal graph drawn in
geographic space, where nodes are intersections and edges are street segments. On the
right, the same city after the transformation, rendered with Gephi and the OpenOrd
force-directed layout. The dual graph has no coordinates, so its arrangement reflects
only how streets connect to one another.*

## From space to semantics

A street network is naturally geographic. In the primal representation every node is
an intersection pinned to coordinates and every edge is a segment with a physical
length. That embedding is ideal for routing and cartography, but it hides the entity
people actually reason about, the street as a whole.

StreetContinuity rebuilds the network around that entity. Consecutive segments that
flow through intersections with little deflection (and, for HICN, share a road class)
are merged into a single node, a continuous street. Two nodes are linked whenever
their streets cross. The result is the dual graph, and the trade is deliberate. The
spatial attribute is discarded and replaced by a semantic one, so nodes no longer
answer "where is this point" but "which street is this", and edges encode the
relation between streets rather than distances between corners. Masucci et al. (2014)
call this moving the network into *information space*.

Working in information space is what makes street-level analyses possible. The degree
of a node counts how many streets one street crosses, path lengths count turns rather
than meters, and classic network measures (centrality, small-world and scale-free
behavior) become statements about the city's structure instead of its geometry.

Two algorithms are provided, both following the dual-graph approach introduced by
Porta et al. (2006) and extended by Masucci et al. (2014).

- **ICN** negotiates continuity purely by geometry. At each intersection, a street
  continues into the neighboring segment that forms the widest continuity angle,
  provided that angle stays above `min_angle` (180 degrees means perfectly straight).
- **HICN** adds hierarchy awareness, so continuity is only negotiated between
  segments of the same road class (a motorway never merges into a residential road).

## Installation

```bash
pip install -e .
```

or, to install only the runtime dependencies,

```bash
pip install -r requirements.txt
```

Python 3.10 to 3.12, with OSMnx 2.0+, NetworkX 2.6+, and NumPy 1.24+.

## Quick start

```python
import osmnx as ox
from street_continuity import from_osmnx, dual_mapper, write_graphml, write_supplementary

# Download a street network from OpenStreetMap.
oxg = ox.graph_from_point((-22.012282, -47.890821), dist=5000)

# Build the primal graph (use_label=True selects HICN, False selects ICN).
primal = from_osmnx(oxg=oxg, use_label=True)

# Trade geographic space for information space.
dual = dual_mapper(primal_graph=primal, min_angle=120)

# Export the result.
write_graphml(graph=dual, filename="dual.graphml", directory="data")
write_supplementary(graph=dual, filename="supplementary.txt", directory="data")
```

## Command-line interface

```bash
# Download a place from OpenStreetMap and export its dual graph (HICN).
python -m street_continuity --place "Ji-Paraná, Brazil" --method hicn --output dual.graphml

# Convert a local pair of node/edge CSV files (ICN).
python -m street_continuity \
    --nodes test-nodes.csv --edges test-edges.csv --data-dir data \
    --method icn --output dual.graphml
```

Run `python -m street_continuity --help` for the full list of input sources
(`--place`, `--point`, `--graphml`, `--nodes`/`--edges`) and options.

## Input and output

A network can come from OSMnx directly, from a GraphML file saved by OSMnx, or from a
pair of CSV files.

- **nodes** `index, latitude, longitude`
- **edges** `index, source, target, length, name, label`

Coordinates are handled internally as `(latitude, longitude)`. CSV input keeps the
length column as given, while networks from OSMnx keep the length OSMnx computed
along the street geometry (falling back to the great-circle distance between the
segment endpoints when the attribute is absent). Continuity angles are always
evaluated between segment endpoints, so curvature within a segment does not
participate in the negotiation.

The output is a GraphML file holding the dual graph, where each node carries its
member street names, member primal nodes, and cumulative length, plus an optional
supplementary text file with one line per street.

## Parameters

| Parameter   | Description                                                          | Default |
|-------------|----------------------------------------------------------------------|---------|
| `min_angle` | Minimum continuity angle in degrees, where 180 is perfectly straight | 120     |
| `use_label` | Selects HICN (`True`) or ICN (`False`)                               | required in the API; the CLI sets it via `--method` (default `hicn`) |

A higher `min_angle` accepts only the straightest continuations, producing more and
shorter streets. A lower value merges through sharper bends into fewer, longer ones.

## Testing

```bash
pip install -e ".[dev]"
pytest --cov=street_continuity --cov-report=term-missing
```

## References

1. S. Porta, P. Crucitti, V. Latora. "The network analysis of urban streets: A dual
   approach." *Physica A*, 369(2), 2006, pp. 853-866.
   [doi:10.1016/j.physa.2005.12.063](https://doi.org/10.1016/j.physa.2005.12.063)
2. A. P. Masucci, K. Stanilov, M. Batty. "Exploring the evolution of London's street
   network in the information space: A dual approach." *Physical Review E*, 89(1),
   2014, 012805. [doi:10.1103/PhysRevE.89.012805](https://doi.org/10.1103/PhysRevE.89.012805)

## Acknowledgement

Thanks to Elisabeth H. Krueger and Xianyuan Zhan for sharing their version of the HICN
algorithm, which helped validate these results (Krueger et al., *Physical Review E*,
95(3), 2017, 032312).

## License

Released under the GNU General Public License v3.0. See [LICENSE](LICENSE).

## Author

**Gabriel Spadon**
([gabriel@spadon.com.br](mailto:gabriel@spadon.com.br))
