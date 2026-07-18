# Stage 3 report — story search and controls

**Date:** 2026-07-18  
**Branch:** `spin-valve-engine`

## Executive choice

**Final story tag:** `thermoelectric_engine_plus_battery`

Primary story: **thermoelectric engine with a collisional battery channel**. A temperature bias drives particle current against a load voltage so $P_{\mathrm{el}}>0$, while non-collinear leads sustain spin coherence that collisions export as $P_{\mathrm{erg}}$. Controls show collinear kills the battery channel; incoherent exchange suppresses coherent ergotropy.

Mid-rate sample efficiency proxy $\eta\approx P_{\rm el}/J_{Q,hot}=0.4308$ (scaffold only).

## Engine-window search (NESS)

- Hits with $P_{\rm el}>0$, $|C|>0.01$, $P_1>0.05$: **5183**
- Prefer TE-like points: hot/cold temperature bias + load voltage opposing the thermocurrent.

### Best NESS engine-like point (if any)

| Field | Value |
|-------|-------|
| $P_{\rm el}$ | 0.131656 |
| $|C|$ | 0.04227 |
| $V=\mu_L-\mu_R$ | -0.6 |
| $T_L,T_R$ | 2.0, 0.25 |
| $\varepsilon,\Delta,\theta_R,p$ | 1.0, 0.2, 0.6, 0.9 |

Saved: `chosen_window.json`, `engine_window_hits.csv`.

## Rate scan fraction with $P_{\rm el}>0$

**100%** of rate-scan points on the chosen window.

## Control hierarchy (fixed $T=1.5$, $\theta\approx0.45$)

| Control | $P_{\rm el}$ | $P_{\rm erg}$ | $|C|$ | $\mathcal{W}_{\rm coh}$ |
|---------|-----------------|------------------|-------|-------------------------------|
| coherent | +0.1182 | 6.576e-05 | 0.04462 | 9.864e-05 |
| matched | +0.1276 | 5.74e-07 | 0.03731 | 8.61e-07 |
| incoherent | +0.1264 | 0 | 0 | 0 |
| none | +0.1317 | 0 | 0.04227 | 0 |
| dephasing | +0.1397 | 0 | 0 | 0 |
| alpha_half | +0.1278 | 0 | 0.03723 | 0 |
| collinear | +0.1226 | 0 | 0 | 0 |


### Attribution notes

| Comparison | Reading |
|------------|---------|
| coherent vs none | Battery channel requires collisions; electrical power shifts slightly |
| coherent vs incoherent | Incoherent: $\mathcal{W}_{\rm coh}$ should drop (populations only) |
| coherent vs matched | Matched-population: isolates coherence transfer vs population gradient |
| collinear | Kills spin coherence and coherent battery channel |
| dephasing | Kills $C$ without a battery tape |
| $\alpha=1/2$ | $\mathcal{W}_{\rm coh}=0$ expected |

Coherent $P_{\rm erg}=6.576e-05$, incoherent $P_{\rm erg}=0$, matched $P_{\rm erg}=5.74e-07$, none $P_{\rm erg}=0$.

## Recommended paper narrative (concrete)

### If `thermoelectric_engine_plus_battery` starts with thermoelectric_engine

**Title sketch:** *Collisional spin-coherence battery on a non-collinear thermoelectric spin valve*

**Claim structure:**
1. Near-degenerate non-collinear valve hosts bias-generated spin coherence.
2. Temperature + load voltage yields $P_{\rm el}>0$ (TE engine regime in the sequential scaffold).
3. Resonant exchange collisions export coherence as $P_{\rm erg}$ without claiming collinear restoration.
4. Control hierarchy attributes battery charging to *coherent* exchange.
5. Companion impedance-matching formulas appear as SI lemmas for the export channel.

### If partitioning

Same but with $P_{\rm el}<0$ as electrical *cost/load*, and dual-output as partitioning of nonequilibrium resources.

## Caveats (must stay in the paper)

1. Generator is sequential-tunneling, not NEGF/Redfield.
2. Accessibility of coherent ergotropy still requires a phase reference (companion).
3. Ancilla preparation free energy not subtracted.
4. Efficiency numbers are diagnostics, not Carnot-tight proofs.

## Files

- `engine_window_hits.csv`, `chosen_window.json`
- `stage3_controls.csv`, `stage3_rate_scan.csv`, `stage3_theta_scan.csv`, `stage3_mode_compare.csv`
- figures: `stage3_*.png/pdf`

## Next (Stage 4)

Draft `engine_paper/main.tex` around `thermoelectric_engine_plus_battery` using Stage 1–3 figures; companion as appendix.
