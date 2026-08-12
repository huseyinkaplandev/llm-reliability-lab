"""Serverless entrypoint. The package lives under src/, which is not on the
path when the function runs from inside api/."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from llm_reliability_lab.api import app  # noqa: E402

__all__ = ["app"]
