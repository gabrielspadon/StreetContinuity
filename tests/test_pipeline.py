"""End-to-end tests exercising the full primal-to-dual pipeline."""

from pathlib import Path

import networkx as nx
import pytest

from street_continuity.file import (
    from_osmnx,
    read_csv,
    write_graphml,
    write_supplementary,
)
from street_continuity.graph import DualGraph, PrimalGraph
from street_continuity.mapper import dual_mapper

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@pytest.fixture
def sample_primal():
    """Primal graph built from the shipped Ji-Parana sample network."""
    return read_csv(
        "test-nodes.csv", "test-edges.csv", str(DATA_DIR), use_label=True, has_header=False
    )


def _brute_force_edges(dual):
    """Reference O(n^2) dual-edge set used to validate the fast builder."""
    edges = set()
    items = list(dual.node_dictionary.items())
    for sid, s in items:
        for tid, t in items:
            if sid < tid and set(s.nodes) & set(t.nodes):
                edges.add((sid, tid))
    return edges


class TestReadCsv:
    def test_reads_sample_network(self, sample_primal):
        assert len(sample_primal.node_dictionary) > 500
        assert len(sample_primal.edge_dictionary) > 800
        # coordinates are stored as (lat, lon); Ji-Parana sits near lat -11.9, lon -62.0
        lat, lon = sample_primal.node_dictionary["0"]
        assert -12.5 < lat < -11.5
        assert -62.5 < lon < -61.5

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            read_csv("nope-nodes.csv", "nope-edges.csv", str(tmp_path), use_label=False)


class TestFromOsmnx:
    @staticmethod
    def _toy_graph():
        g = nx.MultiDiGraph()
        g.add_node(1, y=-11.90, x=-62.00)
        g.add_node(2, y=-11.91, x=-62.00)
        g.add_node(3, y=-11.92, x=-62.00)
        g.add_edge(1, 2, name="Rua A", highway="residential")
        g.add_edge(2, 3, name="Rua A", highway="residential")
        return g

    def test_builds_primal_with_lat_lon(self):
        primal = from_osmnx(self._toy_graph(), use_label=True)
        assert isinstance(primal, PrimalGraph)
        assert len(primal.node_dictionary) == 3
        assert len(primal.edge_dictionary) == 2
        lat, lon = primal.node_dictionary[1]
        assert lat == pytest.approx(-11.90)
        assert lon == pytest.approx(-62.00)

    def test_icn_standardizes_labels(self):
        primal = from_osmnx(self._toy_graph(), use_label=False)
        assert all(e.label == "unclassified" for e in primal.edge_dictionary.values())


class TestDualMapper:
    def test_hicn_produces_dual_graph(self, sample_primal):
        dual = dual_mapper(sample_primal, min_angle=120)
        assert isinstance(dual, DualGraph)
        assert len(dual.node_dictionary) > 0
        assert len(dual.edge_dictionary) > 0

    def test_fast_edge_builder_matches_brute_force(self, sample_primal):
        dual = dual_mapper(sample_primal, min_angle=120)
        assert set(dual.edge_dictionary.values()) == _brute_force_edges(dual)

    def test_min_angle_governs_merging_end_to_end(self):
        # The continuity threshold must apply at every hop of the recursive merge,
        # so raising it can only split streets further, never merge more. A regression
        # that dropped the threshold inside the recursion would break this monotonicity.
        counts = []
        for angle in (90, 120, 150, 175):
            primal = read_csv("test-nodes.csv", "test-edges.csv", str(DATA_DIR), True, False)
            counts.append(len(dual_mapper(primal, min_angle=angle).node_dictionary))
        assert counts == sorted(counts)  # non-decreasing with a stricter threshold
        assert counts[-1] > counts[0]  # the threshold genuinely changes the outcome


class TestWriters:
    def test_write_graphml_and_supplementary(self, sample_primal, tmp_path):
        dual = dual_mapper(sample_primal, min_angle=120)
        write_graphml(dual, filename="dual.graphml", directory=str(tmp_path))
        write_supplementary(dual, filename="supp.txt", directory=str(tmp_path))

        graphml = tmp_path / "dual.graphml"
        supp = tmp_path / "supp.txt"
        assert graphml.exists() and graphml.stat().st_size > 0
        assert supp.exists() and supp.stat().st_size > 0

        # GraphML must be valid XML that networkx can load back.
        reloaded = nx.read_graphml(graphml)
        assert reloaded.number_of_nodes() == len(dual.node_dictionary)

    def test_writers_create_missing_directories(self, sample_primal, tmp_path):
        dual = dual_mapper(sample_primal, min_angle=120)
        nested = tmp_path / "out" / "nested"
        write_graphml(dual, filename="dual.graphml", directory=str(nested))
        write_supplementary(dual, filename="supp.txt", directory=str(nested))
        assert (nested / "dual.graphml").exists()
        assert (nested / "supp.txt").exists()


class TestContinuityRegressions:
    """Regressions for the direction-aware continuity negotiation."""

    @staticmethod
    def _collinear_chain(reverse=False):
        # five collinear nodes going north, four segments of roughly 111 m each
        pg = PrimalGraph()
        pg.node_dictionary = {f"n{i}": (0.001 * i, 0.0) for i in range(5)}
        order = range(4)
        pg.edge_dictionary = {
            eid: PrimalGraph.Edge(eid, f"n{eid}", f"n{eid + 1}", 111.0, "S", "unclassified")
            for eid in (reversed(order) if reverse else order)
        }
        return pg.build_graph()

    @pytest.mark.parametrize("reverse", [False, True])
    def test_collinear_chain_merges_regardless_of_edge_order(self, reverse):
        # Downstream growth must negotiate at the target intersection; before that
        # fix, a forward-ordered chain fragmented into one dual node per segment.
        dual = dual_mapper(self._collinear_chain(reverse), min_angle=150)
        assert len(dual.node_dictionary) == 1
        assert len(dual.edge_dictionary) == 0


class TestOsmnxAttributes:
    @staticmethod
    def _two_node_graph(**edge_attrs):
        g = nx.MultiDiGraph()
        g.add_node(1, y=-11.90, x=-62.00)
        g.add_node(2, y=-11.91, x=-62.00)
        g.add_edge(1, 2, **edge_attrs)
        return g

    def test_honors_osmnx_length_attribute(self):
        g = self._two_node_graph(name="Rua A", highway="residential", length=1234.5)
        primal = from_osmnx(g, use_label=True)
        assert primal.edge_dictionary[0].length == 1234.5

    def test_resolves_list_valued_tags(self):
        g = self._two_node_graph(name=["Rua A", "Rua B"], highway=["primary", "primary_link"])
        primal = from_osmnx(g, use_label=True)
        edge = primal.edge_dictionary[0]
        assert edge.name == "Rua A"
        assert edge.label == "primary"
