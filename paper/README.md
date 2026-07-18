# Small-paper manuscript

This directory contains the journal-shaped manuscript defined by
docs/SMALL_PAPER_SCOPE.md.

Build from this directory after regenerating the figures:

    python -X utf8 ../scripts/run_companion_demo.py
    latexmk -pdf -interaction=nonstopmode main.tex

The compiled submission draft is copied to output/pdf/small_paper_draft.pdf
after verification.

Before circulation or submission, resolve:

- final author list and order;
- affiliations, corresponding author, and ORCID details;
- target journal formatting and length;
- whether the phase-locked reset is presented as engineered control,
  rotating-frame dynamics, or a near-degenerate approximation;
- the accounting convention for ancilla preparation and any phase reference.

All figure source arrays are stored in figures/data as NPZ files. The
full spin-valve transport model is intentionally outside this manuscript.

