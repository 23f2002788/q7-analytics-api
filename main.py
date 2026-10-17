import os
from collections import defaultdict

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


API_KEY = "ak_prs2g3fsfsn337p750trc5il"
EMAIL = os.getenv("ASSIGNMENT_EMAIL", 
                  "23f2002788@ds.study.iitm.ac.in")

app = FastAPI(title="Q7 Analytics API")

# Allow the assignment page to call the API from a browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Event(BaseModel):
    user: str
    amount: float
    ts: int


class AnalyticsRequest(BaseModel):
    events: list[Event]


@app.post("/analytics")
def analytics(
    body: AnalyticsRequest,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    # Reject missing or incorrect API keys.
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    events = body.events
    user_totals = defaultdict(float)

    # Add only positive amounts to revenue and user totals.
    for event in events:
        if event.amount > 0:
            user_totals[event.user] += event.amount

    revenue = sum(user_totals.values())

    # The assignment guarantees there are no ties for top_user.
    top_user = (
        max(user_totals, key=user_totals.get)
        if user_totals
        else None
    )

    return {
        "email": EMAIL,
        "total_events": len(events),
        "unique_users": len({event.user for event in events}),
        "revenue": round(revenue, 2),
        "top_user": top_user,
    }


@app.get("/")
def home():
    return {"message": "Q7 Analytics API is running"}
