from app.core import FirestoreStore, Store


class FakeSnapshot:
    def __init__(self, data):
        self._data = data
        self.exists = data is not None

    def to_dict(self):
        return self._data


class FakeDocument:
    def __init__(self, records, key):
        self.records = records
        self.key = key

    def create(self, data):
        assert self.key not in self.records
        self.records[self.key] = data

    def get(self, transaction=None):
        return FakeSnapshot(self.records.get(self.key))


class FakeCollection:
    def __init__(self, records):
        self.records = records

    def document(self, key):
        return FakeDocument(self.records, key)

    def limit(self, count):
        return self

    def stream(self):
        return []


class FakeTransaction:
    def set(self, document, data):
        document.records[document.key] = data


class FakeClient:
    def transaction(self):
        return FakeTransaction()


class FakeFirestore:
    @staticmethod
    def transactional(function):
        return function


def firestore_store():
    store = FirestoreStore.__new__(FirestoreStore)
    store._firestore = FakeFirestore
    store.client = FakeClient()
    store.collection = FakeCollection({})
    return store


def test_session_persists_and_diagnosis_is_idempotent(tmp_path):
    path = tmp_path / "state.sqlite3"
    store = Store(str(path))
    created = store.create()

    diagnosed = store.diagnose(created["session_id"], 1, "webmcp")
    assert diagnosed["revision"] == 2
    assert diagnosed["state"] == "conflict"
    assert diagnosed["finding"]["title"].startswith("The roadmap session")
    assert diagnosed["events"][0]["source"] == "webmcp"

    repeated = store.diagnose(created["session_id"], 2, "webmcp")
    assert repeated == diagnosed
    assert Store(str(path)).get(created["session_id"]) == diagnosed


def test_diagnosis_rejects_stale_revision(tmp_path):
    store = Store(str(tmp_path / "state.sqlite3"))
    created = store.create()
    store.diagnose(created["session_id"], 1, "human")

    try:
        store.diagnose(created["session_id"], 1, "webmcp")
    except ValueError as error:
        assert str(error) == "stale_state"
    else:
        raise AssertionError("stale diagnosis should fail")


def test_complete_authorized_journey_and_replay(tmp_path):
    store = Store(str(tmp_path / "state.sqlite3"))
    state = store.create()
    state = store.diagnose(state["session_id"], 1, "webmcp")
    state = store.compare(state["session_id"], 2, "webmcp")
    state = store.select(state["session_id"], 3, "shift", "webmcp")
    selected_hash = state["plan_hash"]
    assert state["state"] == "reviewed"

    state = store.update_arrival(state["session_id"], 4, "11:20")
    assert state["plan_hash"] != selected_hash
    assert state["authorization"] is None

    state = store.authorize(state["session_id"], 5, state["plan_hash"], True)
    assert state["state"] == "authorized"
    state = store.execute(state["session_id"], 6, "judge-run-001", "webmcp")
    assert state["state"] == "completed"
    replay = store.execute(state["session_id"], 1, "judge-run-001", "webmcp")
    assert replay["receipt"] == state["receipt"]


def test_firestore_full_journey_and_replay():
    store = firestore_store()
    state = store.create()
    state = store.diagnose(state["session_id"], 1, "webmcp")
    state = store.compare(state["session_id"], 2, "webmcp")
    state = store.select(state["session_id"], 3, "shift", "webmcp")
    state = store.authorize(state["session_id"], 4, state["plan_hash"], True)
    state = store.execute(state["session_id"], 5, "firestore-run-001", "webmcp")

    assert store.ready()
    assert state["state"] == "completed"
    replay = store.execute(state["session_id"], 1, "firestore-run-001", "webmcp")
    assert replay["receipt"] == state["receipt"]

    event = store.record_protocol_event(state["session_id"], {
        "event_type": "receipt_recovered",
        "name": "reload",
        "revision": state["revision"],
        "duration_ms": 12.5,
        "details": {"same_receipt": True},
    })
    restored = store.get(state["session_id"])
    assert event["event_type"] == "receipt_recovered"
    assert restored["revision"] == state["revision"]
    assert restored["protocol_events"][0]["details"]["same_receipt"] is True
