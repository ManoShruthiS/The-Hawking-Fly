# THE HAWKING FLY — Project Specification & Build Brief

**Working title:** The Hawking Fly (alt: *Can a Brain Speak Without a Body?*)
**Domain:** Connectome-constrained computational neuroscience + interactive simulation
**Audience for this document:** a coding agent (or human dev) implementing the system. Everything below is written to be actionable — module boundaries, data sources, and tech choices are explicit, and every claim about "what's real vs. designed" is called out so the build doesn't accidentally overclaim what it's doing.

---

## 0. How to use this document

- Build in the phase order given in §7. Do not attempt the full vision in one pass — it is five real projects stapled together, and Phase 0 alone is a legitimate demo.
- Anywhere this doc cites a neuron count, cell-type count, or dataset version, treat it as **approximate and possibly stale**. Query the live connectome APIs for current numbers rather than hardcoding the figures below.
- §8 (Scientific Honesty & UI Labeling Policy) is not optional polish — apply it to every screen that shows a "decoded" or "inferred" value.

---

## 1. Positioning

**The real question:** given the fly's actual wiring diagram and live sensory input, if we cut the pathway right before it would reach the muscles, can we recover — from upstream neural activity alone — what the fly was about to do?

This is not a made-up premise. It sits inside an active, current research area:

- A connectome-constrained network — architecture fixed by real fly wiring data, with only low-level neuron/synapse parameters fit computationally — has been shown to reproduce real measured neural activity in the fly's visual system. This is published, peer-reviewed, and the model is open-source and pretrained (Lappalainen et al., *Nature*, 2024 — the `flyvis` project).
- A separate whole computational brain model of the fly, explicitly targeting sensorimotor processing, was also published in *Nature* in 2024 (Shiu et al.).
- Researchers have run direct simulations of the fly's ventral nerve cord (its "spinal cord," where leg and wing motor neurons live) to identify the actual three-neuron circuit that generates rhythmic leg movement — a result later confirmed with real optogenetics (2025 preprint). This is functionally the same move as "block the motor gate and read what's upstream."
- Two 2025 papers go further and close the loop entirely — feeding connectome-derived networks into full physics-based fly-body simulators for locomotion and flight (NeuroMechFly v2; a whole-brain "connectomic graph model," sometimes called FlyGM).

**Honest positioning to build from:** this project is not inventing a new method. It's an interactive, narratively-framed instance of a real research direction, built on real connectivity data and, where they exist, real pretrained models — plus custom, simplified models where no published solution exists yet (the brain→premotor "intent" prediction piece is the genuinely novel/hacked-together part, and should be labeled as such).

**Update (Sept 2026) — this project now has a much better dataset to build on.** On September 3, 2026, Google Research, HHMI Janelia's FlyEM team, and the University of Cambridge's Drosophila Connectomics Group jointly published **MaleCNS v1.0** in *Cell*: the first complete connectome of an adult male fruit fly's *entire* central nervous system in one animal — brain, both optic lobes, **and** the ventral nerve cord — 166,700 neurons, \~125 million synapses, CC-BY 4.0, publicly queryable via neuPrint. (Note: this is Google **Research**, not Google DeepMind — different org, easy to conflate.) This is almost certainly where the "166,000 neurons" figure in the original reference image came from.

This changes §4.1/§4.3 below: instead of stitching brain connectivity (FlyWire, one individual) to VNC connectivity (MANC, a different individual), the brain-to-motor-neuron path can now be traced through a single real connectome from a single animal — which is a materially cleaner and more defensible basis for the motor-gate concept. Treat MaleCNS v1.0 as the primary dataset; FlyWire/hemibrain/MANC remain useful as female-fly or partial-coverage alternatives and for cross-checking.

The Stephen-Hawking/wheelchair framing is a legitimate narrative bridge to real BCI/neuroprosthetic research (decoding motor intent when the motor pathway itself is blocked is literally the core problem in paralysis-focused brain-computer interfaces). Keep it, but see §8 — it needs consistent, careful handling, not just a striking thumbnail.

---

## 2. Scientific framing & hypotheses

**Primary question:** How much of a blocked motor output can be predicted from upstream (premotor) neural activity alone, using only the fly's real connectivity structure as a prior?

**Sub-hypotheses to actually test:**

1. A decoder trained only on premotor-layer activity predicts the withheld motor-layer activity significantly better than a shuffled/connectivity-blind baseline.
2. Prediction accuracy degrades in a structured way as you move the "cut point" further upstream (visual periphery → medulla → lobula → descending neuron) — i.e., information about motor output is progressively less recoverable the earlier you intercept it. This is the actual interesting empirical result, not the flashy UI.
3. (Stretch) Different synthetic "histories" fed to structurally identical fly instances produce distinguishable activity signatures — i.e., individuality can emerge from identical wiring plus different experience, not just different wiring.

**What "success" looks like:** a documented, reproducible decoding-accuracy-vs-cut-point curve, plus a working interactive demo that visibly reflects it. Not "the fly told us it was hungry."

---

## 3. The real/designed split (keep this visible everywhere, including in the UI copy)

| Layer Status Notes                                     |                                        |                                                                                                                                                    |
| ------------------------------------------------------ | -------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Optic lobe connectivity & visual neural dynamics       | **Real, pretrained**                   | `flyvis` (Lappalainen et al. 2024) — actual published model, actual connectome-derived weights                                                     |
| Whole-brain / VNC connectivity structure               | **Real data, custom dynamics**         | Real synapse-count graphs from FlyWire/hemibrain/MANC; propagation model on top is a simplified rate model, not a validated biophysical simulation |
| Motor-intent decoder                                   | **Real prediction task, novel method** | Genuine train/test split against withheld ground truth; not published — this is the project's actual contribution                                  |
| "Teach the fly to communicate" discovery mechanic      | **Designed UX, not neuroscience**      | A puzzle layer mapping decoder output classes to symbols. Must be labeled as designed, not discovered biology                                      |
| Multi-fly behavioral fingerprinting                    | **Exploratory, stretch**               | Real signal (different init/history → different trajectories), but "personality" framing is narrative, not a scientific claim                      |
| Wheelchair avatar, neural camera, cinematic brain-dive | **Presentation layer**                 | Entirely designed; no scientific content, purely communicates the real content underneath                                                          |

---

## 4. Functional modules

### 4.1 Connectome data layer

**Purpose:** fetch, cache, and expose queryable fly connectivity graphs.
**Primary dataset — MaleCNS v1.0:** full adult male CNS (brain + both optic lobes + ventral nerve cord), 166,700 neurons, \~125M synapses, published by Google Research/HHMI Janelia FlyEM/University of Cambridge, Sept 2026, CC-BY 4.0. This is the dataset to build on — it means the brain-to-motor path for the motor-gate concept is a single real connectome from one animal, not a cross-dataset stitch.

- Access: `pip install neuprint-python`, free account + token at neuprint.janelia.org, then: 
  ```python
  from neuprint import Client, fetch_neurons, fetch_adjacenciesclient = Client("https://neuprint.janelia.org", dataset='male-cns:v1.0', token=token)neurons, syn_dist = fetch_neurons("DNp01")          # example: giant-fiber descending neuronout_edges, info = fetch_adjacencies("DNp01")

  ```
- `navis` (via `navis.interfaces.neuprint`) gives skeleton geometry for the same dataset — this is what feeds the 3D "neural camera" view (§4.7).
- Raw bulk data is also downloadable directly (multi-GB; don't vendor it in the repo, fetch/cache locally).

**Secondary / fallback datasets:**

- **FlyWire** — full adult *female* brain (\~139k neurons), Princeton/community project. Access via `CAVEclient` / `fafbseg-py`; requires registering and agreeing to FlyWire's community data-use principles.
- **Hemibrain** (Janelia FlyEM) — earlier, partial female central-brain reconstruction (\~25k neurons). Useful for cross-checking cell types, largely superseded by MaleCNS v1.0 for this project's purposes.
- **MANC / FANC** — the VNC-only datasets MaleCNS v1.0 now supersedes for this project (kept here for reference/cross-checking only).

**Tooling:** `neuprint-python` (MaleCNS, hemibrain, MANC), `CAVEclient` + `fafbseg-py` (FlyWire), `navis` (cross-dataset neuron analysis/visualization, Python), `cocoa` (cross-dataset cell-type matching, e.g. tracing a cell type between MaleCNS and FlyWire).

**Output:** cached local connectivity graphs (adjacency + cell-type annotations) as the shared substrate every other module reads from. Don't re-query live APIs at simulation runtime — snapshot to local storage.

**Scoping note (validated by early community usage):** within days of the MaleCNS v1.0 release, independent developers were already building on it — and the pattern that works is a *bounded, anatomy-aware subgraph* (roughly 1,000–5,000 neurons pulled by cell type around a specific circuit), not the full 166,700-neuron graph. That matches this doc's Phase 0/1 scoping exactly — build small and real, don't attempt live whole-brain dynamics (see §10).

### 4.2 Sensory encoding layer

**Purpose:** turn synthetic "world events" (food appears, light off, threat, sound) into activation patterns on real sensory neuron populations.
**Real fly sensory modalities** (for scoping — cover vision first, the rest are custom/simplified):

- **Vision** — compound eyes, R1–R8 photoreceptors → lamina → medulla → lobula, motion detection via T4/T5 cells. This is the one modality with an existing pretrained connectome-constrained model (`flyvis`). Start here.
- **Olfaction** — antennae/maxillary palps → antennal lobe → mushroom body/lateral horn. No pretrained connectome-constrained model as accessible as flyvis, as far as this doc can confirm — verify current literature before assuming otherwise; likely needs a custom encoding (e.g., synthetic odor → antennal lobe glomerulus activation pattern).
- **Mechanosensation** — Johnston's organ (wind, gravity, near-field sound), bristles.
- **Gustation** — taste on legs/proboscis.
- **Thermo/hygrosensation.**

For anything beyond vision, encode synthetic stimuli as hand-designed activation vectors over the relevant sensory neuron types pulled from the connectome annotations, clearly labeled as a simplification.

### 4.3 Core neural simulation / propagation layer

**Purpose:** turn sensory activation into a stream of activity across the graph.

- **Visual pathway:** use `flyvis`'s pretrained network directly — real weights, validated against real recordings. This is your one fully "real" simulation component.
- **Everything downstream of the optic lobe (central brain → descending neurons → VNC premotor circuits):** flyvis does not cover this. Build a simplified linear-nonlinear or leaky-integrate rate model over the real connectivity graph — now traceable end-to-end within MaleCNS v1.0 — similar in spirit to the "activation screen" approach used in the VNC walking-circuit paper (tonic/patterned input to a candidate neuron, propagate through the real weighted graph, read out downstream activity). This is explicitly custom and should be documented as such — it is connectivity-informed, not dynamics-validated.
- **Concrete flagship circuit to anchor Phase 0/1 (not just Phase 2):** the looming-detection-to-escape pathway is one of the best-characterized circuits in fly neuroscience, studied long before connectomics existed, and its neurons are directly queryable by name in MaleCNS v1.0 — visual loom detectors **LC4** and **LPLC2** feeding the **DNp01** "giant fiber" descending neuron, the classic command neuron for the fly's fast escape jump. Using this real, well-documented circuit as the first motor-gate/decoder test case gives the project an actual literature ground truth to validate against, instead of an arbitrary cut point. Recommended over inventing a novel circuit for the first working demo. **Tech:** PyTorch (matches flyvis's own framework, eases integration) for the differentiable propagation model; `networkx` or `scipy.sparse` for graph representation and efficient sparse propagation.

### 4.4 Motor gate ("paralysis") layer

**Purpose:** implement the actual "can't move" mechanic — intercept and zero out activity at a defined motor boundary.

- Pick a concrete, identifiable boundary: descending neurons (brain→VNC bridge) as Level-1 paralysis, or specific VNC motor neurons/motor neuron pools as a deeper level. MANC annotations let you identify real motor neuron cell types by leg/wing target.
- The gate must produce two parallel traces per run: the "visible to decoder" trace (everything upstream of the gate) and the "ground truth" trace (what actually would have fired downstream) — used only for training/evaluating the decoder, never shown to the end user as if it were live-decoded.

### 4.5 Intent decoder layer

**Purpose:** the actual scientific contribution — predict withheld motor-layer activity from premotor activity alone.

- **Build it in stages of increasing semantic ambition — don't jump straight to "intent":** 
  1. **Neural prediction:** premotor activity → the withheld neuron's raw activity (e.g., predict DNp01 activity from LC4/LPLC2). This is the actual regression/classification task and where most of the engineering risk lives.
  2. **Motor-state prediction:** premotor activity → a coarse motor-pool class (e.g., escape / no-escape).
  3. **Behavioral interpretation:** motor-state prediction → a model-inferred behavioral label, explicitly flagged as such (§8).
  4. **Communication mapping:** behavioral label → symbol (§4.6) — this last step is where the designed-UX layer begins; everything before it is the science.
- Baseline: logistic regression / small MLP (scikit-learn or a small PyTorch model) trained on paired (premotor activity → motor activity) examples generated by running the simulation ungated many times.
- **Train/test protocol:** hold out entire stimulus trajectories for testing, not just individual timepoints — a decoder that's only ever seen interpolations of its training trajectories will look better than it is. Report accuracy on genuinely unseen trajectories.
- Validate against **both** a shuffled-connectivity baseline and a shuffled-label baseline to confirm the model is using real structure, not fitting noise or leaking the withheld signal through some backdoor in the propagation code. Re-run both baselines any time the propagation or gate code changes — leakage is the single easiest way for this project to produce a fake result that looks great.
- Report accuracy as a function of cut-point depth (§2, sub-hypothesis 2) — this curve is the project's flagship deliverable (see Phase 1's cut-point slider), not just an internal sanity check.
- Output: a small number of discrete predicted classes (movement direction, "approach," "avoid," "investigate," etc. — define these from what the motor neuron pools you're gating actually correspond to, don't invent labels that aren't grounded in the motor neuron identities).

### 4.6 Communication protocol / discovery mechanic

**Purpose:** the user-facing puzzle layer — mapping decoder output classes to a small symbol set the user has to learn by experimenting (change the environment, observe which symbol correlates).

- This is pure game design on top of §4.5's real output classes. Don't let the symbol set drift from what the decoder can actually distinguish.
- Log user "TEST" actions and environment changes so the discovery mechanic can build a real (in-session) correlation table rather than faking discovery with pre-scripted reveals.

### 4.7 Visualization & UI layer

- Wheelchair-fly avatar and "communication panel" (signal bar + decoded label + confidence) — front-end presentation, React.
- **Make the wheelchair state dynamic, not decorative:** tie it directly to the actual motor-gate state — e.g. a visible indicator that reads "active" (gate open, fly can move) vs. "blocked" (gate closed, motor output withheld) vs. "decoder observing" (upstream activity still visible). This turns the avatar into a real-time readout of §4.4's actual mechanism instead of a static image, and keeps the visual and the science telling the same story.
- "Neural camera" brain-dive: render a subgraph of real neuron skeletons (FlyWire/navis provides 3D skeleton coordinates) in 3D. This is visually the most expensive piece — for a live whole-brain version, precompute/cache the mesh rather than attempting real-time whole-connectome rendering.
- Confidence bars, decoded output, and any "the fly wants X" language must run through the labeling policy in §8.

### 4.8 Multi-fly behavioral fingerprinting (stretch)

Run N independent instances with identical connectome but different random seeds / synthetic histories; store each instance's activity trace; cluster (e.g., simple k-means/UMAP on summary statistics) to see if distinguishable "profiles" emerge. Frame findings as "trajectories differ given identical wiring, different history" — not personality.

### 4.9 Session/run store

Log every run (stimuli sequence, gate point, decoder output, ground truth, user actions) for reproducibility and for the multi-fly stretch mode. SQLite is enough at this scale; move to Postgres only if the multi-fly mode needs concurrent writers.

### 4.10 Embodied simulation layer — FlyGym / NeuroMechFly

**Purpose:** provide the 3D fruit-fly body, biomechanics, physics, sensory embodiment, and environment interaction without rebuilding fly morphology and physics from scratch.

- Use **FlyGym / NeuroMechFly** as the embodied layer when Phase 1 integration begins. It provides an existing digital fly body, MuJoCo-based physics, interactive scene/world support, and simulated sensory interfaces.
- Responsibilities: 3D fly morphology, joints/limb dynamics, MuJoCo physics, terrain/environment interaction, simulated sensory observations, and receipt of motor commands from the Hawking Fly neural engine.
- Interface direction:
  ```
  3D world
      ↓
  FlyGym sensory state
      ↓
  FlyVis / sensory encoder
      ↓
  MaleCNS-based neural simulation
      ↓
  motor-related activity
      ↓
  motor gate
      ↓
  FlyGym / NeuroMechFly body
  ```
- For normal closed-loop runs, motor outputs can drive the embodied fly. For blocked-motor experiments, the selected motor boundary is withheld from the body while the downstream trace is retained internally as ground truth for decoder evaluation.
- **Hybrid-model rule:** FlyGym/NeuroMechFly and MaleCNS are modeling layers representing different specimens / data sources. The combined system must therefore be described as a **hybrid simulation**, not as an exact digital reconstruction of one individual fly.
- Do not make FlyGym a Phase 0 prerequisite. First validate the neural propagation and decoder using the smallest defensible circuit; then connect the validated neural engine to the 3D body/world.

---

## 5. Data sources summary

| Dataset Covers Scale (verify live) Access Package  |                                                                                                       |                                      |                                              |                                          |
| -------------------------------------------------- | ----------------------------------------------------------------------------------------------------- | ------------------------------------ | -------------------------------------------- | ---------------------------------------- |
| **MaleCNS v1.0 (primary)**                         | **Whole male CNS: brain + both optic lobes + VNC, one animal**                                        | **166,700 neurons, \~125M synapses** | neuPrint token, dataset name `male-cns:v1.0` | `neuprint-python`, `navis`               |
| FlyWire                                            | Whole adult *female* brain                                                                            | \~139k neurons                       | CAVE token + community agreement             | `CAVEclient`, `fafbseg-py`, `navis`      |
| Hemibrain                                          | Partial female central brain                                                                          | \~25k neurons                        | neuPrint token (free, manual signup)         | `neuprint-python`                        |
| MANC                                               | Male ventral nerve cord only (superseded here by MaleCNS v1.0)                                        | —                                    | neuPrint token                               | `neuprint-python`                        |
| FANC                                               | Female ventral nerve cord                                                                             | —                                    | —                                            | community tools (`malevnc`-adjacent)     |
| flyvis pretrained model                            | Optic lobe only (65 columnar cell types, \~45.7k cells, from the FIB-25/FIB-19 optic-lobe connectome) | fixed, pretrained                    | pip install, open weights                    | `flyvis` (PyPI/GitHub: TuragaLab/flyvis) |

---

## 6. Technology stack

| Layer Tools                               |                                                                        |
| ----------------------------------------- | ---------------------------------------------------------------------- |
| Connectome access                         | `neuprint-python`, `CAVEclient`, `fafbseg-py`, `navis`, `cocoa`        |
| Pretrained vision model                   | `flyvis` (PyTorch-based)                                               |
| Custom propagation / decoder              | PyTorch, `networkx` / `scipy.sparse`, `scikit-learn`                   |
| Backend API                               | Python 3.11, FastAPI, WebSocket endpoint for streaming activity frames |
| Session/run storage                       | SQLite (Postgres if concurrency demands grow)                          |
| Frontend                                  | React + TypeScript, Tailwind (for the dark control-room aesthetic)     |
| 3D neural camera                          | `three.js` / `react-three-fiber`, fed real neuron skeleton coordinates |
| Embodied fly + physics                    | FlyGym / NeuroMechFly, MuJoCo                                         |
| Charts (confidence bars, decoding curves) | Recharts or D3                                                         |
| Dev/deploy                                | Docker + docker-compose for reproducibility                            |

---

## 7. Build phases

### Phase 0 — Core MVP, broken into sub-stages so the risky part gets validated before anything else is built

Don't build the UI before you know the pipeline works. Order matters here:

- **0A — Propagation validation (no gate, no decoder yet):** pull `flyvis`, run its pretrained model on synthetic stimuli (moving edge, flash, loom), and confirm the custom propagation model (§4.3) can plausibly carry that activity forward to DNp01 (pulled via `neuprint-python`). This just tests whether the pipeline produces sane activity, not whether anything is "decodable" yet. **Before assuming LC4/LPLC2 connect to DNp01 in a particular way, query the actual path in MaleCNS v1.0 rather than relying on older circuit diagrams from the literature — the real reconstruction may include different or additional intermediate neurons than classical physiology papers described.**
- **0B — Motor gate:** withhold the DNp01 (or chosen boundary) trace from what's downstream; produce the paired visible/ground-truth traces described in §4.4.
- **0C — Decoder + baselines:** train the decoder (§4.5) on a held-out split of stimulus trajectories, and confirm it beats both a shuffled-connectivity and a shuffled-label baseline. **This is the actual go/no-go milestone for the whole project** — don't proceed to UI work until this is real and reproducible.
- **0D — Minimal UI:** a single screen — stimulus/world state, a small neural-activity readout for LC4/LPLC2/DNp01, a motor-gate status indicator, and a "model-inferred: X — confidence: Y%" readout. No avatar art, no cinematic layer yet. This is enough to prove the concept end to end.
- **0E — Symbol mapping + wheelchair avatar:** only once 0A–0D work, add the small symbol set and the presentation layer.

**Acceptance:** decoder beats shuffled baselines by a documented margin on held-out stimulus trajectories; end-to-end demo runs from stimulus → decoded output on screen; the real vs. designed split (§3) is visibly reflected in the UI.

### Phase 1

- Integrate **FlyGym / NeuroMechFly** as the embodied 3D body/world layer: connect simulated sensory observations into the Hawking Fly sensory pipeline and route motor outputs from the neural engine into the biomechanical fly body. Treat this as a hybrid integration, not an exact single-animal reconstruction.
- Extend past the optic lobe into central brain/descending neurons using the MaleCNS v1.0 connectivity graph + the custom propagation model (§4.3) — explicitly label this as simplified dynamics.
- Add a second synthetic sensory modality.
- Build the "teach the fly" discovery mechanic (§4.6) with real in-session logging.
- 3D neural camera using real skeleton coordinates for a subgraph (not the whole brain).
- **Flagship visualization — the cut-point curve:** turn sub-hypothesis 2 (§2) into an actual interactive feature — a slider that moves the paralysis boundary upstream (vision → medulla → lobula → descending neuron → motor) and recomputes/displays decoding accuracy at each point. This is arguably the single most valuable output of the whole project — it's what turns the demo from "cool fly" into "a real, testable result" — and is worth prioritizing over additional cosmetic polish elsewhere in this phase.

### Phase 2 / stretch

- MANC-grounded leg/wing motor circuit demo replicating a known, published circuit (e.g., the walking-related descending pathway from the VNC CPG work) — this is your one case where you can validate against literature ground truth, worth flagging as the "we checked this against real neuroscience" flagship moment.
- Progressive paralysis levels (1–5, per the original concept doc).
- 100-fly multi-instance mode with clustering.
- Full whole-brain cinematic render — precomputed, not live.

---

## 8. Scientific honesty & UI labeling policy

- Never phrase a decoded output as "the fly wants X." Use "model-inferred state," "decoded signal," or similar, every time, in every UI surface — confidence bars, panels, and any copy generated procedurally.
- **Keep the poetic tagline and the scientific statement separate.** "Can a Brain Speak Without a Body?" is fine for the narrative/marketing layer, but it implies the brain is producing language, which isn't what's happening. The precise version of what this project actually does is: *"Can upstream neural activity reveal a blocked motor command?"* — use that phrasing anywhere the project is being described technically (README first paragraph, any documentation, any answer to "wait, what does this actually do?").
- Any screen showing a predicted/decoded value must be visually distinguishable from any screen showing raw/ground-truth simulation output.
- The discovery mechanic (§4.6) is a designed puzzle, not an emergent language — don't let marketing or in-app copy imply otherwise.
- Document, in-repo, exactly which layers are pretrained/published (flyvis) vs. custom/simplified (everything downstream) — §3's table should live in the README, not just this spec. The README's first technical paragraph should describe the whole pipeline precisely as: *a hybrid connectome-constrained simulation with a validated pretrained visual component and custom, unvalidated downstream dynamics* — not "a simulation of the fly brain."

---

## 9. Suggested repository structure

```
silent-fly/
  data/
    connectome/              # cached connectome pulls (gitignored)
    stimuli/                 # synthetic sensory stimulus definitions
  services/
    sim-engine/               # Python: flyvis wrapper + custom propagation + motor gate
      connectome/
      sensory/
      propagation/
      motor_gate/
      decoder/
      embodiment/              # FlyGym / NeuroMechFly integration + motor interface
      api/                     # FastAPI app + websocket
    session-store/             # run logging, multi-fly histories
  web/
    app/                        # React + TS frontend
      components/
      three/                     # neural camera 3D viewer
      state/
  notebooks/                    # exploration / decoder validation
  experiments/                  # every decoder/baseline run, reproducible
    loom_escape/
    cutpoint_decode/
    shuffled_baseline/
    ablation/
    # each experiment directory produces: config.json, stimuli.json,
    # model_version, dataset_version (MaleCNS snapshot id), seed,
    # metrics.json, plots/ — so a result is always traceable to an
    # exact run, not "it worked once on my laptop"
  docs/
    spec.md                     # this file
    honesty-policy.md
  docker-compose.yml

```

---

## 10. Risks & open questions

- **Compute:** real-time whole-brain (166k+ neuron) simulation is not realistic for an interactive demo. Scope live simulation to bounded subgraphs; precompute/cache anything whole-brain.
- **FlyGym integration:** the neural model and embodied simulator expose different state/action representations. Define an explicit sensory encoder and motor interface before claiming end-to-end biological behavior; validate each interface independently.
- **Data access friction:** FlyWire requires community-agreement signup; neuPrint requires a personal token. These are manual, one-time human steps — don't try to script around them.
- **Decoder task validity:** the single biggest technical risk is accidental leakage (decoder effectively seeing the ground truth it's supposed to predict). Keep the gate boundary and the train/test split airtight; validate against a shuffled baseline every time the pipeline changes.
- **Coverage gaps:** whether a pretrained connectome-constrained model exists for any modality beyond vision is unconfirmed as of this doc — verify current literature before assuming flyvis-equivalent shortcuts exist elsewhere.
- **Framing:** the wheelchair/Hawking-coded visual identity is a real asset but a real risk — it's most defensible when the science underneath is genuinely being treated seriously (§8), least defensible if it ends up as a skin on a toy demo. Worth a deliberate human decision, not something to default into.

---

## 10b. Local hardware feasibility (e.g. MacBook Air M5)

As scoped in this doc (bounded circuits of \~1,000–5,000 neurons, not live whole-connectome dynamics), this project fits comfortably on a laptop-class machine — including a MacBook Air M5. Specifics:

- **flyvis inference (Phase 0):** the pretrained optic-lobe model (\~45.7k cells) only needs to run forward inference for a handful of timesteps per stimulus, not training from scratch. Trivial on the M5's CPU alone; PyTorch's MPS backend gives GPU acceleration on Apple Silicon if needed, and the M5's GPU cores add hardware matmul acceleration that specifically helps PyTorch workloads.
- **Custom propagation + decoder on a bounded subgraph (Phase 0/1):** a few thousand nodes as a sparse graph is a lightweight computation — negligible load even on the base 16GB unified-memory M5 Air.
- **Loading/querying the full MaleCNS v1.0 graph as data** (not simulating it live): storing the connectivity as a sparse adjacency structure and running annotation/cell-type queries is feasible within 16GB, more comfortable at 24GB+ if you configure it that way — but this doc already recommends against live whole-brain dynamical simulation regardless of hardware (§4.1's scoping note, §10's compute risk), so this isn't actually a constraint you'll hit.
- **What the Air will** ***not*** **be good for:** sustained heavy training runs (e.g., fine-tuning flyvis itself, or training the multi-fly stretch mode's clustering at scale) — the Air is fanless, so long sustained GPU/CPU load will thermal-throttle. If Phase 2's stretch goals grow in that direction, that's the point to move training to a cloud GPU instance and keep the Air for development/inference.
- **Frontend + Neuroglancer exploration:** no local compute concern — both are lightweight/browser-based. FlyGym/MuJoCo embodied simulation should remain bounded to small scenes and controller steps during development; profile it separately from the neural decoder.

Net: the base M5 Air config is fine for everything in Phase 0 and most of Phase 1; a bump to 24GB unified memory buys comfortable headroom, not a hard requirement.

## 11. What this teaches (outcomes, not just deliverables)

- Whether — and how much — connectome structure alone (real wiring, simplified dynamics) lets you predict a blocked motor output from upstream activity, and how that degrades with distance from the gate.
- Which anatomical bottlenecks carry the most decodable information (testable via ablation at different gate points).
- Practical experience with real connectome datasets and their access/tooling ecosystem (MaleCNS/neuPrint, FlyWire, hemibrain, MANC, flyvis, navis) plus embodied simulation through FlyGym/NeuroMechFly.
- A direct, working illustration of the same problem class as real motor-intent decoding in paralysis-focused BCI research — using an organism simple enough to fully instrument and ground-truth.

---

## 12. Final system architecture

The intended end-to-end system is:

```
                         FLYGYM 3D WORLD
                                │
                       sensory observations
                                ↓
                         FLYVIS VISION
                                │
                                ↓
                         MALECNS GRAPH
                                │
                     custom neural dynamics
                                ↓
                         PREMOTOR STATE
                                │
                         ┌──────┴──────┐
                         │  MOTOR GATE │
                         └──────┬──────┘
                                │
                   ┌────────────┴────────────┐
                   ↓                         ↓
             decoder-visible            withheld
                activity               ground truth
                   │                         │
                   ↓                         │
                DECODER ←───────────────────┘
                   │
                   ↓
          model-inferred motor state
                   │
                   ↓
          communication / UI layer
                   │
                   ↓
          THE HAWKING FLY EXPERIENCE
```

The neural experiment remains the source of truth. FlyGym/NeuroMechFly is the embodied 3D body and world layer added after the neural pipeline is validated.

## 12. Glossary

- **Connectome** — the complete wiring diagram of synaptic connections in a nervous system.
- **Descending neuron (DN)** — a neuron that carries signals from the central brain down into the ventral nerve cord, the main brain-to-body bridge.
- **VNC (ventral nerve cord)** — the fly's "spinal cord" equivalent; houses leg/wing motor neurons.
- **MANC / FANC** — Male/Female Adult Nerve Cord connectome datasets.
- **Premotor** — neurons directly upstream of motor neurons, one synapse or a few synapses removed from actually driving muscle.
- **Rate model** — a simplified neuron model representing activity as a continuous firing rate rather than individual spikes.
- **Connectome-constrained network** — a model whose architecture (which units connect to which) is fixed by real measured connectivity, with only lower-level parameters fit computationally.

---

## 13. References

- Google Research, HHMI Janelia FlyEM, and University of Cambridge Drosophila Connectomics Group. "Sexual dimorphism in the complete connectome of the Drosophila male central nervous system." *Cell* (Sept. 2026). Dataset: MaleCNS v1.0. Access/download: https\://male-cns.janelia.org/download/ · Explore: https\://neuprint.janelia.org (dataset `male-cns:v1.0`) · Project page: https\://www\.janelia.org/project-team/flyem/male-cns-connectome
- Lappalainen, J.K. et al. "Connectome-constrained networks predict neural activity across the fly visual system." *Nature* 634, 1132–1140 (2024). https\://doi.org/10.1038/s41586-024-07939-3
- `flyvis` (open-source implementation of the above). https\://github.com/TuragaLab/flyvis
- Shiu, P.K. et al. "A Drosophila computational brain model reveals sensorimotor processing." *Nature* 634, 210–219 (2024).
- Dorkenwald, S. et al. "Neuronal wiring diagram of an adult brain." *Nature* 634, 124–138 (2024). [FlyWire]
- Schlegel, P. et al. "Whole-brain annotation and multi-connectome cell typing of Drosophila." *Nature* 634, 139–152 (2024).
- Zheng, Z. et al. "A complete electron microscopy volume of the brain of adult Drosophila melanogaster." *Cell* 174, 730–743 (2018).
- Vaxenburg, R. et al. "Whole-body physics simulation of fruit fly locomotion." *Nature* (2025).
- "Connectome simulations identify a central pattern generator circuit for fly walking." bioRxiv preprint (2025). [VNC/MANC walking circuit]
- "Whole-Brain Connectomic Graph Model Enables Whole-Body Locomotion Control in Fruit Fly." arXiv preprint.
- "NeuroMechFly v2: simulating embodied sensorimotor control in adult Drosophila." *Nature Methods* (2024/2025). https\://www\.nature.com/articles/s41592-024-02497-y
- neuPrint / `neuprint-python` (Janelia FlyEM) — hemibrain and MANC access. https\://neuprint.janelia.org
- FlyWire / Codex — whole-brain connectome browser. https\://flywire.ai, https\://codex.flywire.ai
- `navis`, `cocoa`, `fafbseg-py` — Python connectomics tooling (flyconnectome GitHub org)