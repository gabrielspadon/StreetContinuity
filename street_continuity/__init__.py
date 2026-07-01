"""
StreetContinuity (SC)
=====================

StreetContinuity is a Python library that implements the Intersection Continuity
Negotiation (ICN) and Hierarchical Intersection Continuity Negotiation (HICN)
algorithms. ICN was first proposed by Porta et al. (2006) and later extended by
Masucci et al. (2014), who introduced the hierarchical (HICN) variant.

The library converts a street network from its *primal* representation (nodes are
intersections, edges are street segments) into its *dual* representation (nodes are
continuous streets, edges are the intersections between them). The transformation
deliberately trades the spatial attribute for a semantic one; the dual graph carries
no geometry and lives in what Masucci et al. call *information space*, where network
measures describe how streets relate instead of where they sit.

References
----------
[1] Sergio Porta, Paolo Crucitti, Vito Latora. "The network analysis of urban
    streets: A dual approach." Physica A, 369(2), 2006, pp. 853-866.
[2] A. P. Masucci, K. Stanilov, M. Batty. "Exploring the evolution of London's
    street network in the information space: A dual approach." Physical Review E,
    89(1), 2014, 012805.

Acknowledgement
---------------
Thanks to Elisabeth H. Krueger and Xianyuan Zhan for sharing their version of the
HICN algorithm, which helped validate these results.
[3] Krueger, E., Klinkhamer, C., Urich, C., Zhan, X., Rao, P. S. C. (2017). "Generic
    patterns in the evolution of urban water networks: Evidence from a large Asian
    city." Physical Review E, 95(3), 032312.

Example
-------
    >>> import osmnx as ox
    >>> from street_continuity.file import from_osmnx, write_graphml, write_supplementary
    >>> from street_continuity.mapper import dual_mapper
    >>>
    >>> oxg = ox.graph_from_point((-22.012282, -47.890821), dist=5000)
    >>> primal = from_osmnx(oxg=oxg, use_label=True)   # use_label=True -> HICN, False -> ICN
    >>> dual = dual_mapper(primal_graph=primal, min_angle=120)
    >>> write_graphml(graph=dual, filename="dual.graphml", directory="data")
    >>> write_supplementary(graph=dual, filename="supplementary.txt", directory="data")

License
-------
Released under the GNU General Public License v3.0.
Copyright 2019, Gabriel Spadon.
    gabriel@spadon.com.br
"""

from street_continuity.file import (
    from_osmnx,
    read_csv,
    read_graphml,
    write_graphml,
    write_supplementary,
)
from street_continuity.graph import DualGraph, PrimalGraph
from street_continuity.mapper import dual_mapper
from street_continuity.util import compute_angle, compute_distance

__version__ = "0.2.0"
__author__ = "Gabriel Spadon"
__license__ = "GPL-3.0-or-later"

__all__ = [
    "PrimalGraph",
    "DualGraph",
    "from_osmnx",
    "read_csv",
    "read_graphml",
    "dual_mapper",
    "write_graphml",
    "write_supplementary",
    "compute_angle",
    "compute_distance",
    "__version__",
]
