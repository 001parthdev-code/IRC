from app.security_engine import analyze


def analyze_ticket(ticket: str) -> dict:
    result = analyze(
        ticket,
        store_if_risky=False
    )

    return {
        "risk_score": result["risk_score"],
        "verdict": result["verdict"],
        "rule_matches": result["rule_matches"],
        "semantic_matches": result["semantic_matches"],
    }