"""Lead generator for the Coulomb-blockade spin valve.

Uses lead-tagged sequential-tunneling / spinor-jump channels
(see ``channels.py``). Completely positive by construction; not a derived
microscopic Redfield equation — validity is limited to the sequential-
tunneling scaffold used for Gates 1–2 and Stage 2 bookkeeping.
"""

from __future__ import annotations

from typing import Tuple

import numpy as np
from scipy.linalg import expm

from .channels import build_channels, full_liouvillian
from .spin_valve import SpinValveParams

DIM = 3


def lead_liouvillian(params: SpinValveParams, side: str | None = None) -> np.ndarray:
    """Superoperator L with ρ̇ = L ρ (column-stacked).

    If ``side`` is 'L' or 'R', return only that lead's dissipator (no Hamiltonian
    drive). If ``side`` is None, return full H + both leads.
    """
    from .channels import dissipator_superop

    channels = build_channels(params)
    if side is None:
        return full_liouvillian(params, channels)
    return dissipator_superop(channels, side=side)  # type: ignore[arg-type]


def evolve_leads(rho: np.ndarray, params: SpinValveParams, t: float) -> np.ndarray:
    """Evolve ρ under the full lead Liouvillian for time t."""
    if t <= 0:
        return np.asarray(rho, dtype=complex).copy()
    L = full_liouvillian(params)
    v = np.asarray(rho, dtype=complex).reshape(-1)
    v_t = expm(L * t) @ v
    rho_t = v_t.reshape((DIM, DIM))
    rho_t = 0.5 * (rho_t + rho_t.conj().T)
    tr = np.trace(rho_t)
    if abs(tr) > 0:
        rho_t = rho_t / tr
    return rho_t


def steady_state_leads(params: SpinValveParams, tol: float = 1e-10) -> np.ndarray:
    """Nullspace of the full lead Liouvillian (continuous NESS, no collisions)."""
    L = full_liouvillian(params)
    _u, _s, vh = np.linalg.svd(L)
    v = vh[-1, :].conj()
    rho = v.reshape((DIM, DIM))
    rho = 0.5 * (rho + rho.conj().T)
    rho = rho / np.trace(rho)
    evals = np.linalg.eigvalsh(rho)
    if np.min(evals) < -1e-8:
        rho = np.eye(DIM, dtype=complex) / DIM
        rho = evolve_leads(rho, params, t=50.0 / max(params.gamma_L, params.gamma_R, 1e-6))
    return rho


def spin_coherence(rho: np.ndarray) -> complex:
    return complex(rho[1, 2])


def populations(rho: np.ndarray) -> Tuple[float, float, float]:
    return float(np.real(rho[0, 0])), float(np.real(rho[1, 1])), float(np.real(rho[2, 2]))
