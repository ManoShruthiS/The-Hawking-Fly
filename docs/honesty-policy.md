# Scientific honesty & UI labeling policy

Applies to every code comment, README, screen, and piece of generated copy in
this project. Non-negotiable. From §8 of the spec (`docs/spec.md`).

## Language rules

- Never phrase a decoded output as "the fly wants X." Use **"model-inferred
  state"**, **"decoded signal"**, or similar, in every UI surface — confidence
  bars, panels, procedurally generated copy.
- Keep the poetic tagline and the scientific statement separate.

  - Narrative / marketing layer: *"Can a Brain Speak Without a Body?"*
  - Technical description (README first paragraph, docs, any answer to "what
    does this actually do?"): *"Can upstream neural activity reveal a blocked
    motor command?"*

- Any screen showing a **predicted/decoded** value must be visually
  distinguishable from any screen showing **raw / ground-truth** simulation
  output.
- The discovery mechanic (§4.6) is a **designed puzzle, not an emergent
  language** — never imply otherwise in marketing or in-app copy.

## Model-layer labels (in-repo)

These live in code docstrings and the README:

- **pretrained / published:** `flyvis` (Lappalainen et al. 2024) — real
  connectome-derived weights, validated against recordings.
- **real data, custom dynamics:** MaleCNS v1.0 / other connectome graphs with
  our simplified rate propagation — *connectivity-informed, not
  dynamics-validated*.
- **real prediction task, novel method:** the motor-intent decoder (§4.5) —
  genuine train/test split, the project's actual contribution.
- **designed UX / presentation:** discovery mechanic, wheelchair avatar,
  neural camera, cinematic layer.

## Hybrid-simulation rule

MaleCNS wiring + FlyVis visual model + custom downstream dynamics + FlyGym /
NeuroMechFly body represent **different specimens / modeling layers**. The
combined system must always be described as a **hybrid simulation**, never as
an exact digital reconstruction of one individual fly.

## Reporting decoded signals

- Prefer "model-inferred: ESCAPE — confidence 71%" over "the fly is about to
  flee."
- Show confidence, show the cut-point / gating context, and label the layer
  being decoded (e.g., "decoded from descending-neuron activity").
- When the motor gate is active, distinguish "decoder-observing" from
  "blocked" and from "gate open" on every relevant surface.