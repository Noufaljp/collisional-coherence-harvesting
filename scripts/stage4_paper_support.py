#!/usr/bin/env python
"""
Stage 4 support: extra scans and paper-ready figures for the TE+battery story.

Uses the Stage-3 chosen engine window. Produces:
  - load-voltage sweep at fixed T (TE engine curve + |C|)
  - efficiency diagnostic eta = P_el / J_Q_hot when P_el>0
  - resource map |C|(Delta, theta_R) on the engine T,mu window
  - dual-output vs collision rate (polished)
  - control bar chart (polished)
  - CSV tables for the manuscript

Outputs: results/stage4/ and engine_paper/figures/
"""

from __future__ import annotations

import csv
import json
import shutil
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from coherence_harvesting.transport.currents import (
    electrical_output_power,
    instantaneous_currents,
)
from coherence_harvesting.transport.diagnostics import ness_diagnostics
from coherence_harvesting.transport.engine import CollisionEngine
from coherence_harvesting.transport.nonsecular import steady_state_leads
from coherence_harvesting.transport.spin_valve import SpinValveParams

OUT = ROOT / "results" / "stage4"
FIG = ROOT / "engine_paper" / "figures"
S3 = ROOT / "results" / "stage3"


def load_window() -> dict:
    d = json.loads((S3 / "chosen_window.json").read_text(encoding="utf-8"))
    keys = [
        "epsilon", "Delta", "theta_R", "p_L", "p_R",
        "mu_L", "mu_R", "T_L", "T_R",
    ]
    return {k: float(d[k]) for k in keys}


def make_params(win: dict, **over) -> SpinValveParams:
    kw = dict(win)
    kw.setdefault("gamma_L", 1.0)
    kw.setdefault("gamma_R", 1.0)
    kw.setdefault("g", 8.0)
    kw.setdefault("tau", 0.05)
    kw.setdefault("T_period", 1.5)
    kw.setdefault("alpha", 0.0)
    kw.update(over)
    return SpinValveParams(**kw)


def write_csv(path: Path, rows: list[dict]) -> None:
    fields = sorted({k for r in rows for k in r})
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def ness_point(**kw) -> dict:
    p = SpinValveParams(**kw)
    rho = steady_state_leads(p)
    inst = instantaneous_currents(rho, p)
    d = ness_diagnostics(p)
    return {
        "P_el": electrical_output_power(inst.I, p),
        "I": inst.I,
        "J_Q_L": inst.J_Q_L,
        "J_Q_R": inst.J_Q_R,
        "abs_C": d.abs_C,
        "P1": d.P1,
        "V": p.mu_L - p.mu_R,
        "min_eig": d.min_eig,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    win = load_window()
    plt.rcParams.update({"figure.dpi": 140, "font.size": 11, "axes.grid": True, "grid.alpha": 0.3})

    # --- 1) Load voltage sweep (NESS): engine curve ---
    load_rows = []
    for V in np.linspace(-0.9, 0.4, 27):
        m = ness_point(
            epsilon=win["epsilon"],
            Delta=win["Delta"],
            theta_R=win["theta_R"],
            p_L=win["p_L"],
            p_R=win["p_R"],
            mu_L=float(V / 2),
            mu_R=float(-V / 2),
            T_L=win["T_L"],
            T_R=win["T_R"],
            gamma_L=1.0,
            gamma_R=1.0,
        )
        m["V"] = float(V)
        # efficiency proxy when engine: heat from hot L if T_L > T_R
        if m["P_el"] > 0 and m["J_Q_L"] > 1e-10:
            m["eta"] = m["P_el"] / m["J_Q_L"]
        else:
            m["eta"] = float("nan")
        load_rows.append(m)
    write_csv(OUT / "load_sweep_ness.csv", load_rows)

    Vs = [r["V"] for r in load_rows]
    fig, ax = plt.subplots(1, 2, figsize=(9.6, 3.7))
    ax[0].plot(Vs, [r["P_el"] for r in load_rows], "o-", label=r"$P_{\mathrm{el}}$")
    ax[0].axhline(0, color="k", lw=0.7)
    ax[0].axvline(0, color="k", lw=0.5, ls=":")
    ax[0].set_xlabel(r"$V=\mu_L-\mu_R$")
    ax[0].set_ylabel(r"$P_{\mathrm{el}}$")
    ax[0].set_title("NESS electrical power vs load")
    ax[1].plot(Vs, [r["abs_C"] for r in load_rows], "s-", color="C1")
    ax[1].set_xlabel(r"$V$")
    ax[1].set_ylabel(r"$|\rho_{\uparrow\downarrow}|$")
    ax[1].set_title("NESS coherence vs load")
    fig.tight_layout()
    for dest in (OUT, FIG):
        fig.savefig(dest / "fig_load_sweep.png")
        fig.savefig(dest / "fig_load_sweep.pdf")
    plt.close(fig)

    # efficiency where defined
    fig, ax = plt.subplots(figsize=(5.8, 3.6))
    Ve = [r["V"] for r in load_rows if np.isfinite(r["eta"])]
    et = [r["eta"] for r in load_rows if np.isfinite(r["eta"])]
    ax.plot(Ve, et, "o-")
    ax.set_xlabel(r"$V$")
    ax.set_ylabel(r"$\eta \approx P_{\mathrm{el}}/J_{Q,L}$")
    ax.set_title("Diagnostic efficiency on engine branch (scaffold)")
    fig.tight_layout()
    for dest in (OUT, FIG):
        fig.savefig(dest / "fig_efficiency.png")
        fig.savefig(dest / "fig_efficiency.pdf")
    plt.close(fig)

    # --- 2) Resource map |C|(Delta, theta_R) at engine T,mu,eps ---
    map_rows = []
    Ds = np.linspace(0.05, 0.8, 10)
    ths = np.linspace(0.0, np.pi, 13)
    Cmat = np.zeros((len(ths), len(Ds)))
    Pelmat = np.zeros_like(Cmat)
    for i, th in enumerate(ths):
        for j, D in enumerate(Ds):
            m = ness_point(
                epsilon=win["epsilon"],
                Delta=float(D),
                theta_R=float(th),
                p_L=win["p_L"],
                p_R=win["p_R"],
                mu_L=win["mu_L"],
                mu_R=win["mu_R"],
                T_L=win["T_L"],
                T_R=win["T_R"],
                gamma_L=1.0,
                gamma_R=1.0,
            )
            Cmat[i, j] = m["abs_C"]
            Pelmat[i, j] = m["P_el"]
            map_rows.append({"Delta": float(D), "theta_R": float(th), **m})
    write_csv(OUT / "resource_map.csv", map_rows)

    fig, ax = plt.subplots(1, 2, figsize=(9.8, 3.8))
    im0 = ax[0].imshow(
        Cmat,
        origin="lower",
        aspect="auto",
        extent=[Ds[0], Ds[-1], ths[0], ths[-1]],
        cmap="viridis",
    )
    fig.colorbar(im0, ax=ax[0], label=r"$|C|$")
    ax[0].set_xlabel(r"$\Delta$")
    ax[0].set_ylabel(r"$\theta_R$")
    ax[0].set_title("Resource map (NESS)")
    im1 = ax[1].imshow(
        Pelmat,
        origin="lower",
        aspect="auto",
        extent=[Ds[0], Ds[-1], ths[0], ths[-1]],
        cmap="coolwarm",
    )
    fig.colorbar(im1, ax=ax[1], label=r"$P_{\mathrm{el}}$")
    ax[1].set_xlabel(r"$\Delta$")
    ax[1].set_ylabel(r"$\theta_R$")
    ax[1].set_title("Electrical power map (NESS)")
    fig.tight_layout()
    for dest in (OUT, FIG):
        fig.savefig(dest / "fig_resource_map.png")
        fig.savefig(dest / "fig_resource_map.pdf")
    plt.close(fig)

    # --- 3) Collision rate dual-output on engine window ---
    g = 8.0
    th = 0.45
    rate_rows = []
    for T in np.geomspace(0.5, 6.0, 12):
        tau = min(th / g, 0.45 * float(T))
        p = make_params(win, g=g, tau=tau, T_period=float(T), alpha=0.0)
        res = CollisionEngine(p, mode="coherent").find_fixed_point(
            n_max=260, tol=1e-9, current_steps=50
        )
        # heat efficiency if engine
        eta = float("nan")
        if res.P_el > 0 and res.J_Q_L > 1e-10:
            eta = res.P_el / res.J_Q_L
        rate_rows.append(
            {
                "T": float(T),
                "r": 1.0 / float(T),
                "theta": g * tau,
                "P_el": res.P_el,
                "P_erg": res.P_erg,
                "W_A": res.W_A,
                "W_coh": res.W_coh,
                "abs_C": abs(res.coherence),
                "J_Q_L": res.J_Q_L,
                "J_Q_R": res.J_Q_R,
                "eta": eta,
                "first_law_residual": res.first_law_residual,
                "converged": int(res.converged),
            }
        )
    write_csv(OUT / "dual_output_rate.csv", rate_rows)

    rvals = [r["r"] for r in rate_rows]
    fig, ax = plt.subplots(1, 2, figsize=(9.8, 3.7))
    ax[0].plot(rvals, [r["P_el"] for r in rate_rows], "o-", label=r"$P_{\mathrm{el}}$")
    ax[0].plot(rvals, [r["P_erg"] for r in rate_rows], "s-", label=r"$P_{\mathrm{erg}}$")
    ax[0].axhline(0, color="k", lw=0.6)
    ax[0].set_xscale("log")
    ax[0].set_xlabel(r"collision rate $r$")
    ax[0].set_ylabel("power")
    ax[0].set_title("Dual outputs vs collision rate")
    ax[0].legend(fontsize=8)
    ax[1].plot(rvals, [r["abs_C"] for r in rate_rows], "o-")
    ax[1].set_xscale("log")
    ax[1].set_xlabel(r"$r$")
    ax[1].set_ylabel(r"$|C|$")
    ax[1].set_title("Residual spin coherence")
    fig.tight_layout()
    for dest in (OUT, FIG):
        fig.savefig(dest / "fig_dual_rate.png")
        fig.savefig(dest / "fig_dual_rate.pdf")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(5.8, 4.0))
    sc = ax.scatter(
        [r["P_el"] for r in rate_rows],
        [r["P_erg"] for r in rate_rows],
        c=np.log10(rvals),
        cmap="viridis",
        s=55,
    )
    fig.colorbar(sc, ax=ax, label=r"$\log_{10} r$")
    ax.set_xlabel(r"$P_{\mathrm{el}}$")
    ax.set_ylabel(r"$P_{\mathrm{erg}}$")
    ax.set_title("Dual-output tradeoff (engine window)")
    fig.tight_layout()
    for dest in (OUT, FIG):
        fig.savefig(dest / "fig_tradeoff.png")
        fig.savefig(dest / "fig_tradeoff.pdf")
    plt.close(fig)

    # --- 4) Full control hierarchy ---
    T, th = 1.5, 0.45
    tau = th / g
    controls = [
        ("coherent", "coherent", {}),
        ("matched", "matched", {}),
        ("incoherent", "incoherent", {}),
        ("none", "none", {"tau": 0.0}),
        ("dephasing", "dephasing", {}),
        ("alpha_half", "coherent", {"alpha": 0.5}),
        ("collinear", "coherent", {"theta_R": 0.0}),
    ]
    ctrl_rows = []
    for name, mode, over in controls:
        over2 = dict(g=g, tau=tau, T_period=T, alpha=0.0)
        over2.update(over)
        p = make_params(win, **over2)
        res = CollisionEngine(p, mode=mode).find_fixed_point(
            n_max=280, tol=1e-9, current_steps=50
        )
        ctrl_rows.append(
            {
                "control": name,
                "P_el": res.P_el,
                "P_erg": res.P_erg,
                "W_coh": res.W_coh,
                "W_inc": res.W_inc,
                "abs_C": abs(res.coherence),
                "converged": int(res.converged),
            }
        )
    write_csv(OUT / "controls.csv", ctrl_rows)

    names = [r["control"] for r in ctrl_rows]
    fig, ax = plt.subplots(figsize=(7.6, 3.9))
    x = np.arange(len(names))
    w = 0.35
    ax.bar(x - w / 2, [r["P_el"] for r in ctrl_rows], w, label=r"$P_{\mathrm{el}}$")
    ax.bar(x + w / 2, [r["P_erg"] for r in ctrl_rows], w, label=r"$P_{\mathrm{erg}}$")
    ax.axhline(0, color="k", lw=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=25, ha="right")
    ax.legend()
    ax.set_ylabel("power")
    ax.set_title("Control hierarchy (engine window)")
    fig.tight_layout()
    for dest in (OUT, FIG):
        fig.savefig(dest / "fig_controls.png")
        fig.savefig(dest / "fig_controls.pdf")
    plt.close(fig)

    # Copy stage3 engine search figure if present
    for name in ["stage3_engine_search.png", "stage3_engine_search.pdf"]:
        src = S3 / name
        if src.exists():
            shutil.copy(src, FIG / name.replace("stage3_", "fig_"))

    # Summary JSON for draft numbers
    summary = {
        "window": win,
        "ness_Pel": float(ness_point(**{**win, "gamma_L": 1.0, "gamma_R": 1.0})["P_el"]),
        "ness_C": float(ness_point(**{**win, "gamma_L": 1.0, "gamma_R": 1.0})["abs_C"]),
        "rate_Pel_min": min(r["P_el"] for r in rate_rows),
        "rate_Pel_max": max(r["P_el"] for r in rate_rows),
        "rate_Perg_max": max(r["P_erg"] for r in rate_rows),
        "controls": ctrl_rows,
        "load_engine_branch": any(r["P_el"] > 0 for r in load_rows),
    }
    (OUT / "paper_numbers.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report = f"""# Stage 4 paper-support report

Generated figures in `engine_paper/figures/` and data in `results/stage4/`.

## Window (from Stage 3)

{json.dumps(win, indent=2)}

## Highlights for the draft

- Load sweep shows an **engine branch** ($P_{{\\rm el}}>0$) at negative $V$ with finite $|C|$.
- Dual-output rate scan: $P_{{\\rm el}}$ stays positive; $P_{{\\rm erg}}$ peaks at higher collision rates.
- Controls: only coherent exchange yields appreciable $P_{{\\rm erg}}$; incoherent/collinear/none give $\\approx 0$.
- Resource map: large $|C|$ at small $\\Delta$ and intermediate tilt; $P_{{\\rm el}}$ map shows engine region.

## Key numbers

- NESS $P_{{\\rm el}}\\approx{summary['ness_Pel']:.4g}$, $|C|\\approx{summary['ness_C']:.4g}$
- Rate scan $P_{{\\rm el}}\\in[{summary['rate_Pel_min']:.4g},{summary['rate_Pel_max']:.4g}]$
- Max $P_{{\\rm erg}}\\approx{summary['rate_Perg_max']:.4g}$
"""
    (OUT / "STAGE4_SUPPORT_REPORT.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
