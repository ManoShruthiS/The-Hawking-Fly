# The Hawking Fly — sim-engine image (Phase 0A: flyvis validation)
# NOTE: flyvis pins a specific torch build. This Dockerfile installs flyvis
# FIRST and lets it pull its own torch pin, then installs the project package.

FROM python:3.11-slim

WORKDIR /app

# System deps minimal for flyvis/sci-stack wheels on Debian
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-lock.txt /app/services/sim-engine/requirements-lock.txt
ENV FLYVIS_ROOT_DIR=/app/data/flyvis

# Install flyvis first so torch is resolved to flyvis's pin
RUN pip install --no-cache-dir flyvis

# Then the rest from the lockfile (skipping flyvis/torch, already present)
RUN pip install --no-cache-dir --no-deps \
    numpy scipy networkx scikit-learn python-dotenv pydantic neuprint-python \
    matplotlib pytest

COPY . /app/services/sim-engine
RUN pip install --no-deps -e /app/services/sim-engine

CMD ["python", "-m", "hawking_fly.experiments.run", "--config", "experiments/loom_escape/config.json"]