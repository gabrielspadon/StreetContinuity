# coding=utf-8
#
#   Copyright 2019, Gabriel Spadon, all rights reserved.
#   This code is under GNU General Public License v3.0.
#       www.spadon.com.br & gabriel@spadon.com.br
#
# Verified on February 1th, 2019.


from streetnegotiation.util import *
from streetnegotiation.graph import *

import numpy as np


def merge_criteria(primal_graph: PrimalGraph, neighbors: list, source: int, src_edge: int, min_angle: float = 120):
    """
    The method uses the law of cosines to calculate the angle between the georeferenced coordinates
    of three given nodes. To this end, we approximate the straight-line distance of the sides of the
    triangles formed by such nodes using the haversine distance. Then, we apply the law of cosines
    to find the angle between the triplet which has the negotiator as the intermediate node.
    :param primal_graph: a street network mapped to a PrimalGraph object
    :param neighbors: list of neighbors of the source node
    :param source: source node (also known as negotiator), which is the middle of the triplet
    :param src_edge: edge from which the source node comes from
    :param min_angle: the minimum angle ]0.0, 180.0] that defines the continuity of two consecutive streets
    :return: ID of the neighbor that forms that highest convex angle or False whenever it does not exist
    """

    # retrieving information about the source edge
    edge = primal_graph.edge_dictionary[src_edge]
    # the target is a node different than the source that comes from the source edge
    target = edge.source if source != edge.source else edge.target
    # the neighbor is always on the opposite side of the target
    candidates = [compute_angle(primal_graph.node_dictionary[neighbor],  # coordinates of the neighbor node
                                primal_graph.node_dictionary[source],    # coordinates of the source node
                                primal_graph.node_dictionary[target])    # coordinates of the target node
                  for neighbor in neighbors]

    # returns the neighbor that forms the highest convex angle or False whenever it does not exist.
    return neighbors[np.argmax(candidates)] if np.max(candidates) >= min_angle else False


def explore_neighborhood(primal_graph: PrimalGraph, dual_edge: DualGraph.Edge, is_upstream=True):
    """
    This method sweeps the upstream and downstream neighborhood when provided with the source and target of a dual node.
    As a result, it provides a list of candidate nodes, which can be used to merge primal edges into dual nodes.
    The direction which the method will follow is given by `is_upstream` attribute, which is True by default.
    :param primal_graph: a street network mapped to a PrimalGraph object
    :param dual_edge: the dual edge being expanded in the current iteration
    :param is_upstream: if true, follows the upstream direction of the neighbors starting from the source node
                        otherwise, follows the downstream direction of the neighbors starting from the target node
    :return: List
    """

    # defining the direction of the neighborhood search
    leading_seed = dual_edge.source if is_upstream else dual_edge.target
    reverse_seed = dual_edge.target if is_upstream else dual_edge.source

    neighborhood = []
    for neighbor in primal_graph.graph[leading_seed].keys():
        # checking whether this is a self-loop or the current edge
        if neighbor != reverse_seed:
            if is_upstream:
                # this is the upstream direction (from neighbor to source)
                eid = primal_graph.graph[neighbor][leading_seed]
            else:
                # this is the downstream direction (from target to neighbor)
                eid = primal_graph.graph[leading_seed][neighbor]
            # retrieving the resulting edge
            edge = primal_graph.edge_dictionary[eid]
            # the streets must be unused and have the same type, both of which are merge conditions
            # ... notice that, when using the ICN instead of the HICN all labels should be standardized
            if not edge.mapped and edge.label == dual_edge.label:
                neighborhood.append(neighbor)

    return neighborhood


def extend_neighborhood(primal_graph: PrimalGraph, neighborhood: list, dual_edge: DualGraph.Edge, min_angle: float, is_upstream=True):
    """
    This method analyzes the candidate nodes and merges the dual node with an unused primal edge.
    This process consists of updating the source and target node (from the primal graph edges) that form the dual node.
    Additionally, we save information about distance and the name of the streets for further validation.
    The direction which the method will follow is given by `is_upstream` attribute, which is True by default.
    :param primal_graph: a street network mapped to a PrimalGraph object
    :param neighborhood: a list of candidate nodes, which can be used to merge primal edges into dual nodes
    :param dual_edge: the dual edge being expanded in the current iteration
    :param min_angle: the minimum angle ]0.0, 180.0] that defines the continuity of two consecutive streets
    :param is_upstream: if true, follows the upstream direction of the neighbors starting from the source node
                        otherwise, follows the downstream direction of the neighbors starting from the target node
    :return: ID of the neighbor that forms that highest convex angle or False whenever it does not exist
    """

    if len(neighborhood):
        # retrieving the neighbor that forms the highest convex angle with the existing dual node
        candidate = merge_criteria(primal_graph, neighborhood, dual_edge.source, dual_edge.src_edge, min_angle)

        if candidate:  # the candidate might not exist
            # defining the direction in which we will extend the neighborhood
            eid = primal_graph.graph[candidate][dual_edge.source] if is_upstream \
                else primal_graph.graph[dual_edge.target][candidate]
            # the primal edge is now mapped and cannot be used again
            primal_graph.edge_dictionary[eid].mapped = True

            if is_upstream:
                dual_edge.source = candidate  # to upstream neighborhood, we update the source of the dual node
            else:
                dual_edge.target = candidate  # otherwise, we update the dual node target

            # the length of the street grows by summing the old length with the one from the merged primal edge
            dual_edge.length = dual_edge.length + primal_graph.edge_dictionary[eid].length

            # storing the name of the primal edge in the list of street names of the dual node
            dual_edge.names.append(primal_graph.edge_dictionary[eid].name)

            # storing the nodes (from the primal graph) that are within the dual node
            if candidate not in dual_edge.nodes:
                dual_edge.nodes.append(candidate)

            if is_upstream:
                dual_edge.src_edge = eid  # new source edge id in case of upstream neighborhood
            else:
                dual_edge.tgt_edge = eid  # new target edge id in case of downstream neighborhood

        return candidate
    return False


def merge_streets(primal_graph: PrimalGraph, dual_edge: DualGraph.Edge, min_angle: float = 120.0):
    """
    This method holds the recursive calls that grow the streets of a city in the form of a dual graph node. First, the
    technique explores the neighborhood looking for candidates and then, it uses the best candidate to form a street.
    :param dual_edge: the dual edge being expanded in the current iteration
    :param primal_graph: a street network mapped to a PrimalGraph object
    :param min_angle: the minimum angle ]0.0, 180.0] that defines the continuity of two consecutive streets
    :return:
    """

    # exploring the neighborhood on the upstream side
    upstream = explore_neighborhood(primal_graph, dual_edge, is_upstream=True)
    # exploring the neighborhood on the downstream side
    downstream = explore_neighborhood(primal_graph, dual_edge, is_upstream=False)

    # the code stops when there are no candidates to expand the street
    if not len(upstream) and not len(downstream):
        return dual_edge

    # growing the street on the upstream side
    upstream_neighbor = extend_neighborhood(primal_graph, upstream, dual_edge, min_angle, is_upstream=True)
    # growing the street on the downstream side
    downstream_neighbor = extend_neighborhood(primal_graph, downstream, dual_edge, min_angle, is_upstream=False)

    # the code stops when no candidates satisfy the merge criteria
    if not upstream_neighbor and not downstream_neighbor:
        return dual_edge

    # if all looks good, we make a recursive call
    merge_streets(dual_edge, primal_graph)


def dual_mapper(primal_graph: PrimalGraph, min_angle: float = 120.0):
    """
    This is a straightforward method, which is capable of mapping a PrimalGraph object into a DualGraph one.
    The method maps the streets of the cities to nodes and the intersections among them to edges.
    :param primal_graph: a street network mapped to a PrimalGraph object
    :param min_angle: the minimum angle ]0.0, 180.0] that defines the continuity of two consecutive streets
    :return: DualGraph
    """

    # creating an empty dual graph
    dual_graph = DualGraph()

    nid = 0
    # populating nodes' dictionary
    for eid in primal_graph.edge_dictionary.keys():
        primal_edge = primal_graph.edge_dictionary[eid]
        if not primal_edge.mapped:
            # setting the primal edge as mapped to dual
            primal_edge.mapped = True
            # using the unmapped primal edge as the seed of the new dual node
            dual_edge = dual_graph.Edge(nid, primal_edge)
            # checking the upstream and downstream neighbors for street continuity
            merge_streets(primal_graph, dual_edge, min_angle)
            # storing the resulting node in the node dictionary
            dual_graph.node_dictionary[nid] = dual_edge
            # incrementing nodes' index
            nid += 1

    eid = 0
    # populating edges' dictionary
    for sid, source in dual_graph.node_dictionary.items():
        for tid, target in dual_graph.node_dictionary.item():
            # [INFO] whenever a node of the primal graph appears at the same time in two or
            # ... more nodes of the dual graph, it means that there is an intersection
            # ... between the streets and a link between two nodes in the dual graph.
            if sid < tid and set(source.nodes) & set(target.nodes):
                # storing the resulting edge in the edge dictionary
                dual_graph.edge_dictionary[eid] = (sid, tid)
                # incrementing edges' index
                eid += 1

    return dual_graph


# if __name__ == '__main__':  # For testing purpose
#     from streetnegotiation.file import *
#     use_label = True
#
#     # I am using the city of Sao Carlos as an example, change as you please.
#     oxg = ox.graph_from_point((-22.012282, -47.890821), distance=400)
#
#     primal_graph = from_osmnx(oxg, use_label)
#
#     dual_mapper(primal_graph)
