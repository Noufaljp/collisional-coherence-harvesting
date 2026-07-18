"""High-level demos and figure generation."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from coherence_harvesting.companion.collision import (
    SystemState,
    analytic_system_map,
    numerical_collision,
    random_valid_doublet_state,
)
from coherence_harvesting.companion.power import (
    CompanionParams,
    ancilla_diagnostics,
    finite_coupling_theta_min,
    fixed_point_state,
    impedance_matched_r,
    numerical_finite_phase_optimum,
    optimize_power,
    plateau_C,
    power_curve,
    power_curve_directed,
    small_angle_bound,
)
from coherence_harvesting.companion.baths import reset_fixed_point_C
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
    """Generate companion-paper figures (publication-oriented set)."""
    _setup_style()
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    data_dir = outdir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    params = CompanionParams(
        gamma_C=1.0,
        gamma_d=1.0,
        c0=0.25,
        s_ss=0.5,
        Delta=0.15,
        theta=0.35,
        alpha=0.0,
    )

    # --- Power curve: exact vs weak ---
    r, P_ex = power_curve(params, exact=True)
    _, P_wk = power_curve(params, r_values=r, exact=False)
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
    np.savez(
        data_dir / "companion_power_curve.npz",
        r=r,
        P_exact=P_ex,
        P_weak=P_wk,
        r_opt=r_opt,
        r_imp=r_imp,
        bound=bound,
    )

    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    ax.plot(r / params.gamma_C, P_ex, lw=2, label="exact ergotropy")
    ax.plot(r / params.gamma_C, P_wk, lw=1.8, ls="--", label="weak extraction")
    ax.axvline(r_opt / params.gamma_C, color="C2", ls="--", label=f"opt r={r_opt:.3g}")
    ax.axvline(r_imp / params.gamma_C, color="C3", ls=":", label="impedance match")
    ax.axhline(bound, color="C4", ls="-.", label="small-angle bound")
    ax.set_xscale("log")
    ax.set_xlabel(r"$r / \gamma_C$")
    ax.set_ylabel(r"$P_{\mathrm{erg}}$")
    ax.set_title("Companion: charging power (exact vs weak)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(outdir / "companion_power_curve.png")
    fig.savefig(outdir / "companion_power_curve.pdf")
    plt.close(fig)

    # --- Fixed-point |C*|/c0 vs r for several theta ---
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    for th in [0.15, 0.35, 0.7, 1.0]:
        p = CompanionParams(
            gamma_C=1.0,
            gamma_d=1.0,
            c0=0.25,
            s_ss=0.5,
            Delta=0.0,  # phi=0 for clean coherence plot; use tiny Delta via validate off
            theta=th,
            alpha=0.0,
            validate=False,
        )
        # Delta=0 is allowed for coherence-only diagnostic
        rr = np.geomspace(1e-2, 100, 100)
        Cabs = []
        for rv in rr:
            C = reset_fixed_point_C(0.25, th, 1.0, float(rv), delta=0.0)
            Cabs.append(abs(C) / 0.25)
        ax.plot(rr, Cabs, label=rf"$\theta={th}$")
    ax.set_xscale("log")
    ax.set_xlabel(r"$r / \gamma_C$")
    ax.set_ylabel(r"$|C^*|/c_0$")
    ax.set_title("Fixed-point coherence vs collision rate")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(outdir / "companion_Cstar_vs_r.png")
    fig.savefig(outdir / "companion_Cstar_vs_r.pdf")
    plt.close(fig)

    # --- Impedance-matching collapse ---
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    for th in [0.2, 0.4, 0.6, 0.9]:
        p = CompanionParams(
            gamma_C=1.0, c0=0.25, s_ss=0.5, Delta=0.1, theta=th, alpha=0.0
        )
        rr, PP = power_curve(p, exact=True)
        Gamma_ext = rr * (1.0 - np.cos(th))
        ax.plot(Gamma_ext / p.gamma_C, PP / np.max(PP), label=rf"$\theta={th}$")
    ax.axvline(1.0, color="k", ls="--", label=r"$\Gamma_{\mathrm{ext}}=\gamma_C$")
    ax.set_xscale("log")
    ax.set_xlabel(r"$\Gamma_{\mathrm{ext}} / \gamma_C = r(1-\cos\theta)/\gamma_C$")
    ax.set_ylabel(r"$P_{\mathrm{erg}} / P_{\max}$")
    ax.set_title("Impedance-matching data collapse")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(outdir / "companion_impedance_collapse.png")
    fig.savefig(outdir / "companion_impedance_collapse.pdf")
    plt.close(fig)

    # --- Plateau + realizability bound ---
    thetas = np.linspace(0.05, 1.2, 20)
    Cvals = [plateau_C(float(th)) for th in thetas]
    g = 10.0
    th_min = finite_coupling_theta_min(1.0, g, params.Delta / params.gamma_C)
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    ax.plot(thetas, Cvals, "o-", label="numerical plateau")
    ax.axhline(0.5, color="k", ls="--", label=r"$1/2$")
    ax.axvline(th_min, color="C3", ls=":", label=rf"$\theta_{{\min}}(g={g:g})$")
    ax.set_xlabel(r"$\theta = g\tau$")
    ax.set_ylabel(r"$\mathcal{C}(\theta)$")
    ax.set_title("Harvesting plateau and finite-coupling bound")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(outdir / "companion_plateau.png")
    fig.savefig(outdir / "companion_plateau.pdf")
    plt.close(fig)

    # --- Finite-phase: analytic vs numeric r_opt ---
    deltas, r_num, r_an = numerical_finite_phase_optimum(params)
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    ax.plot(deltas, r_an, lw=2, label="analytic small-angle")
    ax.plot(deltas, r_num, "o", label="numerical exact")
    ax.set_xlabel(r"$\delta = \Delta/\gamma_C$")
    ax.set_ylabel(r"$r_{\mathrm{opt}} / \gamma_C$")
    ax.set_title("Finite-phase optimum: analytic vs numeric")
    ax.legend()
    fig.tight_layout()
    fig.savefig(outdir / "companion_finite_phase.png")
    fig.savefig(outdir / "companion_finite_phase.pdf")
    plt.close(fig)
    # also bound suppression
    bounds = [
        small_angle_bound(1.0, max(d * 1.0, 1e-9), 0.25, 1.0, d) for d in deltas
    ]
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    ax.plot(deltas, bounds, lw=2)
    ax.set_xlabel(r"$\delta = \Delta/\gamma_C$")
    ax.set_ylabel(r"$P_{\mathrm{erg}}^{\max}$ (small-angle law)")
    ax.set_title("Finite-gap phase suppression of power bound")
    fig.tight_layout()
    fig.savefig(outdir / "companion_finite_phase_bound.png")
    fig.savefig(outdir / "companion_finite_phase_bound.pdf")
    plt.close(fig)

    # --- Reset vs directed leakage ---
    # Match free targets: s_ss = Gu/(Gu+Gd), c0 = s_ss/2
    Gu, Gd = 0.5, 0.5  # s_ss=0.5, c0=0.25
    kappa_D = 1.0
    rr = np.geomspace(0.05, 50, 60)
    p_reset = CompanionParams(
        gamma_C=1.0, gamma_d=1.0, c0=0.25, s_ss=0.5, Delta=0.15, theta=0.35, alpha=0.0
    )
    _, P_reset = power_curve(p_reset, r_values=rr, exact=True)
    _, P_leak = power_curve_directed(
        Gu, Gd, kappa_D, theta=0.35, Delta=0.15, r_values=rr, exact=True
    )
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    ax.plot(rr, P_reset, lw=2, label="phase-locked reset")
    ax.plot(rr, P_leak, lw=2, ls="--", label=rf"directed leakage $\kappa_D={kappa_D}$")
    ax.set_xscale("log")
    ax.set_xlabel(r"$r$")
    ax.set_ylabel(r"$P_{\mathrm{erg}}$")
    ax.set_title("Reset bath vs directed dark leakage")
    ax.legend()
    fig.tight_layout()
    fig.savefig(outdir / "companion_reset_vs_leakage.png")
    fig.savefig(outdir / "companion_reset_vs_leakage.pdf")
    plt.close(fig)

    # --- Accessibility: total / coh / two-copy along power curve ---
    Wtot, Wcoh, Wacc2 = [], [], []
    for rv in r:
        s, d, C = fixed_point_state(params, float(rv))
        diag = ancilla_diagnostics(s, d, C, params.theta, params.alpha, params.Delta)
        Wtot.append(diag["W_total"])
        Wcoh.append(diag["W_coh"])
        Wacc2.append(diag["W_acc2"])
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    ax.plot(r / params.gamma_C, Wtot, label=r"$\mathcal{W}_{\mathrm{total}}$")
    ax.plot(r / params.gamma_C, Wcoh, label=r"$\mathcal{W}_{\mathrm{coh}}$")
    ax.plot(r / params.gamma_C, Wacc2, label=r"$\mathcal{W}_{\mathrm{acc}}^{(2)}$")
    ax.set_xscale("log")
    ax.set_xlabel(r"$r / \gamma_C$")
    ax.set_ylabel("work capacity per ancilla")
    ax.set_title("Total / coherent / two-copy accessible ergotropy")
    ax.legend()
    fig.tight_layout()
    fig.savefig(outdir / "companion_accessibility.png")
    fig.savefig(outdir / "companion_accessibility.pdf")
    plt.close(fig)

    # --- Collision-map validation (analytic vs numeric error) ---
    rng = np.random.default_rng(0)
    errs = []
    for _ in range(200):
        st = random_valid_doublet_state(rng)
        th = float(rng.uniform(0.05, 1.2))
        al = float(rng.uniform(0.0, 1.0))
        s2, d2, C2 = analytic_system_map(st.s, st.d, st.C, th, al)
        rho_S, _ = numerical_collision(st.rho(), al, th)
        stn = SystemState.from_rho(rho_S)
        e = abs(stn.s - s2) + abs(stn.d - d2) + abs(stn.C - C2)
        errs.append(e)
    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    ax.hist(np.log10(np.maximum(errs, 1e-18)), bins=30, color="C0", alpha=0.85)
    ax.set_xlabel(r"$\log_{10}$ map error (analytic vs unitary)")
    ax.set_ylabel("count")
    ax.set_title("Collision-map validation")
    fig.tight_layout()
    fig.savefig(outdir / "companion_collision_validation.png")
    fig.savefig(outdir / "companion_collision_validation.pdf")
    plt.close(fig)

    print("Companion demo complete.")
    print(f"  r_opt = {r_opt:.6g}, P_max = {P_max:.6g}")
    print(f"  impedance-matched r = {r_imp:.6g}")
    print(f"  figures -> {outdir.resolve()}")


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
    ax.plot(r, P_el, "o-", label=r"$P_{\mathrm{el}}$ (proxy)")
    ax.plot(r, P_erg, "s-", label=r"$P_{\mathrm{erg}}$")
    ax.set_xscale("log")
    ax.set_xlabel(r"collision rate $r=1/T$")
    ax.set_ylabel("power")
    ax.set_title("Spin-valve engine: power channels vs collision rate")
    ax.legend()
    fig.tight_layout()
    fig.savefig(outdir / "transport_power_vs_rate.png")
    plt.close(fig)

    # Tilt-angle parametric scan (not a true Pareto frontier)
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
    ax.set_xlabel(r"$P_{\mathrm{el}}$ (proxy)")
    ax.set_ylabel(r"$P_{\mathrm{erg}}$")
    ax.set_title(r"Tilt-angle parametric scan (not a Pareto frontier)")
    fig.tight_layout()
    fig.savefig(outdir / "transport_tilt_scan_thetaR.png")
    # keep old filename as alias for compatibility
    fig.savefig(outdir / "transport_pareto_thetaR.png")
    plt.close(fig)

    res_col = CollisionEngine(base).find_fixed_point()
    res_deph = CollisionEngine(base).dephasing_control_fixed_point()
    fig, ax = plt.subplots(figsize=(5.5, 3.8))
    ax.bar(
        ["collisions", "dephasing only"],
        [res_col.P_el, res_deph.P_el],
        color=["C0", "C1"],
    )
    ax.set_ylabel(r"$P_{\mathrm{el}}$ (proxy)")
    ax.set_title("Control: collisions vs pure dephasing")
    fig.tight_layout()
    fig.savefig(outdir / "transport_dephasing_control.png")
    plt.close(fig)

    print("Transport demo complete.")
    print(f"  figures -> {outdir.resolve()}")


def generate_all_figures(outdir: Path) -> None:
    companion_demo(outdir)
    transport_demo(outdir)
    print("All figures generated.")
