#
#   Copyright 2019, Gabriel Spadon, all rights reserved.
#   This code is under GNU General Public License v3.0.
#       www.spadon.com.br & gabriel@spadon.com.br
#


class PrimalGraph:

    def __init__(self, node_dictionary, edge_dictionary):
        self.node_dictionary = node_dictionary
        self.edge_dictionary = edge_dictionary
        self.graph = {}

    def build_graph(self):
        """

        :return:
        """

        for eid in self.edge_dictionary.keys():
            edge = self.edge_dictionary[eid]

            # if edge.source not in self.node_dictionary.keys() or edge.target not in self.node_dictionary.keys():
            #     print('Please check if all nodes are within the nodes\' dictionary.')

            if edge.source in self.graph.keys():
                self.graph[edge.source][edge.target] = edge.eid
            else:
                self.graph[edge.source] = {edge.target: edge.eid}

            if edge.target in self.graph.keys():
                self.graph[edge.target][edge.source] = edge.eid
            else:
                self.graph[edge.target] = {edge.source: edge.eid}

        return


class PrimalEdge:

    def __init__(self, eid, source, target, length, name, label):
        self.source = source
        self.target = target
        self.length = float(length)
        self.is_used = False
        self.label = label
        self.name = name
        self.eid = eid


class DualEdge:

    def __init__(self, did, primal_edge):
        self.source_eid = primal_edge.eid
        self.target_eid = primal_edge.eid
        self.source = primal_edge.source
        self.target = primal_edge.target
        self.length = primal_edge.length
        self.names = [primal_edge.name]  # dual edge can take different names
        self.label = primal_edge.label  # dual edge can only have 1 label
        self.nodes = [self.source, self.target]  # dual edge takes different nodes
        self.did = did

        # edge_dictionary[eid].is_used = True
