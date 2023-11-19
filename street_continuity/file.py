# coding=utf-8
#
#   Copyright 2019, Gabriel Spadon, all rights reserved.
#   This code is under GNU General Public License v3.0.
#       www.spadon.com.br & gabriel@spadon.com.br
#
# Verified on February 1th, 2019.


from street_continuity.util import *
from street_continuity.graph import *

import csv
import numpy as np
import networkx as nx


def read_csv(nodes_filename: str, edges_filename: str, directory: str, use_label: bool, has_header: bool = False):
    """
    Method for creating a primal graph through two CSV files, one describing the nodes and another the edges.
    Nodes should be organized as {index, longitude, latitude} and edges as {index, source, target, length, name, label}.
    :param nodes_filename: nodes filename
    :param edges_filename: edges filename
    :param directory: full path of the files directory
    :param use_label: if true, it maps streets' type as labels (required for the HICN algorithm)
                      otherwise, streets' type is standardized as "unlabeled" (required for the ICN algorithm)
    :param has_header: if true, it skips the first line when reading the files
    :return: PrimalGraph
    """

    # creating an empty primal graph
    primal_graph = PrimalGraph()

    node_dictionary = {}
    with open(directory + '/' + nodes_filename, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
        for nid, lon, lat in csv_reader:
            if not has_header:
                node_dictionary[nid] = [np.float(lon), np.float(lat)]
            has_header = False
        csv_file.close()

    # updating the dictionary of nodes
    primal_graph.node_dictionary = node_dictionary

    edge_dictionary = {}
    with open(directory + '/' + edges_filename, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',', quotechar='"')

        for eid, source, target, length, name, label in csv_reader:
            if not has_header:
                if compute_distance(node_dictionary[source], node_dictionary[target]) > 0.0:  # sanity check: self-loops are not allowed
                    edge_dictionary[eid] = primal_graph.Edge(eid, source, target, np.float(length),
                                                             name, label if use_label else 'unclassified')
            has_header = False
        csv_file.close()

    # updating the dictionary of edges
    primal_graph.edge_dictionary = edge_dictionary

    # building and returning the resulting PrimalGraph
    return primal_graph.build_graph()


def read_graphml(graphml_file: str, use_label: bool):
    """
    This method loads a GraphML file into an OSMX MultiDiGraph and uses method "from_osmnx" to create a PrimalGraph.
    :param graphml_file: a graph that was saved using the save_graphml() osmnx function
    :param use_label: if true, it maps streets' type as labels (required for the HICN algorithm)
                      otherwise, streets' type are standardized as "unlabeled" (required for the ICN algorithm)
    :return: PrimalGraph
    """

    # the full path should be informed through "graphml_file" parameter
    oxg = ox.load_graphml(filename=graphml_file, folder='')

    return from_osmnx(oxg, use_label)


def from_osmnx(oxg: nx.MultiDiGraph, use_label: bool):
    """
    The method transforms an OSMX MultiDiGraph into a PrimalGraph object
    :param oxg: an OSMX MultiDiGraph
    :param use_label: if true, it maps streets' type as labels (required for the HICN algorithm)
                      otherwise, streets' type are standardized as "unlabeled" (required for the ICN algorithm)
    :return: PrimalGraph
    """

    # creating an empty primal graph
    primal_graph = PrimalGraph()

    # converting a MultiDiGraph into a simple Graph
    oxg = nx.Graph(oxg)

    # removing self-loops from the resulting graph
    oxg.remove_edges_from(nx.selfloop_edges(oxg))

    # latitude (y-axis) and longitude (x-axis)
    node_dictionary = {nid: (data['y'], data['x']) for nid, data in oxg.nodes(data=True)}

    # updating the dictionary of nodes
    primal_graph.node_dictionary = node_dictionary

    eid = 0
    edge_dictionary = {}
    for source, target, data in oxg.edges(data=True):
        name = data.get('name', 'unknown')  # unknown is the default value for streets' name
        label = data.get('highway', 'unclassified')  # unclassified is the default value for streets' type
        length = compute_distance(node_dictionary[source],
                                  node_dictionary[target])  # straight-line distance between source and target nodes

        # creating a new PrimalEdge with information from the current edge
        edge = primal_graph.Edge(eid, source, target, float(length), 'unknown' if type(name) == list else name,
                                 'unclassified' if type(label) == list else label if use_label else 'unclassified')

        # storing the new edge in the edge dictionary
        edge_dictionary[eid] = edge
        eid += 1

    # updating the dictionary of edges
    primal_graph.edge_dictionary = edge_dictionary

    # building and returning the resulting PrimalGraph
    return primal_graph.build_graph()


def write_supplementary(graph: DualGraph, filename: str = 'supplementary.txt', directory: str = '../data'):
    """
    This method saves a supplementary file with all the information of DualNodes within the DualGraph.
    Each line of the file refers to a DualNode and is organized as: index, length, label, names, and list of nodes.
    :param graph: a DualGraph object
    :param filename: name and extension of the output file
    :param directory: full path to save the supplementary file
    :return: None
    """

    # assembling the output file path
    filepath = '{}/{}'.format(directory, filename)

    # will overwrite the file if it exists
    with open(filepath, 'w+') as supplementary_file:
        for nid, data in graph.node_dictionary.items():
            supplementary_file.write('%s, %f, %s, %s, %s\n' % (nid, data.length, data.label, data.names, data.nodes))
        supplementary_file.close()

    return


def write_graphml(graph: DualGraph, filename: str = 'file.graphml', directory: str = '../data'):
    """
    This method writes a DualGraph into a GraphML file using OSMNX and NetworkX libraries.
    :param graph: a DualGraph mapped from a PrimalGraph
    :param filename: name of the output file
    :param directory: full path to save the file
    :return: NetworkX Graph
    """

    nxg = nx.Graph()

    # creating nodes to store the streets of the PrimalGraph
    for nid, data in graph.node_dictionary.items():
        # inserting new node and related attributes
        nxg.add_node(nid)
        # GraphML does not support lists and dictionaries as objects, so we must add attributes one by one
        nxg.nodes[nid]['names'] = str(data.names)
        nxg.nodes[nid]['nodes'] = str(data.nodes)
        nxg.nodes[nid]['edges'] = str(data.edges)
        nxg.nodes[nid]['source'] = data.source
        nxg.nodes[nid]['target'] = data.target
        nxg.nodes[nid]['length'] = data.length
        nxg.nodes[nid]['src_edge'] = data.src_edge
        nxg.nodes[nid]['tgt_edge'] = data.tgt_edge

    # creating edges that connect nodes whenever we have two edges (PrimalEdge) crossings each other
    for eid, (source, target) in graph.edge_dictionary.items():
        # inserting new node and related attributes
        nxg.add_edge(source, target)
        # same happens to this case in here
        nxg.edges[(source, target)]['eid'] = eid

    # assembling the output file path
    filepath = '{}/{}'.format(directory, filename)

    # writing the resulting graph to the informed file path
    nx.write_graphml(G=nxg, path=filepath, encoding='utf-8', prettyprint=True, infer_numeric_types=False)

    return nxg
