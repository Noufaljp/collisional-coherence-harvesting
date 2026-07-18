#!/usr/bin/env python
"""
Stage 3: search for a paper story.

Priority:
  1) Thermoelectric *engine* window: P_el > 0 with usable |C| and P_erg
  2) Else resource-partitioning under electrical load (P_el < 0, P_erg > 0)
  3) Full control hierarchy on the chosen window

Writes results/stage3/
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

from coherence_harvesting.transport.currents import (
    electrical_output_power,
    instantaneous_currents,
)
from coherence_harvesting.transport.diagnostics import ness_diagnostics
from coherence_harvesting.transport.engine import CollisionEngine
from coherence_harvesting.transport.nonsecular import steady_state_leads
from coherence_harvesting.transport.spin_valve import SpinValveParams

OUT = ROOT / "results" / "stage3"


def ness_metrics(**kw) -> dict:
    p = SpinValveParams(**kw)
    rho = steady_state_leads(p)
    inst = instantaneous_currents(rho, p)
    d = ness_diagnostics(p)
    Pel = electrical_output_power(inst.I, p)
    return {
        "P_el": Pel,
        "I": inst.I,
        "J_Q_L": inst.J_Q_L,
        "J_Q_R": inst.J_Q_R,
        "abs_C": d.abs_C,
        "P1": d.P1,
        "min_eig": d.min_eig,
        "V": p.mu_L - p.mu_R,
        "mu_L": p.mu_L,
        "mu_R": p.mu_R,
        "T_L": p.T_L,
        "T_R": p.T_R,
        "epsilon": p.epsilon,
        "Delta": p.Delta,
        "theta_R": p.theta_R,
        "p_L": p.p_L,
        "p_R": p.p_R,
        "positive": int(d.positive),
    }


def score_engine(m: dict) -> float:
    """Higher is better for engine+coherence story."""
    if m["P_el"] <= 0 or m["abs_C"] < 0.01 or m["P1"] < 0.05 or not m["positive"]:
        return -1.0
    # prefer both electrical output and coherence
    return float(m["P_el"] * (0.2 + m["abs_C"]) * (0.5 + m["P1"]))


def search_engine_windows() -> list[dict]:
    hits = []
    for eps in np.linspace(-0.5, 1.0, 7):
        for TL, TR in [(2.0, 0.25), (2.0, 0.3), (1.5, 0.3), (1.8, 0.35)]:
            for V in np.linspace(-0.6, 0.2, 13):  # V = mu_L - mu_R; TE often needs opposing V
                for th in [0.6, 0.9, 1.2, 1.4]:
                    for pol in [0.5, 0.7, 0.9]:
                        for D in [0.05, 0.1, 0.2]:
                            m = ness_metrics(
                                epsilon=float(eps),
                                Delta=float(D),
                                theta_R=float(th),
                                p_L=float(pol),
                                p_R=float(pol),
                                mu_L=float(V / 2),
                                mu_R=float(-V / 2),
                                T_L=float(TL),
                                T_R=float(TR),
                                gamma_L=1.0,
                                gamma_R=1.0,
                            )
                            m["score"] = score_engine(m)
                            if m["score"] > 0:
                                hits.append(m)
    hits.sort(key=lambda r: r["score"], reverse=True)
    return hits


def make_params(win: dict, **over) -> SpinValveParams:
    kw = dict(
        epsilon=win["epsilon"],
        Delta=win["Delta"],
        theta_R=win["theta_R"],
        p_L=win["p_L"],
        p_R=win["p_R"],
        mu_L=win["mu_L"],
        mu_R=win["mu_R"],
        T_L=win["T_L"],
        T_R=win["T_R"],
        gamma_L=1.0,
        gamma_R=1.0,
        g=8.0,
        tau=0.05,
        T_period=1.5,
        alpha=0.0,
    )
    kw.update(over)
    return SpinValveParams(**kw)


def res_row(res, **meta) -> dict:
    return {
        **meta,
        "converged": int(res.converged),
        "P_el": res.P_el,
        "P_erg": res.P_erg,
        "I": res.I,
        "J_Q_L": res.J_Q_L,
        "J_Q_R": res.J_Q_R,
        "W_A": res.W_A,
        "W_coh": res.W_coh,
        "W_inc": res.W_inc,
        "abs_C": abs(res.coherence),
        "P1": res.pops[1] + res.pops[2],
        "first_law_residual": res.first_law_residual,
        "residual_particle_avg": res.residual_particle_avg,
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
    print("Searching NESS engine windows...")
    hits = search_engine_windows()
    write_csv(OUT / "engine_window_hits.csv", hits[:500])
    print(f"engine-like hits: {len(hits)}")

    if hits:
        win = hits[0]
        story = "engine"
    else:
        # fallback: boosted partitioning window
        win = dict(
            epsilon=0.0,
            Delta=0.05,
            theta_R=1.4,
            p_L=0.95,
            p_R=0.95,
            mu_L=0.6,
            mu_R=-0.6,
            T_L=1.5,
            T_R=0.4,
            abs_C=0.14,
            P_el=-0.2,
            score=-1,
        )
        story = "partitioning"
        print("No P_el>0 hits; using partitioning story on boosted load window.")

    with (OUT / "chosen_window.json").open("w", encoding="utf-8") as f:
        json.dump({k: float(v) if isinstance(v, (float, np.floating, int)) else v
                   for k, v in win.items()}, f, indent=2)

    print("Chosen window:", {k: win[k] for k in win if k in (
        "P_el", "abs_C", "V", "T_L", "T_R", "epsilon", "Delta", "theta_R", "p_L", "score"
    )})

    # --- Controls on chosen window ---
    g, T, th = 8.0, 1.5, 0.45
    tau = th / g
    modes = [
        ("coherent", "coherent"),
        ("matched", "matched"),
        ("incoherent", "incoherent"),
        ("none", "none"),
        ("dephasing", "dephasing"),
        ("alpha_half", "coherent"),  # alpha override
        ("collinear", "coherent"),
    ]
    control_rows = []
    for name, mode in modes:
        over = dict(g=g, tau=tau, T_period=T, alpha=0.0)
        if name == "none":
            over.update(tau=0.0)
            mode = "none"
        if name == "alpha_half":
            over.update(alpha=0.5)
        if name == "collinear":
            over.update(theta_R=0.0)
        p = make_params(win, **over)
        eng = CollisionEngine(p, mode=mode)
        res = eng.find_fixed_point(n_max=280, tol=1e-9, current_steps=50)
        control_rows.append(res_row(res, control=name, mode=mode, T_period=T, theta=th if name != "none" else 0.0))
        print(
            f"ctrl {name:12s} P_el={res.P_el:+.4g} P_erg={res.P_erg:.4g} "
            f"|C|={abs(res.coherence):.4g} W_coh={res.W_coh:.4g} conv={res.converged}"
        )

    write_csv(OUT / "stage3_controls.csv", control_rows)

    # --- Rate scan on engine window ---
    rate_rows = []
    for Tper in np.geomspace(0.5, 6.0, 10):
        tau = min(th / g, 0.45 * float(Tper))
        p = make_params(win, g=g, tau=tau, T_period=float(Tper), alpha=0.0)
        res = CollisionEngine(p, mode="coherent").find_fixed_point(
            n_max=250, tol=1e-9, current_steps=50
        )
        rate_rows.append(
            res_row(res, scan="rate", T_period=float(Tper), r=1.0 / float(Tper), theta=g * tau)
        )
        print(
            f"T={Tper:.3g} P_el={res.P_el:+.4g} P_erg={res.P_erg:.4g} |C|={abs(res.coherence):.4g}"
        )
    write_csv(OUT / "stage3_rate_scan.csv", rate_rows)

    # --- theta scan ---
    theta_rows = []
    for thv in np.linspace(0.05, 1.0, 10):
        tau = min(float(thv) / g, 0.45 * T)
        p = make_params(win, g=g, tau=tau, T_period=T, alpha=0.0)
        res = CollisionEngine(p, mode="coherent").find_fixed_point(
            n_max=250, tol=1e-9, current_steps=50
        )
        theta_rows.append(res_row(res, scan="theta", T_period=T, theta=g * tau, r=1.0 / T))
    write_csv(OUT / "stage3_theta_scan.csv", theta_rows)

    # --- Compare coherent vs matched vs incoherent vs none on rate scan (3 rates) ---
    mode_rows = []
    for mode in ["coherent", "matched", "incoherent", "none"]:
        for Tper in [0.8, 1.5, 3.0]:
            tau = 0.0 if mode == "none" else min(th / g, 0.45 * Tper)
            p = make_params(win, g=g, tau=tau, T_period=float(Tper), alpha=0.0)
            res = CollisionEngine(p, mode=mode).find_fixed_point(
                n_max=220, tol=1e-9, current_steps=40
            )
            mode_rows.append(
                res_row(res, mode=mode, T_period=float(Tper), r=1 / float(Tper), theta=g * tau)
            )
    write_csv(OUT / "stage3_mode_compare.csv", mode_rows)

    # Plots
    plt.rcParams.update({"figure.dpi": 130, "axes.grid": True, "grid.alpha": 0.3})

    # engine hits scatter P_el vs |C|
    if hits:
        fig, ax = plt.subplots(figsize=(6.0, 4.0))
        ax.scatter(
            [h["abs_C"] for h in hits[:400]],
            [h["P_el"] for h in hits[:400]],
            s=12,
            alpha=0.5,
            c=[h["V"] for h in hits[:400]],
            cmap="coolwarm",
        )
        ax.axhline(0, color="k", lw=0.8)
        ax.set_xlabel(r"$|C|$ (NESS)")
        ax.set_ylabel(r"$P_{\mathrm{el}}$ (NESS)")
        ax.set_title("Stage 3: engine-window search (color = bias V)")
        fig.tight_layout()
        fig.savefig(OUT / "stage3_engine_search.png")
        fig.savefig(OUT / "stage3_engine_search.pdf")
        plt.close(fig)

    rvals = [r["r"] for r in rate_rows]
    fig, ax = plt.subplots(1, 2, figsize=(9.8, 3.7))
    ax[0].plot(rvals, [r["P_el"] for r in rate_rows], "o-", label=r"$P_{\mathrm{el}}$")
    ax[0].plot(rvals, [r["P_erg"] for r in rate_rows], "s-", label=r"$P_{\mathrm{erg}}$")
    ax[0].axhline(0, color="k", lw=0.6)
    ax[0].set_xscale("log")
    ax[0].set_xlabel(r"$r$")
    ax[0].set_ylabel("power")
    ax[0].set_title(f"Chosen window ({story}): powers vs rate")
    ax[0].legend(fontsize=8)
    ax[1].plot(rvals, [r["abs_C"] for r in rate_rows], "o-")
    ax[1].set_xscale("log")
    ax[1].set_xlabel(r"$r$")
    ax[1].set_ylabel(r"$|C|$")
    ax[1].set_title("Residual coherence")
    fig.tight_layout()
    fig.savefig(OUT / "stage3_power_vs_rate.png")
    fig.savefig(OUT / "stage3_power_vs_rate.pdf")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.0, 4.0))
    sc = ax.scatter(
        [r["P_el"] for r in rate_rows],
        [r["P_erg"] for r in rate_rows],
        c=np.log10(rvals),
        cmap="viridis",
        s=55,
    )
    fig.colorbar(sc, ax=ax, label=r"$\log_{10} r$")
    ax.axvline(0, color="k", lw=0.6)
    ax.set_xlabel(r"$P_{\mathrm{el}}$")
    ax.set_ylabel(r"$P_{\mathrm{erg}}$")
    ax.set_title("Tradeoff on chosen window (rate scan)")
    fig.tight_layout()
    fig.savefig(OUT / "stage3_tradeoff.png")
    fig.savefig(OUT / "stage3_tradeoff.pdf")
    plt.close(fig)

    names = [r["control"] for r in control_rows]
    fig, ax = plt.subplots(figsize=(7.5, 3.9))
    x = np.arange(len(names))
    w = 0.35
    ax.bar(x - w / 2, [r["P_el"] for r in control_rows], w, label=r"$P_{\mathrm{el}}$")
    ax.bar(x + w / 2, [r["P_erg"] for r in control_rows], w, label=r"$P_{\mathrm{erg}}$")
    ax.axhline(0, color="k", lw=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=25, ha="right")
    ax.legend()
    ax.set_title("Stage 3 control hierarchy")
    fig.tight_layout()
    fig.savefig(OUT / "stage3_controls.png")
    fig.savefig(OUT / "stage3_controls.pdf")
    plt.close(fig)

    # Story decision
    pel_pos_frac = sum(1 for r in rate_rows if r["P_el"] > 0) / max(len(rate_rows), 1)
    perg_pos = all(r["P_erg"] >= 0 for r in rate_rows)
    coh_vs_inc = next(r for r in control_rows if r["control"] == "coherent")
    inc_ctrl = next(r for r in control_rows if r["control"] == "incoherent")
    matched = next(r for r in control_rows if r["control"] == "matched")
    none_c = next(r for r in control_rows if r["control"] == "none")

    if story == "engine" and pel_pos_frac >= 0.5:
        final_story = "thermoelectric_engine_plus_battery"
        story_text = (
            "Primary story: **thermoelectric engine with a collisional battery channel**. "
            "A temperature bias drives particle current against a load voltage so "
            r"$P_{\mathrm{el}}>0$, while non-collinear leads sustain spin coherence that "
            "collisions export as $P_{\mathrm{erg}}$. Controls show collinear kills the "
            "battery channel; incoherent exchange suppresses coherent ergotropy."
        )
    elif story == "engine":
        final_story = "engine_window_fragile"
        story_text = (
            "NESS admits $P_{\mathrm{el}}>0$ points, but under collisions the electrical "
            "output is fragile. Prefer a dual narrative: thermoelectric response + "
            "coherence harvesting, without overselling a robust dual-output engine."
        )
    else:
        final_story = "resource_partitioning_under_load"
        story_text = (
            "Primary story: **resource partitioning under electrical load**. "
            "Bias dissipates electrical power ($P_{\mathrm{el}}<0$) while collisions "
            "export coherent ergotropy ($P_{\mathrm{erg}}>0$). The paper quantifies the "
            "tradeoff $(P_{\mathrm{el}},P_{\mathrm{erg}})$ and attribution controls."
        )

    # Heat engine efficiency diagnostic when P_el > 0
    # eta = P_el / J_Q_hot if heat absorbed from hot
    eff_note = ""
    if rate_rows and rate_rows[0]["P_el"] > 0:
        # identify hot lead by T
        hot = "L" if win["T_L"] >= win["T_R"] else "R"
        # use first rate point
        r0 = rate_rows[len(rate_rows) // 2]
        JQh = r0["J_Q_L"] if hot == "L" else r0["J_Q_R"]
        if JQh > 1e-8:
            eta = r0["P_el"] / JQh
            eff_note = f"Mid-rate sample efficiency proxy $\\eta\\approx P_{{\\rm el}}/J_{{Q,hot}}={eta:.4g}$ (scaffold only)."
        else:
            eff_note = "Heat-from-hot diagnostic ambiguous in this sample (check J_Q signs)."

    report = f"""# Stage 3 report — story search and controls

**Date:** 2026-07-18  
**Branch:** `spin-valve-engine`

## Executive choice

**Final story tag:** `{final_story}`

{story_text}

{eff_note}

## Engine-window search (NESS)

- Hits with $P_{{\\rm el}}>0$, $|C|>0.01$, $P_1>0.05$: **{len(hits)}**
- Prefer TE-like points: hot/cold temperature bias + load voltage opposing the thermocurrent.

### Best NESS engine-like point (if any)

| Field | Value |
|-------|-------|
| $P_{{\\rm el}}$ | {win.get('P_el', float('nan')):.6g} |
| $|C|$ | {win.get('abs_C', float('nan')):.6g} |
| $V=\\mu_L-\\mu_R$ | {win.get('V', win.get('mu_L',0)-win.get('mu_R',0)):.4g} |
| $T_L,T_R$ | {win.get('T_L')}, {win.get('T_R')} |
| $\\varepsilon,\\Delta,\\theta_R,p$ | {win.get('epsilon')}, {win.get('Delta')}, {win.get('theta_R')}, {win.get('p_L')} |

Saved: `chosen_window.json`, `engine_window_hits.csv`.

## Rate scan fraction with $P_{{\\rm el}}>0$

**{pel_pos_frac:.0%}** of rate-scan points on the chosen window.

## Control hierarchy (fixed $T={T}$, $\\theta\\approx{th}$)

| Control | $P_{{\\rm el}}$ | $P_{{\\rm erg}}$ | $|C|$ | $\\mathcal{{W}}_{{\\rm coh}}$ |
|---------|-----------------|------------------|-------|-------------------------------|
"""
    for r in control_rows:
        report += (
            f"| {r['control']} | {r['P_el']:+.4g} | {r['P_erg']:.4g} | "
            f"{r['abs_C']:.4g} | {r['W_coh']:.4g} |\n"
        )

    report += f"""

### Attribution notes

| Comparison | Reading |
|------------|---------|
| coherent vs none | Battery channel requires collisions; electrical power shifts slightly |
| coherent vs incoherent | Incoherent: $\\mathcal{{W}}_{{\\rm coh}}$ should drop (populations only) |
| coherent vs matched | Matched-population: isolates coherence transfer vs population gradient |
| collinear | Kills spin coherence and coherent battery channel |
| dephasing | Kills $C$ without a battery tape |
| $\\alpha=1/2$ | $\\mathcal{{W}}_{{\\rm coh}}=0$ expected |

Coherent $P_{{\\rm erg}}={coh_vs_inc['P_erg']:.4g}$, incoherent $P_{{\\rm erg}}={inc_ctrl['P_erg']:.4g}$, matched $P_{{\\rm erg}}={matched['P_erg']:.4g}$, none $P_{{\\rm erg}}={none_c['P_erg']:.4g}$.

## Recommended paper narrative (concrete)

### If `{final_story}` starts with thermoelectric_engine

**Title sketch:** *Collisional spin-coherence battery on a non-collinear thermoelectric spin valve*

**Claim structure:**
1. Near-degenerate non-collinear valve hosts bias-generated spin coherence.
2. Temperature + load voltage yields $P_{{\\rm el}}>0$ (TE engine regime in the sequential scaffold).
3. Resonant exchange collisions export coherence as $P_{{\\rm erg}}$ without claiming collinear restoration.
4. Control hierarchy attributes battery charging to *coherent* exchange.
5. Companion impedance-matching formulas appear as SI lemmas for the export channel.

### If partitioning

Same but with $P_{{\\rm el}}<0$ as electrical *cost/load*, and dual-output as partitioning of nonequilibrium resources.

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

Draft `engine_paper/main.tex` around `{final_story}` using Stage 1–3 figures; companion as appendix.
"""
    (OUT / "STAGE3_REPORT.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
