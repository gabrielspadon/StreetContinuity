#
#   Copyright 2019, Gabriel Spadon, all rights reserved.
#   This code is under GNU General Public License v3.0.
#       gabriel@spadon.com.br
#
"""Command-line interface for StreetContinuity.

The CLI reads a street network from one of several sources, maps it to its dual
representation with the ICN or HICN algorithm, and writes the result to a GraphML
file (optionally along with a supplementary text file).

Examples
--------
    # Download a place from OpenStreetMap and export its dual graph (HICN):
    python -m street_continuity --place "Ji-Paraná, Brazil" --method hicn --output dual.graphml

    # Download a radius around a point (ICN):
    python -m street_continuity --point -11.9227,-62.0015 --dist 3000 \\
        --method icn --output dual.graphml

    # Convert a local pair of node/edge CSV files:
    python -m street_continuity --nodes test-nodes.csv --edges test-edges.csv \\
        --data-dir data --method hicn --output dual.graphml

    # Convert a GraphML file previously saved with OSMnx:
    python -m street_continuity --graphml city.graphml --output dual.graphml
"""

import argparse
import sys
from pathlib import Path

from street_continuity import __version__
from street_continuity.file import (
    read_csv,
    read_graphml,
    write_graphml,
    write_supplementary,
)
from street_continuity.mapper import dual_mapper


def build_parser() -> argparse.ArgumentParser:
    """Assemble the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="street_continuity",
        description="Map a street network to its dual graph using ICN or HICN.",
    )
    parser.add_argument("--version", action="version", version=f"StreetContinuity {__version__}")

    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--place", help="Place name to geocode and download from OpenStreetMap.")
    source.add_argument(
        "--point", help="'lat,lon' centre point to download around (use with --dist)."
    )
    source.add_argument("--graphml", help="Path to a GraphML file saved with OSMnx.")
    source.add_argument("--nodes", help="Node CSV file (use with --edges); {id, lat, lon}.")

    parser.add_argument("--edges", help="Edge CSV file; {id, source, target, length, name, label}.")
    parser.add_argument(
        "--data-dir",
        default=".",
        help="Directory holding the CSV files (default: current).",
    )
    parser.add_argument(
        "--dist",
        type=int,
        default=3000,
        help="Radius in metres for --point (default: 3000).",
    )
    parser.add_argument(
        "--network-type",
        default="drive",
        help="OSMnx network type for --place/--point (default: drive).",
    )
    parser.add_argument(
        "--method",
        choices=("icn", "hicn"),
        default="hicn",
        help="Continuity algorithm: 'icn' ignores road class, 'hicn' respects it (default: hicn).",
    )
    parser.add_argument(
        "--min-angle",
        type=float,
        default=120.0,
        help="Minimum continuity angle in degrees between consecutive segments, "
        "where 180 is perfectly straight (default: 120).",
    )
    parser.add_argument(
        "--has-header", action="store_true", help="Skip the first row of each CSV file."
    )
    parser.add_argument("--output", required=True, help="Output GraphML path for the dual graph.")
    parser.add_argument("--supplementary", help="Optional path for the supplementary text file.")
    return parser


def _load_primal(args: argparse.Namespace, use_label: bool):
    """Build a PrimalGraph from whichever source the user selected."""
    if args.nodes:
        if not args.edges:
            raise SystemExit("--nodes requires --edges.")
        return read_csv(args.nodes, args.edges, args.data_dir, use_label, args.has_header)

    if args.graphml:
        return read_graphml(args.graphml, use_label)

    # remaining sources require OSMnx network access
    import osmnx as ox

    from street_continuity.file import from_osmnx

    if args.place:
        oxg = ox.graph_from_place(args.place, network_type=args.network_type)
    else:  # args.point
        try:
            lat, lon = (float(v) for v in args.point.split(","))
        except ValueError as exc:
            raise SystemExit("--point must be 'lat,lon', e.g. -11.9227,-62.0015.") from exc
        oxg = ox.graph_from_point((lat, lon), dist=args.dist, network_type=args.network_type)

    return from_osmnx(oxg, use_label)


def main(argv: list[str] | None = None) -> int:
    """Entry point for ``python -m street_continuity`` and the console script."""
    args = build_parser().parse_args(argv)
    use_label = args.method == "hicn"

    primal = _load_primal(args, use_label)
    dual = dual_mapper(primal, min_angle=args.min_angle)

    output = Path(args.output)
    if output.parent != Path(""):
        output.parent.mkdir(parents=True, exist_ok=True)
    directory = str(output.parent) if str(output.parent) else "."
    write_graphml(dual, filename=output.name, directory=directory)

    if args.supplementary:
        supp = Path(args.supplementary)
        if str(supp.parent):
            supp.parent.mkdir(parents=True, exist_ok=True)
        write_supplementary(dual, filename=supp.name, directory=str(supp.parent) or ".")

    print(
        f"{args.method.upper()}: {len(primal.node_dictionary)} primal nodes / "
        f"{len(primal.edge_dictionary)} primal edges -> "
        f"{len(dual.node_dictionary)} dual nodes / {len(dual.edge_dictionary)} dual edges",
        file=sys.stderr,
    )
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
