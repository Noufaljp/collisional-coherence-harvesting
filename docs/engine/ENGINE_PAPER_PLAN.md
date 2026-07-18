# Spin-valve engine paper — living plan

**Branch:** `spin-valve-engine`  
**Companion draft:** frozen on `main` / `paper/` as **supporting material** (Sec. II / SI lemmas), not the novelty vehicle.  
**Last updated:** 2026-07-18  

---

## Goal of the big paper

Non-collinear spin-valve transport **generates** spin coherence from voltage/temperature bias (no engineered \(c_0\)). Energy- and charge-conserving collisions **export** part of that resource into an ancilla tape. Report the tradeoff \((P_{\mathrm{el}}, P_{\mathrm{erg}})\) with honest controls.

Companion formulas (map, ergotropy, rate match, accessibility) appear as **lemmas**, not as the main claim.

---

## Repository layout (this branch)

| Path | Role |
|------|------|
| `paper/` | **Companion supporting draft** (keep; do not treat as standalone product) |
| `docs/engine/` | Plans, gate specs, gate reports |
| `src/coherence_harvesting/companion/` | Supporting analytics |
| `src/coherence_harvesting/transport/` | Full-engine numerics (active development) |
| `scripts/gate1_*.py`, `scripts/gate2_*.py` | Gate runners |
| `results/gate1/`, `results/gate2/` | Tables, NPZ, figures, memos |
| `engine_paper/` | Future main-text scaffold for the big paper |

---

## Stages

### Stage 0 — Freeze companion as support

- [x] Companion analytic package + draft on `main`
- [x] Document: companion is SI / Sec. II of engine paper
- [ ] Stop novelty polish on impedance match as headline

### Stage 1 — Gate 1–2 (this decides if a paper exists)

#### Gate 1 — Resource exists without engineered \(c_0\) (**Week 1**)

**Question:** Near-degenerate nonsecular NESS: is spin coherence large enough?

| Check | Pass idea |
|--------|-----------|
| \(\lvert\rho_{\uparrow\downarrow}\rvert\) or \(\lvert\vec S_\perp\rvert\) | Significant vs noise floor (report max; provisional threshold \(\gtrsim 0.05\)) |
| Large \(\Delta/\gamma\) | Resource suppressed |
| Collinear \(\theta_R=0\) | Coherence drops vs non-collinear |
| Positivity | \(\min\mathrm{eig}(\rho)\ge -10^{-8}\) (or document fix) |

**Deliverables:** scan CSV/NPZ, control plots, `results/gate1/GATE1_REPORT.md` with GO / WEAK / NO-GO.

#### Gate 2 — Harvestable in principle (**Week 2**)

**Question:** Can a matched-gap collision put nonzero ergotropy on an ancilla, and does regeneration survive stroboscopically?

| Check | Pass idea |
|--------|-----------|
| One-shot on NESS | \(\mathcal{W}_A>0\) |
| Occupation \(P_1\) | Not tiny |
| Stroboscopic fixed point | Residual \(\lvert C\rvert\) after many cycles |
| Regeneration | Wait interval rebuilds coherence |

**Deliverable:** `results/gate2/GATE2_REPORT.md`.

### Stage 2 — Engine core (only if gates pass)

- Lead-resolved cycle-averaged currents (replace proxy)
- Stroboscopic fixed point with collisions
- Sign convention table for \(P_{\mathrm{el}}\)

### Stage 3 — Paper-real content

- Tradeoff \((P_{\mathrm{el}},P_{\mathrm{erg}})\)
- Controls: no collision / dephasing / population reset / matched-population / collinear
- Narrative: partitioning / tradeoff, not “restored collinear power”

### Stage 4 — Manuscript

1. Intro  
2. Companion lemmas (short)  
3. Transport model  
4. Gate results  
5. Engine + tradeoff  
6. Discussion (accessibility, costs)  
7. SI = companion derivations  

---

## Decision tree

```text
Gate 1 fail     → no big paper (optional tiny companion note only if needed)
Gate 1 pass,
Gate 2 fail     → possible “coherence exists, not harvestable” note
Both pass       → build full engine paper; companion = SI
```

---

## Active work log

| Date | Item | Result |
|------|------|--------|
| 2026-07-18 | Branch `spin-valve-engine` + plan | Opened |
| 2026-07-18 | Gate 1 Week 1 scan | **Verdict GO** (borderline $\|C\|\approx0.050$ at $\Delta/\gamma=0.3$, $\theta_R=\pi/2$; collinear $C=0$; large-$\Delta$ suppressed; all positive). See `results/gate1/GATE1_REPORT.md` |

---

## Relation to companion draft

- **Do not** rewrite `paper/main.tex` for novelty claims on this branch unless needed for SI integration.  
- **Do** import companion map/ergotropy in Gate 2 and later.  
- Primary novelty lives in **bias-generated coherence + export tradeoff**.
