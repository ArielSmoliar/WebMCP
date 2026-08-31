from pathlib import Path

from fastapi.testclient import TestClient

import app.main as main
from app.core import Store


def client(tmp_path) -> TestClient:
    main.store = Store(str(tmp_path / "api.sqlite3"))
    return TestClient(main.app)


def test_gate_one_journey(tmp_path):
    web = client(tmp_path)
    page = web.get("/")
    assert page.status_code == 200
    assert 'id="start-over"' in page.text
    assert "Start new session" in page.text
    assert page.text.index('id="workflow-stages"') < page.text.index('id="narrow-proof-slot"') < page.text.index('id="first-run"')
    assert page.text.index('id="decision"') < page.text.index('id="narrow-evidence-slot"')
    proof = page.text[page.text.index('<aside id="proof-signals"'):page.text.index("</aside>", page.text.index('<aside id="proof-signals"'))]
    assert proof.count("<dd id=") == 3
    assert '<details id="technical-evidence" class="evidence">' in page.text
    assert "impeccable-workflow-1" in page.text
    app_js = (Path(main.__file__).parent.parent / "static" / "app.js").read_text()
    assert "function relocateEvidence(event)" in app_js
    assert 'document.querySelectorAll("#inspect, #compare, .select-repair, #save-arrival, #authorize, #revert, #execute, #start-over, #run-protocol-checks")' in app_js
    assert "authorize_plan" not in app_js
    assert web.get("/healthz").json() == {"status": "ok"}
    assert web.get("/health").json() == {"status": "ok"}
    assert web.get("/readyz").json() == {"status": "ready"}

    created = web.post("/api/session", json={})
    assert created.status_code == 201
    snapshot = created.json()

    diagnosed = web.post(
        f"/api/session/{snapshot['session_id']}/diagnose",
        json={"expected_revision": 1, "source": "webmcp"},
    )
    assert diagnosed.status_code == 200
    assert diagnosed.json()["revision"] == 2

    restored = web.get(f"/api/session/{snapshot['session_id']}")
    assert restored.json() == diagnosed.json()

    telemetry = web.post(
        f"/api/session/{snapshot['session_id']}/protocol-events",
        json={
            "event_type": "registration_success",
            "name": "diagnose_plan",
            "revision": diagnosed.json()["revision"],
            "duration_ms": 8.4,
            "details": {"source": "page"},
        },
    )
    assert telemetry.status_code == 201
    after_telemetry = web.get(f"/api/session/{snapshot['session_id']}").json()
    assert after_telemetry["revision"] == diagnosed.json()["revision"]
    assert after_telemetry["protocol_events"][0]["name"] == "diagnose_plan"


def test_strict_and_stale_requests(tmp_path):
    web = client(tmp_path)
    snapshot = web.post("/api/session", json={}).json()
    endpoint = f"/api/session/{snapshot['session_id']}/diagnose"

    assert web.post(endpoint, json={"expected_revision": 1, "source": "human", "extra": True}).status_code == 422
    assert web.post(endpoint, json={"expected_revision": 1, "source": "human"}).status_code == 200
    stale = web.post(endpoint, json={"expected_revision": 1, "source": "webmcp"})
    assert stale.status_code == 409
    assert stale.json()["detail"] == "stale_state"

    oversized = web.post(
        f"/api/session/{snapshot['session_id']}/protocol-events",
        json={"event_type": "agent_observation", "name": "reported", "revision": 2, "details": {"raw": "x" * 5000}},
    )
    assert oversized.status_code == 422


def test_full_api_journey(tmp_path):
    web = client(tmp_path)
    state = web.post("/api/session", json={}).json()
    sid = state["session_id"]

    state = web.post(f"/api/session/{sid}/diagnose", json={"expected_revision": 1, "source": "webmcp"}).json()
    state = web.post(f"/api/session/{sid}/repairs", json={"expected_revision": 2, "source": "webmcp"}).json()
    state = web.post(f"/api/session/{sid}/selection", json={"expected_revision": 3, "source": "webmcp", "repair_id": "shift"}).json()
    state = web.post(f"/api/session/{sid}/constraint", json={"expected_revision": 4, "source": "human", "arrival": "11:20"}).json()
    assert state["state"] == "reviewed"
    state = web.post(f"/api/session/{sid}/authorize", json={"expected_revision": 5, "source": "human", "plan_hash": state["plan_hash"], "consent": True}).json()
    state = web.post(f"/api/session/{sid}/execute", json={"expected_revision": 6, "source": "webmcp", "idempotency_key": "judge-run-001"}).json()
    assert state["receipt"]["status"] == "reserved"

    replay = web.post(f"/api/session/{sid}/execute", json={"expected_revision": 1, "source": "webmcp", "idempotency_key": "judge-run-001"})
    assert replay.status_code == 200
    assert replay.json()["receipt"] == state["receipt"]
