"""Diagnostics for Gate 1–2: positivity, spin resource, occupation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from .nonsecular import populations, spin_coherence, steady_state_leads
from .spin_valve import SpinValveParams


@dataclass
class NessDiagnostics:
    """Summary of continuous-lead NESS (no collisions)."""

    params: dict[str, Any]
    rho: np.ndarray
    p0: float
    p_up: float
    p_dn: float
    P1: float
    C: complex
    abs_C: float
    S_perp: float
    S_z: float
    min_eig: float
    trace: float
    hermiticity_err: float
    positive: bool
    method: str


def rho_diagnostics(rho: np.ndarray, params: SpinValveParams, method: str = "ness") -> NessDiagnostics:
    rho = np.asarray(rho, dtype=complex)
    rho_h = 0.5 * (rho + rho.conj().T)
    p0, pu, pd = populations(rho_h)
    C = spin_coherence(rho_h)
    # Spin expectation in singly occupied sector (unnormalized by P1):
    # S_x = 2 Re ρ_↑↓, S_y = 2 Im ρ_↑↓, S_z = ρ_↑↑ - ρ_↓↓
    Sx = 2.0 * np.real(C)
    Sy = 2.0 * np.imag(C)
    Sz = pu - pd
    S_perp = float(np.sqrt(Sx * Sx + Sy * Sy))
    evals = np.linalg.eigvalsh(rho_h)
    min_eig = float(np.min(evals))
    tr = float(np.real(np.trace(rho_h)))
    herm = float(np.linalg.norm(rho - rho.conj().T))
    return NessDiagnostics(
        params={
            "Delta": params.Delta,
            "gamma_L": params.gamma_L,
            "gamma_R": params.gamma_R,
            "theta_R": params.theta_R,
            "p_L": params.p_L,
            "p_R": params.p_R,
            "T_L": params.T_L,
            "T_R": params.T_R,
            "mu_L": params.mu_L,
            "mu_R": params.mu_R,
            "epsilon": params.epsilon,
        },
        rho=rho_h,
        p0=p0,
        p_up=pu,
        p_dn=pd,
        P1=pu + pd,
        C=C,
        abs_C=float(abs(C)),
        S_perp=S_perp,
        S_z=float(Sz),
        min_eig=min_eig,
        trace=tr,
        hermiticity_err=herm,
        positive=min_eig >= -1e-8,
        method=method,
    )


def ness_diagnostics(params: SpinValveParams) -> NessDiagnostics:
    rho = steady_state_leads(params)
    return rho_diagnostics(rho, params, method="lead_ness")


def base_params(**overrides) -> SpinValveParams:
    """Default physical-ish window for Gate 1 (near-degenerate, non-collinear)."""
    kw = dict(
        epsilon=0.0,
        Delta=0.3,
        gamma_L=1.0,
        gamma_R=1.0,
        p_L=0.7,
        p_R=0.7,
        theta_R=float(np.pi / 2),
        phi_R=0.0,
        T_L=1.2,
        T_R=0.6,
        mu_L=0.4,
        mu_R=-0.4,
    )
    kw.update(overrides)
    return SpinValveParams(**kw)
