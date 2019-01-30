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


def load_csv(nodes_filename, edges_filename, directory, use_label, has_header=False):
    """

    :param nodes_filename:
    :param edges_filename:
    :param directory:
    :param use_label:
    :param has_header:
    :return:
    """

    node_dictionary  = {}
    with open(directory + '/' + nodes_filename, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
        for nid, lon, lat in csv_reader:
            if not has_header:
                node_dictionary[nid] = [np.float(lon), np.float(lat)]
            else:
                has_header = False

    edge_dictionary  = {}
    with open(directory + '/' + edges_filename, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',', quotechar='"')

        for eid, source, target, length, name, label in csv_reader:
            if not has_header:
                if calculate_distance(source, target) > 0.0:
                    data = PrimalEdge(eid, source, target, length, name, label if use_label else 'unclassified')
                    edge_dictionary[eid] = data
            else:
                has_header = False

    graph_dictionary = build_graph(node_dictionary, edge_dictionary)

    return graph_dictionary, node_dictionary, edge_dictionary


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
        edge = PrimalEdge(eid, source, target, length, 'unknown' if type(name) == list else name,
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