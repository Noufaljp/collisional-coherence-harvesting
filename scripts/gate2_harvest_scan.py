#!/usr/bin/env python
"""
Gate 2 (Week 2): can the NESS coherence be exported by a collision,
and does it regenerate stroboscopically?

Uses Gate-1 boosted window when available, plus original control point.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from coherence_harvesting.companion.ergotropy import (
    bloch_from_rho,
    coherent_incoherent_ergotropy,
    qubit_ergotropy_from_rho,
    two_copy_from_bloch,
)
from coherence_harvesting.transport.diagnostics import base_params, ness_diagnostics
from coherence_harvesting.transport.engine import CollisionEngine, apply_collision
from coherence_harvesting.transport.nonsecular import (
    evolve_leads,
    spin_coherence,
    steady_state_leads,
)
from coherence_harvesting.transport.spin_valve import SpinValveParams

OUT = ROOT / "results" / "gate2"
G1 = ROOT / "results" / "gate1"


def load_boosted_kwargs() -> dict:
    path = G1 / "gate1_best_params.json"
    if path.exists():
        d = json.loads(path.read_text(encoding="utf-8"))
        keys = [
            "Delta", "gamma_L", "gamma_R", "theta_R", "p_L", "p_R",
            "mu_L", "mu_R", "T_L", "T_R", "epsilon",
        ]
        return {k: float(d[k]) for k in keys if k in d}
    return dict(
        Delta=0.15, theta_R=1.0, p_L=0.9, p_R=0.9,
        mu_L=0.6, mu_R=-0.6, T_L=1.5, T_R=0.4,
    )


def one_shot(params: SpinValveParams) -> dict:
    rho = steady_state_leads(params)
    C0 = spin_coherence(rho)
    d0 = ness_diagnostics(params)
    rho_D, rho_A = apply_collision(rho, params)
    C1 = spin_coherence(rho_D)
    W = qubit_ergotropy_from_rho(rho_A, Delta=float(params.Delta_A))
    x, y, z = bloch_from_rho(rho_A)
    parts = coherent_incoherent_ergotropy(z, x, y, float(params.Delta_A))
    W2 = two_copy_from_bloch(x, y, z, float(params.Delta_A))
    return {
        "abs_C_before": float(abs(C0)),
        "abs_C_after": float(abs(C1)),
        "P1": d0.P1,
        "W_A": float(W),
        "W_coh": parts["W_coh"],
        "W_inc": parts["W_inc"],
        "W_acc2": float(W2),
        "z_A": float(z),
        "theta": float(params.theta),
        "g": params.g,
        "tau": params.tau,
        "alpha": params.alpha,
        "Delta": params.Delta,
        "theta_R": params.theta_R,
    }


def stroboscopic(
    params: SpinValveParams, n_max: int = 300, tol: float = 1e-10
) -> dict:
    eng = CollisionEngine(params)
    # track residual coherence during iteration
    rho = steady_state_leads(params)
    hist_C = [float(abs(spin_coherence(rho)))]
    rho_A = None
    converged = False
    n_iter = 0
    for n_iter in range(1, n_max + 1):
        rho, rho_A = eng.step(rho)
        hist_C.append(float(abs(spin_coherence(rho))))
        if n_iter > 5 and abs(hist_C[-1] - hist_C[-2]) < tol and abs(
            hist_C[-1] - hist_C[-3]
        ) < tol:
            # also check density residual roughly
            rho2, _ = eng.step(rho)
            if np.linalg.norm(rho2 - rho) < tol:
                rho = rho2
                converged = True
                break
            rho = rho2
    W = qubit_ergotropy_from_rho(rho_A, Delta=float(params.Delta_A))
    # regeneration diagnostic: after collision, wait only and see C grow
    rho_post = rho
    C_post = abs(spin_coherence(rho_post))
    rho_wait = evolve_leads(rho_post, params, params.waiting_time)
    C_wait = abs(spin_coherence(rho_wait))
    return {
        "converged": int(converged),
        "n_iter": n_iter,
        "abs_C_fp": hist_C[-1],
        "abs_C_history_max": max(hist_C),
        "abs_C_history_min": min(hist_C[1:]) if len(hist_C) > 1 else hist_C[0],
        "W_A_fp": float(W),
        "P_erg": float(params.collision_rate * W),
        "C_post_collision": float(C_post),
        "C_after_wait": float(C_wait),
        "regenerates": int(C_wait > C_post * 1.05 + 1e-12 or C_wait > C_post + 1e-6),
        "theta": float(params.theta),
        "T_period": params.T_period,
        "g": params.g,
        "tau": params.tau,
        "hist_C": hist_C,
    }


def make_params(base_kw: dict, **over) -> SpinValveParams:
    kw = dict(base_kw)
    kw.update(over)
    # collision defaults
    kw.setdefault("g", 8.0)
    kw.setdefault("tau", 0.1)
    kw.setdefault("T_period", 1.5)
    kw.setdefault("alpha", 0.0)
    return SpinValveParams(**kw)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    boost = load_boosted_kwargs()
    original = dict(
        Delta=0.3, theta_R=np.pi / 2, p_L=0.7, p_R=0.7,
        mu_L=0.4, mu_R=-0.4, T_L=1.2, T_R=0.6, epsilon=0.0,
        gamma_L=1.0, gamma_R=1.0,
    )

    windows = {
        "boosted": boost,
        "original_gate1": original,
    }

    one_shot_rows = []
    # scan exchange angle on boosted window
    for name, base in windows.items():
        for theta in np.linspace(0.05, 1.2, 15):
            # theta = g*tau; fix g=8, vary tau
            g = 8.0
            tau = float(theta / g)
            p = make_params(base, g=g, tau=tau, T_period=max(2.0 * tau, 1.0), alpha=0.0)
            r = one_shot(p)
            r["window"] = name
            r["kind"] = "oneshot_theta"
            one_shot_rows.append(r)
        # alpha = 1/2 control
        p = make_params(base, g=8.0, tau=0.1, T_period=1.5, alpha=0.5)
        r = one_shot(p)
        r["window"] = name
        r["kind"] = "oneshot_alpha_half"
        one_shot_rows.append(r)

    # stroboscopic scans: period and theta on boosted
    strobo_rows = []
    histories = {}
    for T in np.geomspace(0.4, 6.0, 10):
        for theta in [0.2, 0.4, 0.7, 1.0]:
            g = 8.0
            tau = min(float(theta / g), 0.9 * float(T))
            p = make_params(boost, g=g, tau=tau, T_period=float(T), alpha=0.0)
            s = stroboscopic(p, n_max=250)
            s["window"] = "boosted"
            s["kind"] = "stroboscopic"
            # drop hist for CSV
            hist = s.pop("hist_C")
            strobo_rows.append(s)
            key = f"T{T:.3g}_th{theta:.2g}"
            histories[key] = hist

    # detailed history at a good point
    # pick max W among oneshot boosted
    cand = [r for r in one_shot_rows if r["window"] == "boosted" and r["kind"] == "oneshot_theta"]
    best_os = max(cand, key=lambda r: r["W_A"])
    g = 8.0
    tau = best_os["tau"]
    p_detail = make_params(boost, g=g, tau=tau, T_period=max(1.5, 3 * tau), alpha=0.0)
    detail = stroboscopic(p_detail, n_max=300)
    hist = detail.pop("hist_C")

    # save CSVs
    def write_csv(path, rows):
        if not rows:
            return
        fields = sorted({k for r in rows for k in r})
        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)

    write_csv(OUT / "gate2_oneshot.csv", one_shot_rows)
    write_csv(OUT / "gate2_stroboscopic.csv", strobo_rows)

    # plots
    plt.rcParams.update({"figure.dpi": 130, "axes.grid": True, "grid.alpha": 0.3})
    for name in windows:
        sub = [r for r in one_shot_rows if r["window"] == name and r["kind"] == "oneshot_theta"]
        th = [r["theta"] for r in sub]
        fig, ax = plt.subplots(1, 2, figsize=(9.5, 3.6))
        ax[0].plot(th, [r["W_A"] for r in sub], "o-", label=r"$\mathcal{W}_A$")
        ax[0].plot(th, [r["W_coh"] for r in sub], "s--", label=r"$\mathcal{W}_{coh}$")
        ax[0].set_xlabel(r"$\theta=g\tau$")
        ax[0].set_ylabel("ergotropy")
        ax[0].set_title(f"One-shot export ({name})")
        ax[0].legend(fontsize=8)
        ax[1].plot(th, [r["abs_C_before"] for r in sub], "o-", label="before")
        ax[1].plot(th, [r["abs_C_after"] for r in sub], "s--", label="after")
        ax[1].set_xlabel(r"$\theta$")
        ax[1].set_ylabel(r"$|C|$")
        ax[1].set_title("Dot coherence one-shot")
        ax[1].legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(OUT / f"gate2_oneshot_{name}.png")
        fig.savefig(OUT / f"gate2_oneshot_{name}.pdf")
        plt.close(fig)

    # stroboscopic W and C vs T at fixed theta=0.4
    sub = [r for r in strobo_rows if abs(r["theta"] - 0.4) < 0.05]
    sub = sorted(sub, key=lambda r: r["T_period"])
    fig, ax = plt.subplots(1, 2, figsize=(9.5, 3.6))
    ax[0].plot([r["T_period"] for r in sub], [r["W_A_fp"] for r in sub], "o-")
    ax[0].set_xscale("log")
    ax[0].set_xlabel(r"$T$ period")
    ax[0].set_ylabel(r"$\mathcal{W}_A$ at fixed point")
    ax[0].set_title(r"Stroboscopic battery (boosted, $\theta\approx0.4$)")
    ax[1].plot([r["T_period"] for r in sub], [r["abs_C_fp"] for r in sub], "o-")
    ax[1].set_xscale("log")
    ax[1].set_xlabel(r"$T$")
    ax[1].set_ylabel(r"$|C|$ fixed point")
    ax[1].set_title("Residual coherence under collisions")
    fig.tight_layout()
    fig.savefig(OUT / "gate2_stroboscopic_vs_T.png")
    fig.savefig(OUT / "gate2_stroboscopic_vs_T.pdf")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.0, 3.6))
    ax.plot(hist, "-")
    ax.set_xlabel("iteration")
    ax.set_ylabel(r"$|C|$")
    ax.set_title("Stroboscopic coherence trajectory (detail point)")
    fig.tight_layout()
    fig.savefig(OUT / "gate2_C_trajectory.png")
    plt.close(fig)

    # verdict
    max_W_boost = max(r["W_A"] for r in cand)
    max_W_orig = max(
        r["W_A"]
        for r in one_shot_rows
        if r["window"] == "original_gate1" and r["kind"] == "oneshot_theta"
    )
    alpha_half = next(
        r for r in one_shot_rows
        if r["window"] == "boosted" and r["kind"] == "oneshot_alpha_half"
    )
    strobo_ok = any(r["W_A_fp"] > 1e-8 and r["abs_C_fp"] > 1e-4 for r in strobo_rows)
    regen = any(r["regenerates"] for r in strobo_rows)
    oneshot_ok = max_W_boost > 1e-8

    if oneshot_ok and strobo_ok and regen:
        verdict = "GO"
    elif oneshot_ok:
        verdict = "WEAK"
    else:
        verdict = "NO-GO"

    # alpha half should have W~0
    report = f"""# Gate 2 report (Week 2)

**Date:** 2026-07-18  
**Branch:** `spin-valve-engine`  
**Scripts:** `scripts/gate2_harvest_scan.py` (plus Gate 1 boost window)

## Question

Can bias-generated NESS coherence be exported by a matched-gap exchange
collision, and does the resource regenerate under stroboscopic driving?

## Windows

| Window | Notes |
|--------|--------|
| `original_gate1` | Week-1 default ($\\|C\\|\\approx 0.05$) |
| `boosted` | Best point from `gate1_boost_scan` |

Boosted base kwargs: `{boost}`

## One-shot collision (NESS → one ancilla)

| Metric | Boosted | Original |
|--------|---------|----------|
| max $\\mathcal{{W}}_A$ over $\\theta$ | {max_W_boost:.4g} | {max_W_orig:.4g} |
| best $\\theta$ (boosted) | {best_os['theta']:.3g} | — |
| $\\|C\\|$ before (at best) | {best_os['abs_C_before']:.4g} | — |
| $\\|C\\|$ after (at best) | {best_os['abs_C_after']:.4g} | — |
| $\\alpha=1/2$ $\\mathcal{{W}}_{{\\rm coh}}$ (boosted) | {alpha_half['W_coh']:.4g} (total $\\mathcal{{W}}$={alpha_half['W_A']:.4g} is population-only) |

## Stroboscopic fixed point (boosted)

| Check | Result |
|-------|--------|
| Some $(T,\\theta)$ with $\\mathcal{{W}}_A>0$ and residual $\\|C\\|$ | {strobo_ok} |
| Wait interval regenerates $C$ after collision (some points) | {regen} |
| Detail point: converged={detail['converged']}, $n$={detail['n_iter']}, $\\|C\\|_{{fp}}$={detail['abs_C_fp']:.4g}, $\\mathcal{{W}}_A$={detail['W_A_fp']:.4g} | |

## Automated checks

| Check | Pass? |
|-------|-------|
| One-shot $\\mathcal{{W}}_A > 0$ | {oneshot_ok} |
| Stroboscopic export + residual $C$ | {strobo_ok} |
| Regeneration after wait | {regen} |
| $\\alpha=1/2$ null coherent charge | {alpha_half['W_coh'] < 1e-9} |

## Verdict: **{verdict}**

- **GO:** proceed to Stage 2 (lead-resolved currents + tradeoff curves).
- **WEAK:** export works one-shot but stroboscopic regeneration is poor.
- **NO-GO:** cannot put ergotropy on the ancilla from this NESS resource.

## Physics notes

1. Export is limited by single occupancy and weak $\\theta$ (only the active block couples).
2. Ground-state ancillas yield mostly **coherent** ergotropy ($z_A<0$); accessibility caveats from the companion still apply.
3. $\\alpha=1/2$ removes local ancilla coherence (back-action without battery charging).

## Files

- `gate2_oneshot.csv`
- `gate2_stroboscopic.csv`
- `gate2_oneshot_*.png/pdf`
- `gate2_stroboscopic_vs_T.png/pdf`
- `gate2_C_trajectory.png`

## Next (Stage 2)

Lead-resolved cycle-averaged currents; full $(P_{{\\rm el}}, P_{{\\rm erg}})$ scans on the boosted window.
"""
    (OUT / "GATE2_REPORT.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
