# Loom-escape experiment (Phase 0A)

Validates that the pipeline produces *sane* activity before any decoder work:

- **flash** — native flyvis `Flashes` dataset
- **moving_edge** — native flyvis `MovingEdge` dataset (small slice: 1 angle, 1 width, 1 speed)
- **loom** — custom expanding-disk stimulus (`hawking_fly.sensory.stimuli.Loom`),
  rendered on the same hexagonal receptor lattice flyvis uses (the canonical
  predator-approach stimulus for the LC4/LPLC2 → DNp01 escape pathway)

Run:

```bash
source .venv/bin/activate
python -m hawking_fly.experiments.run --config experiments/loom_escape/config.json
```

Success bar for 0A: finite, distinguishable mean-response traces per stimulus.
Nothing about decodability is claimed at this stage (that is Phase 0C).

## Circuit status

With no `NEUPRINT_TOKEN` yet, the MaleCNS LC4/LPLC2 → DNp01 hop is *not*
wired. Add the token to `.env`, run the `connectome` exploration notebook/call,
and this experiment gains a `circuit` section.