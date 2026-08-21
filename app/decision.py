from pydantic import BaseModel


MIN_SCORE = 0.70
MIN_MARGIN = 0.15


class DecisionResult(BaseModel):
    decision: str
    confidence: float
    margin: float


def make_decision(scores: dict[str, float]) -> DecisionResult:
    ranked = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True
    )

    _, top_score = ranked[0]
    _, second_score = ranked[1]

    margin = top_score - second_score

    if top_score >= MIN_SCORE and margin >= MIN_MARGIN:
        decision = "automate"
    else:
        decision = "manual_review"

    return DecisionResult(
        decision=decision,
        confidence=top_score,
        margin=margin,
    )