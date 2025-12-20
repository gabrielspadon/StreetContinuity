import pytest
import sys
from pathlib import Path

# Add parent directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from street_continuity.graph import PrimalGraph, DualGraph


class TestPrimalEdge:
    """Test suite for PrimalGraph.Edge nested class."""

    def test_edge_initialization(self):
        """Test that PrimalEdge initializes with correct attributes."""
        edge = PrimalGraph.Edge(
            eid=1,
            source="node1",
            target="node2",
            length=100.5,
            name="Main Street",
            label="primary"
        )

        assert edge.eid == 1
        assert edge.source == "node1"
        assert edge.target == "node2"
        assert edge.length == 100.5
        assert edge.name == "Main Street"
        assert edge.label == "primary"
        assert edge.mapped is False

    def test_edge_default_mapped_flag(self):
        """Test that edge has mapped flag set to False by default."""
        edge = PrimalGraph.Edge(1, "a", "b", 10.0, "street", "road")
        assert edge.mapped is False


class TestPrimalGraph:
    """Test suite for PrimalGraph class."""

    def test_initialization(self):
        """Test that PrimalGraph initializes with empty dictionaries."""
        pg = PrimalGraph()
        assert pg.node_dictionary == {}
        assert pg.edge_dictionary == {}
        assert pg.graph == {}

    def test_set_nodes(self):
        """Test setting node dictionary."""
        pg = PrimalGraph()
        nodes = {"node1": (0, 0), "node2": (1, 1)}
        pg.set_nodes(nodes)
        assert pg.node_dictionary == nodes

    def test_set_edges(self):
        """Test setting edge dictionary."""
        pg = PrimalGraph()
        edge1 = PrimalGraph.Edge(1, "a", "b", 10.0, "street", "road")
        edges = {1: edge1}
        pg.set_edges(edges)
        assert pg.edge_dictionary == edges

    def test_build_graph_single_edge(self):
        """Test building graph with a single edge."""
        pg = PrimalGraph()
        edge = PrimalGraph.Edge(1, "node1", "node2", 100.0, "Main St", "primary")
        pg.set_edges({1: edge})
        pg.build_graph()

        assert "node1" in pg.graph
        assert "node2" in pg.graph
        assert pg.graph["node1"]["node2"] == 1
        assert pg.graph["node2"]["node1"] == 1

    def test_build_graph_multiple_edges(self):
        """Test building graph with multiple edges."""
        pg = PrimalGraph()
        edge1 = PrimalGraph.Edge(1, "a", "b", 10.0, "St 1", "primary")
        edge2 = PrimalGraph.Edge(2, "b", "c", 20.0, "St 2", "secondary")
        edge3 = PrimalGraph.Edge(3, "c", "a", 30.0, "St 3", "tertiary")

        pg.set_edges({1: edge1, 2: edge2, 3: edge3})
        pg.build_graph()

        assert len(pg.graph) == 3
        assert "a" in pg.graph and "b" in pg.graph and "c" in pg.graph
        assert pg.graph["a"]["b"] == 1
        assert pg.graph["b"]["c"] == 2
        assert pg.graph["c"]["a"] == 3

    def test_build_graph_returns_self(self):
        """Test that build_graph returns self for method chaining."""
        pg = PrimalGraph()
        result = pg.build_graph()
        assert result is pg


class TestDualNode:
    """Test suite for DualGraph.Node nested class."""

    def test_node_initialization_from_edge(self):
        """Test that DualNode initializes correctly from a PrimalEdge."""
        primal_edge = PrimalGraph.Edge(
            eid=5,
            source="n1",
            target="n2",
            length=50.0,
            name="Oak Avenue",
            label="residential"
        )

        dual_node = DualGraph.Node(did=1, pge=primal_edge)

        assert dual_node.did == 1
        assert dual_node.src_edge == 5
        assert dual_node.tgt_edge == 5
        assert dual_node.source == "n1"
        assert dual_node.target == "n2"
        assert dual_node.length == 50.0
        assert dual_node.label == "residential"
        assert dual_node.names == ["Oak Avenue"]
        assert dual_node.nodes == ["n1", "n2"]
        assert dual_node.edges == [("n1", "n2")]


class TestDualGraph:
    """Test suite for DualGraph class."""

    def test_initialization(self):
        """Test that DualGraph initializes with empty dictionaries."""
        dg = DualGraph()
        assert dg.node_dictionary == {}
        assert dg.edge_dictionary == {}
        assert dg.graph == {}

    def test_set_nodes(self):
        """Test setting node dictionary in DualGraph."""
        dg = DualGraph()
        primal_edge = PrimalGraph.Edge(1, "a", "b", 10.0, "st", "road")
        dual_node = DualGraph.Node(1, primal_edge)
        nodes = {1: dual_node}
        dg.set_nodes(nodes)
        assert dg.node_dictionary == nodes

    def test_set_edges(self):
        """Test setting edge dictionary in DualGraph."""
        dg = DualGraph()
        edges = {1: (1, 2)}
        dg.set_edges(edges)
        assert dg.edge_dictionary == edges

    def test_build_graph_single_edge(self):
        """Test building dual graph with single edge."""
        dg = DualGraph()
        edges = {1: (1, 2)}
        dg.set_edges(edges)
        dg.build_graph()

        assert 1 in dg.graph
        assert 2 in dg.graph
        assert dg.graph[1][2] == 1
        assert dg.graph[2][1] == 1

    def test_build_graph_multiple_edges(self):
        """Test building dual graph with multiple edges."""
        dg = DualGraph()
        edges = {
            1: (1, 2),
            2: (2, 3),
            3: (3, 1)
        }
        dg.set_edges(edges)
        dg.build_graph()

        assert len(dg.graph) == 3
        assert dg.graph[1][2] == 1
        assert dg.graph[2][3] == 2
        assert dg.graph[3][1] == 3

    def test_build_graph_returns_self(self):
        """Test that build_graph returns self for method chaining."""
        dg = DualGraph()
        result = dg.build_graph()
        assert result is dg


class TestGraphIntegration:
    """Integration tests for graph operations."""

    def test_primal_to_dual_conversion_concept(self):
        """Test conceptual conversion from primal to dual graph."""
        # Create primal graph
        pg = PrimalGraph()
        edge1 = PrimalGraph.Edge(1, "a", "b", 10.0, "Main St", "primary")
        edge2 = PrimalGraph.Edge(2, "b", "c", 15.0, "Main St", "primary")
        pg.set_edges({1: edge1, 2: edge2})
        pg.build_graph()

        # Create dual graph from primal edges
        dg = DualGraph()
        dual_node = DualGraph.Node(1, edge1)

        assert dual_node.names == ["Main St"]
        assert dual_node.edges == [("a", "b")]

    def test_empty_graph_build(self):
        """Test building graphs with no edges."""
        pg = PrimalGraph()
        pg.build_graph()
        assert pg.graph == {}

        dg = DualGraph()
        dg.build_graph()
        assert dg.graph == {}
