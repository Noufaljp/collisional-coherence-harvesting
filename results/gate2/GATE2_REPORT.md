# Gate 2 report (Week 2)

**Date:** 2026-07-18  
**Branch:** `spin-valve-engine`  
**Scripts:** `scripts/gate2_harvest_scan.py` (plus Gate 1 boost window)

## Question

Can bias-generated NESS coherence be exported by a matched-gap exchange
collision, and does the resource regenerate under stroboscopic driving?

## Windows

| Window | Notes |
|--------|--------|
| `original_gate1` | Week-1 default ($\|C\|\approx 0.05$) |
| `boosted` | Best point from `gate1_boost_scan` |

Boosted base kwargs: `{'Delta': 0.05, 'gamma_L': 1.0, 'gamma_R': 1.0, 'theta_R': 1.4, 'p_L': 0.95, 'p_R': 0.95, 'mu_L': 0.6, 'mu_R': -0.6, 'T_L': 1.5, 'T_R': 0.4, 'epsilon': 0.0}`

## One-shot collision (NESS → one ancilla)

| Metric | Boosted | Original |
|--------|---------|----------|
| max $\mathcal{W}_A$ over $\theta$ | 0.002058 | 0.00164 |
| best $\theta$ (boosted) | 1.2 | — |
| $\|C\|$ before (at best) | 0.1391 | — |
| $\|C\|$ after (at best) | 0.05039 | — |
| $\alpha=1/2$ local $\mathcal{W}_{\rm coh}$ (boosted) | $0$ (only population $\mathcal{W}_{\rm inc}>0$) | control: **no coherent** charging |

## Stroboscopic fixed point (boosted)

| Check | Result |
|-------|--------|
| Some $(T,\theta)$ with $\mathcal{W}_A>0$ and residual $\|C\|$ | True |
| Wait interval regenerates $C$ after collision (some points) | True |
| Detail point: converged=1, $n$=19, $\|C\|_{fp}$=0.05131, $\mathcal{W}_A$=0.001647 | |

## Automated checks

| Check | Pass? |
|-------|-------|
| One-shot $\mathcal{W}_A > 0$ | True |
| Stroboscopic export + residual $C$ | True |
| Regeneration after wait | True |
| $\alpha=1/2$ null **coherent** charge ($\mathcal{W}_{\rm coh}=0$) | True |

## Verdict: **GO**

- **GO:** proceed to Stage 2 (lead-resolved currents + tradeoff curves).
- **WEAK:** export works one-shot but stroboscopic regeneration is poor.
- **NO-GO:** cannot put ergotropy on the ancilla from this NESS resource.

## Physics notes

1. Export is limited by single occupancy and weak $\theta$ (only the active block couples).
2. Ground-state ancillas yield mostly **coherent** ergotropy ($z_A<0$); accessibility caveats from the companion still apply.
3. $\alpha=1/2$ removes **coherent** ancilla ergotropy ($\mathcal{W}_{\rm coh}=0$); residual $\mathcal{W}$ is purely incoherent from population transfer — as expected, not a failure of the control.

## Files

- `gate2_oneshot.csv`
- `gate2_stroboscopic.csv`
- `gate2_oneshot_*.png/pdf`
- `gate2_stroboscopic_vs_T.png/pdf`
- `gate2_C_trajectory.png`

## Next (Stage 2)

Lead-resolved cycle-averaged currents; full $(P_{\rm el}, P_{\rm erg})$ scans on the boosted window.
