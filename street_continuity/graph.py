# coding=utf-8
#
#   Copyright 2019, Gabriel Spadon, all rights reserved.
#   This code is under GNU General Public License v3.0.
#       www.spadon.com.br & gabriel@spadon.com.br
#
# Verified on February 1th, 2019.


class PrimalGraph:
    """
    This class gatherer information about the Primal Graph of a given city.
    The nodes and edges are stored in the form of dictionaries and can be mapped into an adjacency list.
    """

    # --- nested class --- #

    class Edge:  # also referred to as PrimalEdge
        """
        Edge is an inner class of PrimalGraph that stores information about the edge that connects a pair of nodes.
        Such information comes straight from the input file, and we assume that they are all correct and verified.
        """

        def __init__(self, eid: int, source: str, target: str, length: float, name: str, label: str):
            self.mapped = False   # [boolean] whether the edge was mapped or not;
            self.source = source  # [string] index of the source node;
            self.target = target  # [string] index of the target node;
            self.length = length  # [float] street length (in meters);
            self.label = label    # [string] street label or class (default: "unclassified");
            self.name = name      # [string] street name (default: "unknown"); and,
            self.eid = eid        # [integer] street index.

    # --- nested class --- #

    def __init__(self):
        self.node_dictionary = {}
        self.edge_dictionary = {}
        self.graph = {}

    def build_graph(self):
        """
        This method creates the adjacency list of the PrimalGraph using the dictionary of edges.
        Such a list stores the id of the edges (PrimalEdge object) that link pairs of nodes.
        :return: PrimalGraph
        """

        for eid, edge in self.edge_dictionary.items():

            # storing the outgoing link
            if edge.source not in self.graph.keys():
                self.graph[edge.source] = {edge.target: None}

            self.graph[edge.source][edge.target] = edge.eid

            # storing the incoming link
            if edge.target not in self.graph.keys():
                self.graph[edge.target] = {edge.source: None}

            self.graph[edge.target][edge.source] = edge.eid

        return self

    def set_nodes(self, node_dictionary: dict):
        self.node_dictionary = node_dictionary

    def set_edges(self, edge_dictionary: dict):
        self.edge_dictionary = edge_dictionary


class DualGraph:
    """
    This class stores information about the Dual Graph that was mapped through a Primal Graph.
    The nodes and edges are stored in the form of dictionaries and can be mapped into an adjacency list.
    """

    # --- nested class --- #

    class Node:  # also referred to as DualNode
        """
        Node is an inner class of DualGraph used to store information about nodes mapped from primal edges.
        Such information is iteratively updated every time a new PrimalEdge is merged into a DualNode.
        """

        def __init__(self, did: int, pge: PrimalGraph.Edge):
            self.src_edge = pge.eid     # [integer] index of the first (left-most) primal edge;
            self.tgt_edge = pge.eid     # [integer] index of the last (right-most) primal edge;
            self.source = pge.source    # [string] index of the source node of the first primal edge;
            self.target = pge.target    # [string] index of the target node of the last primal edge;
            self.length = pge.length    # [float] cumulative length of the whole dual node;
            self.label = pge.label      # [string] label of primal edges within the dual node;
            self.names = [pge.name]     # [list] list with names of all primal edges;
            self.nodes = [pge.source,   # [list] list of all primal nodes within the dual node;
                          pge.target]
            self.edges = [(pge.source,  # [list] list of pairs of edges part of the dual node; and,
                           pge.target)]
            self.did = did              # [integer] dual node index.

    # --- nested class --- #

    def __init__(self):
        self.edge_dictionary = {}  # the edges that connect the dual nodes
        self.node_dictionary = {}  # each item in this dictionary is a set of streets of greatest continuity
        self.graph = {}

    def build_graph(self):
        """
        This method creates the adjacency list of the DualGraph using the dictionary of edges.
        Such a list stores the id of the edges that link pairs of nodes.
        :return: DualGraph
        """

        for eid, edge in self.edge_dictionary.items():

            # storing the outgoing link
            if edge.source not in self.graph.keys():
                self.graph[edge.source] = {edge.target: None}

            self.graph[edge.source][edge.target] = edge.eid

            # storing the incoming link
            if edge.target not in self.graph.keys():
                self.graph[edge.target] = {edge.source: None}

            self.graph[edge.target][edge.source] = edge.eid

        return self

    def set_nodes(self, node_dictionary: dict):
        self.node_dictionary = node_dictionary

    def set_edges(self, edge_dictionary: dict):
        self.edge_dictionary = edge_dictionary
