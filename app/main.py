from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core import build_store


ROOT = Path(__file__).resolve().parent.parent
store = build_store()
app = FastAPI(title="Captain's Table", version="0.1.0")
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")


class DiagnoseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_revision: int = Field(ge=1)
    source: Literal["human", "webmcp"]


class ActionRequest(DiagnoseRequest):
    pass


class SelectRequest(DiagnoseRequest):
    repair_id: Literal["shift", "remote"]


class ArrivalRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_revision: int = Field(ge=1)
    source: Literal["human"]
    arrival: str = Field(pattern=r"^\d{2}:\d{2}$")


class AuthorizeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_revision: int = Field(ge=1)
    source: Literal["human"]
    plan_hash: str = Field(min_length=8, max_length=8)
    consent: bool


class ExecuteRequest(DiagnoseRequest):
    idempotency_key: str = Field(min_length=8, max_length=100)


class ProtocolEventRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    event_type: str = Field(pattern=r"^[a-z][a-z0-9_]{2,39}$")
    name: str = Field(min_length=1, max_length=80)
    revision: int = Field(ge=1)
    duration_ms: float | None = Field(default=None, ge=0, le=120000)
    details: dict[str, Any] = Field(default_factory=dict)

    @field_validator("details")
    @classmethod
    def bounded_details(cls, details: dict[str, Any]) -> dict[str, Any]:
        import json

        if len(json.dumps(details)) > 4000:
            raise ValueError("details_too_large")
        return details


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(ROOT / "static" / "index.html")


@app.get("/health")
@app.get("/healthz")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/readyz")
def ready() -> dict[str, str]:
    try:
        store.ready()
    except Exception as exc:
        raise HTTPException(503, detail="storage_error") from exc
    return {"status": "ready"}


@app.post("/api/session", status_code=201)
def create_session() -> dict:
    return store.create()


@app.get("/api/session/{session_id}")
def get_session(session_id: str) -> dict:
    result = store.get(session_id)
    if not result:
        raise HTTPException(404, detail="not_found")
    return result


@app.post("/api/session/{session_id}/protocol-events", status_code=201)
def protocol_event(session_id: str, request: ProtocolEventRequest) -> dict:
    try:
        return store.record_protocol_event(session_id, request.model_dump())
    except KeyError as exc:
        raise HTTPException(404, detail="not_found") from exc


@app.post("/api/session/{session_id}/diagnose")
def diagnose(session_id: str, request: DiagnoseRequest) -> dict:
    try:
        return store.diagnose(session_id, request.expected_revision, request.source)
    except KeyError as exc:
        raise HTTPException(404, detail="not_found") from exc
    except ValueError as exc:
        raise HTTPException(409, detail=str(exc)) from exc


def run(action):
    try:
        return action()
    except KeyError as exc:
        raise HTTPException(404, detail="not_found") from exc
    except ValueError as exc:
        raise HTTPException(409, detail=str(exc)) from exc


@app.post("/api/session/{session_id}/repairs")
def compare(session_id: str, request: ActionRequest) -> dict:
    return run(lambda: store.compare(session_id, request.expected_revision, request.source))


@app.post("/api/session/{session_id}/selection")
def select(session_id: str, request: SelectRequest) -> dict:
    return run(lambda: store.select(session_id, request.expected_revision, request.repair_id, request.source))


@app.post("/api/session/{session_id}/constraint")
def constraint(session_id: str, request: ArrivalRequest) -> dict:
    return run(lambda: store.update_arrival(session_id, request.expected_revision, request.arrival))


@app.post("/api/session/{session_id}/revert")
def revert(session_id: str, request: ActionRequest) -> dict:
    return run(lambda: store.revert(session_id, request.expected_revision))


@app.post("/api/session/{session_id}/authorize")
def authorize(session_id: str, request: AuthorizeRequest) -> dict:
    return run(lambda: store.authorize(session_id, request.expected_revision, request.plan_hash, request.consent))


@app.post("/api/session/{session_id}/execute")
def execute(session_id: str, request: ExecuteRequest) -> dict:
    return run(lambda: store.execute(session_id, request.expected_revision, request.idempotency_key, request.source))
