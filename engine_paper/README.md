# Engine paper draft — dual-output spin valve

**Story:** `thermoelectric_engine_plus_battery`  
**Branch:** `spin-valve-engine`  
**Supporting companion draft:** `../paper/` (SI lemmas)

## Build

```bash
cd engine_paper
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Regenerate figures / numbers

```bash
python -X utf8 scripts/stage4_paper_support.py
python -X utf8 scripts/stage3_story_search.py   # window search + controls
python -X utf8 scripts/stage2_engine_scan.py    # current module diagnostics
```

## Key result paths

| Path | Content |
|------|---------|
| `results/stage3/STAGE3_REPORT.md` | Story choice |
| `results/stage4/STAGE4_SUPPORT_REPORT.md` | Paper figures |
| `results/stage4/paper_numbers.json` | Numbers used in draft |
| `engine_paper/figures/` | PDF/PNG for `\includegraphics` |

## Iteration log

| Date | Change |
|------|--------|
| 2026-07-18 | v1 draft + stage4 figures from TE window |
