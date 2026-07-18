"""Lead-resolved particle/energy/heat currents and cycle averages.

Sign convention (see docs/engine/SIGN_CONVENTION.md)
----------------------------------------------------
- J_N,α(ρ) = Re Tr[N L_α(ρ)] : rate of change of *dot* particle number due to lead α.
  J_N,L > 0 means particles enter the dot from the left lead.
- At continuous NESS: J_N,L + J_N,R ≈ 0.
- Transport particle current (L → R through the device):
      I ≡ J_N,L   (= −J_N,R at NESS)
- Electrical *output* power (engine convention, ħ = e = 1):
      P_el ≡ −(μ_L − μ_R) I
  so P_el > 0 when the device delivers work to the bias circuit.
- Heat current into the system from lead α:
      J_Q,α = J_E,α − μ_α J_N,α ,  J_E,α = Re Tr[H_D L_α(ρ)]

During a collision the leads are off; period averages use only the waiting
interval and divide by the full period T.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.linalg import expm

from .channels import (
    N_OP,
    JumpChannel,
    build_channels,
    dissipator_action,
    full_liouvillian,
    mu_of,
)
from .spin_valve import SpinValveParams, free_dot_hamiltonian


@dataclass
class InstantCurrents:
    J_N_L: float
    J_N_R: float
    J_E_L: float
    J_E_R: float
    J_Q_L: float
    J_Q_R: float

    @property
    def I(self) -> float:
        """Particle current L→R proxy: into-dot from left."""
        return self.J_N_L

    @property
    def particle_balance(self) -> float:
        return self.J_N_L + self.J_N_R

    @property
    def energy_balance_leads(self) -> float:
        return self.J_E_L + self.J_E_R


@dataclass
class CycleAveragedCurrents:
    """Period averages (collision contributes zero lead current)."""

    J_N_L: float
    J_N_R: float
    J_E_L: float
    J_E_R: float
    J_Q_L: float
    J_Q_R: float
    P_el: float
    I: float
    residual_particle: float  # J_N_L + J_N_R (should be small if N almost steady in wait)
    n_steps: int
    t_wait: float
    T_period: float


def instantaneous_currents(
    rho: np.ndarray,
    params: SpinValveParams,
    channels: list[JumpChannel] | None = None,
) -> InstantCurrents:
    rho = np.asarray(rho, dtype=complex)
    if channels is None:
        channels = build_channels(params)
    H = free_dot_hamiltonian(params)

    def for_side(side: str) -> tuple[float, float, float]:
        Lrho = dissipator_action(channels, rho, side=side)  # type: ignore[arg-type]
        JN = float(np.real(np.trace(N_OP @ Lrho)))
        JE = float(np.real(np.trace(H @ Lrho)))
        JQ = JE - mu_of(params, side) * JN  # type: ignore[arg-type]
        return JN, JE, JQ

    jnl, jel, jql = for_side("L")
    jnr, jer, jqr = for_side("R")
    return InstantCurrents(jnl, jnr, jel, jer, jql, jqr)


def electrical_output_power(I: float, params: SpinValveParams) -> float:
    """P_el = −(μ_L − μ_R) I  with I = J_N,L (into-dot from left)."""
    return float(-(params.mu_L - params.mu_R) * I)


def cycle_average_currents(
    rho_post_collision: np.ndarray,
    params: SpinValveParams,
    n_steps: int = 80,
) -> CycleAveragedCurrents:
    """Integrate lead currents over the waiting interval; average over full period T.

    Starts from the post-collision state (start of waiting). Evolves under the
    full lead Liouvillian. Uses trapezoidal rule.
    """
    t_wait = float(params.waiting_time)
    T = float(params.T_period)
    channels = build_channels(params)
    L = full_liouvillian(params, channels)

    if t_wait <= 0 or n_steps < 1:
        inst = instantaneous_currents(rho_post_collision, params, channels)
        I = inst.I
        return CycleAveragedCurrents(
            J_N_L=0.0,
            J_N_R=0.0,
            J_E_L=0.0,
            J_E_R=0.0,
            J_Q_L=0.0,
            J_Q_R=0.0,
            P_el=electrical_output_power(0.0, params),
            I=0.0,
            residual_particle=0.0,
            n_steps=0,
            t_wait=t_wait,
            T_period=T,
        )

    ts = np.linspace(0.0, t_wait, n_steps + 1)
    samples: list[InstantCurrents] = []
    rho = np.asarray(rho_post_collision, dtype=complex).copy()
    # Precompute propagator for dt
    dt = t_wait / n_steps
    Udt = expm(L * dt)

    for i in range(n_steps + 1):
        samples.append(instantaneous_currents(rho, params, channels))
        if i < n_steps:
            v = rho.reshape(-1)
            v = Udt @ v
            rho = v.reshape((3, 3))
            rho = 0.5 * (rho + rho.conj().T)
            tr = np.trace(rho)
            if abs(tr) > 0:
                rho = rho / tr

    def trap_avg(key: str) -> float:
        ys = np.array([getattr(s, key) for s in samples], dtype=float)
        # ∫_0^{t_wait} y dt / T
        trap = getattr(np, "trapezoid", None) or np.trapz
        integ = float(trap(ys, ts))
        return integ / T

    JN_L = trap_avg("J_N_L")
    JN_R = trap_avg("J_N_R")
    JE_L = trap_avg("J_E_L")
    JE_R = trap_avg("J_E_R")
    JQ_L = trap_avg("J_Q_L")
    JQ_R = trap_avg("J_Q_R")
    I = JN_L
    return CycleAveragedCurrents(
        J_N_L=JN_L,
        J_N_R=JN_R,
        J_E_L=JE_L,
        J_E_R=JE_R,
        J_Q_L=JQ_L,
        J_Q_R=JQ_R,
        P_el=electrical_output_power(I, params),
        I=I,
        residual_particle=JN_L + JN_R,
        n_steps=n_steps,
        t_wait=t_wait,
        T_period=T,
    )


# ---------------------------------------------------------------------------
# Backward-compatible thin wrappers (proxy API deprecated)
# ---------------------------------------------------------------------------


def current_estimate(rho: np.ndarray, params: SpinValveParams) -> float:
    """Deprecated proxy name: now returns lead-resolved J_N,L at state ρ."""
    return instantaneous_currents(rho, params).J_N_L


def electrical_power(I: float, params: SpinValveParams) -> float:
    """Deprecated name: electrical *output* power from particle current I=J_N,L."""
    return electrical_output_power(I, params)


def heat_current_proxy(rho: np.ndarray, params: SpinValveParams) -> float:
    """Heat into the system from the left lead at state ρ."""
    return instantaneous_currents(rho, params).J_Q_L
