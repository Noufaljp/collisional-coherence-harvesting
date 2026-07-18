"""Bath / waiting-time maps for the companion model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np


def reset_fixed_point_C(
    c0: complex,
    theta: float,
    gamma_C: float,
    r: float,
    delta: float = 0.0,
) -> complex:
    """Phase-locked phenomenological fixed-point coherence.

    C* = (1 - q) c0 / (1 - q e^{-iφ} cos θ)
    with q = exp(-γ_C / r), φ = Δ / r, δ = Δ / γ_C optional via delta=Δ.
    """
    if r <= 0:
        raise ValueError("collision rate r must be positive")
    x = gamma_C / r
    q = np.exp(-x)
    phi = delta / r  # delta here is physical gap Δ
    denom = 1.0 - q * np.exp(-1j * phi) * np.cos(theta)
    return (1.0 - q) * c0 / denom


def reset_fixed_point_d(
    s_ss: float,
    theta: float,
    gamma_d: float,
    r: float,
    alpha: float,
) -> float:
    """Population imbalance fixed point for target d_ss = 0."""
    q = np.exp(-gamma_d / r)
    c2 = np.cos(theta) ** 2
    s2 = np.sin(theta) ** 2
    return float(-q * s2 * (1.0 - 2.0 * alpha) * s_ss / (1.0 - q * c2))


@dataclass
class DirectedLeakageParams:
    """Directed dark-leakage bath parameters."""

    Gamma_up: float
    Gamma_down: float
    kappa_D: float
    tau_c: float

    @property
    def A(self) -> float:
        return self.Gamma_up + self.Gamma_down

    @property
    def s_ss(self) -> float:
        return self.Gamma_up / (self.Gamma_up + self.Gamma_down)

    @property
    def c0(self) -> float:
        return 0.5 * self.s_ss


def directed_leakage_waiting_matrix(
    params: DirectedLeakageParams,
) -> Tuple[np.ndarray, np.ndarray]:
    """Affine waiting map: v_- = B v_+ + b."""
    A = params.A
    qB = np.exp(-A * params.tau_c)
    qD = np.exp(-params.kappa_D * params.tau_c)
    if abs(A - params.kappa_D) < 1e-12:
        cross = params.tau_c * np.exp(-A * params.tau_c)
    else:
        cross = (qD - qB) / (A - params.kappa_D)
    B = np.array(
        [
            [qB, -params.Gamma_up * cross],
            [0.0, qD],
        ],
        dtype=float,
    )
    b = np.array([params.s_ss * (1.0 - qB), 0.0], dtype=float)
    return B, b


def bright_dark_collision_matrix(theta: float) -> np.ndarray:
    """R_θ for bright/dark populations (real C sector)."""
    c = np.cos(theta)
    return 0.5 * np.array(
        [
            [1.0 + c, 1.0 - c],
            [1.0 - c, 1.0 + c],
        ],
        dtype=float,
    )


def directed_leakage_fixed_point(
    params: DirectedLeakageParams, theta: float
) -> np.ndarray:
    """v* = (I - B R_θ)^{-1} b  for v = (p_B, p_D)."""
    B, b = directed_leakage_waiting_matrix(params)
    R = bright_dark_collision_matrix(theta)
    M = np.eye(2) - B @ R
    return np.linalg.solve(M, b)


def v_to_s_C(v: np.ndarray) -> Tuple[float, float]:
    """Convert bright/dark populations to (s, C) with real C."""
    pB, pD = float(v[0]), float(v[1])
    s = pB + pD
    C = 0.5 * (pB - pD)
    return s, C
