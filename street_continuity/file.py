#
#   Copyright 2019, Gabriel Spadon, all rights reserved.
#   This code is under GNU General Public License v3.0.
#       gabriel@spadon.com.br
#
# Verified on February 1th, 2019.


import csv
from pathlib import Path

import networkx as nx
import osmnx as ox  # Required for read_graphml function

from street_continuity.graph import DualGraph, PrimalGraph
from street_continuity.util import compute_distance


def read_csv(
    nodes_filename: str,
    edges_filename: str,
    directory: str,
    use_label: bool,
    has_header: bool = False,
):
    """
    Method for creating a primal graph through two CSV files, one describing the nodes and another the edges.
    Nodes should be organized as {index, latitude, longitude} and edges as {index, source, target, length, name, label}.
    :param nodes_filename: nodes filename
    :param edges_filename: edges filename
    :param directory: full path of the files directory
    :param use_label: if true, it maps streets' type as labels (required for the HICN algorithm)
                      otherwise, streets' type is standardized as "unclassified" (required for the ICN algorithm)
    :param has_header: if true, it skips the first line when reading the files
    :return: PrimalGraph
    """

    # creating an empty primal graph
    primal_graph = PrimalGraph()

    # Validate file paths exist before opening
    nodes_path = Path(directory) / nodes_filename
    edges_path = Path(directory) / edges_filename
    if not nodes_path.exists():
        raise FileNotFoundError(f"Nodes file not found: {nodes_path}")
    if not edges_path.exists():
        raise FileNotFoundError(f"Edges file not found: {edges_path}")

    node_dictionary = {}
    with open(nodes_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",", quotechar='"')
        for nid, latitude, longitude in csv_reader:
            if not has_header:
                node_dictionary[nid] = [float(latitude), float(longitude)]
            has_header = False

    # updating the dictionary of nodes
    primal_graph.node_dictionary = node_dictionary

    edge_dictionary = {}
    with open(edges_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",", quotechar='"')

        for eid, source, target, length, name, label in csv_reader:
            if not has_header:
                if (
                    compute_distance(node_dictionary[source], node_dictionary[target]) > 0.0
                ):  # sanity check: self-loops are not allowed
                    edge_dictionary[eid] = primal_graph.Edge(
                        eid,
                        source,
                        target,
                        float(length),
                        name,
                        label if use_label else "unclassified",
                    )
            has_header = False

    # updating the dictionary of edges
    primal_graph.edge_dictionary = edge_dictionary

    # building and returning the resulting PrimalGraph
    return primal_graph.build_graph()


def read_graphml(graphml_file: str, use_label: bool):
    """
    This method loads a GraphML file into an OSMnx MultiDiGraph and uses method "from_osmnx" to create a PrimalGraph.
    :param graphml_file: a graph that was saved using the save_graphml() osmnx function
    :param use_label: if true, it maps streets' type as labels (required for the HICN algorithm)
                      otherwise, streets' type is standardized as "unclassified" (required for the ICN algorithm)
    :return: PrimalGraph
    """

    # the full path should be informed through "graphml_file" parameter
    oxg = ox.load_graphml(graphml_file)

    return from_osmnx(oxg, use_label)


def from_osmnx(oxg: nx.MultiDiGraph, use_label: bool):
    """
    The method transforms an OSMnx MultiDiGraph into a PrimalGraph object
    :param oxg: an OSMnx MultiDiGraph
    :param use_label: if true, it maps streets' type as labels (required for the HICN algorithm)
                      otherwise, streets' type is standardized as "unclassified" (required for the ICN algorithm)
    :return: PrimalGraph
    """

    # creating an empty primal graph
    primal_graph = PrimalGraph()

    # converting a MultiDiGraph into a simple Graph
    oxg = nx.Graph(oxg)

    # removing self-loops from the resulting graph
    oxg.remove_edges_from(nx.selfloop_edges(oxg))

    # latitude (y-axis) and longitude (x-axis)
    node_dictionary = {nid: (data["y"], data["x"]) for nid, data in oxg.nodes(data=True)}

    # updating the dictionary of nodes
    primal_graph.node_dictionary = node_dictionary

    eid = 0
    edge_dictionary = {}
    for source, target, data in oxg.edges(data=True):
        name = data.get("name", "unknown")  # unknown is the default value for streets' name
        label = data.get(
            "highway", "unclassified"
        )  # unclassified is the default value for streets' type

        # OSMnx can return a list for name/highway when simplification merges ways;
        # keep the first value so the street retains a usable name and road class
        if isinstance(name, list):
            name = name[0] if name else "unknown"
        if isinstance(label, list):
            label = label[0] if label else "unclassified"

        # prefer the network length OSMnx provides, which follows the street geometry;
        # fall back to the straight-line distance between the segment endpoints
        length = data.get("length")
        if length is None:
            length = compute_distance(node_dictionary[source], node_dictionary[target])

        # creating a new PrimalEdge with information from the current edge
        edge = primal_graph.Edge(
            eid, source, target, float(length), name, label if use_label else "unclassified"
        )

        # storing the new edge in the edge dictionary
        edge_dictionary[eid] = edge
        eid += 1

    # updating the dictionary of edges
    primal_graph.edge_dictionary = edge_dictionary

    # building and returning the resulting PrimalGraph
    return primal_graph.build_graph()


def write_supplementary(
    graph: DualGraph, filename: str = "supplementary.txt", directory: str = "."
):
    """
    This method saves a supplementary file with all the information of DualNodes within the DualGraph.
    Each line of the file refers to a DualNode and is organized as: index, length, label, names, and list of nodes.
    :param graph: a DualGraph object
    :param filename: name and extension of the output file
    :param directory: full path to save the supplementary file
    :return: None
    """

    # assembling the output file path and creating the directory when missing
    directory_path = Path(directory)
    directory_path.mkdir(parents=True, exist_ok=True)
    filepath = directory_path / filename

    # will overwrite the file if it exists
    with open(filepath, "w+") as supplementary_file:
        for nid, data in graph.node_dictionary.items():
            supplementary_file.write(
                f"{nid}, {data.length:f}, {data.label}, {data.names}, {data.nodes}\n"
            )

    return


def write_graphml(graph: DualGraph, filename: str = "file.graphml", directory: str = "."):
    """
    This method writes a DualGraph into a GraphML file using OSMnx and NetworkX libraries.
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
        nxg.nodes[nid]["names"] = str(data.names)
        nxg.nodes[nid]["nodes"] = str(data.nodes)
        nxg.nodes[nid]["edges"] = str(data.edges)
        nxg.nodes[nid]["source"] = data.source
        nxg.nodes[nid]["target"] = data.target
        nxg.nodes[nid]["length"] = data.length
        nxg.nodes[nid]["src_edge"] = data.src_edge
        nxg.nodes[nid]["tgt_edge"] = data.tgt_edge

    # creating edges that connect nodes whenever we have two edges (PrimalEdge) crossings each other
    for eid, (source, target) in graph.edge_dictionary.items():
        # inserting new node and related attributes
        nxg.add_edge(source, target)
        # same happens to this case in here
        nxg.edges[(source, target)]["eid"] = eid

    # assembling the output file path and creating the directory when missing
    directory_path = Path(directory)
    directory_path.mkdir(parents=True, exist_ok=True)
    filepath = directory_path / filename

    # writing the resulting graph to the informed file path
    nx.write_graphml(
        G=nxg,
        path=filepath,
        encoding="utf-8",
        prettyprint=True,
        infer_numeric_types=False,
    )

    return nxg
