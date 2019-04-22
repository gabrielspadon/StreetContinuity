StreetContinuity (SC)
========

StreetContinuity (SC) is a python library that implements both Intersection Continuity Negotiation (ICN) and Hierarchical Intersection Continuity Negotiation (HICN). ICN was first proposed by Porta et al. (2006) and further enhanced by Masucci et al. (2014), who advanced with the HICN approach.

For details about each implementation, please refer to:

* [Sergio Porta, Paolo Crucitti, Vito Latora, **The network analysis of urban streets: A dual approach**. Physica A: Statistical Mechanics and its Applications, Volume 369, Issue 2, 2006, Pages 853-866, ISSN 0378-4371](https://doi.org/10.1016/j.physa.2005.12.063).

* [Masucci, A. P., Stanilov, K., Batty, M. (2014). **Exploring the evolution of London's street network in the information space: A dual approach**. Physical Review E, 89(1), 012805](https://doi.org/10.1103/PhysRevE.89.012805).

Acknowledgement
--------------

I want to thank Elisabeth H. Krueger and Xianyuan Zhan, who provide me with their version of the HICN.
Their code gave some insights and helped in the process of validation of the results.

For details about their implementation, please refer to:

* [Krueger, E., Klinkhamer, C., Urich, C., Zhan, X., & Rao, P. S. C. (2017). **Generic patterns in the evolution of urban water networks: Evidence from a large Asian city**. Physical Review E, 95(3), 032312](https://dx.doi.org/10.1103/PhysRevE.95.032312).

Dependencies
--------------

* numpy (1.15.4)
* osmnx (0.8.1)
* networkx (2.1)

Instalation (for developers)
--------------

After downloading the SC library, install it on Python 3 using the following commands:


```bash
pip3 install . --user
```

Example
--------------

```python
import osmnx as ox
from street_continuity.all import *

# load the primal graph from osmnx
oxg = ox.graph_from_point((-22.012282, -47.890821), distance=5000)
p_graph = from_osmnx(oxg=oxg, use_label=True)

# alternatively, you can load the graph from a csv file
# p_graph = read_csv(nodes_filename='test-nodes.csv', edges_filename='test-edges.csv', directory='data', use_label=True, has_header=False)

# maps the primal graph to the dual representation
# use_label = True: uses HICN algorithm
# use_label = False: uses ICN algorithm
d_graph = dual_mapper(primal_graph=p_graph, min_angle=90)

# you must create the data directory before running this command
dxg = write_graphml(graph=d_graph, filename='file.graphml', directory='data')
write_supplementary(graph=d_graph, filename='supplementary.txt', directory='data')
```

Result
--------------

This is the resulting graph using Gephi (0.9.2) and [OpenOrd](https://github.com/gephi/gephi/wiki/OpenOrd) layout with default parameters:

![Primal and Dual Graph](https://github.com/gabrielspadon/StreetContinuity/blob/master/images/sc-test.png)

Primal Graph (from OSMNX) on the left and Dual Graph (from StreetContinuity) on the right.
