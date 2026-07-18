"""Observables — re-exports lead-resolved currents (Stage 2).

The old golden-rule proxy is replaced by ``currents.py``. Import from
``currents`` for new code.
"""

from .currents import (
    current_estimate,
    cycle_average_currents,
    electrical_output_power,
    electrical_power,
    heat_current_proxy,
    instantaneous_currents,
)

__all__ = [
    "current_estimate",
    "cycle_average_currents",
    "electrical_output_power",
    "electrical_power",
    "heat_current_proxy",
    "instantaneous_currents",
]
