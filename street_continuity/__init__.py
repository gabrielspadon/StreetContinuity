"""
StreetContinuity (SC)
--------------

    StreetContinuity (SC) is a python library that implements both Intersection Continuity Negotiation (ICN) and
    Hierarchical Intersection Continuity Negotiation (HICN). ICN was first proposed by Porta et al. (2006) and
    further enhanced by Masucci et al. (2014), who advanced with the HICN approach.

    For details about each implementation, please refer to:

    [1] Sergio Porta, Paolo Crucitti, Vito Latora, "The network analysis of urban streets: A dual approach", Physica A:
        Statistical Mechanics and its Applications, Volume 369, Issue 2, 2006, Pages 853-866, ISSN 0378-4371.

    [2] Masucci, A. P., Stanilov, K., Batty, M. (2014). "Exploring the evolution of London's street
        network in the information space: A dual approach." Physical Review E, 89(1), 012805.

Acknowledgement
--------------

    I want to thank Elisabeth H. Krueger and Xianyuan Zhan, who provide me with their version of the HICN.
    Their code gave some insights and helped in the process of validation of the results.

    For details about their implementation, please refer to:

    [3] Krueger, E., Klinkhamer, C., Urich, C., Zhan, X., & Rao, P. S. C. (2017). "Generic patterns in the evolution
        of urban water networks: Evidence from a large Asian city". Physical Review E, 95(3), 032312.

Dependencies
--------------

    * numpy (1.15.4)
    * osmnx (0.8.1)
    * networkx (2.1)

Example
--------------

    >>> import osmnx as ox
    >>> from StreetContinuity.all import *

    >>> oxg = ox.graph_from_point((-22.012282, -47.890821), distance=5000)

    >>> # use_label = True: uses HICN algorithm
    >>> # use_label = False: uses ICN algorithm

    >>> p_graph = from_osmnx(oxg=oxg, use_label=True)
    >>> d_graph = dual_mapper(primal_graph=p_graph, min_angle=120)

    >>> # you must create the data directory before running this command
    >>> write_graphml(graph=d_graph, filename='file.graphml', directory='data')
    >>> write_supplementary(graph=d_graph, filename='supplementary.txt', directory='data')

Links
--------------

    Portfolio::
        https://spadon.com.br/

    Source::
        https://github.com/gabrielspadon/StreetContinuity

Bugs
----
    Please report any bugs that you find at https://github.com/gabrielspadon/StreetContinuity/issues.
    Or, even better, fork the repository on GitHub and create a pull request.

License
-------
    Released under the GNU General Public License v3.0 (GLP-3.0).
    Copyright 2019, Gabriel Spadon, all rights reserved.
        www.spadon.com.br & gabriel@spadon.com.br
"""

import sys

if sys.version_info[:2] < (3, 4):
    m = "Python 3.4 or later is required by StreetContinuity (%d.%d was detected)."
    raise ImportError(m % sys.version_info[:2])
