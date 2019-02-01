# coding=utf-8
#
#   Copyright 2019, Gabriel Spadon, all rights reserved.
#   This code is under GNU General Public License v3.0.
#       www.spadon.com.br & gabriel@spadon.com.br
#


from streetnegotiation.util import *
from streetnegotiation.graph import *

import numpy as np


def dual_mapper(primal_graph: PrimalGraph, min_angle: float = 120.0):
    """
    This is a straightforward method, which is capable of mapping a PrimalGraph object into a DualGraph one.
    The method maps the streets of the cities to the nodes and the intersections among them to the edges.
    :param primal_graph: a street networks mapped to a PrimalGraph object
    :param min_angle: is the minimum angle ]0.0, 180.0] that define the continuity of two consecutive streets
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


def merge_streets(primal_graph: PrimalGraph, dual_edge: DualGraph.Edge, min_angle: float = 120.0):
    """

    :param dual_edge:
    :param primal_graph: a street networks mapped to a PrimalGraph object
    :param min_angle: is the minimum angle ]0.0, 180.0] that define the continuity of two consecutive streets
    :return:
    """

    upstream_neighbors = []
    for target in primal_graph.graph[dual_edge.source].keys():
        if target != dual_edge.target:
            eid = primal_graph.graph[target][dual_edge.source]
            edge = primal_graph.edge_dictionary[eid]
            if not edge.mapped and edge.label == dual_edge.label:
                upstream_neighbors.append(target)

    downstream_neighbors = []
    for source in primal_graph.graph[dual_edge.target].keys():
        if source != dual_edge.source:
            eid = primal_graph.graph[dual_edge.target][source]
            edge = primal_graph.edge_dictionary[eid]
            if not edge.mapped and edge.label == dual_edge.label:
                downstream_neighbors.append(source)

    if not len(upstream_neighbors) and not len(downstream_neighbors):
        return dual_edge

    # branch to both upstream and downstream neighbors
    upstream_neighbor, downstream_neighbor = False, False

    # first process upstream neighbors
    if len(upstream_neighbors):
        upstream_neighbor = merge_criteria(primal_graph, upstream_neighbors, dual_edge.source, dual_edge.src_edge, min_angle)

        if upstream_neighbor:
            eid = primal_graph.graph[upstream_neighbor][dual_edge.source]
            primal_graph.edge_dictionary[eid].mapped = True

            dual_edge.source = upstream_neighbor
            dual_edge.length = dual_edge.length + primal_graph.edge_dictionary[eid].length

            if primal_graph.edge_dictionary[eid].name not in dual_edge.names:
                dual_edge.names.append(primal_graph.edge_dictionary[eid].name)

            if upstream_neighbor not in dual_edge.nodes:
                dual_edge.nodes.append(upstream_neighbor)

            dual_edge.src_edge = eid

    # second process downstream neighbors
    if len(downstream_neighbors):
        downstream_neighbor = merge_criteria(primal_graph, downstream_neighbors, dual_edge.target, dual_edge.tgt_edge, min_angle)

        if downstream_neighbor:
            eid = primal_graph.graph[dual_edge.target][downstream_neighbor]
            primal_graph.edge_dictionary[eid].mapped = True

            dual_edge.target = downstream_neighbor
            dual_edge.length = dual_edge.length + primal_graph.edge_dictionary[eid].length

            if primal_graph.edge_dictionary[eid].name in dual_edge.names:
                dual_edge.names.append(primal_graph.edge_dictionary[eid].name)

            if downstream_neighbor not in dual_edge.nodes:
                dual_edge.nodes.append(downstream_neighbor)

            dual_edge.tgt_edge = eid

    # final check: if none of from neighbors or end neighbors satisfy the StreetNegotiation rule
    if not upstream_neighbor and not downstream_neighbor:
        return dual_edge

    merge_streets(dual_edge, primal_graph)  # recursive call


def merge_criteria(primal_graph, neighbors, source, src_edge, min_angle: float = 120):
    edge = primal_graph.edge_dictionary[src_edge]
    target = edge.source if source != edge.source else edge.target
    candidates = [compute_angle(primal_graph.node_dictionary[neighbor],
                                primal_graph.node_dictionary[source],
                                primal_graph.node_dictionary[target]) for neighbor in neighbors]

    if max(candidates) >= min_angle:
        # return the neighbor that forms the highest convex angle
        return neighbors[np.argmax(candidates)]

    return False


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
