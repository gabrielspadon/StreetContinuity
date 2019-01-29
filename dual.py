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
Released under the GNU General Public License v3.0 (GLP-3.0):
   Copyright (C) 2019 by Gabriel Spadon <gabriel@spadon.com.br>
"""

import csv
import math
import osmnx as ox
import numpy as np
import networkx as nx

min_angle = 120  # the angle (in degrees) must lie in range ]0, 180]
node_dictionary = {}  # dictionary of nodes form the primal network {node_id: [longitude, latitude]}
edge_dictionary = {}  # dictionary of PrimalEdge {edge_id: PrimalEdge}
dual_dictionary = {}  # dictionary of DualEdge {dual_id: DualEdge}
graph = {}  # primal graph that joins node_dictionary and edge_dictionary


class PrimalEdge:
    def __init__(self, eid, source, target, length, name, label):
        self.source = source
        self.target = target
        self.length = float(length)
        self.is_used = False
        self.label = label
        self.name = name
        self.eid = eid


def primal_mapper(directory, nodes_filename, edges_filename, use_label, has_header=False):

    global node_dictionary  # updating the global nodes variable
    with open(directory + '/' + nodes_filename, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
        for nid, lon, lat in csv_reader:
            if not has_header:
                node_dictionary[nid] = [np.float(lon), np.float(lat)]
            else:
                has_header = False

    print('[P] #Nodes: %d' % len(node_dictionary.keys()))

    global edge_dictionary  # updating the global edges variable
    with open(directory + '/' + edges_filename, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',', quotechar='"')

        for eid, source, target, length, name, label in csv_reader:
            if not has_header:
                if calculate_distance(source, target) > 0.0:
                    data = PrimalEdge(eid, source, target, length, name, label if use_label else 'unclassified')
                    edge_dictionary[eid] = data
            else:
                has_header = False

    print('[P] #Edges: %d' % len(edge_dictionary.keys()))

    global graph  # updating the global graph variable
    for eid in edge_dictionary.keys():
        edge = edge_dictionary[eid]

        if edge.source in graph.keys():
            graph[edge.source][edge.target] = edge.eid
        else:
            graph[edge.source] = {edge.target: edge.eid}

        if edge.target in graph.keys():
            graph[edge.target][edge.source] = edge.eid
        else:
            graph[edge.target] = {edge.source: edge.eid}

    return


# helper function, compute the unit direction vector
def calculate_distance(source, target):
    # extracting nodes coordinates
    src_lon, src_lat = node_dictionary[source]
    tgt_lon, tgt_lat = node_dictionary[target]
    # calculating the double-precision floating-point length of the edge
    return np.round(ox.great_circle_vec(src_lat, src_lon, tgt_lat, tgt_lon), 2)


def compute_angle(neighbor, source, target):
    # estimating the triangle's sides length
    d_sn = calculate_distance(neighbor, source)
    d_nt = calculate_distance(source, target)
    d_st = calculate_distance(neighbor, target)

    # calculating the law of cosines: cos(angle) = (a² + b² - c²) / (2ab)
    cos_law = min(max(-1, (((d_sn ** 2) + (d_nt ** 2) - (d_st ** 2)) / (2 * d_sn * d_nt))), 1)
    return math.acos(cos_law) * (180 / math.pi)


class DualEdge:
    # define the dual edge data, take a primal edge as start point
    def __init__(self, did, eid):
        self.source_eid = edge_dictionary[eid].eid
        self.target_eid = edge_dictionary[eid].eid
        self.source = edge_dictionary[eid].source
        self.target = edge_dictionary[eid].target
        self.length = edge_dictionary[eid].length
        self.names = [edge_dictionary[eid].name]  # dual edge can take different names
        self.label = edge_dictionary[eid].label  # dual edge can only have 1 label
        self.nodes = [self.source, self.target]  # dual edge takes different nodes
        self.did = did

        edge_dictionary[eid].is_used = True

    def merge_streets(self):
        # Use a initial dual edge as a seed, grow it from both end, util it cannot grow any further
        # recursively calling extendDuelEdge to achieve the objective
        downstream_neighbors = []
        upstream_neighbors = []

        # first, resolve all upstream neighbors
        for i in graph[self.source].keys():
            if i != self.target:  # check if the edge is not the current edge
                edge = edge_dictionary[graph[i][self.source]]
                if not edge.is_used and edge.label == self.label:
                    upstream_neighbors.append(i)

        for i in graph[self.target].keys():
            if i != self.source:  # check if the edge is not the current edge
                edge = edge_dictionary[graph[self.target][i]]
                if not edge.is_used and edge.label == self.label:
                    downstream_neighbors.append(i)

        # recursion exit condition
        if not len(upstream_neighbors) or not len(downstream_neighbors):
            return self

        # branch to both upstream and downstream neighbors
        upstream_neighbor, downstream_neighbor = False, False

        # first process upstream neighbors
        if len(upstream_neighbors):
            upstream_neighbor = self.merge_criteria(upstream_neighbors, self.source, self.source_eid)

            if upstream_neighbor:
                eid = graph[upstream_neighbor][self.source]
                edge_dictionary[eid].is_used = True

                self.source = upstream_neighbor
                self.length = self.length + edge_dictionary[eid].length

                if edge_dictionary[eid].name not in self.names:
                    self.names.append(edge_dictionary[eid].name)

                if upstream_neighbor not in self.nodes:
                    self.nodes.append(upstream_neighbor)

                self.source_eid = eid

        # second process downstream neighbors
        if len(downstream_neighbors):
            downstream_neighbor = self.merge_criteria(downstream_neighbors, self.target, self.target_eid)

            if downstream_neighbor:
                eid = graph[self.target][downstream_neighbor]
                edge_dictionary[eid].is_used = True

                self.target = downstream_neighbor
                self.length = self.length + edge_dictionary[eid].length

                if edge_dictionary[eid].name in self.names:
                    self.names.append(edge_dictionary[eid].name)

                if downstream_neighbor not in self.nodes:
                    self.nodes.append(downstream_neighbor)

                self.target_eid = eid

        # final check: if none of from neighbors or end neighbors satisfy the ICN rule
        if not upstream_neighbor and not downstream_neighbor:
            return self

        self.merge_streets()  # recursive call

    @staticmethod
    def merge_criteria(neighbors, source, source_eid):
        edge = edge_dictionary[source_eid]
        target = edge.source if source != edge.source else edge.target
        candidates = [compute_angle(neighbor, source, target) for neighbor in neighbors]

        if max(candidates) >= min_angle:
            # index = np.argmax(candidates)
            # print('Angle (%s, %s, %s): %.2f' % (neighbors[index], source, target, max(candidates)))
            return neighbors[np.argmax(candidates)]  # return the neighbor that forms the highest convex angle

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
            edge.merge_streets()
            dual_dictionary[eid] = edge
            eid += 1

    print('[D] #Nodes: %d' % (eid - 1))
    print_supplementary(directory, file_prefix)
    print_dual(directory, file_prefix)


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


def build_graph(node_dictionary, edge_dictionary):
    """

    :param node_dictionary:
    :param edge_dictionary:
    :return:
    """

    graph_dictionary = {}
    for eid in edge_dictionary.keys():
        edge = edge_dictionary[eid]

        if edge.source not in node_dictionary.keys() or edge.target not in node_dictionary.keys():
            print('Please check if all nodes are within the nodes\' dictionary.')

        if edge.source in graph_dictionary.keys():
            graph_dictionary[edge.source][edge.target] = edge.eid
        else:
            graph_dictionary[edge.source] = {edge.target: edge.eid}

        if edge.target in graph_dictionary.keys():
            graph_dictionary[edge.target][edge.source] = edge.eid
        else:
            graph_dictionary[edge.target] = {edge.source: edge.eid}

    return graph_dictionary


if __name__ == '__main__':  # For testing purpose
    use_label = True

    # I am using the city of Sao Carlos as an example, change as you please.
    oxg = ox.graph_from_point((-22.012282, -47.890821), distance=10000)

    graph, node_dictionary, edge_dictionary = load_osmnx(oxg, use_label)

    # # Input parameter: parameter to change
    path = 'data/'
    outfile = 'dual'
    # nodes_file = '1100015_nodes.csv'
    # edges_file = '1100015_edges.csv'
    # directed = False
    # labeled = True
    # # MaxAngle = 0.92  # 0.707#0.866 # 30 degree in radius
    #
    # # Intermediate variables
    # # node_dictionary = node_mapper(directory, nodes_filename)
    # # edge_dictionary = edge_mapper(directory, edges_filename, use_label)
    # # graph = graph_mapper(is_directed)
    # primal_mapper(path, nodes_file, edges_file, labeled, directed)
    #
    # # Main function: Do not change
    dual_mapper(path, outfile)
