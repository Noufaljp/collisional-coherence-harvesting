#!/usr/bin/env python
"""
Stage 2: rigorous lead-resolved cycle-averaged currents + (P_el, P_erg) scans.

Uses boosted Gate-1 window. Writes results/stage2/.
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

from coherence_harvesting.transport.currents import instantaneous_currents
from coherence_harvesting.transport.engine import CollisionEngine
from coherence_harvesting.transport.nonsecular import steady_state_leads
from coherence_harvesting.transport.spin_valve import SpinValveParams

OUT = ROOT / "results" / "stage2"
G1 = ROOT / "results" / "gate1"


def boosted_base() -> dict:
    path = G1 / "gate1_best_params.json"
    d = json.loads(path.read_text(encoding="utf-8"))
    keys = [
        "Delta", "gamma_L", "gamma_R", "theta_R", "p_L", "p_R",
        "mu_L", "mu_R", "T_L", "T_R", "epsilon",
    ]
    return {k: float(d[k]) for k in keys if k in d}


def make_params(base: dict, **over) -> SpinValveParams:
    kw = dict(base)
    kw.update(over)
    kw.setdefault("g", 8.0)
    kw.setdefault("tau", 0.08)
    kw.setdefault("T_period", 1.5)
    kw.setdefault("alpha", 0.0)
    return SpinValveParams(**kw)


def row_from_result(res, **meta) -> dict:
    return {
        **meta,
        "converged": int(res.converged),
        "n_iter": res.n_iter,
        "P_el": res.P_el,
        "P_erg": res.P_erg,
        "I": res.I,
        "J_N_L": res.J_N_L,
        "J_N_R": res.J_N_R,
        "J_E_L": res.J_E_L,
        "J_E_R": res.J_E_R,
        "J_Q_L": res.J_Q_L,
        "J_Q_R": res.J_Q_R,
        "residual_particle_avg": res.residual_particle_avg,
        "particle_balance_instant": res.particle_balance_instant,
        "W_A": res.W_A,
        "W_coh": res.W_coh,
        "W_inc": res.W_inc,
        "W_acc2": res.W_acc2,
        "E_A": res.E_A,
        "abs_C": abs(res.coherence),
        "P1": res.pops[1] + res.pops[2],
        "dE_wait": res.dE_wait,
        "dE_collision": res.dE_collision,
        "dN_wait": res.dN_wait,
        "dN_collision": res.dN_collision,
        "first_law_residual": res.first_law_residual,
        "theta": meta.get("theta", np.nan),
        "T_period": meta.get("T_period", np.nan),
        "r": meta.get("r", np.nan),
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    fields = sorted({k for r in rows for k in r})
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    base = boosted_base()

    # --- NESS conservation diagnostics ---
    p0 = make_params(base, tau=0.0, T_period=1.0)
    rho0 = steady_state_leads(p0)
    inst0 = instantaneous_currents(rho0, p0)
    ness = {
        "J_N_L": inst0.J_N_L,
        "J_N_R": inst0.J_N_R,
        "balance": inst0.particle_balance,
        "J_E_L": inst0.J_E_L,
        "J_E_R": inst0.J_E_R,
        "J_Q_L": inst0.J_Q_L,
        "J_Q_R": inst0.J_Q_R,
        "I": inst0.I,
        "P_el": -(p0.mu_L - p0.mu_R) * inst0.I,
    }
    (OUT / "ness_currents.json").write_text(json.dumps(ness, indent=2), encoding="utf-8")

    # --- Scan collision rate (period) at fixed theta ---
    g = 8.0
    theta_fixed = 0.4
    periods = np.geomspace(0.5, 8.0, 12)
    rate_rows = []
    for T in periods:
        tau = min(theta_fixed / g, 0.5 * float(T))
        p = make_params(base, g=g, tau=tau, T_period=float(T), alpha=0.0)
        res = CollisionEngine(p).find_fixed_point(n_max=300, tol=1e-9, current_steps=60)
        rate_rows.append(
            row_from_result(
                res,
                scan="rate",
                T_period=float(T),
                r=1.0 / float(T),
                theta=g * tau,
                control="collision",
            )
        )
        print(
            f"T={T:.3g} conv={res.converged} P_el={res.P_el:.4g} P_erg={res.P_erg:.4g} "
            f"|C|={abs(res.coherence):.4g} bal={res.residual_particle_avg:.3e} "
            f"FL={res.first_law_residual:.3e}"
        )

    # --- Scan theta at fixed period ---
    T_fixed = 1.5
    theta_rows = []
    for th in np.linspace(0.05, 1.0, 12):
        tau = min(float(th) / g, 0.5 * T_fixed)
        p = make_params(base, g=g, tau=tau, T_period=T_fixed, alpha=0.0)
        res = CollisionEngine(p).find_fixed_point(n_max=300, tol=1e-9, current_steps=60)
        theta_rows.append(
            row_from_result(
                res,
                scan="theta",
                T_period=T_fixed,
                r=1.0 / T_fixed,
                theta=g * tau,
                control="collision",
            )
        )

    # --- Controls at fixed (T, theta) ---
    T_c, th_c = 1.5, 0.4
    tau_c = th_c / g
    controls = {}
    # collisions
    p_col = make_params(base, g=g, tau=tau_c, T_period=T_c, alpha=0.0)
    controls["collision"] = CollisionEngine(p_col).find_fixed_point(
        n_max=300, tol=1e-9, current_steps=60
    )
    # no collision: pure lead NESS, cycle-average over T with tau=0
    p_nc = make_params(base, g=g, tau=0.0, T_period=T_c, alpha=0.0)
    controls["no_collision"] = CollisionEngine(p_nc).find_fixed_point(
        n_max=50, tol=1e-9, current_steps=60
    )
    # dephasing
    p_de = make_params(base, g=g, tau=tau_c, T_period=T_c, alpha=0.0)
    controls["dephasing"] = CollisionEngine(p_de).dephasing_control_fixed_point(
        n_max=300, tol=1e-9, current_steps=60
    )
    # alpha = 1/2
    p_ah = make_params(base, g=g, tau=tau_c, T_period=T_c, alpha=0.5)
    controls["alpha_half"] = CollisionEngine(p_ah).find_fixed_point(
        n_max=300, tol=1e-9, current_steps=60
    )
    # collinear
    p_cl = make_params(base, g=g, tau=tau_c, T_period=T_c, alpha=0.0, theta_R=0.0)
    controls["collinear"] = CollisionEngine(p_cl).find_fixed_point(
        n_max=300, tol=1e-9, current_steps=60
    )

    control_rows = []
    for name, res in controls.items():
        control_rows.append(
            row_from_result(
                res,
                scan="control",
                control=name,
                T_period=T_c,
                r=1.0 / T_c,
                theta=th_c if name != "no_collision" else 0.0,
            )
        )
        print(
            f"control {name}: P_el={res.P_el:.4g} P_erg={res.P_erg:.4g} "
            f"|C|={abs(res.coherence):.4g} W_coh={res.W_coh:.4g}"
        )

    write_csv(OUT / "stage2_rate_scan.csv", rate_rows)
    write_csv(OUT / "stage2_theta_scan.csv", theta_rows)
    write_csv(OUT / "stage2_controls.csv", control_rows)

    # Plots
    plt.rcParams.update({"figure.dpi": 130, "axes.grid": True, "grid.alpha": 0.3})

    rvals = [r["r"] for r in rate_rows]
    fig, ax = plt.subplots(1, 2, figsize=(9.8, 3.7))
    ax[0].plot(rvals, [r["P_el"] for r in rate_rows], "o-", label=r"$P_{\mathrm{el}}$")
    ax[0].plot(rvals, [r["P_erg"] for r in rate_rows], "s-", label=r"$P_{\mathrm{erg}}$")
    ax[0].set_xscale("log")
    ax[0].set_xlabel(r"$r=1/T$")
    ax[0].set_ylabel("power")
    ax[0].set_title(r"Stage 2: powers vs collision rate ($\theta\approx 0.4$)")
    ax[0].legend(fontsize=8)
    ax[1].plot(rvals, [r["abs_C"] for r in rate_rows], "o-")
    ax[1].set_xscale("log")
    ax[1].set_xlabel(r"$r$")
    ax[1].set_ylabel(r"$|C|$ at FP")
    ax[1].set_title("Residual coherence")
    fig.tight_layout()
    fig.savefig(OUT / "stage2_power_vs_rate.png")
    fig.savefig(OUT / "stage2_power_vs_rate.pdf")
    plt.close(fig)

    ths = [r["theta"] for r in theta_rows]
    fig, ax = plt.subplots(figsize=(6.0, 3.8))
    ax.plot(ths, [r["P_el"] for r in theta_rows], "o-", label=r"$P_{\mathrm{el}}$")
    ax.plot(ths, [r["P_erg"] for r in theta_rows], "s-", label=r"$P_{\mathrm{erg}}$")
    ax.set_xlabel(r"$\theta=g\tau$")
    ax.set_ylabel("power")
    ax.set_title(r"Stage 2: powers vs exchange angle ($T=1.5$)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "stage2_power_vs_theta.png")
    fig.savefig(OUT / "stage2_power_vs_theta.pdf")
    plt.close(fig)

    # tradeoff scatter rate scan
    fig, ax = plt.subplots(figsize=(5.8, 4.0))
    sc = ax.scatter(
        [r["P_el"] for r in rate_rows],
        [r["P_erg"] for r in rate_rows],
        c=np.log10(rvals),
        cmap="viridis",
        s=50,
    )
    fig.colorbar(sc, ax=ax, label=r"$\log_{10} r$")
    ax.set_xlabel(r"$P_{\mathrm{el}}$ (output convention)")
    ax.set_ylabel(r"$P_{\mathrm{erg}}$")
    ax.set_title("Tradeoff scan (rate; not a true Pareto frontier)")
    fig.tight_layout()
    fig.savefig(OUT / "stage2_tradeoff_rate.png")
    fig.savefig(OUT / "stage2_tradeoff_rate.pdf")
    plt.close(fig)

    # control bar chart
    names = [r["control"] for r in control_rows]
    fig, ax = plt.subplots(figsize=(7.0, 3.8))
    x = np.arange(len(names))
    w = 0.35
    ax.bar(x - w / 2, [r["P_el"] for r in control_rows], w, label=r"$P_{\mathrm{el}}$")
    ax.bar(x + w / 2, [r["P_erg"] for r in control_rows], w, label=r"$P_{\mathrm{erg}}$")
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=20, ha="right")
    ax.set_ylabel("power")
    ax.set_title("Stage 2 controls at fixed $(T,\\theta)$")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "stage2_controls.png")
    fig.savefig(OUT / "stage2_controls.pdf")
    plt.close(fig)

    # Report
    bal = ness["balance"]
    report = f"""# Stage 2 report — lead-resolved currents and engine scans

**Date:** 2026-07-18  
**Branch:** `spin-valve-engine`  
**Convention:** [`docs/engine/SIGN_CONVENTION.md`](../docs/engine/SIGN_CONVENTION.md)

## What was implemented

1. Lead-tagged jump channels (`transport/channels.py`).
2. Instantaneous currents from the **same** dissipators as the dynamics:
   $J_{{N,\\alpha}}$, $J_{{E,\\alpha}}$, $J_{{Q,\\alpha}}$.
3. Cycle average over the waiting interval, normalized by full period $T$
   (leads off during collision).
4. Electrical output power $P_{{\\rm el}}= -(\\mu_L-\\mu_R)\\,I$ with $I=\\bar J_{{N,L}}$.
5. Battery $P_{{\\rm erg}}=r\\mathcal{{W}}_A$ with coh/inc split.
6. Dot first-law residual over one period at the stroboscopic fixed point.
7. Controls: no collision, dephasing, $\\alpha=1/2$, collinear.

## Continuous NESS check (no collisions)

| Quantity | Value |
|----------|-------|
| $J_{{N,L}}$ | {ness['J_N_L']:.6g} |
| $J_{{N,R}}$ | {ness['J_N_R']:.6g} |
| $J_{{N,L}}+J_{{N,R}}$ | {bal:.3e} |
| $P_{{\\rm el}}$ (NESS) | {ness['P_el']:.6g} |

Particle balance should be $\\sim 0$ (numerical).

## Rate scan (boosted window, $\\theta\\approx 0.4$)

| $T$ | $r$ | $P_{{\\rm el}}$ | $P_{{\\rm erg}}$ | $\\|C\\|$ | FL residual |
|-----|-----|----------------|------------------|--------|-------------|
"""
    for r in rate_rows:
        report += (
            f"| {r['T_period']:.3g} | {r['r']:.3g} | {r['P_el']:.4g} | {r['P_erg']:.4g} | "
            f"{r['abs_C']:.4g} | {r['first_law_residual']:.2e} |\n"
        )

    report += f"""

## Controls ($T={T_c}$, $\\theta\\approx{th_c}$)

| Control | $P_{{\\rm el}}$ | $P_{{\\rm erg}}$ | $\\|C\\|$ | $\\mathcal{{W}}_{{\\rm coh}}$ |
|---------|----------------|------------------|--------|------------------------------|
"""
    for r in control_rows:
        report += (
            f"| {r['control']} | {r['P_el']:.4g} | {r['P_erg']:.4g} | "
            f"{r['abs_C']:.4g} | {r['W_coh']:.4g} |\n"
        )

    report += f"""

## Interpretation (rigorous but scaffold-limited)

- Currents are **lead-resolved and cycle-averaged** from the sequential-tunneling
  generator — not NEGF.
- $P_{{\\rm el}}$ uses the **output** sign convention in SIGN_CONVENTION.md.
  On this biased window the NESS $P_{{\\rm el}}$ may be negative (electrical
  *input* / thermoelectric fridge or dissipative bias regime). That does **not**
  invalidate the current module; it means this default point is not claimed
  as a thermoelectric engine. The Stage-2 deliverable is correct bookkeeping
  and the co-variation of $(P_{{\\rm el}},P_{{\\rm erg}})$ under collisions.
- $P_{{\\rm erg}}$ remains small when $\\Delta$ is small (matched-gap tradeoff).
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
for $P_{{\\rm el}}>0$ windows if an engine narrative is desired, or frame
honestly as resource partitioning under electrical load.
"""
    (OUT / "STAGE2_REPORT.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
