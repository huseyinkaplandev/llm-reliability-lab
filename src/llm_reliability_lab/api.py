from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from .models import EvalReport, EvalSuite
from .report import render_html
from .runner import evaluate_suite

app = FastAPI(title="LLM Reliability Lab", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/evaluate", response_model=EvalReport)
def evaluate(suite: EvalSuite) -> EvalReport:
    return evaluate_suite(suite)


@app.post("/evaluate/html", response_class=HTMLResponse)
def evaluate_html(suite: EvalSuite) -> str:
    return render_html(evaluate_suite(suite))
