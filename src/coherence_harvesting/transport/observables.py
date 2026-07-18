"""Transport observables (coarse sequential-tunneling estimates)."""

from __future__ import annotations

import numpy as np

from .spin_valve import SpinValveParams, fermi, free_dot_hamiltonian, lead_gamma_matrix


def current_estimate(rho: np.ndarray, params: SpinValveParams) -> float:
    """Net particle current L → R (positive = left to right) at state ρ.

    Uses a sequential-tunneling golden-rule estimate:
    I ~ Γ_L^{in} p0 - Γ_L^{out} p1  balanced against right lead.
    This is a transparent proxy for scans, not a full NEGF current.
    """
    H = free_dot_hamiltonian(params)
    Eu = float(np.real(H[1, 1]))
    Ed = float(np.real(H[2, 2]))
    E_spin = 0.5 * (Eu + Ed)

    p0 = float(np.real(rho[0, 0]))
    p1 = float(np.real(rho[1, 1] + rho[2, 2]))

    def lead_rates(gamma, p, th, ph, T, mu):
        Gam = lead_gamma_matrix(gamma, p, th, ph)
        # total in/out rates ~ Tr(Γ) * f / 2 channels averaged
        gtot = float(np.real(np.trace(Gam)))
        f = fermi(E_spin, mu, T)
        return gtot * f, gtot * (1.0 - f)

    Lin, Lout = lead_rates(
        params.gamma_L, params.p_L, 0.0, 0.0, params.T_L, params.mu_L
    )
    Rin, Rout = lead_rates(
        params.gamma_R, params.p_R, params.theta_R, params.phi_R, params.T_R, params.mu_R
    )

    # net particles leaving left lead (into dot) minus leaving right lead
    I_L = Lin * p0 - Lout * p1
    I_R = Rin * p0 - Rout * p1
    # stationarity would give I_L + I_R ≈ 0; net transport current ≈ I_L
    return float(I_L)


def electrical_power(I: float, params: SpinValveParams) -> float:
    """P_el = I * (μ_L - μ_R)  (particle current × bias)."""
    return float(I * (params.mu_L - params.mu_R))


def heat_current_proxy(rho: np.ndarray, params: SpinValveParams) -> float:
    """Very coarse hot-lead heat proxy ~ energy flow from left lead."""
    H = free_dot_hamiltonian(params)
    E = float(np.real(np.trace(H @ rho)))
    I = current_estimate(rho, params)
    # Q_h ~ I * (E - mu_L) rough
    return float(I * (E - params.mu_L))
