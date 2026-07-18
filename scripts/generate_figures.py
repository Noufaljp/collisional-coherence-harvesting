#!/usr/bin/env python
"""Generate all demo figures for the study."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from coherence_harvesting.scripts_api import generate_all_figures

if __name__ == "__main__":
    generate_all_figures(ROOT / "figures")
