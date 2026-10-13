from fastapi.testclient import TestClient

from llm_reliability_lab.api import app

client = TestClient(app)


def test_health() -> None:
    assert client.get("/health").json() == {"status": "ok"}


def test_evaluate_endpoint() -> None:
    response = client.post(
        "/evaluate",
        json={
            "name": "api",
            "cases": [
                {
                    "id": "one",
                    "query": "Q",
                    "response": "Fact [doc-1].",
                    "retrieved_ids": ["doc-1"],
                    "expected_citations": ["doc-1"],
                    "expected_facts": ["Fact"],
                    "latency_ms": 100,
                }
            ],
        },
    )
    assert response.status_code == 200
    assert response.json()["summary"]["pass_rate"] == 1


def test_source_lists_the_dataset_and_the_evaluator() -> None:
    files = {item["path"]: item for item in client.get("/source").json()}
    assert "hallucinated-citation" in files["sample_data/eval_cases.jsonl"]["content"]
    assert "def citation_scores" in files["src/llm_reliability_lab/metrics.py"]["content"]
    assert files[".github/workflows/ci.yml"]["group"] == "CI gate"
