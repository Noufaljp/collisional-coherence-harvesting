"""Verify analytic collision map against exact joint unitary."""

from __future__ import annotations

import numpy as np
import pytest

from coherence_harvesting.companion.collision import (
    SystemState,
    analytic_ancilla_bloch,
    analytic_system_map,
    numerical_collision,
    random_valid_doublet_state,
)


@pytest.mark.parametrize("theta", [0.1, 0.5, 1.0, np.pi / 2])
@pytest.mark.parametrize("alpha", [0.0, 0.25, 0.5])
def test_analytic_matches_numerical(theta: float, alpha: float) -> None:
    rng = np.random.default_rng(42)
    for _ in range(8):
        st = random_valid_doublet_state(rng)
        # force real C for simpler ancilla y-check sometimes; keep general
        s2, d2, C2 = analytic_system_map(st.s, st.d, st.C, theta, alpha)
        rho_S_out, rho_A_out = numerical_collision(st.rho(), alpha, theta)
        st_num = SystemState.from_rho(rho_S_out)

        assert abs(st_num.s - s2) < 1e-9
        assert abs(st_num.d - d2) < 1e-9
        assert abs(st_num.C - C2) < 1e-9

        x, y, z = analytic_ancilla_bloch(st.s, st.d, st.C, theta, alpha)
        # numerical Bloch from rho_A with basis |↓>,|↑>
        p_up = float(np.real(rho_A_out[1, 1]))
        z_n = 2 * p_up - 1
        coh = rho_A_out[1, 0]  # ρ_{↑↓}
        # Match paper convention: x=2 Re ρ_{↑↓}, y=-2 Im ρ_{↑↓}
        x_n = 2 * np.real(coh)
        y_n = -2 * np.imag(coh)
        assert abs(z - z_n) < 1e-9
        assert abs(x - x_n) < 1e-9
        assert abs(y - y_n) < 1e-9


def test_s_invariant() -> None:
    st = SystemState(s=0.4, d=0.1, C=0.05 + 0.02j, p0=0.6)
    s2, _, _ = analytic_system_map(st.s, st.d, st.C, theta=0.7, alpha=0.0)
    assert abs(s2 - st.s) < 1e-14


def test_alpha_half_null_local_coherence() -> None:
    st = SystemState(s=0.5, d=0.0, C=0.2, p0=0.5)
    x, y, z = analytic_ancilla_bloch(st.s, st.d, st.C, theta=0.4, alpha=0.5)
    assert abs(x) < 1e-14
    assert abs(y) < 1e-14
