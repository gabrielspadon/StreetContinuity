"""
Street Continuity Negotiation (SCN)
========
    Street Continuity Negotiation (SCN) is a python library that implements both Intersection Continuity Negotiation
    (ICN) and Hierarchical Intersection Continuity Negotiation (HICN). ICN was first proposed by Porta et al. (2006)
    and further enhanced by Masucci et al. (2014), who introduced the HICN approach.

    For details about each implementation, please refer to:

    [1] Sergio Porta, Paolo Crucitti, Vito Latora, "The network analysis of urban streets: A dual approach", Physica A:
        Statistical Mechanics and its Applications, Volume 369, Issue 2, 2006, Pages 853-866, ISSN 0378-4371.

    [2] Masucci, A. P., Stanilov, K., Batty, M. (2014). "Exploring the evolution of London's street
        network in the information space: A dual approach." Physical Review E, 89(1), 012805.

    I want to thank Elisabeth H. Krueger and Xianyuan Zhan, who provide me with a preliminary version of the HICN.
    Their implementation gave information of how to build this one. I made several improvements, from continuation
    criteria to algorithmic optimization, but I keep using their classes structure.

    For details about their implementation, please refer to:

    [3] Krueger, E., Klinkhamer, C., Urich, C., Zhan, X., & Rao, P. S. C. (2017). "Generic patterns in the evolution
        of urban water networks: Evidence from a large Asian city". Physical Review E, 95(3), 032312.

    Website (including documentation)::
        TODO:: https://XXXXXX.spadon.com.br/

    Source::
        https://github.com/gabrielspadon/XXXXXX

    Bug reports::
        TODO:: https://github.com/gabrielspadon/XXXX/issues

Simple example
--------------
    TODO:: >>> import XXXXX as XXXX

Bugs
----
    Please report any bugs that you find `here <https://github.com/gabrielspadon/XXX/issues>`.
    Or, even better, fork the repository on GitHub and create a pull request.

License
-------
    Released under the GNU General Public License v3.0 (GLP-3.0).
    Copyright 2019, Gabriel Spadon, all rights reserved.
        www.spadon.com.br & gabriel@spadon.com.br
"""

from util import *
from graph import *

import numpy as np

# min_angle = 120  # the angle (in degrees) must lie in range ]0, 180]
# node_dictionary = {}  # dictionary of nodes form the primal network {node_id: [longitude, latitude]}
# edge_dictionary = {}  # dictionary of PrimalEdge {edge_id: PrimalEdge}
# dual_dictionary = {}  # dictionary of DualEdge {dual_id: DualEdge}
# graph = {}  # primal graph that joins node_dictionary and edge_dictionary


def merge_streets(edual, gprimal):
    # Use a initial dual edge as a seed, grow it from both end, util it cannot grow any further
    # recursively calling extendDuelEdge to achieve the objective
    downstream_neighbors = []
    upstream_neighbors = []

    # first, resolve all upstream neighbors
    for i in gprimal.graph[edual.source].keys():
        if i != edual.target:  # check if the edge is not the current edge
            edge = gprimal.edge_dictionary[gprimal.graph[i][edual.source]]
            if not edge.is_used and edge.label == edual.label:
                upstream_neighbors.append(i)

    for i in gprimal.graph[edual.target].keys():
        if i != edual.source:  # check if the edge is not the current edge
            edge = gprimal.edge_dictionary[gprimal.graph[edual.target][i]]
            if not edge.is_used and edge.label == edual.label:
                downstream_neighbors.append(i)

    # recursion exit condition
    if not len(upstream_neighbors) or not len(downstream_neighbors):
        return edual

    # branch to both upstream and downstream neighbors
    upstream_neighbor, downstream_neighbor = False, False

    # first process upstream neighbors
    if len(upstream_neighbors):
        upstream_neighbor = edual.merge_criteria(upstream_neighbors, edual.source, edual.source_eid)

        if upstream_neighbor:
            eid = gprimal.graph[upstream_neighbor][edual.source]
            gprimal.edge_dictionary[eid].is_used = True

            edual.source = upstream_neighbor
            edual.length = edual.length + gprimal.edge_dictionary[eid].length

            if gprimal.edge_dictionary[eid].name not in edual.names:
                edual.names.append(gprimal.edge_dictionary[eid].name)

            if upstream_neighbor not in edual.nodes:
                edual.nodes.append(upstream_neighbor)

            edual.source_eid = eid

    # second process downstream neighbors
    if len(downstream_neighbors):
        downstream_neighbor = edual.merge_criteria(downstream_neighbors, edual.target, edual.target_eid)

        if downstream_neighbor:
            eid = gprimal.graph[edual.target][downstream_neighbor]
            gprimal.edge_dictionary[eid].is_used = True

            edual.target = downstream_neighbor
            edual.length = edual.length + gprimal.edge_dictionary[eid].length

            if gprimal.edge_dictionary[eid].name in edual.names:
                edual.names.append(gprimal.edge_dictionary[eid].name)

            if downstream_neighbor not in edual.nodes:
                edual.nodes.append(downstream_neighbor)

            edual.target_eid = eid

    # final check: if none of from neighbors or end neighbors satisfy the ICN rule
    if not upstream_neighbor and not downstream_neighbor:
        return edual

    merge_streets()  # recursive call


def merge_criteria(neighbors, source, source_eid):
    edge = edge_dictionary[source_eid]
    target = edge.source if source != edge.source else edge.target
    candidates = [compute_angle(neighbor, source, target) for neighbor in neighbors]

    if max(candidates) >= min_angle:
        # return the neighbor that forms the highest convex angle
        return neighbors[np.argmax(candidates)]

    return False


def print_supplementary(directory, file_prefix):
    filename = directory + '/' + file_prefix + "_supplementary.txt"
    with open(filename, 'w') as txt_file:
        for did in dual_dictionary.keys():
            edge = dual_dictionary[did]
            txt_file.write('%s, %f, %s, %s, %s\n' % (did, edge.length, edge.label, edge.names, edge.nodes))
        txt_file.close()


def print_dual(directory, file_prefix):
    filename = directory + '/' + file_prefix + "_dual.csv"
    did = 0  # dual edge ID
    with open(filename, 'w') as csv_file:
        for i in dual_dictionary.keys():
            for j in dual_dictionary.keys():
                if i < j:
                    common = list(set(dual_dictionary[i].nodes).intersection(dual_dictionary[j].nodes))
                    if len(common) > 0:
                        # we found a dual edge here
                        csv_file.write('%s, %s, %s\n' % (did, i, j))
                        did += 1

    print("[D] #Edges: " + str(did - 1))
    csv_file.close()


def dual_mapper(directory, file_prefix):
    global dual_dictionary
    eid = 0
    # iterate through the edge eIDs and grow the dual edges
    for i in edge_dictionary.keys():
        if not edge_dictionary[i].is_used:
            # we found an unused edge, use it as a seed and grow the dual edge
            edge = DualEdge(eid, i)
            merge_streets()
            dual_dictionary[eid] = edge
            eid += 1

    print('[D] #Nodes: %d' % (eid - 1))
    print_supplementary(directory, file_prefix)
    print_dual(directory, file_prefix)


# if __name__ == '__main__':  # For testing purpose
#     use_label = True
#
#     # I am using the city of Sao Carlos as an example, change as you please.
#     oxg = ox.graph_from_point((-22.012282, -47.890821), distance=10000)
#
#     graph, node_dictionary, edge_dictionary = load_osmnx(oxg, use_label)
#
#     # # Input parameter: parameter to change
#     path = 'data/'
#     outfile = 'dual'
#     # nodes_file = '1100015_nodes.csv'
#     # edges_file = '1100015_edges.csv'
#     # directed = False
#     # labeled = True
#     # # MaxAngle = 0.92  # 0.707#0.866 # 30 degree in radius
#     #
#     # # Intermediate variables
#     # # node_dictionary = node_mapper(directory, nodes_filename)
#     # # edge_dictionary = edge_mapper(directory, edges_filename, use_label)
#     # # graph = graph_mapper(is_directed)
#     # primal_mapper(path, nodes_file, edges_file, labeled, directed)
#     #
#     # # Main function: Do not change
#     dual_mapper(path, outfile)
