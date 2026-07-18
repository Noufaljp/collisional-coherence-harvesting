"""Minimal V-system companion model: collision map, baths, ergotropy, power."""

from .collision import (
    analytic_system_map,
    analytic_ancilla_bloch,
    numerical_collision,
)
from .baths import reset_fixed_point_C, directed_leakage_fixed_point
from .ergotropy import (
    qubit_ergotropy,
    two_copy_accessible_work,
    coherent_incoherent_ergotropy,
    one_copy_accessible_work,
)
from .power import (
    power_curve,
    optimize_power,
    impedance_matched_r,
    CompanionParams,
    finite_coupling_theta_min,
)
from .physicality import check_doublet_physical, check_companion_params

__all__ = [
    "analytic_system_map",
    "analytic_ancilla_bloch",
    "numerical_collision",
    "reset_fixed_point_C",
    "directed_leakage_fixed_point",
    "qubit_ergotropy",
    "two_copy_accessible_work",
    "coherent_incoherent_ergotropy",
    "one_copy_accessible_work",
    "power_curve",
    "optimize_power",
    "impedance_matched_r",
    "CompanionParams",
    "finite_coupling_theta_min",
    "check_doublet_physical",
    "check_companion_params",
]
