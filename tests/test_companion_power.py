"""Companion power, ergotropy, physicality, and accessibility tests."""

from __future__ import annotations

import numpy as np
import pytest

from coherence_harvesting.companion.baths import (
    DirectedLeakageParams,
    directed_leakage_fixed_point,
    reset_fixed_point_C,
)
from coherence_harvesting.companion.ergotropy import (
    coherent_incoherent_ergotropy,
    one_copy_accessible_work,
    qubit_ergotropy,
    two_copy_accessible_work,
    two_copy_accessible_work_matrix,
)
from coherence_harvesting.companion.physicality import (
    UnphysicalStateError,
    check_companion_params,
    check_doublet_physical,
)
from coherence_harvesting.companion.power import (
    CompanionParams,
    finite_coupling_theta_min,
    impedance_matched_r,
    optimize_power,
    power_curve,
    power_curve_directed,
)


def test_reset_fixed_point_limits() -> None:
    c0 = 0.25
    C_slow = reset_fixed_point_C(c0, theta=0.3, gamma_C=1.0, r=1e-3, delta=0.0)
    assert abs(C_slow - c0) < 1e-3
    C_fast = reset_fixed_point_C(c0, theta=0.3, gamma_C=1.0, r=1e3, delta=0.0)
    assert abs(C_fast) < 0.05


def test_power_has_interior_maximum() -> None:
    params = CompanionParams(theta=0.4, Delta=0.2, c0=0.25, gamma_C=1.0)
    r, P = power_curve(params)
    r_opt, P_max = optimize_power(params)
    assert P_max >= np.max(P) * 0.98
    assert r.min() < r_opt < r.max()
    r_imp = impedance_matched_r(1.0, 0.4, 0.2)
    assert 0.2 * r_imp < r_opt < 5 * r_imp


def test_directed_leakage_fixed_point_physical() -> None:
    params = DirectedLeakageParams(
        Gamma_up=0.3, Gamma_down=0.7, kappa_D=0.5, tau_c=1.0
    )
    v = directed_leakage_fixed_point(params, theta=0.5)
    assert np.all(v >= -1e-10)
    assert float(v.sum()) <= 1.0 + 1e-8


def test_directed_leakage_power_curve_runs() -> None:
    rr = np.geomspace(0.1, 20, 12)
    _, P = power_curve_directed(
        0.5, 0.5, 1.0, theta=0.35, Delta=0.15, r_values=rr, exact=True
    )
    assert np.all(np.isfinite(P))
    assert np.max(P) > 0


def test_ergotropy_passive_ground() -> None:
    assert abs(qubit_ergotropy(z=-1.0, x=0.0, y=0.0, Delta=1.0)) < 1e-14


def test_coherent_incoherent_split() -> None:
    # ground-biased with coherence: W_inc = 0, W_coh = W_total
    parts = coherent_incoherent_ergotropy(z=-0.5, x=0.0, y=0.4, Delta=1.0)
    assert parts["W_inc"] == 0.0
    assert abs(parts["W_coh"] - parts["W_total"]) < 1e-12
    # inverted population: incoherent ergotropy present
    parts2 = coherent_incoherent_ergotropy(z=0.5, x=0.0, y=0.0, Delta=1.0)
    assert parts2["W_inc"] == pytest.approx(0.5)
    assert parts2["W_coh"] == pytest.approx(0.0)


def test_one_copy_accessibility_policy() -> None:
    z, y = -0.5, 0.3
    W_ref = one_copy_accessible_work(z, 0.0, y, 1.0, has_phase_reference=True)
    W_noref = one_copy_accessible_work(z, 0.0, y, 1.0, has_phase_reference=False)
    assert W_noref == 0.0
    assert W_ref > 0.0


def test_two_copy_piecewise_vs_matrix() -> None:
    rng = np.random.default_rng(1)
    Delta = 1.0
    for _ in range(40):
        a = float(rng.uniform(0.5, 0.95))
        b = 1.0 - a
        cmax = np.sqrt(a * b)
        c = float(rng.uniform(0.0, cmax))
        W_an = two_copy_accessible_work(a, b, c, Delta)
        W_mx = two_copy_accessible_work_matrix(a, b, c, Delta)
        assert abs(W_an - W_mx) < 1e-9


def test_two_copy_regimes() -> None:
    # regime 1: inactive
    assert two_copy_accessible_work(0.95, 0.05, 0.05, 1.0) == 0.0
    # regime 2: first activation (a=0.7,b=0.3): thr1=b(a-b)=0.12, thr2=a(a-b)=0.28
    a, b = 0.7, 0.3
    c2 = 0.20  # between 0.12 and 0.28
    c = np.sqrt(c2)
    W = two_copy_accessible_work(a, b, c, 1.0)
    assert abs(W - (c2 - b * (a - b))) < 1e-12
    # regime 3: a=0.6,b=0.4, |c|=0.45 → c2=0.2025; thr1=0.08, thr2=0.12, ab=0.24
    W3 = two_copy_accessible_work(0.6, 0.4, 0.45, 1.0)
    assert abs(W3 - (2 * 0.45**2 - (0.6 - 0.4))) < 1e-12
    assert abs(W3 - two_copy_accessible_work_matrix(0.6, 0.4, 0.45, 1.0)) < 1e-9


def test_physicality_rejects_bad_params() -> None:
    with pytest.raises(UnphysicalStateError):
        CompanionParams(c0=0.4, s_ss=0.5)
    with pytest.raises(UnphysicalStateError):
        check_doublet_physical(0.5, 0.0, 0.4)
    assert check_companion_params(1.0, 1.0, 0.25, 0.5, 0.2, 0.3, 0.0)


def test_finite_coupling_theta_min() -> None:
    th = finite_coupling_theta_min(gamma_C=1.0, g=20.0, delta_over_gamma=0.0)
    assert abs(th - 2.0 / 20.0) < 1e-14
