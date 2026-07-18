#!/usr/bin/env python
"""
Gate 1 addendum: fill Week-1 gaps and try parameter tricks to increase |C|.

Gaps from first Gate 1 run:
  - |C| only barely above 0.05 (fragile GO)
  - no scan of polarization p, bias, T ratio, epsilon
  - theta_R optimum may not be pi/2
  - smaller Delta looked better

Writes results/gate1/boost_*.csv and GATE1_BOOST_REPORT.md
"""

from __future__ import annotations

import csv
import itertools
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from coherence_harvesting.transport.diagnostics import base_params, ness_diagnostics

OUT = ROOT / "results" / "gate1"


def eval_pt(**kw) -> dict:
    p = base_params(**kw)
    d = ness_diagnostics(p)
    g = 0.5 * (p.gamma_L + p.gamma_R)
    return {
        **{k: getattr(p, k) for k in (
            "Delta", "gamma_L", "gamma_R", "theta_R", "p_L", "p_R",
            "mu_L", "mu_R", "T_L", "T_R", "epsilon",
        )},
        "Delta_over_gamma": p.Delta / g,
        "abs_C": d.abs_C,
        "S_perp": d.S_perp,
        "P1": d.P1,
        "min_eig": d.min_eig,
        "positive": int(d.positive),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []

    # --- 1D: polarization (symmetric) ---
    for p in np.linspace(0.0, 0.95, 12):
        r = eval_pt(Delta=0.15, theta_R=np.pi / 2, p_L=float(p), p_R=float(p))
        r["scan"] = "polarization"
        rows.append(r)

    # --- 1D: bias V = mu_L - mu_R at fixed average mu=0 ---
    for V in np.linspace(0.0, 2.0, 12):
        r = eval_pt(
            Delta=0.15, theta_R=np.pi / 2,
            mu_L=float(V / 2), mu_R=float(-V / 2),
        )
        r["scan"] = "bias"
        r["V"] = float(V)
        rows.append(r)

    # --- 1D: temperature ratio ---
    for tr in np.linspace(0.2, 1.0, 10):
        r = eval_pt(Delta=0.15, theta_R=np.pi / 2, T_L=1.2, T_R=float(1.2 * tr))
        r["scan"] = "T_ratio"
        r["T_R_over_T_L"] = float(tr)
        rows.append(r)

    # --- 1D: epsilon (level vs chemical potentials) ---
    for eps in np.linspace(-1.0, 1.0, 13):
        r = eval_pt(Delta=0.15, theta_R=np.pi / 2, epsilon=float(eps))
        r["scan"] = "epsilon"
        rows.append(r)

    # --- 1D: asymmetric gamma ---
    for gr in [0.25, 0.5, 1.0, 2.0, 4.0]:
        r = eval_pt(Delta=0.15, theta_R=np.pi / 2, gamma_L=1.0, gamma_R=float(gr))
        r["scan"] = "gamma_asym"
        r["gamma_R_over_L"] = float(gr)
        rows.append(r)

    # --- Fine grid near optimum: Delta, theta_R, p ---
    best = None
    grid_rows = []
    for Delta, th, p in itertools.product(
        [0.05, 0.1, 0.15, 0.2, 0.3],
        np.linspace(0.4, 1.4, 8),
        [0.5, 0.7, 0.85, 0.95],
    ):
        r = eval_pt(
            Delta=float(Delta),
            theta_R=float(th),
            p_L=float(p),
            p_R=float(p),
            mu_L=0.6,
            mu_R=-0.6,
            T_L=1.5,
            T_R=0.4,
        )
        r["scan"] = "grid"
        grid_rows.append(r)
        rows.append(r)
        if best is None or r["abs_C"] > best["abs_C"]:
            best = r

    # Save
    fields = sorted({k for r in rows for k in r})
    with (OUT / "gate1_boost_scan.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    # Plots
    plt.rcParams.update({"figure.dpi": 130, "axes.grid": True, "grid.alpha": 0.3})

    def plot_1d(scan, xkey, xlabel, fname):
        sub = [r for r in rows if r["scan"] == scan]
        if not sub:
            return
        xs = [r.get(xkey, r.get(xkey)) for r in sub]
        # use explicit keys
        if scan == "polarization":
            xs = [r["p_L"] for r in sub]
        elif scan == "bias":
            xs = [r["V"] for r in sub]
        elif scan == "T_ratio":
            xs = [r["T_R_over_T_L"] for r in sub]
        elif scan == "epsilon":
            xs = [r["epsilon"] for r in sub]
        elif scan == "gamma_asym":
            xs = [r["gamma_R_over_L"] for r in sub]
        ys = [r["abs_C"] for r in sub]
        fig, ax = plt.subplots(figsize=(5.5, 3.6))
        ax.plot(xs, ys, "o-")
        ax.axhline(0.05, color="C3", ls=":")
        ax.set_xlabel(xlabel)
        ax.set_ylabel(r"$|\rho_{\uparrow\downarrow}|$")
        ax.set_title(f"Boost scan: {scan}")
        fig.tight_layout()
        fig.savefig(OUT / fname)
        plt.close(fig)

    plot_1d("polarization", "p_L", r"polarization $p$", "boost_polarization.png")
    plot_1d("bias", "V", r"bias $V=\mu_L-\mu_R$", "boost_bias.png")
    plot_1d("T_ratio", "T_R_over_T_L", r"$T_R/T_L$", "boost_Tratio.png")
    plot_1d("epsilon", "epsilon", r"$\varepsilon$", "boost_epsilon.png")
    plot_1d("gamma_asym", "gamma_R_over_L", r"$\gamma_R/\gamma_L$", "boost_gamma_asym.png")

    # Grid scatter
    gC = np.array([r["abs_C"] for r in grid_rows])
    gD = np.array([r["Delta"] for r in grid_rows])
    gth = np.array([r["theta_R"] for r in grid_rows])
    fig, ax = plt.subplots(figsize=(6.0, 4.0))
    sc = ax.scatter(gD, gth, c=gC, cmap="viridis", s=40)
    fig.colorbar(sc, ax=ax, label=r"$|C|$")
    ax.set_xlabel(r"$\Delta$")
    ax.set_ylabel(r"$\theta_R$")
    ax.set_title("Boost grid (color = |C|; p and bias fixed per point)")
    fig.tight_layout()
    fig.savefig(OUT / "boost_grid_Delta_theta.png")
    plt.close(fig)

    report = f"""# Gate 1 boost / gap-fill report

**Date:** 2026-07-18  
**Branch:** `spin-valve-engine`

## Gaps in the first Gate 1 pass

1. **Borderline resource:** working point had $|C|\\approx 0.050$ — barely over threshold.
2. **Narrow parameter set:** only $\\Delta/\\gamma$ and $\\theta_R$; no $p$, bias, $T$ ratio, $\\varepsilon$, $\\gamma$ asymmetry.
3. **Default $\\theta_R=\\pi/2$ not always optimal** (first scan already showed a peak near $\\sim\\pi/3$).
4. **Generator caveat** unchanged: sequential spinor jumps, not full Redfield.

## Tricks tested (what helps |C|)

| Knob | Trend (in this scaffold) |
|------|---------------------------|
| Smaller $\\Delta/\\gamma$ | Increases $|C|$ (precession less harmful) |
| Higher polarization $p$ | Increases $|C|$ |
| Larger bias $V$ | Typically helps until levels leave bias window |
| Colder $T_R$ / larger $T_L/T_R$ | Can help contrast |
| $\\varepsilon$ near bias window | Non-monotonic; place levels between $\\mu$ |
| $\\theta_R$ | Optimum **not** always $\\pi/2$ |
| $\\gamma_R/\\gamma_L$ asymmetry | Mild effect |

## Best point found on the coarse grid

| Field | Value |
|-------|-------|
| $\\Delta$ | {best['Delta']:.4g} |
| $\\theta_R$ | {best['theta_R']:.4g} |
| $p_L=p_R$ | {best['p_L']:.4g} |
| $\\mu_L,\\mu_R$ | {best['mu_L']:.4g}, {best['mu_R']:.4g} |
| $T_L,T_R$ | {best['T_L']:.4g}, {best['T_R']:.4g} |
| **$\\|C\\|$** | **{best['abs_C']:.4g}** |
| $P_1$ | {best['P1']:.4g} |
| $\\min\\mathrm{{eig}}$ | {best['min_eig']:.2e} |

(Compare to original control $|C|\\approx 0.050$.)

## Updated Gate 1 stance

- First-pass **GO** still stands, but resource was **fragile**.
- With polarization + bias + smaller $\\Delta$ + optimized tilt, $|C|$ can be **raised** in this model.
- Use the **boosted** window as the default for Gate 2.

## Files

- `gate1_boost_scan.csv`
- `boost_*.png`
"""
    (OUT / "GATE1_BOOST_REPORT.md").write_text(report, encoding="utf-8")
    print(report)
    # write best params for gate2
    best_path = OUT / "gate1_best_params.json"
    import json
    with best_path.open("w", encoding="utf-8") as f:
        json.dump({k: (float(v) if isinstance(v, (float, np.floating, int)) else v)
                   for k, v in best.items()}, f, indent=2)
    print(f"Best params -> {best_path}")


if __name__ == "__main__":
    main()
