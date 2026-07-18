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

- [x] Lead-resolved cycle-averaged currents (replace proxy) — `channels.py`, `currents.py`
- [x] Stroboscopic fixed point with collisions + bookkeeping — `engine.py`
- [x] Sign convention table — `docs/engine/SIGN_CONVENTION.md`
- [x] Rate / \(\theta\) scans + controls — `results/stage2/STAGE2_REPORT.md`
- [ ] Engine-regime search \(P_{\mathrm{el}}>0\) (optional Stage 3)

### Stage 3 — Paper-real content

- [x] Engine-window search \(P_{\mathrm{el}}>0\) with coherence
- [x] Tradeoff \((P_{\mathrm{el}},P_{\mathrm{erg}})\) on chosen TE window
- [x] Controls: coherent / matched / incoherent / none / dephasing / \(\alpha=1/2\) / collinear
- [x] **Chosen story:** `thermoelectric_engine_plus_battery` — see `results/stage3/STAGE3_REPORT.md`

### Stage 4 — Manuscript

- [x] v1 draft: `engine_paper/main.tex` + `main.pdf` (~4 pp)
- [x] Paper figures via `scripts/stage4_paper_support.py` → `engine_paper/figures/`
- [x] Numbers frozen in `results/stage4/paper_numbers.json`
- [ ] Coauthor pass / expand SI companion appendix into the PDF
- [ ] Journal target lock (PRE/PRA)  

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
| 2026-07-18 | Gate 1 Week 1 scan | **GO** (borderline $\|C\|\approx0.050$). See `results/gate1/GATE1_REPORT.md` |
| 2026-07-18 | Gate 1 boost / gap-fill | $\|C\|$ raised to **~0.14** via $p$, bias, small $\Delta$, tilt. See `results/gate1/GATE1_BOOST_REPORT.md` |
| 2026-07-18 | Gate 2 harvest | **GO**: one-shot $\mathcal{W}_A>0$, stroboscopic residual $C$, regeneration; $\alpha=1/2$ has $\mathcal{W}_{\rm coh}=0$. See `results/gate2/GATE2_REPORT.md` |
| 2026-07-18 | Stage 2 currents | Lead-resolved currents + bookkeeping. See `results/stage2/STAGE2_REPORT.md` |
| 2026-07-18 | Stage 3 story | **Engine story works.** See `results/stage3/STAGE3_REPORT.md` |
| 2026-07-18 | Stage 4 draft | Engine manuscript v1 + support figures (load sweep, resource map, dual rate, controls). See `engine_paper/main.pdf`, `results/stage4/` |

---

## Relation to companion draft

- **Do not** rewrite `paper/main.tex` for novelty claims on this branch unless needed for SI integration.  
- **Do** import companion map/ergotropy in Gate 2 and later.  
- Primary novelty lives in **bias-generated coherence + export tradeoff**.
