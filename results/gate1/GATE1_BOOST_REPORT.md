# Gate 1 boost / gap-fill report

**Date:** 2026-07-18  
**Branch:** `spin-valve-engine`

## Gaps in the first Gate 1 pass

1. **Borderline resource:** working point had $|C|\approx 0.050$ — barely over threshold.
2. **Narrow parameter set:** only $\Delta/\gamma$ and $\theta_R$; no $p$, bias, $T$ ratio, $\varepsilon$, $\gamma$ asymmetry.
3. **Default $\theta_R=\pi/2$ not always optimal** (first scan already showed a peak near $\sim\pi/3$).
4. **Generator caveat** unchanged: sequential spinor jumps, not full Redfield.

## Tricks tested (what helps |C|)

| Knob | Trend (in this scaffold) |
|------|---------------------------|
| Smaller $\Delta/\gamma$ | Increases $|C|$ (precession less harmful) |
| Higher polarization $p$ | Increases $|C|$ |
| Larger bias $V$ | Typically helps until levels leave bias window |
| Colder $T_R$ / larger $T_L/T_R$ | Can help contrast |
| $\varepsilon$ near bias window | Non-monotonic; place levels between $\mu$ |
| $\theta_R$ | Optimum **not** always $\pi/2$ |
| $\gamma_R/\gamma_L$ asymmetry | Mild effect |

## Best point found on the coarse grid

| Field | Value |
|-------|-------|
| $\Delta$ | 0.05 |
| $\theta_R$ | 1.4 |
| $p_L=p_R$ | 0.95 |
| $\mu_L,\mu_R$ | 0.6, -0.6 |
| $T_L,T_R$ | 1.5, 0.4 |
| **$\|C\|$** | **0.1391** |
| $P_1$ | 0.6144 |
| $\min\mathrm{eig}$ | 1.57e-01 |

(Compare to original control $|C|\approx 0.050$.)

## Updated Gate 1 stance

- First-pass **GO** still stands, but resource was **fragile**.
- With polarization + bias + smaller $\Delta$ + optimized tilt, $|C|$ can be **raised** in this model.
- Use the **boosted** window as the default for Gate 2.

## Files

- `gate1_boost_scan.csv`
- `boost_*.png`
