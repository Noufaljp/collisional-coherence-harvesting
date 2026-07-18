# Publication Readiness — Living Checklist & Agent Handoff

**Project:** Collisional harvesting of dissipatively stabilized spin coherence  
**Workspace:** `C:\Users\noufaljp\Desktop\Coherence_work`  
**Primary code repo:** `collisional-coherence-harvesting/`  
**GitHub:** https://github.com/Noufaljp/collisional-coherence-harvesting  

| Field | Value |
|--------|--------|
| **Document role** | Single living checklist for *any* agent/human. Read this first. |
| **First written** | 18 July 2026 |
| **Last updated** | 18 July 2026 (post companion easy-package commit `5d77b33`) |
| **Current HEAD (local/main)** | `5d77b33` — *Companion package: accessibility, physicality, leakage, and paper figures* |
| **Tests** | `28 passed` (`python -m pytest -q`) |
| **Companion paper readiness** | ~70% code/figures; manuscript still internal note |
| **Full spin-valve paper readiness** | ~25% scaffold only; **not** submission-ready |

### How agents must use this file

1. **Read this file first** before coding.
2. **Update this file in the same PR/session** when you complete or block a task (change `[ ]` → `[x]`, bump **Last updated**, note commit hash).
3. Keep **one** truth: prefer editing  
   - workspace: `Coherence_work/PUBLICATION_READINESS_AGENT_NOTE.md`  
   - and mirror to: `collisional-coherence-harvesting/docs/PUBLICATION_READINESS.md` (in the git repo).  
4. Do **not** claim transport figures as quantitative engine output until §T items are closed.
5. Prefer **companion paper closure** over NEGF unless the user asks for the full engine.

---

## 0. Executive status (one screen)

### Defensible scientific claim

> A non-collinear (or bath-stabilized V-type) system continuously regenerates a local coherent resource; energy- and charge-conserving collisions export part of it into an ancilla battery. Treat electrical power and battery ergotropy as **coexisting** outputs — **not** “SWAP restores collinear thermoelectric power.”

### Two layers

| Layer | Goal | Status |
|--------|------|--------|
| **A. Companion model** | Analytic + validated numerics → short paper | Strong; easy package largely done |
| **B. Spin-valve engine** | Lead-resolved currents, controls, thermo, Pareto | Proof-of-concept only |

### Recommended order of work

1. Finish remaining **companion** checklist (§C, §M) → arXiv-ready short paper.  
2. Only then: **transport kernel + thermo** (§T) → full engine paper.  
3. Repo hygiene / CI (§R) can run in parallel with low risk.

---

## 1. Workspace map

| Path | Role | Notes for agents |
|------|------|------------------|
| `collisional-coherence-harvesting/` | **Active git repo** | All new code lives here |
| `…/src/coherence_harvesting/companion/` | Analytic core | Collision, baths, ergotropy, power, physicality |
| `…/src/coherence_harvesting/transport/` | Engine scaffold | Proxy currents; incomplete controls |
| `…/scripts/` + `scripts_api.py` | Figure demos | `python -X utf8 scripts/run_companion_demo.py` |
| `…/tests/` | Unit tests | Must stay green |
| `…/notes/` | Research note (tex/pdf) | Not yet journal structure |
| `…/notebooks/tutorial.ipynb` | Tutorial | **Tracked** as of `5d77b33` |
| `…/figures/` | Generated plots | Companion PNG+PDF; data in `figures/data/` |
| `revised_notes/` | Duplicate of notes | **Do not maintain a second copy** — sync into repo `notes/` only |
| `original_draft/` | Legacy failed manuscript | Provenance only; do not patch into a paper |
| `calculations/` | Old Mathematica PDF + non-executable nb | Not reproducible; prefer Python |
| `archive/` | ZIP of old notes | Provenance |
| `PUBLICATION_READINESS_AGENT_NOTE.md` | **This living checklist** | Keep updated |

### Verified strengths (do not re-break)

- Collision algebra: analytic map vs exact \(6\times6\) unitary (`companion/collision.py`, tests).
- Finite matched gap \(\Delta_A=\Delta\): work-free + nonzero battery energy.
- Impedance matching \(\Gamma_{\rm ext}=r(1-\cos\theta)\simeq\gamma_C\); demo: \(r_{\rm opt}\approx15.80\), \(r_{\rm imp}\approx16.68\).
- Two-copy accessible work: **full piecewise + matrix** (fixed in `5d77b33`).
- CompanionParams physicality validation.
- Directed leakage power curves + comparison figure.

### Commands (Windows-safe)

```powershell
cd C:\Users\noufaljp\Desktop\Coherence_work\collisional-coherence-harvesting
git status --short --branch
python -m pytest -q
python -X utf8 scripts\run_companion_demo.py
python -X utf8 scripts\run_transport_demo.py
```

Use `-X utf8` to avoid Unicode console errors on some Windows setups.

---

## 2. Living checklist — DONE

Update this section when things complete. Format: `- [x] item — commit/note`.

### 2.1 Companion analytics (done)

- [x] Analytic collision map \((s,d,C)\) + ancilla Bloch — validated vs unitary
- [x] Finite matched-gap Hamiltonian structure (in notes + code convention \(\Delta_A=\Delta\))
- [x] Phenomenological phase-locked reset fixed point \(C^*\)
- [x] Directed dark-leakage fixed point \(v^*=(I-\mathcal{B}R_\theta)^{-1}b\)
- [x] Exact qubit ergotropy \(W=\frac{\Delta}{2}(z+|r|)\)
- [x] Weak-extraction approximation for coherent charging
- [x] Impedance matching + small-angle power bound
- [x] Finite-phase analytic law \(r_{\rm opt}(\delta)\), \(P_{\max}(\delta)\)
- [x] Finite-coupling bound \(\theta\gtrsim 2\gamma_C\sqrt{1+\delta^2}/g\)
- [x] **Two-copy accessible work full piecewise formula** (regimes 1–3) — `ergotropy.py`
- [x] **Matrix-based two-copy ergotropy cross-check** + random-state tests
- [x] **Coherent / incoherent ergotropy split** (`coherent_incoherent_ergotropy`)
- [x] **One-copy accessibility policy** (`has_phase_reference` True/False)
- [x] **CompanionParams + doublet physicality checks** (`physicality.py`)
- [x] **Directed leakage wired into power** (`power_curve_directed`, `charging_power_directed`)
- [x] **Reset vs leakage power figure**
- [x] **Exact vs weak power curves figure**
- [x] **Finite-phase numeric vs analytic \(r_{\rm opt}\) figure**
- [x] **Impedance-matching collapse figure**
- [x] **\(|C^*|/c_0\) vs \(r\) for several \(\theta\)**
- [x] **Plateau \(\mathcal{C}(\theta)\) + \(\theta_{\min}\) mark**
- [x] **Collision-map validation histogram**
- [x] **Accessibility figure** (total / coh / two-copy along curve)
- [x] Tutorial notebook committed + README link
- [x] Tests expanded **22 → 28**

### 2.2 Transport scaffold (done at demo level only)

- [x] 3-level Coulomb-blockade space + polarized \(\Gamma_\alpha\)
- [x] CP jump generator that retains spin coherence (not derived Redfield)
- [x] Stroboscopic collision engine + iterative fixed point
- [x] Demo scans: rate, \(\theta_R\) scatter, dephasing bar chart
- [x] Plot relabeled as **tilt-angle parametric scan** (not true Pareto); old filename kept as alias

### 2.3 Repo (done)

- [x] Public GitHub repo + MIT license + pyproject package layout
- [x] Companion figures PNG+PDF under `figures/`
- [x] Some numeric data dump: `figures/data/companion_power_curve.npz`

---

## 3. Living checklist — TO DO (detailed)

Legend: **P0** = blocks companion paper · **P1** = companion polish · **P2** = full engine · **P3** = repo/journal hygiene.

When finishing an item: check the box, add `— done in <commit>`, and move a one-line summary to §2 if useful.

---

### §C — Companion paper (code remaining) — P0/P1

#### C1. Bath narrative locked [P0]

- [ ] **C1.1** Document in code docstring + notes: reset model is **engineered phase-locked affine map**, not a generic thermal GKLS steady coherence at finite \(\Delta\).
- [ ] **C1.2** Either:
  - (a) derive/implement minimal V-system GKLS near degeneracy that produces \(c_0\), **or**
  - (b) explicitly restrict paper to \(\Delta\ll\gamma_C\) + phase-locked / rotating-frame language.
- [ ] **C1.3** Expand leakage comparison figure to include \(|C^*|\), physicality margin, and scan over \(\kappa_D/\gamma_C\) (note §4.8 asked for this; currently only \(P_{\rm erg}\) at one \(\kappa_D\)).

**Acceptance:** Paper methods section can state bath assumptions without referee-killing ambiguity; every plotted leakage point is physical.

#### C2. Accessibility story complete [P0]

- [ ] **C2.1** Update `notes/coherence_harvesting_note.tex` accessibility section to the **three-regime** two-copy formula (code is already correct; **manuscript still has old one-line formula**).
- [ ] **C2.2** State operation class clearly: time-translation covariant / no phase ref ⇒ \(W_{\rm acc}^{(1)}=W_{\rm inc}\); with phase ref ⇒ \(W_{\rm total}\).
- [ ] **C2.3** Optional: finite-\(N\) tape accessibility (harder; can be “open problem” if stated).

**Acceptance:** Note/paper equations match `two_copy_accessible_work` tests; no claim that two ancillas “automatically unlock” work.

#### C3. Validation completeness [P1]

- [ ] **C3.1** Table or plot: weak vs exact relative error vs \(\theta\) and \(r\).
- [ ] **C3.2** Finite-coupling: plot reachable fraction of ideal bound vs \(g/\gamma_C\).
- [ ] **C3.3** Assert physicality for **every** point written into companion figure data files (hook `check_doublet_physical` in figure loop; fail loud).
- [ ] **C3.4** Save **all** companion figure source data as CSV/NPZ (not only power curve).

**Acceptance:** WP B acceptance criteria: every asymptotic has a numeric check; no unphysical plot points.

#### C4. Companion manuscript conversion [P0 for submission]

- [ ] **C4.1** Convert `notes/coherence_harvesting_note.tex` from internal research note → journal structure:
  1. Intro + narrow novelty  
  2. Model + allowed ops  
  3. Collision channel  
  4. Bath + fixed point  
  5. Ergotropy / accessibility / power  
  6. Impedance matching + bounds  
  7. Numerics + feasibility  
  8. Discussion / limits  
  9. Appendices  
- [ ] **C4.2** Remove TOC-as-roadmap, “executive status”, “stuck points” tables from submitted PDF (keep in this checklist instead).
- [ ] **C4.3** Real BibTeX (`.bib`) with DOIs; cite in context (current note lists ~12, cites ~4).
- [ ] **C4.4** Resolve **authorship** vs original draft (Jaseem / De / Solanki / Vinjanampathy / Muralidharan) before public posting.
- [ ] **C4.5** Scheme figure (diagram): bath → V-system → collision → ancilla tape.

**Acceptance:** Standalone PDF readable by a referee unfamiliar with this checklist.

---

### §T — Full spin-valve / transport engine — P2

Do **not** treat demo figures as paper results until these close.

#### T1. Lead-resolved currents (replaces proxy) [P2 — critical]

**Files:** `transport/observables.py`, `nonsecular.py`, `engine.py`

- [ ] **T1.1** Tag every jump channel by lead side (`L`/`R`).
- [ ] **T1.2** Implement from the **same** dissipator used in \(\dot\rho\):
  ```text
  J_N,α(ρ) = Tr[ N_D  L_α(ρ) ]
  J_E,α(ρ) = Tr[ H_D  L_α(ρ) ]
  J_Q,α    = J_E,α − μ_α J_N,α
  ```
- [ ] **T1.3** **Cycle-average** over the full waiting interval (not a single post-wait snapshot).
- [ ] **T1.4** Enforce/diagnose \(J_{N,L}+J_{N,R}=0\) at no-collision NESS and period-integrated at collision fixed point.
- [ ] **T1.5** Fix **sign convention** to match manuscript:  
  \(P_{\rm el}= -(\mu_L-\mu_R)\bar J_N\) for electrical **output**; document in one sign table.
- [ ] **T1.6** Remove or hard-label `current_estimate()` as deprecated proxy.

**Acceptance:** Trace preservation; particle conservation diagnostics; documented current orientation; first-law residual reportable.

#### T2. Generator identity [P2]

**File:** `transport/nonsecular.py`

- [ ] **T2.1** Choose and document **one**:
  - Near-degenerate / singular-coupling GKLS, **or**
  - Born–Markov Redfield / first-order von Neumann with positivity monitoring.
- [ ] **T2.2** Stop calling it “Redfield” unless derived.
- [ ] **T2.3** Local detailed balance / one-lead equilibrium test.
- [ ] **T2.4** Decide Lamb shift / exchange field: include or justify omit.

**Acceptance:** Methods paragraph + validity domain \(\Delta/\gamma\), temperatures, couplings.

#### T3. Dephasing control fixed point [P2]

**File:** `transport/engine.py` → `dephasing_control_fixed_point`

- [ ] **T3.1** Remove unconditional `converged=True`.
- [ ] **T3.2** Real residual vs `tol` (Frobenius/trace norm).
- [ ] **T3.3** Prefer CPTP superoperator composition + unit-eigenvector solve; cross-check iteration.

**Acceptance:** Same convergence standards as collision fixed point.

#### T4. Stroboscopic map as superoperator [P2]

- [ ] **T4.1** Build lead propagator \(e^{\mathcal L t}\) once per parameter set.
- [ ] **T4.2** Collision channel as \(9\times9\) superoperator on vec(\(\rho_D\)).
- [ ] **T4.3** Fixed point = unit eigenvector; report spectral gap.
- [ ] **T4.4** Agree with iterative map to numerical tolerance.

#### T5. Control hierarchy (attribution) [P2]

Same timing, same current evaluator for all:

- [ ] no collision  
- [ ] pure spin dephasing  
- [ ] classical population reset  
- [ ] incoherent exchange  
- [ ] coherent partial exchange  
- [ ] matched-population coherent exchange  
- [ ] collinear device reference  

**Acceptance:** Paper can separate geometric spin-valve loss from local coherence effects.

#### T6. Thermodynamic bookkeeping [P2]

Per period at fixed point, report:

- [ ] \(\Delta E_{\rm dot}\), \(\Delta E_{\rm ancilla}\)
- [ ] \(J_{E,L}, J_{E,R}, J_{Q,L}, J_{Q,R}\)
- [ ] \(P_{\rm el}\), switching work
- [ ] ancilla: \(\Delta E\), \(W_{\rm total}\), \(W_{\rm coh}\), \(W_{\rm inc}\), \(W_{\rm acc}^{(1)}\), \(W_{\rm acc}^{(2)}\), \(\Delta S\), purity, ergotropy/energy ratio
- [ ] preparation free-energy lower bound \(\Delta F_A\)
- [ ] entropy production estimate
- [ ] **Do not** add ergotropy into first-law as a separate energy current

#### T7. Engine regime search + true Pareto [P2]

Current default scan is **electrical input** (proxy \(P_{\rm el}<0\)). 

- [ ] **T7.1** Search parameters for feasible engine set, e.g.  
  \(P_{\rm el}>0\), \(J_{Q,{\rm hot}}>0\), \(0\le\eta\le\eta_{\rm Carnot}\), \(P_{\rm erg}\ge0\), physical state, small first-law residual.
- [ ] **T7.2** Scan dims: \(\theta_R,p_{L,R},\Delta/\gamma,\mu,T_L/T_R,g\tau,\gamma T,\Delta_A-\Delta,\alpha\), dephasing.
- [ ] **T7.3** True non-dominated frontier from multi-D scan + tolerances — **not** a 9-point \(\theta_R\) scatter.
- [ ] **T7.4** If no positive \(P_{\rm el}\) regime exists: publish as **honest tradeoff / negative result** with controls (still valid if bookkeeping is clean).

#### T8. Full-engine figures [P2]

- [ ] Resource map before collisions  
- [ ] Control hierarchy panel  
- [ ] Cycle-averaged \(P_{\rm el}\), \(P_{\rm erg}\) vs \(r\)  
- [ ] Non-dominated frontier  
- [ ] First-law residual / entropy production  
- [ ] Robustness: dephasing, detuning, finite \(\tau\)  
- [ ] Experimental timescale table  

---

### §R — Repository / reproducibility — P3

- [ ] **R1** Mirror this checklist into `collisional-coherence-harvesting/docs/PUBLICATION_READINESS.md` and keep both in sync (or make repo copy canonical and link from workspace).
- [ ] **R2** `CITATION.cff`
- [ ] **R3** Pinned lockfile (exact numpy/scipy/matplotlib versions used: e.g. Py 3.12.10, np 2.1.x, sp 1.14.x, mpl 3.9.x)
- [ ] **R4** CI: pytest on Windows + Linux, ≥2 Python versions
- [ ] **R5** Lint/format config (ruff/black optional)
- [ ] **R6** Execute tutorial in CI **or** convert to deterministic `scripts/run_tutorial_checks.py`
- [ ] **R7** Figure regression: store key scalars (r_opt, P_max) and fail on large drift
- [ ] **R8** Single canonical LaTeX tree (drop dual maintenance of `revised_notes/` vs `notes/`)
- [ ] **R9** Release tag + Zenodo DOI when paper freezes
- [ ] **R10** Avoid Unicode in print paths that break cp1252 consoles (or always document `-X utf8`)

---

### §M — Manuscript / process — P0/P3

- [ ] **M1** Companion journal draft (see C4)
- [ ] **M2** Authorship + contributions agreed
- [ ] **M3** Literature positioning: novelty = combination (spin-valve / V-system + charge-conserving collisional battery + periodic fixed-point bookkeeping), **not** generic collision models alone
- [ ] **M4** Full-engine paper only after §T critical path

---

## 4. Definition of “publication-ready”

### Companion paper — ready when

- [x] Collision algebra validated  
- [x] Two-copy formula corrected + tested  
- [x] Physicality checks on params/states  
- [x] Core analytic figures generated  
- [ ] Bath mechanism explicit (C1)  
- [ ] Manuscript equations match code (C2)  
- [ ] Journal structure + BibTeX (C4)  
- [ ] All figure data reproducible from committed scripts/data (C3/R)  
- [ ] Authorship resolved (M2)  

### Full spin-valve paper — ready when

- [ ] Lead-resolved cycle-averaged currents (T1)  
- [ ] Generator derivation/identity (T2)  
- [ ] Controls hierarchy (T5)  
- [ ] Thermo balances close (T6)  
- [ ] Feasible engine **or** framed negative/tradeoff (T7)  
- [ ] True Pareto / multi-D scan (T7)  
- [ ] Experimental timescale discussion (T8)  

---

## 5. Priority queue for the next agent

Do in order unless user overrides:

| Priority | ID | Task | Effort (rough) |
|----------|-----|------|----------------|
| 1 | C2.1 | Sync note tex to three-regime two-copy formula | S |
| 2 | C1.1–C1.2 | Lock bath language in notes + docstrings | S |
| 3 | C1.3 | Leakage scan figures (\(\kappa_D\), margin, \(|C^*|\)) | S–M |
| 4 | C3 | Full data dumps + physicality assert in figure gen | S |
| 5 | C4 | Journal-shaped companion manuscript | M–L |
| 6 | T3 | Fix dephasing convergence bug | S |
| 7 | T1 | Lead-resolved cycle-averaged currents | L |
| 8 | T2 | Generator identity | L |
| 9 | T5–T7 | Controls + thermo + regime search | L |
| 10 | R2–R4 | Citation, lockfile, CI | S–M |

**S** < 1 session · **M** 1–2 sessions · **L** multi-session.

---

## 6. Scientific constraints (do not regress)

1. Exact degeneracy + nonzero ancilla ergotropy + strict energy conservation are incompatible without finite matched \(\Delta\).  
2. Symmetric bright–dark mixing kills steady coherence; use directed leakage or phase-locked reset.  
3. Single-copy coherent ergotropy is not free without a phase reference.  
4. Two copies do **not** generically unlock coherent ergotropy (piecewise threshold).  
5. Ergotropy is **not** an extra term in the first law.  
6. Secular Lindblad at large \(\Delta/\gamma\) destroys the resource; near-degeneracy is required for the valve.  
7. Old draft errors (stationary NEGF + unmodelled SWAP, mean energy as ergotropy, correlation matrix as qubit) must not reappear.

---

## 7. Change log (append-only)

| Date | Commit / note | What changed in readiness |
|------|----------------|---------------------------|
| 2026-07-18 | initial assessment | Full audit; transport proxy, two-copy incomplete, notebook untracked, 22 tests |
| 2026-07-18 | `5d77b33` | Two-copy piecewise+matrix; coh/inc; physicality; leakage power; companion figure set; tutorial tracked; 28 tests; living checklist created |

*(Agents: add a row every time you complete a checklist block.)*

---

## 8. Quick “is the easy package done?”

| Item from user easy list | Done? |
|--------------------------|-------|
| Two-copy full piecewise + matrix | **Yes** |
| Coherent/incoherent split | **Yes** |
| Physicality checks | **Yes** |
| Directed leakage in power + vs reset | **Yes** (expand \(\kappa_D\) scan still open: C1.3) |
| Finite-phase / finite-coupling / exact vs weak numerics | **Yes** |
| Companion paper figures (main set) | **Yes** |
| Tutorial commit + README | **Yes** |
| Parameter validation tests | **Yes** |
| Update this living checklist | **Yes** (this file) |
| Manuscript tex sync + journal draft | **No** — still open |
| Full transport publication stack | **No** — still open |
