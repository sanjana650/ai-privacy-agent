from uuid import uuid4

from fastapi import FastAPI, HTTPException

from app.agent.agent import investigate_log
from app.models.schemas import (
    InvestigationRequest,
    InvestigationResponse,
)


app = FastAPI(
    title="AI Privacy Investigation Agent",
    version="0.1.0",
)


investigations: dict[str, InvestigationResponse] = {}


@app.get("/api/v1/health")
def health_check():
    return {"status": "healthy"}


@app.post(
    "/api/v1/investigations",
    response_model=InvestigationResponse,
)
def create_investigation(
    request: InvestigationRequest,
) -> InvestigationResponse:

    report = investigate_log(request.log)

    investigation_id = str(uuid4())

    response = InvestigationResponse(
        investigation_id=investigation_id,
        **report.model_dump(),
    )

    investigations[investigation_id] = response

    return response


@app.get(
    "/api/v1/investigations/{investigation_id}",
    response_model=InvestigationResponse,
)
def get_investigation(
    investigation_id: str,
) -> InvestigationResponse:

    investigation = investigations.get(
        investigation_id
    )

    if investigation is None:
        raise HTTPException(
            status_code=404,
            detail="Investigation not found",
        )

    return investigation