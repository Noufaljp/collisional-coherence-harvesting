"""Collision map for the V-system / ancilla exchange.

Basis conventions
-----------------
System (3 levels): |0>, |1>, |2>
Ancilla (2 levels): |↓>=0, |↑>=1

Active exchange subspace: |1↓>, |2↑>
Interaction angle: θ = g τ
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np
from scipy.linalg import expm


# Joint basis ordering: system ⊗ ancilla with ancilla as the fast index
# |s,a> -> index = 2*s + a, dimension 6
JOINT_DIM = 6


def _ket(s: int, a: int) -> np.ndarray:
    v = np.zeros(JOINT_DIM, dtype=complex)
    v[2 * s + a] = 1.0
    return v


def exchange_hamiltonian(g: float = 1.0) -> np.ndarray:
    """H_int / ħ in the joint basis (so U = exp(-i H τ) with θ = g τ)."""
    h = np.zeros((JOINT_DIM, JOINT_DIM), dtype=complex)
    # |1↓> = (1,0), |2↑> = (2,1)
    i = 2 * 1 + 0
    j = 2 * 2 + 1
    h[i, j] = g
    h[j, i] = g
    return h


def collision_unitary(theta: float) -> np.ndarray:
    """U(θ) = exp(-i H_int τ / ħ) with θ = g τ."""
    # On active block: [[cosθ, -i sinθ], [-i sinθ, cosθ]]
    # Build via Hamiltonian with g=1, τ=θ
    return expm(-1j * exchange_hamiltonian(1.0) * theta)


@dataclass
class SystemState:
    """Doublet variables plus ground population (implicit: p0 = 1 - s)."""

    s: float
    d: float
    C: complex
    p0: float | None = None

    def rho(self) -> np.ndarray:
        """3×3 density matrix in {|0>,|1>,|2>}."""
        s, d, C = float(self.s), float(self.d), complex(self.C)
        rho11 = 0.5 * (s + d)
        rho22 = 0.5 * (s - d)
        p0 = 1.0 - s if self.p0 is None else float(self.p0)
        # Clip tiny negatives from numerical noise
        p0 = max(p0, 0.0)
        rho = np.array(
            [
                [p0, 0.0, 0.0],
                [0.0, rho11, C],
                [0.0, np.conjugate(C), rho22],
            ],
            dtype=complex,
        )
        return rho

    @classmethod
    def from_rho(cls, rho: np.ndarray) -> "SystemState":
        rho = np.asarray(rho, dtype=complex)
        s = float(np.real(rho[1, 1] + rho[2, 2]))
        d = float(np.real(rho[1, 1] - rho[2, 2]))
        C = complex(rho[1, 2])
        p0 = float(np.real(rho[0, 0]))
        return cls(s=s, d=d, C=C, p0=p0)


def analytic_system_map(
    s: float, d: float, C: complex, theta: float, alpha: float
) -> Tuple[float, float, complex]:
    """Closed-form system map after one collision.

    Returns (s', d', C').
    """
    c2 = np.cos(theta) ** 2
    s2 = np.sin(theta) ** 2
    s_out = s
    d_out = c2 * d - s2 * (1.0 - 2.0 * alpha) * s
    C_out = np.cos(theta) * C
    return float(s_out), float(d_out), complex(C_out)


def analytic_ancilla_bloch(
    s: float, d: float, C: complex, theta: float, alpha: float
) -> Tuple[float, float, float]:
    """Outgoing ancilla Bloch vector (x, y, z) for real/complex C.

    z = 2 p_↑ - 1.
    """
    p_up = alpha + 0.5 * np.sin(theta) ** 2 * (s * (1.0 - 2.0 * alpha) + d)
    coh = -1j * np.sin(theta) * (1.0 - 2.0 * alpha) * C
    x = 2.0 * np.real(coh)
    y = -2.0 * np.imag(coh)
    z = 2.0 * p_up - 1.0
    return float(x), float(y), float(z)


def numerical_collision(
    rho_S: np.ndarray, alpha: float, theta: float
) -> Tuple[np.ndarray, np.ndarray]:
    """Exact joint unitary collision + partial traces.

    Parameters
    ----------
    rho_S : (3,3) system density matrix
    alpha : ancilla excited population (input diagonal)
    theta : exchange angle

    Returns
    -------
    rho_S_out : (3,3)
    rho_A_out : (2,2)
    """
    rho_S = np.asarray(rho_S, dtype=complex)
    rho_A = np.diag([1.0 - alpha, alpha]).astype(complex)
    rho = np.kron(rho_S, rho_A)
    U = collision_unitary(theta)
    rho_out = U @ rho @ U.conj().T

    # Partial trace over ancilla (dim 2)
    rho_S_out = np.zeros((3, 3), dtype=complex)
    for a in range(2):
        rho_S_out += rho_out[a::2, a::2]

    # Partial trace over system
    rho_A_out = np.zeros((2, 2), dtype=complex)
    for s in range(3):
        blk = rho_out[2 * s : 2 * s + 2, 2 * s : 2 * s + 2]
        rho_A_out += blk

    return rho_S_out, rho_A_out


def random_valid_doublet_state(
    rng: np.random.Generator | None = None,
) -> SystemState:
    """Sample a physical V-system state with random doublet coherence."""
    rng = rng or np.random.default_rng()
    p0 = float(rng.uniform(0.05, 0.6))
    s = 1.0 - p0
    # populations in doublet
    t = float(rng.uniform(0.0, 1.0))
    rho11 = t * s
    rho22 = (1.0 - t) * s
    d = rho11 - rho22
    # |C|^2 <= rho11 rho22
    cmax = np.sqrt(max(rho11 * rho22, 0.0))
    amp = float(rng.uniform(0.0, cmax))
    phase = float(rng.uniform(0.0, 2.0 * np.pi))
    C = amp * np.exp(1j * phase)
    return SystemState(s=s, d=d, C=C, p0=p0)
