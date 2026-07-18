"""Charging power, impedance matching, finite-phase bounds, directed leakage."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Tuple

import numpy as np
from scipy.optimize import minimize_scalar

from .baths import (
    DirectedLeakageParams,
    directed_leakage_fixed_point,
    reset_fixed_point_C,
    reset_fixed_point_d,
    v_to_s_C,
)
from .collision import analytic_ancilla_bloch
from .ergotropy import (
    coherent_incoherent_ergotropy,
    qubit_ergotropy,
    two_copy_from_bloch,
    weak_coherent_ergotropy,
)
from .physicality import check_companion_params, check_doublet_physical, physicality_margin


@dataclass
class CompanionParams:
    """Parameters for the phenomenological companion engine."""

    gamma_C: float = 1.0
    gamma_d: float = 1.0
    c0: float = 0.25
    s_ss: float = 0.5
    Delta: float = 0.2  # matched gap (small but finite)
    theta: float = 0.3
    alpha: float = 0.0
    validate: bool = True

    def __post_init__(self) -> None:
        if self.validate:
            check_companion_params(
                self.gamma_C,
                self.gamma_d,
                self.c0,
                self.s_ss,
                self.Delta,
                self.theta,
                self.alpha,
            )


def impedance_matched_r(
    gamma_C: float, theta: float, delta_over_gamma: float = 0.0
) -> float:
    """r_opt ≈ γ_C √(1+δ²) / (1 - cos θ)."""
    eps = 1.0 - np.cos(theta)
    if eps < 1e-14:
        return np.inf
    return float(gamma_C * np.sqrt(1.0 + delta_over_gamma**2) / eps)


def finite_coupling_theta_min(
    gamma_C: float, g: float, delta_over_gamma: float = 0.0
) -> float:
    """Realizability: θ ≳ 2 γ_C √(1+δ²) / g  (with θ = g τ ≤ g/r)."""
    if g <= 0:
        return np.inf
    return float(2.0 * gamma_C * np.sqrt(1.0 + delta_over_gamma**2) / g)


def small_angle_bound(
    gamma_C: float,
    Delta: float,
    c0: float,
    z_A: float = 1.0,
    delta_over_gamma: float = 0.0,
) -> float:
    """P_max ≈ (γ_C Δ c0² / |z_A|) / (1 + √(1+δ²))."""
    return float(
        (gamma_C * Delta * abs(c0) ** 2 / abs(z_A))
        / (1.0 + np.sqrt(1.0 + delta_over_gamma**2))
    )


def fixed_point_state(
    params: CompanionParams, r: float, *, check: bool = True
) -> Tuple[float, float, complex]:
    """(s*, d*, C*) for phenomenological reset model."""
    if r <= 0:
        raise ValueError("r must be positive")
    C = reset_fixed_point_C(
        c0=params.c0,
        theta=params.theta,
        gamma_C=params.gamma_C,
        r=r,
        delta=params.Delta,
    )
    d = reset_fixed_point_d(
        s_ss=params.s_ss,
        theta=params.theta,
        gamma_d=params.gamma_d,
        r=r,
        alpha=params.alpha,
    )
    s = params.s_ss
    if check:
        check_doublet_physical(s, d, C)
    return s, d, C


def fixed_point_directed_leakage(
    Gamma_up: float,
    Gamma_down: float,
    kappa_D: float,
    r: float,
    theta: float,
    alpha: float = 0.0,
) -> Tuple[float, float, complex]:
    """(s*, d*, C*) from directed dark-leakage bath (real-C sector).

    Here d* = 0 in the bright/dark population description with real C:
    s = p_B + p_D, C = (p_B - p_D)/2, d = ρ11 - ρ22 = 0 when C is the only imbalance
    in the bright/dark basis with equal diagonal weights in energy basis... 

    For the bright/dark model with real C:
      ρ11 = (s + d)/2, and with pure bright/dark populations and no extra d from
      energy-basis imbalance beyond C: actually p_B = s/2 + C, p_D = s/2 - C implies
      d = 0 and C real.
    """
    if r <= 0:
        raise ValueError("r must be positive")
    params = DirectedLeakageParams(
        Gamma_up=Gamma_up,
        Gamma_down=Gamma_down,
        kappa_D=kappa_D,
        tau_c=1.0 / r,
    )
    v = directed_leakage_fixed_point(params, theta)
    s, C = v_to_s_C(v)
    d = 0.0
    # Collision with alpha ≠ 0 can induce d; include post-collision d via population map
    # at fixed point of d with s fixed: use same formula as reset with gamma_d ~ A
    A = Gamma_up + Gamma_down
    d = reset_fixed_point_d(s_ss=s, theta=theta, gamma_d=A, r=r, alpha=alpha)
    check_doublet_physical(s, d, C)
    return s, d, complex(C)


def ancilla_diagnostics(
    s: float, d: float, C: complex, theta: float, alpha: float, Delta: float
) -> dict:
    """Full battery diagnostics for one outgoing ancilla."""
    x, y, z = analytic_ancilla_bloch(s, d, C, theta, alpha)
    parts = coherent_incoherent_ergotropy(z, x, y, Delta)
    W_acc2 = two_copy_from_bloch(x, y, z, Delta)
    E_A = 0.5 * Delta * (1.0 + z)  # Tr(ρ H) with H=Δ|↑><↑|
    return {
        "x": x,
        "y": y,
        "z": z,
        "E_A": float(E_A),
        "W_total": parts["W_total"],
        "W_coh": parts["W_coh"],
        "W_inc": parts["W_inc"],
        "W_acc2": float(W_acc2),
        "ergotropy_fraction": float(parts["W_total"] / E_A) if E_A > 1e-15 else 0.0,
        "margin": physicality_margin(s, d, C),
    }


def per_collision_ergotropy(
    params: CompanionParams, r: float, exact: bool = True
) -> float:
    s, d, C = fixed_point_state(params, r)
    x, y, z = analytic_ancilla_bloch(s, d, C, params.theta, params.alpha)
    if exact:
        return qubit_ergotropy(z, x, y, params.Delta)
    return weak_coherent_ergotropy(C, params.theta, z, params.Delta)


def charging_power(params: CompanionParams, r: float, exact: bool = True) -> float:
    return r * per_collision_ergotropy(params, r, exact=exact)


def charging_power_directed(
    Gamma_up: float,
    Gamma_down: float,
    kappa_D: float,
    r: float,
    theta: float,
    Delta: float,
    alpha: float = 0.0,
    exact: bool = True,
) -> float:
    s, d, C = fixed_point_directed_leakage(
        Gamma_up, Gamma_down, kappa_D, r, theta, alpha
    )
    x, y, z = analytic_ancilla_bloch(s, d, C, theta, alpha)
    if exact:
        W = qubit_ergotropy(z, x, y, Delta)
    else:
        W = weak_coherent_ergotropy(C, theta, z, Delta)
    return r * W


def power_curve(
    params: CompanionParams,
    r_values: np.ndarray | None = None,
    exact: bool = True,
) -> Tuple[np.ndarray, np.ndarray]:
    if r_values is None:
        r_opt = impedance_matched_r(
            params.gamma_C, params.theta, params.Delta / params.gamma_C
        )
        if not np.isfinite(r_opt):
            r_opt = params.gamma_C
        r_values = np.geomspace(max(r_opt * 1e-2, 1e-3), r_opt * 50, 120)
    P = np.array([charging_power(params, float(r), exact=exact) for r in r_values])
    return r_values, P


def power_curve_directed(
    Gamma_up: float,
    Gamma_down: float,
    kappa_D: float,
    theta: float,
    Delta: float,
    r_values: np.ndarray,
    alpha: float = 0.0,
    exact: bool = True,
) -> Tuple[np.ndarray, np.ndarray]:
    P = np.array(
        [
            charging_power_directed(
                Gamma_up, Gamma_down, kappa_D, float(r), theta, Delta, alpha, exact
            )
            for r in r_values
        ]
    )
    return r_values, P


def optimize_power(
    params: CompanionParams,
    exact: bool = True,
    r_bounds: Tuple[float, float] | None = None,
) -> Tuple[float, float]:
    """Return (r_opt, P_max) by 1D scalar optimization on log r."""
    r_guess = impedance_matched_r(
        params.gamma_C, params.theta, params.Delta / params.gamma_C
    )
    if not np.isfinite(r_guess) or r_guess <= 0:
        r_guess = params.gamma_C
    if r_bounds is None:
        r_bounds = (r_guess * 1e-3, r_guess * 100)

    def objective(log_r: float) -> float:
        return -charging_power(params, float(np.exp(log_r)), exact=exact)

    res = minimize_scalar(
        objective,
        bounds=(np.log(r_bounds[0]), np.log(r_bounds[1])),
        method="bounded",
    )
    r_opt = float(np.exp(res.x))
    return r_opt, charging_power(params, r_opt, exact=exact)


def plateau_C(theta: float, gamma_C: float = 1.0) -> float:
    """Numerical harvesting prefactor C(θ) at φ≈0 (tiny Δ)."""
    params = CompanionParams(
        gamma_C=gamma_C,
        gamma_d=gamma_C,
        c0=0.25,
        s_ss=0.5,
        Delta=1e-6,
        theta=theta,
        alpha=0.0,
    )
    r_opt, P = optimize_power(params, exact=True)
    s, d, C = fixed_point_state(params, r_opt)
    x, y, z = analytic_ancilla_bloch(s, d, C, params.theta, params.alpha)
    pref = params.gamma_C * params.Delta * abs(params.c0) ** 2 / max(abs(z), 1e-12)
    return float(P / pref)


def numerical_finite_phase_optimum(
    params: CompanionParams,
    deltas: np.ndarray | None = None,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """For each δ=Δ/γ_C, optimize power and compare to analytic r_opt(δ).

    Returns (deltas, r_opt_num / γ_C, r_opt_analytic / γ_C).
    """
    if deltas is None:
        deltas = np.linspace(0.0, 4.0, 17)
    r_num = []
    r_an = []
    base = params
    for dlt in deltas:
        Delta = float(dlt) * base.gamma_C
        p = CompanionParams(
            gamma_C=base.gamma_C,
            gamma_d=base.gamma_d,
            c0=base.c0,
            s_ss=base.s_ss,
            Delta=max(Delta, 1e-9),
            theta=base.theta,
            alpha=base.alpha,
        )
        r_o, _ = optimize_power(p, exact=True)
        r_num.append(r_o / base.gamma_C)
        r_an.append(
            impedance_matched_r(base.gamma_C, base.theta, float(dlt)) / base.gamma_C
        )
    return np.asarray(deltas), np.asarray(r_num), np.asarray(r_an)
