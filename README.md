# StreetContinuity

Street network continuity analysis using Intersection Continuity Negotiation (ICN) and Hierarchical ICN (HICN).

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## Overview

StreetContinuity is a Python library that implements both **Intersection Continuity Negotiation (ICN)** and **Hierarchical Intersection Continuity Negotiation (HICN)**. These algorithms analyze street networks by identifying continuous streets based on geometric and hierarchical properties.

ICN was first proposed by Porta et al. (2006) and further enhanced by Masucci et al. (2014), who advanced with the HICN approach.

For details about each implementation, please refer to:

* [Sergio Porta, Paolo Crucitti, Vito Latora, **The network analysis of urban streets: A dual approach**. Physica A: Statistical Mechanics and its Applications, Volume 369, Issue 2, 2006, Pages 853-866, ISSN 0378-4371](https://doi.org/10.1016/j.physa.2005.12.063).

* [Masucci, A. P., Stanilov, K., Batty, M. (2014). **Exploring the evolution of London's street network in the information space: A dual approach**. Physical Review E, 89(1), 012805](https://doi.org/10.1103/PhysRevE.89.012805).

Acknowledgement
--------------

I want to thank Elisabeth H. Krueger and Xianyuan Zhan, who provide me with their version of the HICN.
Their code gave some insights and helped in the process of validation of the results.

For details about their implementation, please refer to:

* [Krueger, E., Klinkhamer, C., Urich, C., Zhan, X., & Rao, P. S. C. (2017). **Generic patterns in the evolution of urban water networks: Evidence from a large Asian city**. Physical Review E, 95(3), 032312](https://dx.doi.org/10.1103/PhysRevE.95.032312).

## Features

- **ICN Algorithm**: Detect street continuity based on geometric angles
- **HICN Algorithm**: Hierarchical continuity using street names and classification
- **Primal-Dual Conversion**: Convert street networks (primal) to continuity graphs (dual)
- **OSMnx Integration**: Direct import from OpenStreetMap data
- **Multiple I/O Formats**: CSV, GraphML, and supplementary data export

## Installation

### For Users

```bash
pip install -e .
```

### For Developers

```bash
git clone https://github.com/gabrielspadon/street-continuity.git
cd street-continuity
pip install -e ".[dev]"
```

## Requirements

- Python 3.10+
- numpy >= 1.26.0
- osmnx >= 1.7.0
- networkx >= 3.2.0

## Quick Start

### Basic Usage with OSMnx

```python
import osmnx as ox
from street_continuity.all import *

# Download street network from OpenStreetMap
oxg = ox.graph_from_point(
    (-22.012282, -47.890821),  # São Carlos, Brazil
    distance=5000,
    network_type='drive'
)

# Convert to primal graph format
# use_label=True: uses street names (HICN)
# use_label=False: ignores names (ICN)
p_graph = from_osmnx(oxg=oxg, use_label=True)

# Map primal graph to dual representation
# min_angle: minimum angle (degrees) for continuity
d_graph = dual_mapper(primal_graph=p_graph, min_angle=90)

# Export results
write_graphml(graph=d_graph, filename='street_continuity.graphml', directory='output')
write_supplementary(graph=d_graph, filename='supplementary.txt', directory='output')
```

### Loading from CSV Files

```python
from street_continuity.all import *

# Load graph from CSV files
p_graph = read_csv(
    nodes_filename='nodes.csv',
    edges_filename='edges.csv',
    directory='data',
    use_label=True,  # Use HICN (with street names)
    has_header=True
)

# Process as above
d_graph = dual_mapper(primal_graph=p_graph, min_angle=90)
```

### Understanding ICN vs HICN

```python
# ICN: Geometric continuity only
d_graph_icn = dual_mapper(primal_graph=p_graph, min_angle=90)

# HICN: Geometric + hierarchical (name/classification)
# Already applied when use_label=True in from_osmnx/read_csv
```

## Project Structure

```
street-continuity/
├── street_continuity/
│   ├── __init__.py
│   ├── graph.py          # PrimalGraph and DualGraph classes
│   ├── mapper.py         # Primal-to-dual conversion logic
│   ├── file.py           # I/O operations
│   ├── util.py           # Distance and angle calculations
│   └── all.py            # Convenience imports
├── tests/
│   ├── test_graph.py     # Graph class tests
│   └── test_util.py      # Utility function tests
└── setup.py
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=street_continuity

# Run specific test file
pytest tests/test_graph.py -v
```

## Algorithm Details

### Intersection Continuity Negotiation (ICN)

ICN identifies continuous streets by:
1. Computing deflection angles at each intersection
2. Selecting edge pairs with smallest deflection angle
3. Merging edges below threshold into dual nodes

### Hierarchical ICN (HICN)

HICN extends ICN by:
1. Prioritizing edges with matching street names
2. Considering street classification (primary, secondary, etc.)
3. Only merging edges with same hierarchy level

## Visualization

Export to GraphML and visualize with [Gephi](https://gephi.org/):

```python
# Export dual graph
write_graphml(graph=d_graph, filename='output.graphml', directory='viz')

# In Gephi:
# 1. Import output.graphml
# 2. Apply OpenOrd layout
# 3. Color by street name/classification
```

## CSV File Format

### Nodes File
```csv
node_id,latitude,longitude
1,40.7128,-74.0060
2,40.7589,-73.9851
```

### Edges File
```csv
source,target,length,name,classification
1,2,523.4,Broadway,primary
2,3,312.1,Broadway,primary
```

## Author

**Gabriel Spadon**
- Email: gabriel@spadon.com.br
- Website: [www.spadon.com.br](https://www.spadon.com.br)
- Affiliation: Dalhousie University

## Citation

If you use StreetContinuity in your research, please cite:

```bibtex
@software{spadon_street_continuity,
  author = {Spadon, Gabriel},
  title = {StreetContinuity: Street Network Analysis via ICN and HICN},
  year = {2024},
  url = {https://github.com/gabrielspadon/street-continuity}
}
```

## License

Copyright 2019-2024 Gabriel Spadon

GNU General Public License v3.0

See [LICENSE](LICENSE) for details.
