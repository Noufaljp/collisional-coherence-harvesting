# Stage 2 sign and bookkeeping conventions

**Branch:** `spin-valve-engine`  
**Code:** `transport/channels.py`, `transport/currents.py`, `transport/engine.py`

## Operators

| Symbol | Meaning |
|--------|---------|
| \(N_D\) | \(\mathrm{diag}(0,1,1)\) on \(\{\lvert0\rangle,\lvert\uparrow\rangle,\lvert\downarrow\rangle\}\) |
| \(H_D\) | free-dot Hamiltonian |
| \(L_\alpha\) | dissipator contribution of lead \(\alpha\in\{L,R\}\) only |

## Instantaneous currents

\[
J_{N,\alpha}(\rho)=\mathrm{Re}\,\mathrm{Tr}\!\big[N_D\,\mathcal L_\alpha(\rho)\big],
\qquad
J_{E,\alpha}(\rho)=\mathrm{Re}\,\mathrm{Tr}\!\big[H_D\,\mathcal L_\alpha(\rho)\big],
\qquad
J_{Q,\alpha}=J_{E,\alpha}-\mu_\alpha J_{N,\alpha}.
\]

- \(J_{N,L}>0\): particles **enter the dot from L**.
- Continuous NESS: \(J_{N,L}+J_{N,R}\approx 0\).

## Transport particle current

\[
I \equiv J_{N,L}\quad(= -J_{N,R}\ \text{at continuous NESS}).
\]

## Electrical output power

\[
P_{\mathrm{el}} \equiv -(\mu_L-\mu_R)\,I .
\]

- Engine-style sign: **\(P_{\mathrm{el}}>0\)** means power delivered **to** the bias circuit.
- Bias \(V=\mu_L-\mu_R\) (we set \(e=1\)).

## Cycle average (with collisions)

- Leads evolve only during waiting time \(\tau_c=T-\tau\); **off during collision**.
- Cycle average:
  \[
  \bar J = \frac1T\int_0^{\tau_c}\! J\!\big(\rho(t)\big)\,dt .
  \]
- \(P_{\mathrm{el}}\) and \(\bar I\) use this average.
- Battery: \(P_{\mathrm{erg}}=r\,\mathcal W_A\), \(r=1/T\), ergotropy of the outgoing ancilla at the stroboscopic fixed point.

## First-law check (dot energy)

Over one period at the fixed point:
\[
\Delta E_{\mathrm{wait}} \approx \big(\bar J_{E,L}+\bar J_{E,R}\big)\,T,
\qquad
\Delta E_{\mathrm{wait}}+\Delta E_{\mathrm{collision}}\approx 0.
\]
Report residual \(\Delta E_{\mathrm{wait}}-(\bar J_{E,L}+\bar J_{E,R})T+\Delta E_{\mathrm{collision}}\).

## What is *not* claimed

- NEGF-accurate currents (this is the sequential-tunneling scaffold).
- Net device efficiency including ancilla preparation free energy.
- That ergotropy is an independent energy current in the first law.
