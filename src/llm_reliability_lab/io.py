import json
from pathlib import Path

from .models import EvalCase, EvalConfig, EvalSuite


def load_jsonl(path: str | Path, *, name: str | None = None) -> EvalSuite:
    source = Path(path)
    cases = [EvalCase.model_validate_json(line) for line in source.read_text().splitlines() if line]
    return EvalSuite(name=name or source.stem, cases=cases, config=EvalConfig())


def write_json(data: object, path: str | Path) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(data, indent=2) + "\n")
