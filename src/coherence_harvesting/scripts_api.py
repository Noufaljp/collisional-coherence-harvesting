"""High-level demos and figure generation."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from coherence_harvesting.companion.power import (
    CompanionParams,
    impedance_matched_r,
    optimize_power,
    power_curve,
    small_angle_bound,
    plateau_C,
)
from coherence_harvesting.transport.engine import CollisionEngine
from coherence_harvesting.transport.spin_valve import SpinValveParams


def _setup_style() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 140,
            "font.size": 11,
            "axes.grid": True,
            "grid.alpha": 0.3,
        }
    )


def companion_demo(outdir: Path) -> None:
    _setup_style()
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    params = CompanionParams(
        gamma_C=1.0,
        gamma_d=1.0,
        c0=0.25,
        s_ss=0.5,
        Delta=0.15,
        theta=0.35,
        alpha=0.0,
    )
    r, P = power_curve(params, exact=True)
    r_opt, P_max = optimize_power(params, exact=True)
    r_imp = impedance_matched_r(
        params.gamma_C, params.theta, params.Delta / params.gamma_C
    )
    bound = small_angle_bound(
        params.gamma_C,
        params.Delta,
        params.c0,
        z_A=1.0,
        delta_over_gamma=params.Delta / params.gamma_C,
    )

    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    ax.plot(r / params.gamma_C, P, lw=2, label=r"$P_{\mathrm{erg}}(r)$")
    ax.axvline(r_opt / params.gamma_C, color="C1", ls="--", label=f"opt r={r_opt:.3g}")
    ax.axvline(r_imp / params.gamma_C, color="C2", ls=":", label="impedance match")
    ax.axhline(bound, color="C3", ls="-.", label="small-angle bound (approx)")
    ax.set_xscale("log")
    ax.set_xlabel(r"$r / \gamma_C$")
    ax.set_ylabel(r"$P_{\mathrm{erg}}$")
    ax.set_title("Companion model: charging power vs collision rate")
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(outdir / "companion_power_curve.png")
    plt.close(fig)

    # plateau vs theta
    thetas = np.linspace(0.05, 1.2, 18)
    Cvals = [plateau_C(float(th)) for th in thetas]
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    ax.plot(thetas, Cvals, "o-", label="numerical")
    ax.axhline(0.5, color="k", ls="--", label=r"$1/2$ plateau")
    ax.set_xlabel(r"$\theta = g\tau$")
    ax.set_ylabel(r"$\mathcal{C}(\theta)$")
    ax.set_title("Harvesting plateau vs exchange angle")
    ax.legend()
    fig.tight_layout()
    fig.savefig(outdir / "companion_plateau.png")
    plt.close(fig)

    # finite-phase suppression
    deltas = np.linspace(0.0, 5.0, 40)
    bounds = [
        small_angle_bound(1.0, 0.2, 0.25, 1.0, d) for d in deltas
    ]
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    ax.plot(deltas, bounds, lw=2)
    ax.set_xlabel(r"$\delta = \Delta/\gamma_C$")
    ax.set_ylabel(r"$P_{\mathrm{erg}}^{\max}$ (scaled)")
    ax.set_title("Finite-gap phase suppression")
    fig.tight_layout()
    fig.savefig(outdir / "companion_finite_phase.png")
    plt.close(fig)

    print("Companion demo complete.")
    print(f"  r_opt = {r_opt:.6g}, P_max = {P_max:.6g}")
    print(f"  impedance-matched r = {r_imp:.6g}")
    print(f"  figures → {outdir.resolve()}")


def transport_demo(outdir: Path) -> None:
    _setup_style()
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    base = SpinValveParams(
        epsilon=0.0,
        Delta=0.3,
        gamma_L=1.0,
        gamma_R=1.0,
        p_L=0.7,
        p_R=0.7,
        theta_R=np.pi / 2,
        T_L=1.2,
        T_R=0.6,
        mu_L=0.4,
        mu_R=-0.4,
        g=8.0,
        tau=0.08,
        T_period=1.5,
        alpha=0.0,
    )

    # Scan collision period (rate)
    periods = np.geomspace(0.4, 8.0, 12)
    P_el, P_erg, coh = [], [], []
    for T in periods:
        p = SpinValveParams(**{**base.__dict__, "T_period": float(T)})
        eng = CollisionEngine(p)
        res = eng.find_fixed_point(n_max=250, tol=1e-9)
        P_el.append(res.P_el)
        P_erg.append(res.P_erg)
        coh.append(abs(res.coherence))
        print(
            f"T={T:.3g}: converged={res.converged} n={res.n_iter} "
            f"P_el={res.P_el:.4g} P_erg={res.P_erg:.4g} |C|={abs(res.coherence):.4g}"
        )

    r = 1.0 / periods
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    ax.plot(r, P_el, "o-", label=r"$P_{\mathrm{el}}$")
    ax.plot(r, P_erg, "s-", label=r"$P_{\mathrm{erg}}$")
    ax.set_xscale("log")
    ax.set_xlabel(r"collision rate $r=1/T$")
    ax.set_ylabel("power")
    ax.set_title("Spin-valve engine: power channels vs collision rate")
    ax.legend()
    fig.tight_layout()
    fig.savefig(outdir / "transport_power_vs_rate.png")
    plt.close(fig)

    # Pareto-like scatter over theta_R
    thetas = np.linspace(0.0, np.pi, 9)
    pe, pr = [], []
    for th in thetas:
        p = SpinValveParams(**{**base.__dict__, "theta_R": float(th)})
        res = CollisionEngine(p).find_fixed_point(n_max=200)
        pe.append(res.P_el)
        pr.append(res.P_erg)

    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    sc = ax.scatter(pe, pr, c=thetas, cmap="viridis", s=60)
    fig.colorbar(sc, ax=ax, label=r"$\theta_R$")
    ax.set_xlabel(r"$P_{\mathrm{el}}$")
    ax.set_ylabel(r"$P_{\mathrm{erg}}$")
    ax.set_title(r"Tradeoff scan over right-lead tilt $\theta_R$")
    fig.tight_layout()
    fig.savefig(outdir / "transport_pareto_thetaR.png")
    plt.close(fig)

    # Dephasing control vs collisions
    res_col = CollisionEngine(base).find_fixed_point()
    res_deph = CollisionEngine(base).dephasing_control_fixed_point()
    fig, ax = plt.subplots(figsize=(5.5, 3.8))
    ax.bar(
        ["collisions", "dephasing only"],
        [res_col.P_el, res_deph.P_el],
        color=["C0", "C1"],
    )
    ax.set_ylabel(r"$P_{\mathrm{el}}$")
    ax.set_title("Control: collisions vs pure dephasing")
    fig.tight_layout()
    fig.savefig(outdir / "transport_dephasing_control.png")
    plt.close(fig)

    print("Transport demo complete.")
    print(f"  figures → {outdir.resolve()}")


def generate_all_figures(outdir: Path) -> None:
    companion_demo(outdir)
    transport_demo(outdir)
    print("All figures generated.")
