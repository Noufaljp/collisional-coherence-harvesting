"""Stroboscopic collision engine with lead-resolved bookkeeping."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np
from scipy.linalg import expm

from ..companion.ergotropy import (
    bloch_from_rho,
    coherent_incoherent_ergotropy,
    qubit_ergotropy_from_rho,
    two_copy_from_bloch,
)
from .currents import CycleAveragedCurrents, cycle_average_currents, instantaneous_currents
from .nonsecular import evolve_leads, populations, spin_coherence, steady_state_leads
from .spin_valve import SpinValveParams, free_dot_hamiltonian, joint_exchange_hamiltonian


@dataclass
class EngineResult:
    """Fixed-point engine report with Stage-2 currents and battery diagnostics."""

    rho_D: np.ndarray  # post-collision fixed point
    rho_wait: np.ndarray  # pre-collision (end of wait)
    rho_A_out: np.ndarray
    # electrical / heat (cycle-averaged over full period T)
    P_el: float
    I: float
    J_N_L: float
    J_N_R: float
    J_E_L: float
    J_E_R: float
    J_Q_L: float
    J_Q_R: float
    residual_particle_avg: float
    # continuous-NESS diagnostics on wait endpoint (instantaneous)
    particle_balance_instant: float
    # battery
    P_erg: float
    W_A: float
    W_coh: float
    W_inc: float
    W_acc2: float
    E_A: float  # Tr(ρ_A H_A)
    # state
    coherence: complex
    pops: tuple[float, float, float]
    n_iter: int
    converged: bool
    # energy bookkeeping on the dot over one period at FP
    dE_wait: float
    dE_collision: float
    dN_wait: float
    dN_collision: float
    first_law_residual: float
    notes: str = ""


def collision_unitary(params: SpinValveParams) -> np.ndarray:
    H = joint_exchange_hamiltonian(params.g)
    return expm(-1j * H * params.tau)


def apply_collision(
    rho_D: np.ndarray, params: SpinValveParams
) -> tuple[np.ndarray, np.ndarray]:
    """One exchange collision with a fresh ancilla; return (ρ_D', ρ_A_out)."""
    alpha = params.alpha
    rho_A = np.diag([1.0 - alpha, alpha]).astype(complex)
    rho = np.kron(rho_D, rho_A)
    U = collision_unitary(params)
    rho_out = U @ rho @ U.conj().T

    rho_D_out = np.zeros((3, 3), dtype=complex)
    for a in range(2):
        rho_D_out += rho_out[a::2, a::2]

    rho_A_out = np.zeros((2, 2), dtype=complex)
    for s in range(3):
        rho_A_out += rho_out[2 * s : 2 * s + 2, 2 * s : 2 * s + 2]

    rho_D_out = 0.5 * (rho_D_out + rho_D_out.conj().T)
    rho_A_out = 0.5 * (rho_A_out + rho_A_out.conj().T)
    return rho_D_out, rho_A_out


def _dot_energy(rho: np.ndarray, params: SpinValveParams) -> float:
    H = free_dot_hamiltonian(params)
    return float(np.real(np.trace(H @ rho)))


def _dot_N(rho: np.ndarray) -> float:
    return float(np.real(rho[1, 1] + rho[2, 2]))


class CollisionEngine:
    """Stroboscopic map: lead waiting → collision → repeat."""

    def __init__(self, params: SpinValveParams):
        self.params = params

    def step(self, rho_D: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        rho_wait = evolve_leads(rho_D, self.params, self.params.waiting_time)
        return apply_collision(rho_wait, self.params)

    def find_fixed_point(
        self,
        rho0: Optional[np.ndarray] = None,
        n_max: int = 400,
        tol: float = 1e-10,
        current_steps: int = 80,
    ) -> EngineResult:
        if rho0 is None:
            rho = steady_state_leads(self.params)
        else:
            rho = np.asarray(rho0, dtype=complex).copy()

        rho_A_out = np.diag([1.0 - self.params.alpha, self.params.alpha]).astype(complex)
        converged = False
        n_iter = 0
        for n_iter in range(1, n_max + 1):
            rho_new, rho_A_out = self.step(rho)
            err = np.linalg.norm(rho_new - rho)
            rho = rho_new
            if err < tol:
                converged = True
                break

        # Period structure at FP:
        #   rho = post-collision
        #   rho_wait = after leads for waiting_time (pre-collision)
        #   apply_collision(rho_wait) ≈ rho
        rho_wait = evolve_leads(rho, self.params, self.params.waiting_time)
        rho_check, rho_A_out = apply_collision(rho_wait, self.params)

        cyc = cycle_average_currents(rho, self.params, n_steps=current_steps)
        inst_wait = instantaneous_currents(rho_wait, self.params)

        W_A = qubit_ergotropy_from_rho(rho_A_out, Delta=float(self.params.Delta_A))
        x, y, z = bloch_from_rho(rho_A_out)
        parts = coherent_incoherent_ergotropy(z, x, y, float(self.params.Delta_A))
        W_acc2 = two_copy_from_bloch(x, y, z, Delta=float(self.params.Delta_A))
        E_A = float(self.params.Delta_A) * float(np.real(rho_A_out[1, 1]))
        P_erg = self.params.collision_rate * W_A

        # Dot energy / particle over wait and collision at FP
        E0 = _dot_energy(rho, self.params)
        E1 = _dot_energy(rho_wait, self.params)
        E2 = _dot_energy(rho_check, self.params)
        N0 = _dot_N(rho)
        N1 = _dot_N(rho_wait)
        N2 = _dot_N(rho_check)
        dE_wait = E1 - E0
        dE_coll = E2 - E1
        dN_wait = N1 - N0
        dN_coll = N2 - N1

        # First-law residual on the *dot energy* over one period:
        # ΔE_dot = 0 = dE_wait + dE_coll
        # Lead energy into the system over wait: ∫(J_E,L+J_E,R)dt = (J_E,L_bar+J_E,R_bar)*T
        # so dE_wait should ≈ (J_E,L + J_E,R)_avg * T
        lead_energy_in = (cyc.J_E_L + cyc.J_E_R) * self.params.T_period
        first_law_residual = (dE_wait - lead_energy_in) + dE_coll

        return EngineResult(
            rho_D=rho,
            rho_wait=rho_wait,
            rho_A_out=rho_A_out,
            P_el=cyc.P_el,
            I=cyc.I,
            J_N_L=cyc.J_N_L,
            J_N_R=cyc.J_N_R,
            J_E_L=cyc.J_E_L,
            J_E_R=cyc.J_E_R,
            J_Q_L=cyc.J_Q_L,
            J_Q_R=cyc.J_Q_R,
            residual_particle_avg=cyc.residual_particle,
            particle_balance_instant=inst_wait.particle_balance,
            P_erg=P_erg,
            W_A=W_A,
            W_coh=parts["W_coh"],
            W_inc=parts["W_inc"],
            W_acc2=float(W_acc2),
            E_A=E_A,
            coherence=spin_coherence(rho),
            pops=populations(rho),
            n_iter=n_iter,
            converged=converged,
            dE_wait=dE_wait,
            dE_collision=dE_coll,
            dN_wait=dN_wait,
            dN_collision=dN_coll,
            first_law_residual=first_law_residual,
            notes="P_el = -(mu_L-mu_R)*I with I=cycle-avg J_N,L; leads off during collision",
        )

    def dephasing_control_fixed_point(
        self,
        n_max: int = 400,
        tol: float = 1e-10,
        current_steps: int = 80,
    ) -> EngineResult:
        """Period map: lead evolve full period, then kill spin coherence (no collision)."""
        params = self.params
        rho = steady_state_leads(params)
        converged = False
        n_iter = 0
        for n_iter in range(1, n_max + 1):
            rho_new = evolve_leads(rho, params, params.T_period)
            rho_new = rho_new.copy()
            rho_new[1, 2] = 0.0
            rho_new[2, 1] = 0.0
            rho_new = 0.5 * (rho_new + rho_new.conj().T)
            tr = np.trace(rho_new)
            if abs(tr) > 0:
                rho_new = rho_new / tr
            err = np.linalg.norm(rho_new - rho)
            rho = rho_new
            if err < tol:
                converged = True
                break

        # treat full period as "wait" for averaging (no collision)
        # construct a synthetic post-dephasing state as period start
        cyc = cycle_average_currents(rho, params, n_steps=current_steps)
        # override: for dephasing control, wait time is full T_period
        # cycle_average uses params.waiting_time — temporarily inconsistent.
        # Fix by averaging over T_period with a local params clone.
        p2 = SpinValveParams(**{**params.__dict__, "tau": 0.0, "T_period": params.T_period})
        cyc = cycle_average_currents(rho, p2, n_steps=current_steps)

        return EngineResult(
            rho_D=rho,
            rho_wait=rho,
            rho_A_out=np.diag([1.0, 0.0]),
            P_el=cyc.P_el,
            I=cyc.I,
            J_N_L=cyc.J_N_L,
            J_N_R=cyc.J_N_R,
            J_E_L=cyc.J_E_L,
            J_E_R=cyc.J_E_R,
            J_Q_L=cyc.J_Q_L,
            J_Q_R=cyc.J_Q_R,
            residual_particle_avg=cyc.residual_particle,
            particle_balance_instant=instantaneous_currents(rho, params).particle_balance,
            P_erg=0.0,
            W_A=0.0,
            W_coh=0.0,
            W_inc=0.0,
            W_acc2=0.0,
            E_A=0.0,
            coherence=spin_coherence(rho),
            pops=populations(rho),
            n_iter=n_iter,
            converged=converged,
            dE_wait=0.0,
            dE_collision=0.0,
            dN_wait=0.0,
            dN_collision=0.0,
            first_law_residual=0.0,
            notes="dephasing control: no ancilla; currents cycle-averaged over full period",
        )
