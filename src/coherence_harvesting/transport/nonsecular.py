"""Nonsecular lead generator for the Coulomb-blockade spin valve.

We implement a *physically motivated* Redfield-style / first-order sequential-
tunneling generator on the 3-level Fock space {|0>, |↑>, |↓>} that:

1. Allows charge exchange with polarized leads (populations).
2. Retains spin coherences in the singly occupied sector (nonsecular).
3. Generates steady spin coherence for non-collinear lead polarizations.

This is the minimal numerical engine needed for the full-paper layer. It is
not a full nonequilibrium Green's function theory; positivity is monitored
and a mild secular cutoff can be applied if needed.
"""

from __future__ import annotations

from typing import Tuple

import numpy as np
from scipy.linalg import expm

from .spin_valve import SpinValveParams, fermi, free_dot_hamiltonian, lead_gamma_matrix


# Basis: 0 = empty, 1 = up, 2 = down
DIM = 3


def _dissipator(L: np.ndarray, rho: np.ndarray) -> np.ndarray:
    Ld = L.conj().T
    return L @ rho @ Ld - 0.5 * (Ld @ L @ rho + rho @ Ld @ L)


def sequential_jump_ops(
    params: SpinValveParams,
) -> list[Tuple[np.ndarray, float]]:
    """Build weighted jump operators for left/right leads.

    For each lead α and spin channel in the lead eigenbasis of Γ_α, we add
    in/out tunneling at the corresponding Fermi factors.
    """
    H = free_dot_hamiltonian(params)
    E0 = float(np.real(H[0, 0]))
    Eu = float(np.real(H[1, 1]))
    Ed = float(np.real(H[2, 2]))

    ops: list[Tuple[np.ndarray, float]] = []

    for side, gamma, p, th, ph, T, mu in [
        ("L", params.gamma_L, params.p_L, 0.0, 0.0, params.T_L, params.mu_L),
        (
            "R",
            params.gamma_R,
            params.p_R,
            params.theta_R,
            params.phi_R,
            params.T_R,
            params.mu_R,
        ),
    ]:
        Gam = lead_gamma_matrix(gamma, p, th, ph)
        # eigendecompose Γ = U diag(λ) U† in spin subspace
        evals, evecs = np.linalg.eigh(Gam)
        for k in range(2):
            lam = float(max(np.real(evals[k]), 0.0))
            if lam < 1e-14:
                continue
            # spinor components on |↑>, |↓>
            cu = evecs[0, k]
            cd = evecs[1, k]
            # tunneling operator empty ↔ spinor: L_+ |0> = cu|↑> + cd|↓>
            L_in = np.zeros((DIM, DIM), dtype=complex)
            L_in[1, 0] = cu
            L_in[2, 0] = cd
            # effective level for Fermi: use spinor energy expectation
            E_spin = float(np.real(abs(cu) ** 2 * Eu + abs(cd) ** 2 * Ed))
            f = fermi(E_spin, mu, T)
            # rates: Γ_in ~ λ f, Γ_out ~ λ (1-f)
            ops.append((L_in, lam * f))
            L_out = L_in.conj().T
            ops.append((L_out, lam * (1.0 - f)))

    return ops


def lead_liouvillian(params: SpinValveParams) -> np.ndarray:
    """Superoperator L such that ρ̇ = L ρ  (column-stacked, dim 9)."""
    H = free_dot_hamiltonian(params)
    jumps = sequential_jump_ops(params)

    # Build Liouvillian: -i[H,ρ] + ∑ γ D[L]ρ
    # vec form: (-i H⊗I + i I⊗H^T) + ...
    I = np.eye(DIM, dtype=complex)
    Lsup = -1j * (np.kron(H, I) - np.kron(I, H.T))

    for Lop, rate in jumps:
        if rate <= 0:
            continue
        Ld = Lop.conj().T
        # D[L]ρ = L ρ L† - 1/2 {L†L, ρ}
        # vec: (L⊗L*) - 1/2 ( (L†L)⊗I + I⊗(L†L)^T )
        LL = Ld @ Lop
        Lsup += rate * (
            np.kron(Lop, Lop.conj())
            - 0.5 * (np.kron(LL, I) + np.kron(I, LL.T))
        )

    # Mild pure dephasing on charge sector only (optional stabilizer)
    # not applied by default.

    return Lsup


def evolve_leads(rho: np.ndarray, params: SpinValveParams, t: float) -> np.ndarray:
    """Evolve ρ under lead Liouvillian for time t."""
    if t <= 0:
        return np.asarray(rho, dtype=complex).copy()
    L = lead_liouvillian(params)
    v = np.asarray(rho, dtype=complex).reshape(-1)
    v_t = expm(L * t) @ v
    rho_t = v_t.reshape((DIM, DIM))
    # Hermitize / renormalize softly
    rho_t = 0.5 * (rho_t + rho_t.conj().T)
    tr = np.trace(rho_t)
    if abs(tr) > 0:
        rho_t = rho_t / tr
    return rho_t


def steady_state_leads(params: SpinValveParams, tol: float = 1e-10) -> np.ndarray:
    """Nullspace of the lead Liouvillian (continuous NESS, no collisions)."""
    L = lead_liouvillian(params)
    # Solve L v = 0 with Tr ρ = 1
    # Use SVD
    u, s, vh = np.linalg.svd(L)
    v = vh[-1, :].conj()
    rho = v.reshape((DIM, DIM))
    rho = 0.5 * (rho + rho.conj().T)
    # shift to physical if needed
    rho = rho / np.trace(rho)
    # ensure positivity by tiny mix with identity if needed
    evals = np.linalg.eigvalsh(rho)
    if np.min(evals) < -1e-8:
        # fall back: long evolution from mixed state
        rho = np.eye(DIM, dtype=complex) / DIM
        rho = evolve_leads(rho, params, t=50.0 / max(params.gamma_L, params.gamma_R, 1e-6))
    return rho


def spin_coherence(rho: np.ndarray) -> complex:
    """ρ_{↑↓} = ρ_{12} in our basis."""
    return complex(rho[1, 2])


def populations(rho: np.ndarray) -> Tuple[float, float, float]:
    return float(np.real(rho[0, 0])), float(np.real(rho[1, 1])), float(np.real(rho[2, 2]))
