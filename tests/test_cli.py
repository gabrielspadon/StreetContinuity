"""Tests for the ``python -m street_continuity`` command-line interface."""

from pathlib import Path

import networkx as nx
import pytest

from street_continuity.__main__ import main

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def test_csv_to_graphml(tmp_path):
    out = tmp_path / "dual.graphml"
    code = main(
        [
            "--nodes",
            "test-nodes.csv",
            "--edges",
            "test-edges.csv",
            "--data-dir",
            str(DATA_DIR),
            "--method",
            "hicn",
            "--min-angle",
            "120",
            "--output",
            str(out),
        ]
    )
    assert code == 0
    assert out.exists() and out.stat().st_size > 0
    assert nx.read_graphml(out).number_of_nodes() > 0


def test_writes_supplementary(tmp_path):
    out = tmp_path / "dual.graphml"
    supp = tmp_path / "supp.txt"
    code = main(
        [
            "--nodes",
            "test-nodes.csv",
            "--edges",
            "test-edges.csv",
            "--data-dir",
            str(DATA_DIR),
            "--method",
            "icn",
            "--output",
            str(out),
            "--supplementary",
            str(supp),
        ]
    )
    assert code == 0
    assert supp.exists() and supp.stat().st_size > 0


def test_nodes_without_edges_errors(tmp_path):
    with pytest.raises(SystemExit):
        main(
            [
                "--nodes",
                "test-nodes.csv",
                "--data-dir",
                str(DATA_DIR),
                "--output",
                str(tmp_path / "o.graphml"),
            ]
        )


def test_bad_point_errors(tmp_path):
    with pytest.raises(SystemExit):
        main(["--point", "not-a-coordinate", "--output", str(tmp_path / "o.graphml")])


def test_version_flag(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert "StreetContinuity" in capsys.readouterr().out
