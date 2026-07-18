"""Command-line entry points."""

from __future__ import annotations

import argparse
from pathlib import Path


def run_companion(argv: list[str] | None = None) -> None:
    from coherence_harvesting.scripts_api import companion_demo

    parser = argparse.ArgumentParser(description="Run companion-model demo")
    parser.add_argument(
        "--outdir",
        type=Path,
        default=Path("figures"),
        help="Directory for figures",
    )
    args = parser.parse_args(argv)
    companion_demo(args.outdir)


def run_transport(argv: list[str] | None = None) -> None:
    from coherence_harvesting.scripts_api import transport_demo

    parser = argparse.ArgumentParser(description="Run spin-valve engine demo")
    parser.add_argument("--outdir", type=Path, default=Path("figures"))
    args = parser.parse_args(argv)
    transport_demo(args.outdir)


def run_figures(argv: list[str] | None = None) -> None:
    from coherence_harvesting.scripts_api import generate_all_figures

    parser = argparse.ArgumentParser(description="Generate all paper figures")
    parser.add_argument("--outdir", type=Path, default=Path("figures"))
    args = parser.parse_args(argv)
    generate_all_figures(args.outdir)
