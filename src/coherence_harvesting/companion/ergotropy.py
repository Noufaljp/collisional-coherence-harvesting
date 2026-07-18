"""Qubit ergotropy and accessibility diagnostics."""

from __future__ import annotations

from typing import Dict, Tuple

import numpy as np


def bloch_from_rho(rho: np.ndarray) -> Tuple[float, float, float]:
    """Bloch vector for qubit in basis {|↓>, |↑>}."""
    rho = np.asarray(rho, dtype=complex)
    x = 2.0 * np.real(rho[1, 0])
    y = 2.0 * np.imag(rho[1, 0])
    z = float(np.real(rho[1, 1] - rho[0, 0]))
    return float(x), float(y), float(z)


def rho_from_bloch(x: float, y: float, z: float) -> np.ndarray:
    """Qubit density matrix in basis {|↓>, |↑>}."""
    p_dn = 0.5 * (1.0 - z)
    p_up = 0.5 * (1.0 + z)
    c = 0.5 * (x + 1j * y)  # ρ_{↑↓}
    return np.array([[p_dn, np.conjugate(c)], [c, p_up]], dtype=complex)


def qubit_ergotropy(z: float, x: float = 0.0, y: float = 0.0, Delta: float = 1.0) -> float:
    """Total ergotropy for H = Δ |↑><↑|: W = (Δ/2)(z + |r|)."""
    r = float(np.sqrt(x * x + y * y + z * z))
    r = min(r, 1.0)
    return float(0.5 * Delta * (z + r))


def qubit_ergotropy_from_rho(rho: np.ndarray, Delta: float = 1.0) -> float:
    x, y, z = bloch_from_rho(rho)
    return qubit_ergotropy(z, x, y, Delta)


def coherent_incoherent_ergotropy(
    z: float, x: float = 0.0, y: float = 0.0, Delta: float = 1.0
) -> Dict[str, float]:
    """Francica-style split of total ergotropy into coherent and incoherent parts.

    For H = Δ|↑><↑|:
      W_total = (Δ/2)(z + |r|)
      W_inc   = ergotropy of the dephased state (x=y=0) = (Δ/2)(z + |z|)
              = Δ max(z, 0)
      W_coh   = W_total - W_inc
    """
    r = float(np.sqrt(x * x + y * y + z * z))
    r = min(r, 1.0)
    W_total = 0.5 * Delta * (z + r)
    W_inc = 0.5 * Delta * (z + abs(z))  # = Delta * max(z, 0)
    W_coh = W_total - W_inc
    return {
        "W_total": float(W_total),
        "W_inc": float(W_inc),
        "W_coh": float(max(W_coh, 0.0)),
        "r": r,
        "z": float(z),
    }


def one_copy_accessible_work(
    z: float,
    x: float = 0.0,
    y: float = 0.0,
    Delta: float = 1.0,
    *,
    has_phase_reference: bool = False,
) -> float:
    """Operational one-copy accessible work under a stated class of operations.

    Without a phase reference (time-translation covariant / energy-preserving
    operations only): coherent ergotropy of a single ground-biased qubit is
    inaccessible → W_acc^(1) = W_inc only.

    With an explicit phase reference: full total ergotropy is accessible.
    """
    parts = coherent_incoherent_ergotropy(z, x, y, Delta)
    if has_phase_reference:
        return parts["W_total"]
    return parts["W_inc"]


def weak_coherent_ergotropy(
    C_star: complex, theta: float, z_A: float, Delta: float = 1.0
) -> float:
    """Weak-extraction approximation ΔW ≈ Δ sin²θ |C*|² / |z_A|."""
    if abs(z_A) < 1e-14:
        r_trans = 2.0 * abs(np.sin(theta) * C_star)
        return float(0.5 * Delta * r_trans)
    return float(Delta * (np.sin(theta) ** 2) * abs(C_star) ** 2 / abs(z_A))


def two_copy_accessible_work(
    a: float, b: float, c_abs: float, Delta: float = 1.0
) -> float:
    """Piecewise accessible work from energy-dephased ρ_A^{⊗2}.

    Convention: single-copy matrix [[a, c], [c*, b]] with a + b = 1,
    a = ground (E=0) population, b = excited (E=Δ) population, ground-biased a ≥ b.

    After global energy dephasing of ρ^{⊗2}, ergotropy is (publication note §4.6):

        0,                              |c|² ≤ b(a−b)
        Δ [|c|² − b(a−b)],              b(a−b) < |c|² ≤ a(a−b)
        Δ [2|c|² − (a−b)],              a(a−b) < |c|² ≤ a b
    """
    a = float(a)
    b = float(b)
    c2 = float(c_abs) ** 2
    # Ensure ground-biased ordering for the formula as stated
    if a < b - 1e-15:
        a, b = b, a
    thr1 = b * (a - b)
    thr2 = a * (a - b)
    thr3 = a * b  # positivity upper bound ab ≥ |c|²
    if c2 <= thr1 + 1e-15:
        return 0.0
    if c2 <= thr2 + 1e-15:
        return float(Delta * (c2 - thr1))
    # third regime (and clamp at positivity bound)
    c2_eff = min(c2, thr3)
    return float(Delta * (2.0 * c2_eff - (a - b)))


def two_copy_accessible_work_matrix(
    a: float, b: float, c_abs: float, Delta: float = 1.0
) -> float:
    """Direct matrix calculation: energy-dephase ρ^{⊗2}, then ergotropy vs H⊗I+I⊗H."""
    a = float(a)
    b = float(b)
    c = float(c_abs)
    # Single-copy in energy basis |g>, |e>: ρ = [[a, c], [c, b]] (c real wlog)
    # Two-copy computational order |gg>, |ge>, |eg>, |ee|
    # Populations:
    #   P_gg = a², P_ee = b²
    #   one-excitation block in {|ge>, |eg>}: [[ab, |c|²], [|c|², ab]] after energy dephasing
    #   (off-diagonal between ge and eg is |c|² from coherence products; cross energy blocks dephased)
    #
    # Full product before dephasing has more structure; energy dephasing kills coherences between
    # different total energy. The one-excitation coherences that survive are between |ge> and |eg|.
    ab = a * b
    # Energy-dephased two-copy state (block diagonal in total excitation)
    # E=0: |gg>
    # E=Δ: span{|ge>, |eg>}
    # E=2Δ: |ee>
    # Eigenvalues of one-excitation block: ab ± |c|²
    lam0 = a * a
    lam2 = b * b
    lam_p = ab + c * c
    lam_m = ab - c * c
    # Numerical floor
    evals_rho = np.array([lam0, lam_p, lam_m, lam2], dtype=float)
    # Clip tiny negatives from roundoff
    evals_rho = np.maximum(evals_rho, 0.0)
    # Energies of the four product basis labels in that same order after sorting by energy:
    # For ergotropy we pair largest populations with lowest energies.
    energies = np.array([0.0, Delta, Delta, 2.0 * Delta], dtype=float)
    # Passive energy: sort populations descending, energies ascending
    p_sorted = np.sort(evals_rho)[::-1]
    e_sorted = np.sort(energies)
    E = float(np.dot(evals_rho, energies))  # same multiset of energy labels
    # Actually careful: lam_p and lam_m both sit at energy Δ, so
    E = lam0 * 0.0 + (lam_p + lam_m) * Delta + lam2 * (2.0 * Delta)
    E_pass = float(np.dot(p_sorted, e_sorted))
    return float(max(E - E_pass, 0.0))


def two_copy_from_bloch(
    x: float, y: float, z: float, Delta: float = 1.0
) -> float:
    """Two-copy accessible work from Bloch vector (↓/↑ basis)."""
    p_up = 0.5 * (1.0 + z)
    p_dn = 0.5 * (1.0 - z)
    a = p_dn  # ground
    b = p_up  # excited
    c_abs = 0.5 * np.sqrt(x * x + y * y)
    return two_copy_accessible_work(a, b, c_abs, Delta)


def two_copy_from_bloch_matrix(
    x: float, y: float, z: float, Delta: float = 1.0
) -> float:
    p_up = 0.5 * (1.0 + z)
    p_dn = 0.5 * (1.0 - z)
    c_abs = 0.5 * np.sqrt(x * x + y * y)
    return two_copy_accessible_work_matrix(p_dn, p_up, c_abs, Delta)
