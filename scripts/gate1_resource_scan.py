#!/usr/bin/env python
"""
Gate 1 (Week 1): does a bias-generated spin coherence exist in the NESS?

Scans Delta/gamma and theta_R; collinear and large-Delta controls; positivity log.

Outputs: results/gate1/
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from coherence_harvesting.transport.diagnostics import base_params, ness_diagnostics

OUT = ROOT / "results" / "gate1"
THRESH_ABS_C = 0.05
THRESH_P1 = 0.05
POS_EIG = -1e-8


def run_point(**kw) -> dict:
    p = base_params(**kw)
    d = ness_diagnostics(p)
    gamma = 0.5 * (p.gamma_L + p.gamma_R)
    return {
        "Delta": p.Delta,
        "Delta_over_gamma": p.Delta / gamma,
        "theta_R": p.theta_R,
        "p_L": p.p_L,
        "p_R": p.p_R,
        "mu_L": p.mu_L,
        "mu_R": p.mu_R,
        "T_L": p.T_L,
        "T_R": p.T_R,
        "abs_C": d.abs_C,
        "S_perp": d.S_perp,
        "S_z": d.S_z,
        "P1": d.P1,
        "p0": d.p0,
        "min_eig": d.min_eig,
        "positive": int(d.positive),
        "hermiticity_err": d.hermiticity_err,
        "trace": d.trace,
        "pass_C": int(d.abs_C >= THRESH_ABS_C),
        "pass_P1": int(d.P1 >= THRESH_P1),
        "pass_pos": int(d.positive),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    gamma = 1.0

    for D in np.geomspace(0.05, 50.0, 16):
        r = run_point(
            Delta=float(D * gamma), gamma_L=gamma, gamma_R=gamma, theta_R=np.pi / 2
        )
        r["scan"] = "Delta"
        rows.append(r)

    for th in np.linspace(0.0, np.pi, 13):
        r = run_point(Delta=0.3, gamma_L=1.0, gamma_R=1.0, theta_R=float(th))
        r["scan"] = "theta_R"
        rows.append(r)

    controls = [
        ("near_deg_noncollinear", dict(Delta=0.3, theta_R=np.pi / 2)),
        ("near_deg_collinear", dict(Delta=0.3, theta_R=0.0)),
        ("large_Delta_noncollinear", dict(Delta=20.0, theta_R=np.pi / 2)),
        ("large_Delta_collinear", dict(Delta=20.0, theta_R=0.0)),
        ("mid_Delta_noncollinear", dict(Delta=2.0, theta_R=np.pi / 2)),
    ]
    for name, kw in controls:
        r = run_point(**kw)
        r["scan"] = "control"
        r["control"] = name
        rows.append(r)

    fieldnames = sorted({k for r in rows for k in r.keys()})
    csv_path = OUT / "gate1_scan.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    np.savez(
        OUT / "gate1_scan.npz",
        **{
            k: np.array([r.get(k) for r in rows])
            for k in fieldnames
            if k != "control"
        },
    )

    plt.rcParams.update(
        {"figure.dpi": 140, "font.size": 11, "axes.grid": True, "grid.alpha": 0.3}
    )

    drows = [r for r in rows if r["scan"] == "Delta"]
    x = np.array([r["Delta_over_gamma"] for r in drows], dtype=float)
    yC = np.array([r["abs_C"] for r in drows], dtype=float)
    yP = np.array([r["P1"] for r in drows], dtype=float)
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    ax.plot(x, yC, "o-", label=r"$|\rho_{\uparrow\downarrow}|$")
    ax.plot(x, yP, "s--", label=r"$P_1$")
    ax.axhline(THRESH_ABS_C, color="C3", ls=":", label=rf"thresh $|C|={THRESH_ABS_C}$")
    ax.set_xscale("log")
    ax.set_xlabel(r"$\Delta / \gamma$")
    ax.set_ylabel("NESS resource")
    ax.set_title(r"Gate 1: resource vs $\Delta/\gamma$ ($\theta_R=\pi/2$)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "gate1_absC_vs_Delta.png")
    fig.savefig(OUT / "gate1_absC_vs_Delta.pdf")
    plt.close(fig)

    trows = [r for r in rows if r["scan"] == "theta_R"]
    th = np.array([r["theta_R"] for r in trows], dtype=float)
    yC = np.array([r["abs_C"] for r in trows], dtype=float)
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    ax.plot(th, yC, "o-")
    ax.axhline(THRESH_ABS_C, color="C3", ls=":")
    ax.set_xlabel(r"$\theta_R$")
    ax.set_ylabel(r"$|\rho_{\uparrow\downarrow}|$")
    ax.set_title(r"Gate 1: resource vs tilt ($\Delta/\gamma=0.3$)")
    fig.tight_layout()
    fig.savefig(OUT / "gate1_absC_vs_thetaR.png")
    fig.savefig(OUT / "gate1_absC_vs_thetaR.pdf")
    plt.close(fig)

    with (OUT / "positivity_log.txt").open("w", encoding="utf-8") as f:
        f.write("Gate 1 positivity log\n")
        f.write(f"threshold min_eig >= {POS_EIG}\n\n")
        n_fail = 0
        for r in rows:
            ok = r["min_eig"] >= POS_EIG
            if not ok:
                n_fail += 1
            f.write(
                f"scan={r['scan']} Delta={r['Delta']:.4g} theta_R={r['theta_R']:.4g} "
                f"min_eig={r['min_eig']:.3e} positive={ok}\n"
            )
        f.write(f"\nfailures: {n_fail} / {len(rows)}\n")

    near = next(r for r in rows if r.get("control") == "near_deg_noncollinear")
    col = next(r for r in rows if r.get("control") == "near_deg_collinear")
    large = next(r for r in rows if r.get("control") == "large_Delta_noncollinear")

    checks = {
        "near_deg_absC": near["abs_C"] >= THRESH_ABS_C,
        "near_deg_P1": near["P1"] >= THRESH_P1,
        "near_deg_positive": near["min_eig"] >= POS_EIG,
        "collinear_smaller_C": col["abs_C"] <= near["abs_C"] * 0.5 + 1e-12
        or col["abs_C"] < THRESH_ABS_C,
        "large_Delta_suppressed": large["abs_C"] < near["abs_C"] * 0.5,
        "all_positive": all(r["min_eig"] >= POS_EIG for r in rows),
    }
    if (
        sum(checks.values()) >= 5
        and checks["near_deg_absC"]
        and checks["near_deg_P1"]
    ):
        verdict = "GO"
    elif checks["near_deg_absC"] or near["abs_C"] >= 0.02:
        verdict = "WEAK"
    else:
        verdict = "NO-GO"

    report = f"""# Gate 1 report (Week 1)

**Date:** 2026-07-18  
**Branch:** `spin-valve-engine`  
**Script:** `scripts/gate1_resource_scan.py`  
**Generator:** sequential-tunneling / spinor-jump lead Liouvillian
(`transport/nonsecular.py`) — **not** a derived Redfield model.
Gate 1 is an existence check inside this scaffold.

## Provisional thresholds

| Quantity | Threshold |
|----------|-----------|
| $\\|\\rho_{{\\uparrow\\downarrow}}\\|$ | $\\ge {THRESH_ABS_C}$ |
| $P_1$ | $\\ge {THRESH_P1}$ |
| $\\min\\mathrm{{eig}}(\\rho)$ | $\\ge {POS_EIG}$ |

## Control points

| Control | $\\Delta/\\gamma$ | $\\theta_R$ | $\\|C\\|$ | $P_1$ | $\\min\\mathrm{{eig}}$ |
|---------|-----------------|------------|--------|-------|------------------------|
| near-deg non-collinear | {near['Delta_over_gamma']:.3g} | {near['theta_R']:.3g} | {near['abs_C']:.4g} | {near['P1']:.4g} | {near['min_eig']:.2e} |
| near-deg collinear | {col['Delta_over_gamma']:.3g} | {col['theta_R']:.3g} | {col['abs_C']:.4g} | {col['P1']:.4g} | {col['min_eig']:.2e} |
| large-$\\Delta$ non-collinear | {large['Delta_over_gamma']:.3g} | {large['theta_R']:.3g} | {large['abs_C']:.4g} | {large['P1']:.4g} | {large['min_eig']:.2e} |

## Automated checks

| Check | Result |
|-------|--------|
| near-deg $\\|C\\|$ above threshold | {checks['near_deg_absC']} |
| near-deg $P_1$ above threshold | {checks['near_deg_P1']} |
| near-deg positivity | {checks['near_deg_positive']} |
| collinear reduces/suppresses $C$ | {checks['collinear_smaller_C']} |
| large $\\Delta$ suppresses $C$ vs near-deg | {checks['large_Delta_suppressed']} |
| all scan points positive | {checks['all_positive']} |

## Verdict: **{verdict}**

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
"""
    (OUT / "GATE1_REPORT.md").write_text(report, encoding="utf-8")
    print(report)
    print(f"Wrote results to {OUT}")


if __name__ == "__main__":
    main()
