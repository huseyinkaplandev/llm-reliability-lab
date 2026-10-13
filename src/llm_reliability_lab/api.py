from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse

from .io import load_jsonl
from .models import EvalReport, EvalSuite, SourceFile
from .report import render_html
from .runner import evaluate_suite

app = FastAPI(title="LLM Reliability Lab", version="0.1.0")

_ROOT = Path(__file__).resolve().parents[2]

_SOURCE_FILES = (
    ("Dataset", "sample_data/eval_cases.jsonl"),
    ("Evaluator", "src/llm_reliability_lab/models.py"),
    ("Evaluator", "src/llm_reliability_lab/metrics.py"),
    ("Evaluator", "src/llm_reliability_lab/runner.py"),
    ("Evaluator", "src/llm_reliability_lab/report.py"),
    ("Evaluator", "src/llm_reliability_lab/cli.py"),
    ("Evaluator", "src/llm_reliability_lab/io.py"),
    ("Evaluator", "src/llm_reliability_lab/api.py"),
    ("Tests", "tests/test_metrics.py"),
    ("Tests", "tests/test_runner.py"),
    ("Tests", "tests/test_api.py"),
    ("CI gate", ".github/workflows/ci.yml"),
    ("Project", "pyproject.toml"),
    ("Project", "Dockerfile"),
)


@lru_cache(maxsize=1)
def _sample_suite() -> EvalSuite:
    """The bundled suite, so the hosted demo has something to run on arrival."""
    return load_jsonl(_ROOT / "sample_data" / "eval_cases.jsonl", name="sample suite")


@app.get("/", include_in_schema=False)
def demo() -> FileResponse:
    return FileResponse(_ROOT / "demo" / "index.html")


@app.get("/sample", response_model=EvalSuite)
def sample() -> EvalSuite:
    return _sample_suite()


@lru_cache(maxsize=1)
def _source_files() -> list[SourceFile]:
    """The files the demo shows, read from the deployed bundle itself."""
    files = []
    for group, relative_path in _SOURCE_FILES:
        path = _ROOT / relative_path
        if path.is_file():
            content = path.read_text(encoding="utf-8")
            files.append(SourceFile(group=group, path=relative_path, content=content))
    return files


@app.get("/source", response_model=list[SourceFile])
def source() -> list[SourceFile]:
    return _source_files()


@app.get("/report/sample", response_class=HTMLResponse, include_in_schema=False)
def sample_report() -> str:
    return render_html(evaluate_suite(_sample_suite()))


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/evaluate", response_model=EvalReport)
def evaluate(suite: EvalSuite) -> EvalReport:
    return evaluate_suite(suite)


@app.post("/evaluate/html", response_class=HTMLResponse)
def evaluate_html(suite: EvalSuite) -> str:
    return render_html(evaluate_suite(suite))
