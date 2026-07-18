# Stage 2 report — lead-resolved currents and engine scans

**Date:** 2026-07-18  
**Branch:** `spin-valve-engine`  
**Convention:** [`docs/engine/SIGN_CONVENTION.md`](../docs/engine/SIGN_CONVENTION.md)

## What was implemented

1. Lead-tagged jump channels (`transport/channels.py`).
2. Instantaneous currents from the **same** dissipators as the dynamics:
   $J_{N,\alpha}$, $J_{E,\alpha}$, $J_{Q,\alpha}$.
3. Cycle average over the waiting interval, normalized by full period $T$
   (leads off during collision).
4. Electrical output power $P_{\rm el}= -(\mu_L-\mu_R)\,I$ with $I=\bar J_{N,L}$.
5. Battery $P_{\rm erg}=r\mathcal{W}_A$ with coh/inc split.
6. Dot first-law residual over one period at the stroboscopic fixed point.
7. Controls: no collision, dephasing, $\alpha=1/2$, collinear.

## Continuous NESS check (no collisions)

| Quantity | Value |
|----------|-------|
| $J_{N,L}$ | 0.165756 |
| $J_{N,R}$ | -0.165756 |
| $J_{N,L}+J_{N,R}$ | 5.551e-17 |
| $P_{\rm el}$ (NESS) | -0.198908 |

Particle balance should be $\sim 0$ (numerical).

## Rate scan (boosted window, $\theta\approx 0.4$)

| $T$ | $r$ | $P_{\rm el}$ | $P_{\rm erg}$ | $\|C\|$ | FL residual |
|-----|-----|----------------|------------------|--------|-------------|
| 0.5 | 2 | -0.2021 | 0.0003321 | 0.1303 | -2.24e-03 |
| 0.643 | 1.55 | -0.2015 | 0.0002653 | 0.1317 | -2.37e-03 |
| 0.828 | 1.21 | -0.2009 | 0.0002092 | 0.1324 | -2.48e-03 |
| 1.07 | 0.939 | -0.2004 | 0.0001636 | 0.1325 | -2.57e-03 |
| 1.37 | 0.73 | -0.2 | 0.0001271 | 0.1323 | -2.63e-03 |
| 1.76 | 0.567 | -0.1997 | 9.829e-05 | 0.1318 | -2.68e-03 |
| 2.27 | 0.441 | -0.1995 | 7.576e-05 | 0.1312 | -2.71e-03 |
| 2.92 | 0.343 | -0.1994 | 5.827e-05 | 0.1304 | -2.73e-03 |
| 3.76 | 0.266 | -0.1992 | 4.48e-05 | 0.1297 | -2.75e-03 |
| 4.83 | 0.207 | -0.1992 | 3.449e-05 | 0.129 | -2.76e-03 |
| 6.22 | 0.161 | -0.1991 | 2.661e-05 | 0.1286 | -2.76e-03 |
| 8 | 0.125 | -0.1991 | 2.059e-05 | 0.1283 | -2.77e-03 |


## Controls ($T=1.5$, $\theta\approx0.4$)

| Control | $P_{\rm el}$ | $P_{\rm erg}$ | $\|C\|$ | $\mathcal{W}_{\rm coh}$ |
|---------|----------------|------------------|--------|------------------------------|
| collision | -0.1999 | 0.000116 | 0.1322 | 0.0001739 |
| no_collision | -0.1989 | 0 | 0.1391 | 0 |
| dephasing | -0.2731 | 0 | 0 | 0 |
| alpha_half | -0.2004 | 0.0005807 | 0.1249 | 0 |
| collinear | -0.2376 | 0 | 0 | 0 |


## Interpretation (rigorous but scaffold-limited)

- Currents are **lead-resolved and cycle-averaged** from the sequential-tunneling
  generator — not NEGF.
- $P_{\rm el}$ uses the **output** sign convention in SIGN_CONVENTION.md.
  On this biased window the NESS $P_{\rm el}$ may be negative (electrical
  *input* / thermoelectric fridge or dissipative bias regime). That does **not**
  invalidate the current module; it means this default point is not claimed
  as a thermoelectric engine. The Stage-2 deliverable is correct bookkeeping
  and the co-variation of $(P_{\rm el},P_{\rm erg})$ under collisions.
- $P_{\rm erg}$ remains small when $\Delta$ is small (matched-gap tradeoff).
- True multi-parameter Pareto + engine-regime search is **Stage 3 / WP F**.

## Files

- `ness_currents.json`
- `stage2_rate_scan.csv`, `stage2_theta_scan.csv`, `stage2_controls.csv`
- `stage2_power_vs_rate.png/pdf`
- `stage2_power_vs_theta.png/pdf`
- `stage2_tradeoff_rate.png/pdf`
- `stage2_controls.png/pdf`

## Next

Stage 3: expand controls (matched-population, incoherent exchange), search
for $P_{\rm el}>0$ windows if an engine narrative is desired, or frame
honestly as resource partitioning under electrical load.
