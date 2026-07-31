from pydantic import BaseModel, Field, model_validator


class EvalCase(BaseModel):
    id: str = Field(min_length=1)
    query: str = Field(min_length=1)
    response: str = Field(min_length=1)
    retrieved_ids: list[str] = Field(default_factory=list)
    expected_citations: list[str] = Field(default_factory=list)
    expected_facts: list[str] = Field(default_factory=list)
    should_abstain: bool = False
    latency_ms: float = Field(ge=0)
    input_tokens: int = Field(ge=0, default=0)
    output_tokens: int = Field(ge=0, default=0)

    @model_validator(mode="after")
    def validate_expectations(self) -> "EvalCase":
        if self.should_abstain and (self.expected_citations or self.expected_facts):
            raise ValueError("abstention cases cannot require citations or facts")
        return self


class EvalConfig(BaseModel):
    latency_slo_ms: float = Field(default=1500, gt=0)
    input_cost_per_million: float = Field(default=0.15, ge=0)
    output_cost_per_million: float = Field(default=0.60, ge=0)
    minimum_case_score: float = Field(default=0.80, ge=0, le=1)


class EvalSuite(BaseModel):
    name: str = Field(min_length=1)
    cases: list[EvalCase] = Field(min_length=1)
    config: EvalConfig = Field(default_factory=EvalConfig)


class CaseResult(BaseModel):
    id: str
    passed: bool
    score: float
    citation_precision: float
    citation_recall: float
    fact_recall: float
    abstention_correct: bool
    latency_slo_pass: bool
    estimated_cost_usd: float
    failures: list[str]


class EvalSummary(BaseModel):
    total_cases: int
    passed_cases: int
    pass_rate: float
    mean_score: float
    citation_precision: float
    citation_recall: float
    fact_recall: float
    latency_slo_pass_rate: float
    total_estimated_cost_usd: float


class EvalReport(BaseModel):
    suite: str
    summary: EvalSummary
    cases: list[CaseResult]
