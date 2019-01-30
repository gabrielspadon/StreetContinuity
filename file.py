#
#   Copyright 2019, Gabriel Spadon, all rights reserved.
#   This code is under GNU General Public License v3.0.
#       www.spadon.com.br & gabriel@spadon.com.br
#

from util import *
from graph import *

import csv
import numpy as np
import networkx as nx


def load_csv(nodes_filename: str, edges_filename: str, directory: str, use_label: bool, has_header: bool = False):
    """
    Method for creating a primal graph through two CSV files, one describing the vertices and another the edges.
    Nodes should be organized as {index, longitude, latitude} and edges as {index, source, target, length, name, label}.
    :param nodes_filename: nodes filename
    :param edges_filename: edges filename
    :param directory: full path of the files directory
    :param use_label: if true, it uses street types as labels
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

    # updating the dictionary of nodes
    primal_graph.node_dictionary = node_dictionary

    edge_dictionary = {}
    with open(directory + '/' + edges_filename, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',', quotechar='"')

        for eid, source, target, length, name, label in csv_reader:
            if not has_header:
                if calculate_distance(source, target) > 0.0:  # sanity check: self-loops are not allowed
                    edge_dictionary[eid] = primal_graph.Edge(eid, source, target, np.float(length),
                                                             name, label if use_label else 'unclassified')
            has_header = False

    # updating the dictionary of edges
    primal_graph.edge_dictionary = edge_dictionary

    # building and returning the resulting primal graph
    return primal_graph.build_graph()


def load_osmnx(oxg, use_label):
    """

    :param oxg:
    :param use_label:
    :return:
    """

    global node_dictionary

    # Direction is not important in this case, so let's use a simple Graph.
    oxg = nx.Graph(oxg)  # MultiDiGraph (input) ~> Graph (output)

    # Removing self loops from the graph.
    oxg.remove_edges_from(oxg.selfloop_edges())

    # latitude [y] and longitude [x] (must keep the order)
    node_dictionary = {nid: [data['y'], data['x']] for nid, data in oxg.nodes(data=True)}

    eid = 0
    edge_dictionary = {}
    for source, target, data in oxg.edges(data=True):
        length = calculate_distance(source, target)  # approximating the distance between source and target
        label = data.get('highway', 'unclassified')  # using 'unclassified' as the default value for highways
        name = data.get('name', 'unknown')  # 'unknown' is the default value for street name attribute

        # creating a new PrimalEdge object with the collected information
        edge = PrimalEdge(eid, source, target, float(length), 'unknown' if type(name) == list else name,
                          'unclassified' if type(label) == list else label if use_label else 'unclassified')

        # storing the new edge in the edge dictionary
        edge_dictionary[eid] = edge
        eid += 1

    graph_dictionary = build_graph(node_dictionary, edge_dictionary)

    return graph_dictionary, node_dictionary, edge_dictionary


def load_graphml(graphml_file, use_label):
    """

    :param graphml_file:
    :param use_label:
    :return:
    """

    oxg = ox.load_graphml(filename=graphml_file, folder='')

    return load_osmnx(oxg, use_label)


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
