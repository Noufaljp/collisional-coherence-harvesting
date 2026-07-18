# Small paper scope — what forms this paper

**Status:** Writing-ready companion paper (not the full spin-valve engine paper)  
**Last updated:** 18 July 2026  
**Code/figures:** `collisional-coherence-harvesting` (main), commit series through `5d77b33`+  
**Living checklist:** [`PUBLICATION_READINESS.md`](PUBLICATION_READINESS.md)  
**Detailed theory:** `notes/coherence_harvesting_note.tex` / `.pdf` (internal; rewrite into journal form)

This note freezes **what the small paper is**. Anything not listed here is out of scope for the first submission.

---

## 1. One-sentence claim

A V-type system with continuously renewed doublet coherence can charge a stream of ancilla qubits via energy- and charge-conserving exchange collisions; the charging power is maximized by **impedance matching** the extraction rate to the bath’s coherence regrowth rate, with a finite matched gap required for nonzero battery energy and honest accounting of **accessible** vs total ergotropy.

---

## 2. What this paper is / is not

| This paper **is** | This paper **is not** |
|-------------------|------------------------|
| Analytic (+ validated numeric) **companion model** | Full non-collinear spin-valve transport engine |
| Collisional **coherence harvesting** bound | “SWAP restores collinear thermoelectric power” |
| Quantum-battery / repeated-interaction theory | NEGF device simulation |
| Upper bounds + accessibility caveats | Claim that coherent ergotropy is always free work |
| Short theory paper (letter / short PRE-style) | Comprehensive experimental proposal |

**Sequel (explicitly deferred):** lead-resolved spin-valve dynamics, cycle-averaged \(P_{\mathrm{el}}\), control hierarchy, true \((P_{\mathrm{el}},P_{\mathrm{erg}})\) Pareto frontier. Mention only in outlook.

---

## 3. Physical model (must appear)

### 3.1 System

- V-type three-level system: ground \(\lvert 0\rangle\), doublet \(\lvert 1\rangle,\lvert 2\rangle\).
- Variables: \(s=\rho_{11}+\rho_{22}\), \(d=\rho_{11}-\rho_{22}\), \(C=\rho_{12}\).
- Bright/dark picture: coherence as bright–dark imbalance when \(C\) is real.

### 3.2 Ancilla tape

- Qubit ancillas, typically prepared in the ground state (\(\alpha=0\)).
- Hamiltonian \(H_A=\Delta\lvert\uparrow\rangle\langle\uparrow\rvert\) (matched gap).
- Stream of independent collisions at rate \(r=1/T\).

### 3.3 Interaction

- Exchange only on the active block \(\{\lvert 1\downarrow\rangle,\lvert 2\uparrow\rangle\}\).
- Angle \(\theta=g\tau\).
- **Finite matched gap** \(\Delta_A=\Delta>0\) so that
  - \([H_S+H_A,H_{\mathrm{int}}]=0\) (work-free collision),
  - ancilla carries nonzero energetic ergotropy.
- Particle-number conserving on the intended sector.

### 3.4 Bath / renewal (state clearly — do not oversell)

Present **two** models, both allowed if language is honest:

1. **Phase-locked phenomenological reset** (analytic benchmark): affine map regenerating \(C\to c_0\) at rate \(\gamma_C\), with free precession phase \(\phi=\Delta/r\).
2. **Directed dark-leakage bath** (minimal safer renewal): bright state pumped/relaxed; dark population leaks; **not** symmetric bright–dark mixing (which kills \(C\)).

**Required sentence:** a lab-frame steady coherence at finite \(\Delta\) with a single undriven thermal bath is not generic; either operate with \(\Delta\ll\gamma_C\), use a phase reference / rotating frame, or treat the reset map as an engineered renewal. The paper’s main formulas use the reset model; leakage is a comparison.

---

## 4. Core results that *form* the paper

These are the publishable results (already in code/notes):

### R1 — Closed-form collision map

\[
s'=s,\quad
d'=\cos^2\theta\, d-\sin^2\theta(1-2\alpha)s,\quad
C'=\cos\theta\, C,
\]
plus outgoing ancilla Bloch / coherence. Validated against exact joint unitary.

### R2 — Stroboscopic fixed point

\[
C^*=\frac{(1-q_C)c_0}{1-q_C e^{-i\phi}\cos\theta},\quad
q_C=e^{-\gamma_C/r},\quad \phi=\Delta/r.
\]

### R3 — Ancilla ergotropy

\[
\mathcal{W}_A=\frac{\Delta}{2}\bigl(z_A+|r_A|\bigr),
\]
with coherent/incoherent split; weak-extraction limit
\[
\Delta\mathcal{W}_A\simeq\frac{\Delta\sin^2\theta\,|C^*|^2}{|z_A|}.
\]

### R4 — Impedance matching (organizing principle)

\[
\Gamma_{\mathrm{ext}}=r(1-\cos\theta)\simeq\gamma_C
\quad\Rightarrow\quad
r_{\mathrm{opt}}\simeq\frac{\gamma_C\sqrt{1+\delta^2}}{1-\cos\theta},\quad
\delta=\Delta/\gamma_C.
\]
At \(\phi=0\), system sits near \(|C^*|\sim c_0/2\) at maximum power.

### R5 — Harvesting bound and plateau

Small-angle zero-phase bound
\[
P_{\mathrm{erg}}^{\max}\simeq\frac{\gamma_C\Delta c_0^2}{2|z_A|},
\]
with flat plateau \(\mathcal{C}(\theta)=\tfrac12-\theta^4/96+\cdots\).

Finite-phase suppression
\[
P_{\mathrm{erg}}^{\max}(\delta)\simeq\frac{\gamma_C\Delta c_0^2}{|z_A|}\,\frac{1}{1+\sqrt{1+\delta^2}}.
\]

### R6 — Realizability

\[
\theta\gtrsim\frac{2\gamma_C\sqrt{1+\delta^2}}{g}
\quad(\theta=g\tau\le g/r).
\]
Linear in \(\gamma_C/g\), not square-root.

### R7 — Accessibility (honest)

- **One copy, no phase reference:** coherent ergotropy not operationally free; \(W_{\mathrm{acc}}^{(1)}=W_{\mathrm{inc}}\) (often \(0\) if ground-biased).
- **Two copies, energy-dephased product:** piecewise formula
  \[
  \begin{aligned}
  &0, && |c|^2\le b(a-b),\\
  &\Delta\bigl(|c|^2-b(a-b)\bigr), && b(a-b)<|c|^2\le a(a-b),\\
  &\Delta\bigl(2|c|^2-(a-b)\bigr), && a(a-b)<|c|^2\le ab,
  \end{aligned}
  \]
  for ground-biased \(\rho=\begin{pmatrix}a&c\\c^*&b\end{pmatrix}\).
- In the weak harvesting regime, two-copy activation is **typically not** met → report total \(\mathcal{W}\) as an **upper bound**.

### R8 — Dark-state renewal

Symmetric bright–dark mixing \(\Rightarrow C_{\mathrm{ss}}=0\). Directed leakage sustains a resource; compare \(P_{\mathrm{erg}}\) (and ideally \(|C^*|\)) to the reset model.

---

## 5. Suggested paper structure

1. **Introduction** — coherence as a resource; collisional batteries; gap in continuous harvesting from a *stabilized* coherence; state what we do *not* claim (no collinear restoration).
2. **Model** — V-system, matched-gap exchange, ancilla tape, bath assumptions.
3. **Collision channel** — map + unitary validation (brief).
4. **Fixed point and ergotropy** — \(C^*\), \(\mathcal{W}_A\), coh/inc.
5. **Power and impedance matching** — optimum, plateau, finite \(\delta\), realizability.
6. **Accessibility** — one- and two-copy; upper bound language.
7. **Directed leakage comparison** — short.
8. **Discussion** — phase reference; preparation cost of ground ancillas (mention, optional bound); outlook to spin valve as fermionic analogue.
9. **Appendices** — algebra of the map; piecewise two-copy derivation.

Target length: **short article / letter-like** (roughly 4–8 pages main text + appendix), not a long review of the failed SWAP engine (that critique can be 1–2 paragraphs or SI).

---

## 6. Figures that form the paper

Use (or lightly polish) existing outputs in `figures/`:

| # | Figure | File (approx.) | Role |
|---|--------|----------------|------|
| 1 | Scheme | *(to draw)* | Bath → V-system → collision → ancilla tape |
| 2 | Collision validation | `companion_collision_validation` | Analytic vs unitary |
| 3 | \(\lvert C^*\rvert/c_0\) vs \(r\) | `companion_Cstar_vs_r` | Fixed-point resource |
| 4 | \(P_{\mathrm{erg}}(r)\) exact vs weak | `companion_power_curve` | Main power result |
| 5 | Impedance-match collapse | `companion_impedance_collapse` | Organizing principle |
| 6 | Plateau + \(\theta_{\min}\) | `companion_plateau` | Flat optimum + realizability |
| 7 | Finite-\(\delta\) \(r_{\mathrm{opt}}\) / bound | `companion_finite_phase*` | Gap vs precession tradeoff |
| 8 | Reset vs directed leakage | `companion_reset_vs_leakage` | Bath robustness |
| 9 | \(\mathcal{W}_{\mathrm{tot}},\mathcal{W}_{\mathrm{coh}},\mathcal{W}_{\mathrm{acc}}^{(2)}\) | `companion_accessibility` | Honesty about extractability |

**Do not include** transport proxy \(P_{\mathrm{el}}\) plots as quantitative results in this paper (optional one-line outlook only).

---

## 7. Explicit non-claims (put in text)

1. We do **not** claim that exporting coherence restores collinear spin-valve electrical power.  
2. We do **not** claim single-ancilla coherent ergotropy is free work without a phase reference.  
3. We do **not** claim two ancillas always unlock the resource.  
4. We do **not** present the spin-valve numerics in the repo as a finished device theory.  
5. Ergotropy is **not** added as an extra energy current in the first law.  
6. arXiv:2602.18300 (minimal thermal-qubit RI no-go) is only a **background RI cite**, not a central comparison—do not over-discuss.  
7. Gross \(P_{\rm erg}\) is not a complete net device efficiency without preparation / phase-reference costs.

---

## 8. What is left before submission (small paper only)

From the living checklist, **in scope**:

| Item | Needed? |
|------|---------|
| Journal-shaped manuscript from the note | **Yes — main remaining work** |
| Sync accessibility section to 3-regime formula | **Yes** |
| Clear bath/phase paragraph | **Yes** |
| Scheme figure | **Yes** (simple) |
| Authorship resolved | **Yes** |
| Clean BibTeX / citations | **Yes** |
| Optional: \(\kappa_D\) scan, more data dumps | Polish |
| Full transport engine (§T) | **Out of scope** |

**Conclusion:** The **scientific skeleton of the small paper is defined and largely coded/figured**. Remaining work is **write, frame, and freeze**—not invent a new model.

---

## 9. Working title options

1. *Collisional harvesting of dissipatively stabilized coherence: impedance matching and accessible ergotropy*  
2. *Impedance-matched collisional charging from a bath-renewed coherent doublet*  
3. *Work-free exchange collisions as a continuous coherence-to-battery converter*

---

## 10. Pointers for authors / agents

- **Implementations:** `src/coherence_harvesting/companion/`  
- **Regenerate figures:** `python -X utf8 scripts/run_companion_demo.py`  
- **Tutorial:** `notebooks/tutorial.ipynb`  
- **Do not expand scope** into spin-valve currents without opening the full-engine checklist in `PUBLICATION_READINESS.md`.

---

## 11. One-line summary for collaborators

> **Small paper = companion V-system + matched-gap collisions + impedance-matched power + accessibility caveats + leakage comparison; spin valve is outlook only.**
