import re

from .models import EvalCase, EvalConfig

CITATION_PATTERN = re.compile(r"\[([A-Za-z0-9_.:-]+)\]")
ABSTENTION_MARKERS = (
    "not enough evidence",
    "insufficient evidence",
    "cannot answer from the provided",
    "don't have enough information",
    "do not have enough information",
)


def extract_citations(text: str) -> set[str]:
    return set(CITATION_PATTERN.findall(text))


def safe_ratio(numerator: int, denominator: int, *, empty_value: float = 1.0) -> float:
    return empty_value if denominator == 0 else numerator / denominator


def citation_scores(case: EvalCase) -> tuple[float, float]:
    cited = extract_citations(case.response)
    retrieved = set(case.retrieved_ids)
    expected = set(case.expected_citations)
    valid = cited & retrieved
    precision = safe_ratio(len(valid), len(cited), empty_value=1.0 if not expected else 0.0)
    recall = safe_ratio(len(cited & expected), len(expected))
    return precision, recall


def fact_recall(case: EvalCase) -> float:
    response = case.response.casefold()
    matched = sum(fact.casefold() in response for fact in case.expected_facts)
    return safe_ratio(matched, len(case.expected_facts))


def abstention_correct(case: EvalCase) -> bool:
    has_marker = any(marker in case.response.casefold() for marker in ABSTENTION_MARKERS)
    return has_marker if case.should_abstain else not has_marker


def estimated_cost_usd(case: EvalCase, config: EvalConfig) -> float:
    input_cost = case.input_tokens * config.input_cost_per_million / 1_000_000
    output_cost = case.output_tokens * config.output_cost_per_million / 1_000_000
    return input_cost + output_cost
