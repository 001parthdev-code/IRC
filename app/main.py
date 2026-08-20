from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.classifier import classify_ticket


app = FastAPI(title="Support Ticket Triage")


class TicketInput(BaseModel):
    ticket: str = Field(
        min_length=1,
        max_length=5000
    )


@app.post("/tickets")
def create_ticket(data: TicketInput):

    classification = classify_ticket(
        data.ticket
    )

    return {
        "ticket": data.ticket,
        "classification": classification
    }