# hawking-fly (sim-engine)

Python package backing The Hawking Fly project. See the repo root README.

Install order matters — flyvis pins its own torch build:

```bash
python3.11 -m venv .venv            # from repo root
source .venv/bin/activate
pip install flyvis                  # pulls pinned torch
pip install -e "services/sim-engine[dev]"
```

When the environment is successfully built, freeze exact versions:

```bash
pip freeze > services/sim-engine/requirements-lock.txt
```

**Working versions as of Phase 0A validation (Sept 16 2026):**
- flyvis: 1.2.0
- torch: 2.14.0 (pulled by flyvis, macOS arm64 CPU — MPS not used by flyvis by default)
- scipy: 1.17.1, numpy: 2.4.6, networkx: 3.6.1, scikit-learn: 1.9.1
- neuprint-python: 0.6.3, pydantic: 2.13.5