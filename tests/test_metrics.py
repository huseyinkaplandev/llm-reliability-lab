from llm_reliability_lab.metrics import (
    abstention_correct,
    citation_scores,
    estimated_cost_usd,
    extract_citations,
    fact_recall,
)
from llm_reliability_lab.models import EvalCase, EvalConfig


def case(**overrides: object) -> EvalCase:
    values = {
        "id": "one",
        "query": "question",
        "response": "Answer [doc-1].",
        "retrieved_ids": ["doc-1"],
        "expected_citations": ["doc-1"],
        "expected_facts": ["Answer"],
        "latency_ms": 100,
    }
    values.update(overrides)
    return EvalCase(**values)


def test_extracts_unique_citations() -> None:
    assert extract_citations("A [doc-1], B [doc-1], C [doc:2]") == {"doc-1", "doc:2"}


def test_citation_precision_rejects_unretrieved_sources() -> None:
    precision, recall = citation_scores(case(response="Answer [fake]."))
    assert precision == 0
    assert recall == 0


def test_fact_recall_is_case_insensitive() -> None:
    assert fact_recall(case(response="the ANSWER is here [doc-1].")) == 1


def test_abstention_policy() -> None:
    abstain = case(
        response="There is not enough evidence to answer.",
        retrieved_ids=[],
        expected_citations=[],
        expected_facts=[],
        should_abstain=True,
    )
    assert abstention_correct(abstain)


def test_cost_estimate() -> None:
    priced = case(input_tokens=1_000_000, output_tokens=1_000_000)
    assert estimated_cost_usd(priced, EvalConfig()) == 0.75
