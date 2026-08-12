from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse

from .io import load_jsonl
from .models import EvalReport, EvalSuite
from .report import render_html
from .runner import evaluate_suite

app = FastAPI(title="LLM Reliability Lab", version="0.1.0")

_ROOT = Path(__file__).resolve().parents[2]


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
