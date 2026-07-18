"""Smoke tests for the spin-valve collision engine."""

from __future__ import annotations

import numpy as np

from coherence_harvesting.transport.engine import CollisionEngine
from coherence_harvesting.transport.nonsecular import steady_state_leads, spin_coherence
from coherence_harvesting.transport.spin_valve import SpinValveParams


def test_lead_ness_is_physical() -> None:
    params = SpinValveParams(theta_R=np.pi / 2, Delta=0.2)
    rho = steady_state_leads(params)
    assert abs(np.trace(rho) - 1) < 1e-8
    evals = np.linalg.eigvalsh(rho)
    assert np.min(evals) > -1e-8


def test_noncollinear_generates_coherence() -> None:
    collinear = SpinValveParams(theta_R=0.0, Delta=0.15, p_L=0.8, p_R=0.8)
    tilted = SpinValveParams(theta_R=np.pi / 2, Delta=0.15, p_L=0.8, p_R=0.8)
    c0 = abs(spin_coherence(steady_state_leads(collinear)))
    c1 = abs(spin_coherence(steady_state_leads(tilted)))
    # tilted should typically produce more energy-basis coherence near degeneracy
    assert c1 >= c0 - 1e-6


def test_engine_converges() -> None:
    params = SpinValveParams(
        Delta=0.25,
        g=6.0,
        tau=0.1,
        T_period=1.0,
        theta_R=np.pi / 2,
    )
    res = CollisionEngine(params).find_fixed_point(n_max=300, tol=1e-9)
    assert res.converged
    assert abs(np.trace(res.rho_D) - 1) < 1e-8
    assert res.W_A >= -1e-12
    assert res.P_erg >= -1e-12
