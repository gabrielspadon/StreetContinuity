# StreetContinuity

Primal-to-dual street network transformation using ICN and HICN algorithms.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## Overview

StreetContinuity transforms street networks from primal representation (nodes=intersections, edges=street segments) to dual representation (nodes=streets, edges=intersections) using Intersection Continuity Negotiation (ICN) and Hierarchical ICN (HICN) algorithms. Based on Porta et al. (2006) and Masucci et al. (2014).

## Features

- **ICN Algorithm**: Groups street segments by angular continuity (45 deg threshold)
- **HICN Algorithm**: Multi-level continuity with road hierarchy awareness
- **OSMnx Integration**: Direct import from OpenStreetMap
- **Multiple I/O Formats**: CSV, GraphML, and supplementary data export

## Installation

```bash
pip install -r requirements.txt
pip install -e .
```

### Requirements

- Python 3.10+
- OSMnx 2.0+, NetworkX
- geopandas, numpy

## Quick Start

```python
import osmnx as ox
from street_continuity.graph import from_osmnx
from street_continuity.mapper import dual_mapper
from street_continuity.file import write_graphml, write_supplementary

# Download street network
oxg = ox.graph_from_point((-22.012282, -47.890821), dist=5000)

# Convert to primal graph (use_label=True for HICN, False for ICN)
p_graph = from_osmnx(oxg=oxg, use_label=True)

# Map to dual graph
d_graph = dual_mapper(primal_graph=p_graph, min_angle=120)

# Export
write_graphml(graph=d_graph, filename='dual.graphml', directory='data')
write_supplementary(graph=d_graph, filename='supplementary.txt', directory='data')
```

## CLI

```bash
python -m street_continuity \
    --city "San Francisco, USA" \
    --method hicn \
    --output dual_graph.graphml
```

## Algorithms

### ICN (Intersection Continuity Negotiation)

Groups street segments by angular continuity at intersections:
- Threshold: 45 deg maximum deflection angle
- Result: Named street strokes

### HICN (Hierarchical ICN)

Extends ICN with road hierarchy awareness:
- Considers road class (motorway > primary > residential)
- Weighted angle + hierarchy scoring

## Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `min_angle` | Min angle for continuity (degrees) | 120 |
| `use_label` | Use HICN (True) or ICN (False) | True |

## Project Structure

```
street_continuity/
  __init__.py     # Package documentation
  mapper.py       # Primal-to-dual mapping
  graph.py        # Graph construction from OSMnx
  file.py         # GraphML, CSV, supplementary I/O
  util.py         # Angle calculations, helpers
  all.py          # Convenience imports
tests/            # Unit tests
data/             # Sample data
```

## Dual Graph Properties

- **Nodes**: Street strokes (continuous segments)
- **Edges**: Intersections between strokes
- **Attributes**: length, name, road_class, geometry

## Testing

```bash
pytest tests/ -v --cov=street_continuity --cov-report=term-missing
```

## References

- Porta et al. (2006). [The network analysis of urban streets: A dual approach](https://doi.org/10.1016/j.physa.2005.12.063). Physica A, 369(2), 853-866.
- Masucci et al. (2014). [Exploring the evolution of London's street network](https://doi.org/10.1103/PhysRevE.89.012805). Physical Review E, 89(1), 012805.

## License

GNU General Public License v3.0

## Author

**Gabriel Spadon** - Dalhousie University
[gabriel@spadon.com.br](mailto:gabriel@spadon.com.br)
