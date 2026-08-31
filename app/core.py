from __future__ import annotations

import hashlib
import json
import os
import secrets
import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any


SCENARIO: dict[str, Any] = {
    "title": "New York leadership offsite",
    "dates": "October 12–14",
    "people": 8,
    "budget": 7200,
    "arrival": "11:40",
    "agenda": [
        {"time": "09:30", "title": "Roadmap decisions", "required": 8},
        {"time": "12:30", "title": "Working lunch", "required": 8},
        {"time": "14:00", "title": "Operating model", "required": 6},
    ],
}


def canonical_hash(plan: dict[str, Any]) -> str:
    payload = json.dumps(plan, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()[:8].upper()


class Store:
    def __init__(self, path: str | None = None) -> None:
        self.path = path or os.getenv("CAPTAINS_TABLE_DB", ".data/captains-table.sqlite3")
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS sessions "
                "(id TEXT PRIMARY KEY, revision INTEGER NOT NULL, state TEXT NOT NULL, "
                "payload TEXT NOT NULL, updated_at TEXT NOT NULL)"
            )

    def connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, timeout=5)
        db.row_factory = sqlite3.Row
        return db

    def ready(self) -> bool:
        with self.connect() as db:
            db.execute("SELECT 1").fetchone()
        return True

    def create(self) -> dict[str, Any]:
        session_id = secrets.token_urlsafe(18)
        payload = {
            "session_id": session_id,
            "revision": 1,
            "state": "draft",
            "plan": SCENARIO,
            "plan_hash": canonical_hash(SCENARIO),
            "finding": None,
            "events": [],
        }
        with self.connect() as db:
            db.execute(
                "INSERT INTO sessions VALUES (?, ?, ?, ?, ?)",
                (session_id, 1, "draft", json.dumps(payload), datetime.now(UTC).isoformat()),
            )
        return payload

    def get(self, session_id: str) -> dict[str, Any] | None:
        with self.connect() as db:
            row = db.execute("SELECT payload FROM sessions WHERE id = ?", (session_id,)).fetchone()
        return json.loads(row["payload"]) if row else None

    def diagnose(self, session_id: str, expected_revision: int, source: str) -> dict[str, Any]:
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT payload FROM sessions WHERE id = ?", (session_id,)).fetchone()
            if not row:
                raise KeyError("not_found")
            payload = json.loads(row["payload"])
            if payload["revision"] != expected_revision:
                raise ValueError("stale_state")
            if payload["finding"]:
                return payload
            payload["revision"] += 1
            payload["state"] = "conflict"
            payload["finding"] = {
                "title": "The roadmap session starts before everyone arrives",
                "detail": "Two required attendees arrive at 11:40, more than two hours after the 09:30 start.",
            }
            payload["events"].insert(0, {
                "source": source,
                "action": "diagnose_plan",
                "revision": payload["revision"],
                "summary": "Found the late-arrival conflict.",
            })
            db.execute(
                "UPDATE sessions SET revision=?, state=?, payload=?, updated_at=? WHERE id=?",
                (payload["revision"], payload["state"], json.dumps(payload), datetime.now(UTC).isoformat(), session_id),
            )
        return payload

    def mutate(self, session_id: str, expected_revision: int, operation) -> dict[str, Any]:
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT payload FROM sessions WHERE id = ?", (session_id,)).fetchone()
            if not row:
                raise KeyError("not_found")
            payload = json.loads(row["payload"])
            if payload["revision"] != expected_revision:
                raise ValueError("stale_state")
            changed = operation(payload)
            if changed:
                payload["revision"] += 1
                payload["plan_hash"] = canonical_hash(payload["plan"])
            db.execute(
                "UPDATE sessions SET revision=?, state=?, payload=?, updated_at=? WHERE id=?",
                (payload["revision"], payload["state"], json.dumps(payload), datetime.now(UTC).isoformat(), session_id),
            )
        return payload

    def compare(self, session_id: str, expected_revision: int, source: str) -> dict[str, Any]:
        def operation(payload: dict[str, Any]) -> bool:
            if payload["state"] not in {"conflict", "options"}:
                raise ValueError("invalid_state")
            if payload.get("options"):
                return False
            payload["options"] = [
                {"id": "shift", "name": "Shift the roadmap session", "time": "12:15", "cost": 180, "attendance": "8 of 8", "tradeoff": "Shorter working lunch"},
                {"id": "remote", "name": "Keep 09:30 with remote access", "time": "09:30", "cost": 260, "attendance": "8 of 8", "tradeoff": "Two people join remotely"},
            ]
            payload["state"] = "options"
            payload["events"].insert(0, {"source": source, "action": "compare_repairs", "revision": payload["revision"] + 1, "summary": "Compared two feasible repairs."})
            return True
        return self.mutate(session_id, expected_revision, operation)

    def select(self, session_id: str, expected_revision: int, repair_id: str, source: str) -> dict[str, Any]:
        def operation(payload: dict[str, Any]) -> bool:
            if payload["state"] not in {"options", "reviewed", "authorized"}:
                raise ValueError("invalid_state")
            option = next((item for item in payload.get("options", []) if item["id"] == repair_id), None)
            if not option:
                raise ValueError("invalid_input")
            if payload.get("selection") == repair_id:
                return False
            payload["previous_plan"] = payload["plan"].copy()
            payload["selection"] = repair_id
            payload["plan"] = {**payload["plan"], "agenda": [
                {**item, "time": option["time"] if index == 0 else item["time"]}
                for index, item in enumerate(payload["plan"]["agenda"])
            ], "budget": payload["plan"]["budget"] + option["cost"]}
            payload["state"] = "reviewed"
            payload["authorization"] = None
            payload["events"].insert(0, {"source": source, "action": "select_repair", "revision": payload["revision"] + 1, "summary": f"Selected {option['name'].lower()}."})
            return True
        return self.mutate(session_id, expected_revision, operation)

    def update_arrival(self, session_id: str, expected_revision: int, arrival: str) -> dict[str, Any]:
        if arrival < "08:00" or arrival > "18:00":
            raise ValueError("invalid_input")
        def operation(payload: dict[str, Any]) -> bool:
            if payload["state"] not in {"reviewed", "authorized"}:
                raise ValueError("invalid_state")
            if payload["plan"]["arrival"] == arrival:
                return False
            payload["previous_plan"] = payload["plan"].copy()
            payload["plan"] = {**payload["plan"], "arrival": arrival}
            payload["authorization"] = None
            payload["state"] = "reviewed"
            payload["events"].insert(0, {"source": "human", "action": "adjust_arrival", "revision": payload["revision"] + 1, "summary": "Changed arrival time. Review is required again."})
            return True
        return self.mutate(session_id, expected_revision, operation)

    def revert(self, session_id: str, expected_revision: int) -> dict[str, Any]:
        def operation(payload: dict[str, Any]) -> bool:
            if payload["state"] != "reviewed" or not payload.get("previous_plan"):
                raise ValueError("invalid_state")
            payload["plan"] = payload.pop("previous_plan")
            payload["selection"] = None
            payload["authorization"] = None
            payload["events"].insert(0, {"source": "human", "action": "revert_change", "revision": payload["revision"] + 1, "summary": "Reverted the latest plan change."})
            return True
        return self.mutate(session_id, expected_revision, operation)

    def authorize(self, session_id: str, expected_revision: int, plan_hash: str, consent: bool) -> dict[str, Any]:
        if not consent:
            raise ValueError("authorization_required")
        def operation(payload: dict[str, Any]) -> bool:
            if payload["state"] != "reviewed" or payload["plan_hash"] != plan_hash:
                raise ValueError("plan_changed")
            payload["state"] = "authorized"
            payload["authorization"] = {"plan_hash": plan_hash, "scope": "reserve_offsite", "expires_at": (datetime.now(UTC) + timedelta(minutes=15)).isoformat()}
            payload["events"].insert(0, {"source": "human", "action": "authorize_plan", "revision": payload["revision"] + 1, "summary": "Authorized exactly this plan version."})
            return True
        return self.mutate(session_id, expected_revision, operation)

    def execute(self, session_id: str, expected_revision: int, idempotency_key: str, source: str) -> dict[str, Any]:
        current = self.get(session_id)
        if current and current.get("receipt") and current["receipt"]["idempotency_key"] == idempotency_key:
            return current
        def operation(payload: dict[str, Any]) -> bool:
            if payload["state"] != "authorized" or not payload.get("authorization"):
                raise ValueError("authorization_required")
            if datetime.fromisoformat(payload["authorization"]["expires_at"]) < datetime.now(UTC):
                payload["state"] = "reviewed"
                payload["authorization"] = None
                raise ValueError("authorization_expired")
            payload["state"] = "completed"
            payload["receipt"] = {"confirmation": f"CT-{secrets.token_hex(3).upper()}", "idempotency_key": idempotency_key, "plan_hash": payload["plan_hash"], "status": "reserved"}
            payload["events"].insert(0, {"source": source, "action": "execute_authorized_plan", "revision": payload["revision"] + 1, "summary": "Created the reservation receipt."})
            return True
        return self.mutate(session_id, expected_revision, operation)


class FirestoreStore(Store):
    """Production store using Firestore transactions for revision-safe mutations."""

    def __init__(self, project: str | None = None, database: str | None = None) -> None:
        from google.cloud import firestore

        self._firestore = firestore
        self.client = firestore.Client(
            project=project or os.getenv("GOOGLE_CLOUD_PROJECT"),
            database=database or os.getenv("CAPTAINS_TABLE_FIRESTORE_DATABASE", "(default)"),
        )
        self.collection = self.client.collection(
            os.getenv("CAPTAINS_TABLE_FIRESTORE_COLLECTION", "captains_table_sessions")
        )

    def ready(self) -> bool:
        list(self.collection.limit(1).stream())
        return True

    def create(self) -> dict[str, Any]:
        session_id = secrets.token_urlsafe(18)
        payload = {
            "session_id": session_id,
            "revision": 1,
            "state": "draft",
            "plan": SCENARIO,
            "plan_hash": canonical_hash(SCENARIO),
            "finding": None,
            "events": [],
        }
        self.collection.document(session_id).create({
            "payload": payload,
            "revision": 1,
            "state": "draft",
            "updated_at": datetime.now(UTC),
        })
        return payload

    def get(self, session_id: str) -> dict[str, Any] | None:
        snapshot = self.collection.document(session_id).get()
        if not snapshot.exists:
            return None
        return snapshot.to_dict()["payload"]

    def _transactional_mutation(self, session_id: str, expected_revision: int, operation) -> dict[str, Any]:
        document = self.collection.document(session_id)
        transaction = self.client.transaction()

        @self._firestore.transactional
        def apply(transaction):
            snapshot = document.get(transaction=transaction)
            if not snapshot.exists:
                raise KeyError("not_found")
            payload = snapshot.to_dict()["payload"]
            if payload["revision"] != expected_revision:
                raise ValueError("stale_state")
            changed = operation(payload)
            if changed:
                payload["revision"] += 1
                payload["plan_hash"] = canonical_hash(payload["plan"])
                transaction.set(document, {
                    "payload": payload,
                    "revision": payload["revision"],
                    "state": payload["state"],
                    "updated_at": datetime.now(UTC),
                })
            return payload

        return apply(transaction)

    def diagnose(self, session_id: str, expected_revision: int, source: str) -> dict[str, Any]:
        def operation(payload: dict[str, Any]) -> bool:
            if payload["finding"]:
                return False
            payload["state"] = "conflict"
            payload["finding"] = {
                "title": "The roadmap session starts before everyone arrives",
                "detail": "Two required attendees arrive at 11:40, more than two hours after the 09:30 start.",
            }
            payload["events"].insert(0, {
                "source": source,
                "action": "diagnose_plan",
                "revision": payload["revision"] + 1,
                "summary": "Found the late-arrival conflict.",
            })
            return True

        return self._transactional_mutation(session_id, expected_revision, operation)

    def mutate(self, session_id: str, expected_revision: int, operation) -> dict[str, Any]:
        return self._transactional_mutation(session_id, expected_revision, operation)

    def execute(self, session_id: str, expected_revision: int, idempotency_key: str, source: str) -> dict[str, Any]:
        document = self.collection.document(session_id)
        transaction = self.client.transaction()

        @self._firestore.transactional
        def apply(transaction):
            snapshot = document.get(transaction=transaction)
            if not snapshot.exists:
                raise KeyError("not_found")
            payload = snapshot.to_dict()["payload"]
            if payload.get("receipt", {}).get("idempotency_key") == idempotency_key:
                return payload
            if payload["revision"] != expected_revision:
                raise ValueError("stale_state")
            if payload["state"] != "authorized" or not payload.get("authorization"):
                raise ValueError("authorization_required")
            if datetime.fromisoformat(payload["authorization"]["expires_at"]) < datetime.now(UTC):
                raise ValueError("authorization_expired")
            payload["state"] = "completed"
            payload["revision"] += 1
            payload["receipt"] = {
                "confirmation": f"CT-{secrets.token_hex(3).upper()}",
                "idempotency_key": idempotency_key,
                "plan_hash": payload["plan_hash"],
                "status": "reserved",
            }
            payload["events"].insert(0, {
                "source": source,
                "action": "execute_authorized_plan",
                "revision": payload["revision"],
                "summary": "Created the reservation receipt.",
            })
            transaction.set(document, {
                "payload": payload,
                "revision": payload["revision"],
                "state": payload["state"],
                "updated_at": datetime.now(UTC),
            })
            return payload

        return apply(transaction)


def build_store():
    backend = os.getenv("CAPTAINS_TABLE_STORAGE", "sqlite").lower()
    if backend == "firestore":
        return FirestoreStore()
    if backend != "sqlite":
        raise ValueError(f"unsupported storage backend: {backend}")
    return Store()
