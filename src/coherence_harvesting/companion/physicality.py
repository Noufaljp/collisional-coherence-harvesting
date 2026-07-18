"""Physicality checks for companion-model states and parameters."""

from __future__ import annotations

from typing import Tuple

import numpy as np


class UnphysicalStateError(ValueError):
    """Raised when a density-matrix constraint is violated."""


def check_doublet_physical(
    s: float,
    d: float,
    C: complex,
    *,
    tol: float = 1e-10,
    raise_on_fail: bool = True,
) -> bool:
    """Check 0 ≤ s ≤ 1, |d| ≤ s, |C|² ≤ (s² − d²)/4."""
    s = float(s)
    d = float(d)
    c2 = abs(complex(C)) ** 2
    ok = True
    msgs = []
    if s < -tol or s > 1.0 + tol:
        ok = False
        msgs.append(f"s={s} outside [0,1]")
    if abs(d) > s + tol:
        ok = False
        msgs.append(f"|d|={abs(d)} > s={s}")
    bound = max((s * s - d * d) / 4.0, 0.0)
    if c2 > bound + tol:
        ok = False
        msgs.append(f"|C|^2={c2} > bound={bound}")
    if not ok and raise_on_fail:
        raise UnphysicalStateError("; ".join(msgs))
    return ok


def check_companion_params(
    gamma_C: float,
    gamma_d: float,
    c0: float,
    s_ss: float,
    Delta: float,
    theta: float,
    alpha: float,
    *,
    tol: float = 1e-10,
    raise_on_fail: bool = True,
) -> bool:
    """Validate CompanionParams and free steady coherence bound |c0| ≤ s_ss/2."""
    msgs = []
    ok = True
    for name, val in [
        ("gamma_C", gamma_C),
        ("gamma_d", gamma_d),
        ("Delta", Delta),
    ]:
        if float(val) < -tol:
            ok = False
            msgs.append(f"{name}={val} < 0")
    if not (0.0 - tol <= s_ss <= 1.0 + tol):
        ok = False
        msgs.append(f"s_ss={s_ss} outside [0,1]")
    if not (0.0 - tol <= alpha <= 1.0 + tol):
        ok = False
        msgs.append(f"alpha={alpha} outside [0,1]")
    # Free target: d_ss=0, |c0| ≤ s_ss/2
    if abs(c0) > 0.5 * s_ss + tol:
        ok = False
        msgs.append(f"|c0|={abs(c0)} > s_ss/2={0.5 * s_ss}")
    # also run doublet check on free target
    try:
        check_doublet_physical(s_ss, 0.0, c0, tol=tol, raise_on_fail=True)
    except UnphysicalStateError as exc:
        ok = False
        msgs.append(str(exc))
    if not ok and raise_on_fail:
        raise UnphysicalStateError("; ".join(msgs))
    return ok


def physicality_margin(s: float, d: float, C: complex) -> float:
    """Positive slack to the coherence bound: (s²−d²)/4 − |C|²."""
    return float((s * s - d * d) / 4.0 - abs(complex(C)) ** 2)
