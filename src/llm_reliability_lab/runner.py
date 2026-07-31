from statistics import fmean

from .metrics import abstention_correct, citation_scores, estimated_cost_usd, fact_recall
from .models import CaseResult, EvalCase, EvalReport, EvalSuite, EvalSummary


def evaluate_case(case: EvalCase, suite: EvalSuite) -> CaseResult:
    precision, recall = citation_scores(case)
    facts = fact_recall(case)
    abstention = abstention_correct(case)
    latency = case.latency_ms <= suite.config.latency_slo_ms
    cost = estimated_cost_usd(case, suite.config)

    quality_metrics = [precision, recall, facts, float(abstention)]
    score = fmean(quality_metrics)
    failures: list[str] = []
    if precision < 1:
        failures.append("invalid_citation")
    if recall < 1:
        failures.append("missing_citation")
    if facts < 1:
        failures.append("missing_expected_fact")
    if not abstention:
        failures.append("abstention_policy")
    if not latency:
        failures.append("latency_slo")

    return CaseResult(
        id=case.id,
        passed=score >= suite.config.minimum_case_score and latency,
        score=score,
        citation_precision=precision,
        citation_recall=recall,
        fact_recall=facts,
        abstention_correct=abstention,
        latency_slo_pass=latency,
        estimated_cost_usd=cost,
        failures=failures,
    )


def evaluate_suite(suite: EvalSuite) -> EvalReport:
    results = [evaluate_case(case, suite) for case in suite.cases]
    summary = EvalSummary(
        total_cases=len(results),
        passed_cases=sum(result.passed for result in results),
        pass_rate=fmean(float(result.passed) for result in results),
        mean_score=fmean(result.score for result in results),
        citation_precision=fmean(result.citation_precision for result in results),
        citation_recall=fmean(result.citation_recall for result in results),
        fact_recall=fmean(result.fact_recall for result in results),
        latency_slo_pass_rate=fmean(float(result.latency_slo_pass) for result in results),
        total_estimated_cost_usd=sum(result.estimated_cost_usd for result in results),
    )
    return EvalReport(suite=suite.name, summary=summary, cases=results)
