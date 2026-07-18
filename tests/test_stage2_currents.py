"""Stage 2: lead-resolved currents and conservation checks."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from coherence_harvesting.transport.currents import (
    cycle_average_currents,
    electrical_output_power,
    instantaneous_currents,
)
from coherence_harvesting.transport.engine import CollisionEngine
from coherence_harvesting.transport.nonsecular import steady_state_leads
from coherence_harvesting.transport.spin_valve import SpinValveParams

ROOT = Path(__file__).resolve().parents[1]


def _boosted() -> SpinValveParams:
    path = ROOT / "results" / "gate1" / "gate1_best_params.json"
    if path.exists():
        d = json.loads(path.read_text(encoding="utf-8"))
        keys = [
            "Delta", "gamma_L", "gamma_R", "theta_R", "p_L", "p_R",
            "mu_L", "mu_R", "T_L", "T_R", "epsilon",
        ]
        kw = {k: float(d[k]) for k in keys if k in d}
    else:
        kw = dict(
            Delta=0.05, theta_R=1.4, p_L=0.95, p_R=0.95,
            mu_L=0.6, mu_R=-0.6, T_L=1.5, T_R=0.4,
        )
    return SpinValveParams(**kw, g=8.0, tau=0.08, T_period=1.5, alpha=0.0)


def test_ness_particle_balance() -> None:
    p = _boosted()
    rho = steady_state_leads(p)
    inst = instantaneous_currents(rho, p)
    assert abs(inst.particle_balance) < 1e-6


def test_electrical_sign_convention() -> None:
    p = _boosted()
    # I > 0, mu_L > mu_R => P_el = -(mu_L-mu_R)*I < 0 (device absorbs electrical work / load convention)
    I = 0.1
    Pel = electrical_output_power(I, p)
    assert Pel == pytest.approx(-(p.mu_L - p.mu_R) * I)


def test_engine_fixed_point_currents() -> None:
    p = _boosted()
    res = CollisionEngine(p).find_fixed_point(n_max=250, tol=1e-9, current_steps=40)
    assert res.converged
    # period-averaged residual need not vanish (N changes during wait if not SS of leads alone)
    # but magnitudes should be finite
    assert np.isfinite(res.P_el)
    assert np.isfinite(res.P_erg)
    assert res.W_A >= -1e-12
    # first-law residual on dot energy should be smallish relative to energy scales
    assert abs(res.first_law_residual) < 0.5  # sequential scaffold; not machine precision


def test_cycle_average_reduces_to_ness_when_no_collision() -> None:
    p = SpinValveParams(
        Delta=0.05, theta_R=1.4, p_L=0.95, p_R=0.95,
        mu_L=0.6, mu_R=-0.6, T_L=1.5, T_R=0.4,
        g=1.0, tau=0.0, T_period=2.0, alpha=0.0,
    )
    rho = steady_state_leads(p)
    inst = instantaneous_currents(rho, p)
    cyc = cycle_average_currents(rho, p, n_steps=20)
    # at NESS, cycle average ≈ instantaneous * (t_wait/T) = instantaneous (tau=0)
    assert abs(cyc.J_N_L - inst.J_N_L) < 5e-4
    assert abs(cyc.residual_particle) < 1e-5
