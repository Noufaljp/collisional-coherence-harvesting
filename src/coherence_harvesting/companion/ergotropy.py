"""Qubit ergotropy and accessibility diagnostics."""

from __future__ import annotations

from typing import Tuple

import numpy as np


def bloch_from_rho(rho: np.ndarray) -> Tuple[float, float, float]:
    """Bloch vector of a qubit density matrix."""
    rho = np.asarray(rho, dtype=complex)
    x = 2.0 * np.real(rho[0, 1])  # if basis is |↑>,|↓> this needs care
    # We use basis |↓>, |↑> as (0,1): ρ = [[p↓, c], [c*, p↑]]
    # standard Bloch: z = p↑ - p↓ for σ_z = |↑><↑| - |↓><↓|
    x = 2.0 * np.real(rho[1, 0])  # <σ_x> with off-diag between ↓ and ↑
    y = 2.0 * np.imag(rho[1, 0])
    z = float(np.real(rho[1, 1] - rho[0, 0]))
    return float(x), float(y), float(z)


def qubit_ergotropy(z: float, x: float = 0.0, y: float = 0.0, Delta: float = 1.0) -> float:
    """Ergotropy for H = Δ |↑><↑| and Bloch vector (x,y,z).

    W = (Δ/2) (z + |r|)
    """
    r = np.sqrt(x * x + y * y + z * z)
    # clip physical range
    r = min(r, 1.0)
    return float(0.5 * Delta * (z + r))


def qubit_ergotropy_from_rho(rho: np.ndarray, Delta: float = 1.0) -> float:
    x, y, z = bloch_from_rho(rho)
    return qubit_ergotropy(z, x, y, Delta)


def weak_coherent_ergotropy(
    C_star: complex, theta: float, z_A: float, Delta: float = 1.0
) -> float:
    """Weak-extraction approximation ΔW ≈ Δ sin²θ |C*|² / |z_A|."""
    if abs(z_A) < 1e-14:
        # fall back to exact formula with pure transverse Bloch
        r_trans = 2.0 * abs(np.sin(theta) * C_star)
        return float(0.5 * Delta * (0.0 + r_trans))  # z≈0 edge case
    return float(Delta * (np.sin(theta) ** 2) * abs(C_star) ** 2 / abs(z_A))


def two_copy_accessible_work(
    a: float, b: float, c_abs: float, Delta: float = 1.0
) -> float:
    """Accessible work from energy-dephased ρ_A^{⊗2}.

    W_acc^(2) = Δ max{0, |c|² - b(a-b)} for a+b=1, a>b (ground-biased).
    """
    return float(Delta * max(0.0, c_abs**2 - b * (a - b)))


def two_copy_from_bloch(
    x: float, y: float, z: float, Delta: float = 1.0
) -> float:
    """Convenience: convert Bloch (↓/↑ basis) to two-copy accessible work."""
    p_up = 0.5 * (1.0 + z)
    p_dn = 0.5 * (1.0 - z)
    # matrix [[a,c],[c*,b]] with a=p_up? Our analytic note used
    # ρ_A = [[a, c],[c*, b]] with H=Δ|↑><↑| and a>b meaning more ground?
    # In note: a is ground? Looking at note:
    # ρ_A = [[a,c],[c*,b]], a+b=1, a>b, and λ0=a², λ2=b² with E=0,2Δ
    # So a = ground population (E=0), b = excited (E=Δ).
    a = p_dn
    b = p_up
    c_abs = 0.5 * np.sqrt(x * x + y * y)
    if a < b:
        # not ground-biased; still use formula with ordering
        a, b = b, a
    return two_copy_accessible_work(a, b, c_abs, Delta)
