from app.core import Store


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
