"""Lead-tagged jump channels and Liouvillians.

Each tunneling process is labeled by lead side so that particle and energy
currents can be reconstructed from the *same* dissipators that generate the
dynamics:

    J_N,α(ρ) = Re Tr[ N_D  L_α(ρ) ]
    J_E,α(ρ) = Re Tr[ H_D  L_α(ρ) ]
    J_Q,α(ρ) = J_E,α - μ_α J_N,α

where L_α is the Lindblad dissipator contribution of lead α only.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np

from .spin_valve import SpinValveParams, fermi, free_dot_hamiltonian, lead_gamma_matrix

Side = Literal["L", "R"]
DIM = 3

# Number operator on the Coulomb-blockade Fock space {|0>,|↑>,|↓>}
N_OP = np.diag([0.0, 1.0, 1.0]).astype(complex)


@dataclass(frozen=True)
class JumpChannel:
    """One jump operator with rate and lead tag."""

    side: Side
    op: np.ndarray  # system jump operator L
    rate: float


def build_channels(params: SpinValveParams) -> list[JumpChannel]:
    """Sequential-tunneling channels for L and R (spinor eigenchannels of Γ)."""
    H = free_dot_hamiltonian(params)
    Eu = float(np.real(H[1, 1]))
    Ed = float(np.real(H[2, 2]))

    specs: list[tuple[Side, float, float, float, float, float, float]] = [
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
    ]
    channels: list[JumpChannel] = []
    for side, gamma, p, th, ph, T, mu in specs:
        Gam = lead_gamma_matrix(gamma, p, th, ph)
        evals, evecs = np.linalg.eigh(Gam)
        for k in range(2):
            lam = float(max(np.real(evals[k]), 0.0))
            if lam < 1e-14:
                continue
            cu = evecs[0, k]
            cd = evecs[1, k]
            L_in = np.zeros((DIM, DIM), dtype=complex)
            L_in[1, 0] = cu
            L_in[2, 0] = cd
            E_spin = float(np.real(abs(cu) ** 2 * Eu + abs(cd) ** 2 * Ed))
            f = fermi(E_spin, mu, T)
            if lam * f > 0:
                channels.append(JumpChannel(side, L_in, lam * f))
            if lam * (1.0 - f) > 0:
                channels.append(JumpChannel(side, L_in.conj().T, lam * (1.0 - f)))
    return channels


def _dissipator(L: np.ndarray, rho: np.ndarray) -> np.ndarray:
    Ld = L.conj().T
    return L @ rho @ Ld - 0.5 * (Ld @ L @ rho + rho @ Ld @ L)


def dissipator_action(
    channels: list[JumpChannel], rho: np.ndarray, side: Side | None = None
) -> np.ndarray:
    """Apply ∑ rate D[L] for channels matching side (or all if side is None)."""
    out = np.zeros_like(rho, dtype=complex)
    for ch in channels:
        if side is not None and ch.side != side:
            continue
        if ch.rate <= 0:
            continue
        out += ch.rate * _dissipator(ch.op, rho)
    return out


def hamiltonian_superop(H: np.ndarray) -> np.ndarray:
    I = np.eye(H.shape[0], dtype=complex)
    return -1j * (np.kron(H, I) - np.kron(I, H.T))


def dissipator_superop(channels: list[JumpChannel], side: Side | None = None) -> np.ndarray:
    """Superoperator for dissipative part only (column-stacked)."""
    dim = DIM
    I = np.eye(dim, dtype=complex)
    Lsup = np.zeros((dim * dim, dim * dim), dtype=complex)
    for ch in channels:
        if side is not None and ch.side != side:
            continue
        if ch.rate <= 0:
            continue
        Lop = ch.op
        Ld = Lop.conj().T
        LL = Ld @ Lop
        Lsup += ch.rate * (
            np.kron(Lop, Lop.conj())
            - 0.5 * (np.kron(LL, I) + np.kron(I, LL.T))
        )
    return Lsup


def full_liouvillian(params: SpinValveParams, channels: list[JumpChannel] | None = None) -> np.ndarray:
    if channels is None:
        channels = build_channels(params)
    H = free_dot_hamiltonian(params)
    return hamiltonian_superop(H) + dissipator_superop(channels, side=None)


def mu_of(params: SpinValveParams, side: Side) -> float:
    return params.mu_L if side == "L" else params.mu_R
