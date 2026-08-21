from fastapi import FastAPI
from pydantic import BaseModel, Field

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.explainer import explain_ticket
from app.classifier import classify_ticket
from app.decision import make_decision
from app.security import analyze_ticket

from contextlib import asynccontextmanager
import subprocess
import time
import requests

from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_ollama_running()
    yield


app = FastAPI(
    title="Support Ticket Triage",
    lifespan=lifespan
)
app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)


class TicketInput(BaseModel):
    ticket: str = Field(
        min_length=1,
        max_length=5000
    )


@app.post("/tickets")
def create_ticket(data: TicketInput):

    # 1. Semantic classification
    classification = classify_ticket(data.ticket)

    # 2. Security analysis
    security = analyze_ticket(data.ticket)

    # 3. Decision based on semantic evidence
    decision = make_decision(
        classification["scores"]
    )

    # 4. Security override
    if security["verdict"] != "SAFE":
        decision.decision = "manual_review"

    # 5. Generate explanation AFTER the final decision
    reason = explain_ticket(
        ticket=data.ticket,
        category=classification["category"],
        decision=decision.decision,
        scores=classification["scores"],
        security=security,
    )


    # 6. Return final result
    return {
        "ticket": data.ticket,
        "category": classification["category"],
        "evidence_score": decision.confidence,
        "margin": decision.margin,
        "decision": decision.decision,
        "reason": reason,
        "security": security,
    }

def ensure_ollama_running():
    try:
        requests.get(
            "http://127.0.0.1:11434/api/tags",
            timeout=2
        )

        print("Ollama is already running.")
        return

    except requests.RequestException:
        print("Ollama is not running. Starting it...")

    subprocess.Popen(
        ["ollama", "serve"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )

    for _ in range(20):
        try:
            requests.get(
                "http://127.0.0.1:11434/api/tags",
                timeout=1
            )

            print("Ollama is ready.")
            return

        except requests.RequestException:
            time.sleep(0.5)

    raise RuntimeError("Ollama failed to start.")


@app.get("/")
def home():
    return FileResponse("app/static/index.html")

