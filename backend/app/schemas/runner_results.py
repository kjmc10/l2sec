from pydantic import BaseModel


class FindingInput(BaseModel):
    name: str | None
    severity: str | None
    confidence: str | None
    url: str | None
    method: str | None
    cwe: str | None
    owasp_category: str | None
    evidence: str | None
    remediation: str | None


class RunnerResultsPayload(BaseModel):
    findings: list[FindingInput]