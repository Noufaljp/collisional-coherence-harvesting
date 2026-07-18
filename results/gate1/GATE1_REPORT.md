# Gate 1 report (Week 1)

**Date:** 2026-07-18  
**Branch:** `spin-valve-engine`  
**Script:** `scripts/gate1_resource_scan.py`  
**Generator:** sequential-tunneling / spinor-jump lead Liouvillian
(`transport/nonsecular.py`) — **not** a derived Redfield model.
Gate 1 is an existence check inside this scaffold.

## Provisional thresholds

| Quantity | Threshold |
|----------|-----------|
| $\|\rho_{\uparrow\downarrow}\|$ | $\ge 0.05$ |
| $P_1$ | $\ge 0.05$ |
| $\min\mathrm{eig}(\rho)$ | $\ge -1e-08$ |

## Control points

| Control | $\Delta/\gamma$ | $\theta_R$ | $\|C\|$ | $P_1$ | $\min\mathrm{eig}$ |
|---------|-----------------|------------|--------|-------|------------------------|
| near-deg non-collinear | 0.3 | 1.57 | 0.05006 | 0.6284 | 2.53e-01 |
| near-deg collinear | 0.3 | 0 | 0 | 0.6351 | 2.63e-01 |
| large-$\Delta$ non-collinear | 20 | 1.57 | 0.0004615 | 0.5264 | 6.82e-02 |

## Automated checks

| Check | Result |
|-------|--------|
| near-deg $\|C\|$ above threshold | True |
| near-deg $P_1$ above threshold | True |
| near-deg positivity | True |
| collinear reduces/suppresses $C$ | True |
| large $\Delta$ suppresses $C$ vs near-deg | True |
| all scan points positive | True |

## Verdict: **GO**

- **GO:** proceed to Gate 2 (harvestability).
- **WEAK:** resource present but modest — refine window/generator.
- **NO-GO:** no usable coherent resource in this scaffold.

## Files

- `gate1_scan.csv` / `gate1_scan.npz`
- `gate1_absC_vs_Delta.png/pdf`
- `gate1_absC_vs_thetaR.png/pdf`
- `positivity_log.txt`

## Next

Gate 2 (Week 2): one-shot collision ergotropy on NESS + stroboscopic regeneration.
