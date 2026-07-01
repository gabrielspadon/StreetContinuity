"""Tests for the public package surface and the GraphML reader."""

import networkx as nx
import pytest

import street_continuity as sc
from street_continuity.file import read_csv, read_graphml


def test_top_level_exports():
    assert sc.__version__
    for name in sc.__all__:
        assert hasattr(sc, name)


def test_all_module_reexports_public_api():
    import street_continuity.all as sc_all

    for name in sc_all.__all__:
        assert hasattr(sc_all, name)


def test_missing_edges_file_raises(tmp_path):
    # The nodes file exists but the edges file does not.
    (tmp_path / "nodes.csv").write_text("0,-11.9,-62.0\n1,-11.91,-62.01\n")
    with pytest.raises(FileNotFoundError):
        read_csv("nodes.csv", "missing-edges.csv", str(tmp_path), use_label=False)


def test_read_graphml_round_trip(tmp_path):
    import osmnx as ox

    g = nx.MultiDiGraph(crs="epsg:4326")
    g.add_node(1, x=-62.00, y=-11.90)
    g.add_node(2, x=-62.00, y=-11.91)
    g.add_node(3, x=-62.00, y=-11.92)
    g.add_edge(1, 2, name="Rua A", highway="residential")
    g.add_edge(2, 3, name="Rua A", highway="residential")

    path = tmp_path / "toy.graphml"
    ox.save_graphml(g, path)

    primal = read_graphml(str(path), use_label=True)
    assert len(primal.node_dictionary) == 3
    assert len(primal.edge_dictionary) == 2
