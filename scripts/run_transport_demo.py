#!/usr/bin/env python
"""Generate spin-valve engine demo figures."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from coherence_harvesting.scripts_api import transport_demo

if __name__ == "__main__":
    transport_demo(ROOT / "figures")
