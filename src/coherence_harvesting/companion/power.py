"""Charging power, impedance matching, and finite-phase bounds."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Tuple

import numpy as np
from scipy.optimize import minimize_scalar

from .baths import reset_fixed_point_C, reset_fixed_point_d
from .collision import analytic_ancilla_bloch
from .ergotropy import qubit_ergotropy, weak_coherent_ergotropy


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


def impedance_matched_r(gamma_C: float, theta: float, delta_over_gamma: float = 0.0) -> float:
    """r_opt ≈ γ_C √(1+δ²) / (1 - cos θ)."""
    eps = 1.0 - np.cos(theta)
    if eps < 1e-14:
        return np.inf
    return float(gamma_C * np.sqrt(1.0 + delta_over_gamma**2) / eps)


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


def fixed_point_state(params: CompanionParams, r: float) -> Tuple[float, float, complex]:
    """(s*, d*, C*) for phenomenological reset model."""
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
    return params.s_ss, d, C


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


def plateau_C(theta: float, gamma_C: float = 1.0, n_r: int = 80) -> float:
    """Numerical harvesting prefactor C(θ) = sin²θ f(x_opt) at φ=0, Δ→0+."""
    # Use tiny Delta for ergotropy scale; ratio cancels in C if we normalize carefully.
    # Better: use weak formula with |z_A|=1 and extract prefactor.
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
    # P ≈ r * (Δ sin²θ |C*|² / |z|) → for weak: P = (γ Δ c0² / |z|) * C(θ)
    # so C(θ) = P * |z| / (γ Δ c0²)
    s, d, C = fixed_point_state(params, r_opt)
    x, y, z = analytic_ancilla_bloch(s, d, C, params.theta, params.alpha)
    pref = params.gamma_C * params.Delta * abs(params.c0) ** 2 / max(abs(z), 1e-12)
    return float(P / pref)
