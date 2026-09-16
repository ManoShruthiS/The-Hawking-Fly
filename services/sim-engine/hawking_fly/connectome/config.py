"""Connection configuration — neuPrint token/dataset settings read from .env.

The neuPrint token is a manual, one-time human step (free account at
https://neuprint.janelia.org). This module only *reads* credentials; it never
hardcodes or commits one.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel

_PROJECT_ROOT = Path(__file__).resolve().parents[4]  # repo root


class ConnectomeConfig(BaseModel):
    token: str | None = None
    dataset: str = "male-cns:v1.0"
    server: str = "https://neuprint.janelia.org"

    @property
    def has_token(self) -> bool:
        return bool(self.token and self.token.strip())


@lru_cache(maxsize=1)
def get_config() -> ConnectomeConfig:
    load_dotenv(_PROJECT_ROOT / ".env", override=False)
    import os

    return ConnectomeConfig(
        token=os.getenv("NEUPRINT_TOKEN") or None,
        dataset=os.getenv("NEUPRINT_DATASET", "male-cns:v1.0"),
        server=os.getenv("NEUPRINT_SERVER", "https://neuprint.janelia.org"),
    )