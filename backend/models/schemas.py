from pydantic import BaseModel, Field, field_validator


class LabInput(BaseModel):
    test_name: str = Field(min_length=1, max_length=100)
    value: float = Field(allow_inf_nan=False)
    unit: str = Field(min_length=1, max_length=30)
    date: str | None = Field(default=None, max_length=30)

    @field_validator("test_name", "unit")
    @classmethod
    def strip_required(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value


class AnalyzeRequest(BaseModel):
    labs: list[LabInput] = Field(min_length=1, max_length=30)


class LabResult(BaseModel):
    test_name: str
    value: float
    unit: str
    status: str
    reference_range: str
    classification_reason: str
    direction: str
    normal_low: float | None = None
    normal_high: float | None = None
    date: str | None = None
    explanation: str
    next_step: str


class AnalyzeResponse(BaseModel):
    results: list[LabResult]
    agent_activity: list[dict] = []
    overall_summary: dict
