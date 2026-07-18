"""Companion power and fixed-point smoke tests."""

from __future__ import annotations

import numpy as np

from coherence_harvesting.companion.baths import (
    DirectedLeakageParams,
    directed_leakage_fixed_point,
    reset_fixed_point_C,
)
from coherence_harvesting.companion.ergotropy import (
    qubit_ergotropy,
    two_copy_accessible_work,
)
from coherence_harvesting.companion.power import (
    CompanionParams,
    impedance_matched_r,
    optimize_power,
    power_curve,
)


def test_reset_fixed_point_limits() -> None:
    c0 = 0.25
    # slow collisions: C* → c0
    C_slow = reset_fixed_point_C(c0, theta=0.3, gamma_C=1.0, r=1e-3, delta=0.0)
    assert abs(C_slow - c0) < 1e-3
    # fast collisions: C* → 0
    C_fast = reset_fixed_point_C(c0, theta=0.3, gamma_C=1.0, r=1e3, delta=0.0)
    assert abs(C_fast) < 0.05


def test_power_has_interior_maximum() -> None:
    params = CompanionParams(theta=0.4, Delta=0.2, c0=0.25, gamma_C=1.0)
    r, P = power_curve(params)
    r_opt, P_max = optimize_power(params)
    assert P_max >= np.max(P) * 0.98
    assert r.min() < r_opt < r.max()
    # near impedance matching order of magnitude
    r_imp = impedance_matched_r(1.0, 0.4, 0.2)
    assert 0.2 * r_imp < r_opt < 5 * r_imp


def test_directed_leakage_fixed_point_physical() -> None:
    params = DirectedLeakageParams(
        Gamma_up=0.3, Gamma_down=0.7, kappa_D=0.5, tau_c=1.0
    )
    v = directed_leakage_fixed_point(params, theta=0.5)
    assert np.all(v >= -1e-10)
    assert float(v.sum()) <= 1.0 + 1e-8


def test_ergotropy_passive_ground() -> None:
    # pure ground: z=-1, r=1 → W=0
    assert abs(qubit_ergotropy(z=-1.0, x=0.0, y=0.0, Delta=1.0)) < 1e-14


def test_two_copy_threshold() -> None:
    # weak coherent, ground biased: typically zero
    W = two_copy_accessible_work(a=0.95, b=0.05, c_abs=0.05, Delta=1.0)
    assert W == 0.0
    # large coherence can activate
    W2 = two_copy_accessible_work(a=0.6, b=0.4, c_abs=0.45, Delta=1.0)
    assert W2 > 0.0
