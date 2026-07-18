# Architecture

## Companion model

Analytic pipeline used as the theory backbone of the paper:

1. Build system state \((s,d,C)\)
2. Apply closed-form collision map (validated against \(6\times6\) unitary)
3. Wait under bath (phase-locked reset or directed dark leakage)
4. Iterate to fixed point
5. Compute ancilla ergotropy and charging power \(P_{\mathrm{erg}}=r\,\mathcal{W}_A\)
6. Optimize over collision rate \(r\)

Key result: impedance matching \(\Gamma_{\mathrm{ext}}=r(1-\cos\theta)\simeq\gamma_C\).

## Transport engine

Numerical full-engine layer:

1. Sequential-tunneling / Redfield-style nonsecular lead Liouvillian on \(\{|0\rangle,|\uparrow\rangle,|\downarrow\rangle\}\)
2. Waiting evolution \(e^{\mathcal{L}t}\)
3. Energy- and charge-conserving exchange collision with a fresh ancilla
4. Fixed point of the stroboscopic map
5. Report \((P_{\mathrm{el}}, P_{\mathrm{erg}})\) and controls (dephasing, tilt scans)

Currents are **proxies** for development; swap in a NEGF evaluator later if needed.
