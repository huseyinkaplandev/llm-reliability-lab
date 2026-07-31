from llm_reliability_lab.models import EvalCase, EvalSuite
from llm_reliability_lab.report import render_html
from llm_reliability_lab.runner import evaluate_suite


def good_case(identifier: str = "good") -> EvalCase:
    return EvalCase(
        id=identifier,
        query="What is the policy?",
        response="The policy is 30 days [policy-1].",
        retrieved_ids=["policy-1"],
        expected_citations=["policy-1"],
        expected_facts=["30 days"],
        latency_ms=300,
    )


def test_evaluate_suite_passes_grounded_case() -> None:
    report = evaluate_suite(EvalSuite(name="smoke", cases=[good_case()]))
    assert report.summary.pass_rate == 1
    assert report.cases[0].failures == []


def test_latency_failure_fails_case() -> None:
    slow = good_case("slow").model_copy(update={"latency_ms": 2000})
    result = evaluate_suite(EvalSuite(name="slow", cases=[slow])).cases[0]
    assert not result.passed
    assert "latency_slo" in result.failures


def test_html_report_surfaces_failures() -> None:
    bad = good_case("bad").model_copy(update={"response": "Unsupported [fake]."})
    html = render_html(evaluate_suite(EvalSuite(name="report", cases=[bad])))
    assert "FAIL" in html
    assert "invalid_citation" in html
