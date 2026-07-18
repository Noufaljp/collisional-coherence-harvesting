# Collisional Coherence Harvesting

**Repository:** numerical and analytic codebase for *collisional harvesting of dissipatively stabilized spin coherence*.

This project studies how a continuously regenerated coherent resource — either from a bath-stabilized V-type three-level system or from a non-collinear quantum-dot spin valve — can be exported into a stream of ancilla qubits by charge- and energy-conserving exchange collisions.

| Layer | Status | Role |
|--------|--------|------|
| **Companion model** | Analytic + numerical | Closed-form collision map, fixed point, ergotropy, impedance-matched power |
| **Spin-valve engine** | Numerical | Nonsecular lead dynamics, stroboscopic fixed point, \((P_{\mathrm{el}}, P_{\mathrm{erg}})\) scans |

Theory notes live in [`notes/`](notes/).

---

## Quick start

```bash
# clone
git clone https://github.com/Noufaljp/collisional-coherence-harvesting.git
cd collisional-coherence-harvesting

# environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

pip install -e ".[dev]"
```

### Run tests

```bash
pytest -q
```

### Tutorial notebook

Concise walkthrough of the companion model and spin-valve demos:

```bash
jupyter notebook notebooks/tutorial.ipynb
# or:
jupyter lab notebooks/tutorial.ipynb
```

### Generate figures

On Windows, prefer UTF-8 mode if the console encoding is limited:

```bash
python -X utf8 scripts/run_companion_demo.py
python -X utf8 scripts/run_transport_demo.py
# or both:
python -X utf8 scripts/generate_figures.py
```

Figures (PNG + PDF for companion) are written to `figures/`; numeric source data to `figures/data/`.

---

## Package layout

```
src/coherence_harvesting/
  companion/          # V-system collision map, baths, ergotropy, power
  transport/          # spin valve, nonsecular leads, stroboscopic engine
  scripts_api.py      # high-level demos
  cli.py              # entry points
scripts/              # runnable demos
tests/                # unit + smoke tests
notes/                # research notes (LaTeX/PDF)
docs/                 # reading list and documentation
figures/              # generated plots
```

### Companion model (analytic core)

- Finite matched gap \(\Delta_A=\Delta\) makes the exchange work-free with nonzero battery energy
- Closed-form map for \((s,d,C)\) and outgoing ancilla Bloch vector
- Impedance matching: \(\Gamma_{\mathrm{ext}}=r(1-\cos\theta)\simeq\gamma_C\)
- Finite-phase suppression and accessibility diagnostics (one-/two-copy)

### Spin-valve engine (numerical full-paper layer)

- Coulomb-blockade Fock space \(\{|0\rangle,|\uparrow\rangle,|\downarrow\rangle\}\)
- Polarized leads with non-collinear \(\Gamma_R(\theta_R)\)
- Sequential-tunneling / Redfield-style **nonsecular** generator that retains spin coherence
- Stroboscopic map: lead waiting \(\to\) exchange collision \(\to\) fixed point
- Observables: proxy electrical power, ancilla ergotropy / charging power, dephasing control

> The transport current is a **sequential-tunneling proxy** suitable for method development and tradeoff scans. A full NEGF current module can be swapped in later without changing the engine structure.

---

## Minimal path to a full-engine paper

1. Nonsecular lead model that keeps coherence (implemented; refine as needed)
2. Stroboscopic fixed point of collisions (implemented)
3. Main figure: tradeoff \((P_{\mathrm{el}}, P_{\mathrm{erg}})\) + controls (demo scripts)
4. Honest bookkeeping: matched gap, ergotropy, accessible vs total work

See `notes/coherence_harvesting_note.pdf` for the full research note.

---

## Citation / contact

Author: **Noufal Jaseem**

If you use this repository, please cite the accompanying note/paper when available.

---

## License

MIT — see [LICENSE](LICENSE).
