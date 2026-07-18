"""Spin-valve model definitions (Coulomb-blockade dot + polarized leads).

Hilbert space of the transport dot (strong blockade):
    |0> empty, |↑> = |1>, |↓> = |2>
so the singly occupied sector is a spin-1/2 with optional splitting Δ.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class SpinValveParams:
    """Minimal non-collinear spin-valve parameters."""

    # Energies
    epsilon: float = 0.0  # charge energy of single occupancy
    Delta: float = 0.2  # spin splitting (near-degenerate when ≲ γ)
    # Lead couplings
    gamma_L: float = 1.0
    gamma_R: float = 1.0
    p_L: float = 0.8
    p_R: float = 0.8
    theta_R: float = np.pi / 2  # non-collinear tilt of right lead
    phi_R: float = 0.0
    # Thermodynamics
    T_L: float = 1.0
    T_R: float = 0.5
    mu_L: float = 0.5
    mu_R: float = -0.5
    # Collision / ancilla
    g: float = 5.0
    tau: float = 0.1  # collision duration → θ = g τ
    T_period: float = 2.0  # full period
    alpha: float = 0.0  # ancilla input excited population
    Delta_A: float | None = None  # matched gap; default = Delta

    def __post_init__(self) -> None:
        if self.Delta_A is None:
            self.Delta_A = self.Delta

    @property
    def theta(self) -> float:
        return self.g * self.tau

    @property
    def waiting_time(self) -> float:
        return max(self.T_period - self.tau, 0.0)

    @property
    def collision_rate(self) -> float:
        return 1.0 / self.T_period


def free_dot_hamiltonian(params: SpinValveParams) -> np.ndarray:
    """H_D in basis {|0>, |↑>, |↓>}."""
    e = params.epsilon
    d = params.Delta
    return np.diag([0.0, e + 0.5 * d, e - 0.5 * d]).astype(complex)


def free_ancilla_hamiltonian(params: SpinValveParams) -> np.ndarray:
    """H_A in basis {|↓>, |↑>} with gap Δ_A on |↑>."""
    return np.diag([0.0, params.Delta_A]).astype(complex)


def lead_gamma_matrix(
    gamma: float,
    p: float,
    theta: float = 0.0,
    phi: float = 0.0,
) -> np.ndarray:
    """2×2 spin broadening matrix Γ in the {|↑>, |↓>} basis."""
    c, s = np.cos(theta), np.sin(theta)
    eip = np.exp(1j * phi)
    return gamma * np.array(
        [
            [1.0 + p * c, p * eip * s],
            [p * np.exp(-1j * phi) * s, 1.0 - p * c],
        ],
        dtype=complex,
    )


def fermi(E: float, mu: float, T: float) -> float:
    if T <= 0:
        return 1.0 if E < mu else (0.5 if E == mu else 0.0)
    x = (E - mu) / T
    # stable
    if x > 40:
        return 0.0
    if x < -40:
        return 1.0
    return float(1.0 / (1.0 + np.exp(x)))


def joint_exchange_hamiltonian(g: float = 1.0) -> np.ndarray:
    """H_int on (dot ⊗ ancilla), dim 6.

    Active block: |↑_D ↓_A> ↔ |↓_D ↑_A>  (indices: ↑=1, ↓=2; A: ↓=0, ↑=1)
    """
    h = np.zeros((6, 6), dtype=complex)
    # |↑↓> = s=1,a=0 → idx 2
    # |↓↑> = s=2,a=1 → idx 5
    i, j = 2 * 1 + 0, 2 * 2 + 1
    h[i, j] = g
    h[j, i] = g
    return h
