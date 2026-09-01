import os
import socket
import subprocess
import time
from pathlib import Path

import pytest

playwright = pytest.importorskip("playwright.sync_api")
from playwright.sync_api import expect, sync_playwright


ROOT = Path(__file__).resolve().parent.parent
MODEL_CONTEXT_MOCK = """
(() => {
  const registrations = [];
  Object.defineProperty(document, "modelContext", {
    configurable: true,
    value: {
      registerTool: async (tool, options = {}) => {
        if (window.__rejectWebMCPRegistrations) throw new Error("registration_rejected");
        const entry = { tool, aborted: Boolean(options.signal?.aborted) };
        options.signal?.addEventListener("abort", () => { entry.aborted = true; }, { once: true });
        registrations.push(entry);
      },
    },
  });
  window.__webmcp = {
    registrations,
    active: () => registrations.filter((entry) => !entry.aborted),
    names: () => registrations.filter((entry) => !entry.aborted).map((entry) => entry.tool.name),
    invoke: async (name, args = {}) => {
      const entry = registrations.findLast((candidate) => !candidate.aborted && candidate.tool.name === name);
      if (!entry) throw new Error(`tool_not_registered:${name}`);
      return entry.tool.execute(args);
    },
  };
})();
"""


def _free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture(scope="module")
def live_server(tmp_path_factory):
    port = _free_port()
    data_dir = tmp_path_factory.mktemp("browser-data")
    env = os.environ.copy()
    env.update({
        "CAPTAINS_TABLE_STORAGE": "sqlite",
        "CAPTAINS_TABLE_DB": str(data_dir / "browser.sqlite3"),
    })
    process = subprocess.Popen(
        [os.sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd=ROOT,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(process.stderr.read())
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                break
        except OSError:
            time.sleep(0.05)
    else:
        process.terminate()
        raise RuntimeError("local browser-test server did not start")
    yield f"http://127.0.0.1:{port}"
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as manager:
        launch = {"headless": True}
        executable = os.getenv("PLAYWRIGHT_CHROMIUM_EXECUTABLE")
        if executable:
            launch["executable_path"] = executable
        instance = manager.chromium.launch(**launch)
        yield instance
        instance.close()


def new_page(browser, *, webmcp=True, reject_registrations=False):
    context = browser.new_context()
    if webmcp:
        context.add_init_script(MODEL_CONTEXT_MOCK)
        if reject_registrations:
            context.add_init_script("window.__rejectWebMCPRegistrations = true")
    return context, context.new_page()


def wait_for_tools(page, expected):
    page.wait_for_function(
        "expected => JSON.stringify(window.__webmcp.names().sort()) === JSON.stringify(expected.sort())",
        arg=expected,
    )
    assert "authorize_plan" not in page.evaluate("window.__webmcp.names()")


def invoke(page, name, args=None):
    return page.evaluate("([name, args]) => window.__webmcp.invoke(name, args)", [name, args or {}])


def test_complete_webmcp_journey_and_receipt_recovery(browser, live_server):
    context, page = new_page(browser)
    page.goto(live_server)
    expect(page.locator("#operation-status")).to_have_text("Decision ready.")
    expect(page.locator("#connection")).to_have_text("WebMCP connected")
    wait_for_tools(page, ["inspect_decision", "diagnose_plan", "report_observed_capabilities"])

    invoke(page, "diagnose_plan")
    expect(page.locator("#status-label")).to_have_text("Conflict found")
    wait_for_tools(page, ["inspect_decision", "diagnose_plan", "compare_repairs", "report_observed_capabilities"])

    invoke(page, "compare_repairs")
    expect(page.locator("#status-label")).to_have_text("Repairs ready")
    wait_for_tools(page, ["inspect_decision", "diagnose_plan", "compare_repairs", "select_repair", "report_observed_capabilities"])

    invoke(page, "select_repair", {"repair_id": "shift"})
    expect(page.locator("#status-label")).to_have_text("Ready for review")
    expect(page.locator("#review")).to_be_visible()
    wait_for_tools(page, ["inspect_decision", "diagnose_plan", "compare_repairs", "select_repair", "prepare_authorization", "report_observed_capabilities"])
    invoke(page, "prepare_authorization")
    expect(page.locator("#review-note")).to_contain_text("cannot authorize")

    page.locator("#authorize").click()
    expect(page.locator("#status-label")).to_have_text("Authorized")
    wait_for_tools(page, ["inspect_decision", "diagnose_plan", "select_repair", "execute_authorized_plan", "report_observed_capabilities"])

    invoke(page, "execute_authorized_plan", {"idempotency_key": "browser-journey-001"})
    expect(page.locator("#status-label")).to_have_text("Reserved")
    expect(page.locator("#receipt")).to_be_visible()
    confirmation = page.locator("#confirmation").inner_text()
    assert confirmation.startswith("CT-")
    wait_for_tools(page, ["inspect_decision", "report_observed_capabilities"])

    page.reload()
    expect(page.locator("#operation-status")).to_have_text("Decision ready.")
    expect(page.locator("#confirmation")).to_have_text(confirmation)
    expect(page.locator("#metric-recovery")).to_have_text("Verified")
    context.close()


def test_stale_tool_handle_is_rejected_without_mutation(browser, live_server):
    context, page = new_page(browser)
    page.goto(live_server)
    wait_for_tools(page, ["inspect_decision", "diagnose_plan", "report_observed_capabilities"])
    page.evaluate("window.__staleDiagnose = window.__webmcp.active().find(entry => entry.tool.name === 'diagnose_plan').tool.execute")
    invoke(page, "diagnose_plan")
    expect(page.locator("#revision")).to_contain_text("R2")

    with pytest.raises(playwright.Error, match="stale_state"):
        page.evaluate("window.__staleDiagnose({})")
    expect(page.locator("#revision")).to_contain_text("R2")
    expect(page.locator("#action-error-copy")).to_have_text("The plan changed before this action completed. Reload the decision and try again.")
    context.close()


def test_manual_and_rejected_registration_modes_remain_usable(browser, live_server):
    context, page = new_page(browser, webmcp=False)
    page.goto(live_server)
    expect(page.locator("#connection")).to_have_text("Manual mode")
    expect(page.locator("#mode-copy")).to_contain_text("does not expose page tools")
    page.evaluate("document.querySelector('#inspect').click()")
    expect(page.locator("#status-label")).to_have_text("Conflict found")
    context.close()

    context, page = new_page(browser, reject_registrations=True)
    page.goto(live_server)
    expect(page.locator("#connection")).to_have_text("Tool access unavailable")
    expect(page.locator("#mode-copy")).to_contain_text("still usable here")
    page.locator("#inspect").click()
    expect(page.locator("#status-label")).to_have_text("Conflict found")
    context.close()


def test_stale_page_surfaces_recovery_and_scoped_busy_state(browser, live_server):
    context, page = new_page(browser)
    page.goto(live_server)
    expect(page.locator("#operation-status")).to_have_text("Decision ready.")
    session_id = page.evaluate("localStorage.getItem('captains-table-session')")
    response = page.request.post(
        f"{live_server}/api/session/{session_id}/diagnose",
        data={"expected_revision": 1, "source": "webmcp"},
    )
    assert response.ok

    def delayed(route):
        time.sleep(0.15)
        route.continue_()

    page.route("**/api/session/*/diagnose", delayed)
    pending = page.evaluate("""() => {
      document.querySelector('#inspect').click();
      return {
        busy: document.querySelector('#decision').getAttribute('aria-busy'),
        disabled: document.querySelector('#inspect').disabled,
        status: document.querySelector('#operation-status').textContent,
      };
    }""")
    assert pending == {
        "busy": "true",
        "disabled": True,
        "status": "Inspecting the plan for its blocking constraint…",
    }
    expect(page.locator("#action-error-copy")).to_have_text("The plan changed before this action completed. Reload the decision and try again.")
    expect(page.locator("#decision")).to_have_attribute("aria-busy", "false")
    context.close()


@pytest.mark.parametrize(
    ("error_code", "visible_copy"),
    [
        ("invalid_state", "This action is no longer available for the current plan state."),
        ("plan_changed", "The authorized version no longer matches the current plan. Review it again."),
        ("authorization_required", "Review and authorize this exact plan before creating the reservation."),
        ("authorization_expired", "Authorization expired. Review and authorize the current plan again."),
        ("storage_error", "Persistent storage is temporarily unavailable. Try again in a moment."),
        ("inventory_changed", "The service could not complete this action. Check the connection and try again."),
    ],
)
def test_public_failures_have_visible_recovery(browser, live_server, error_code, visible_copy):
    context, page = new_page(browser)
    page.goto(live_server)
    expect(page.locator("#operation-status")).to_have_text("Decision ready.")
    page.route(
        "**/api/session/*/diagnose",
        lambda route: route.fulfill(status=409, content_type="application/json", body=f'{{"detail":"{error_code}"}}'),
    )

    page.locator("#inspect").click()
    expect(page.locator("#action-error")).to_be_visible()
    expect(page.locator("#action-error-copy")).to_have_text(visible_copy)
    expect(page.locator("#inspect")).to_be_enabled()
    expect(page.locator("#operation-status")).to_have_text("Action needs attention.")
    context.close()


def test_two_tabs_resolve_one_winner_and_one_stale_page(browser, live_server):
    context, first = new_page(browser)
    first.goto(live_server)
    expect(first.locator("#operation-status")).to_have_text("Decision ready.")
    second = context.new_page()
    second.goto(live_server)
    expect(second.locator("#operation-status")).to_have_text("Decision ready.")
    assert first.evaluate("localStorage.getItem('captains-table-session')") == second.evaluate(
        "localStorage.getItem('captains-table-session')"
    )

    first.evaluate("document.querySelector('#inspect').click()")
    second.evaluate("document.querySelector('#inspect').click()")
    expect(first.locator("#operation-status")).not_to_have_text("Inspecting the plan for its blocking constraint…")
    expect(second.locator("#operation-status")).not_to_have_text("Inspecting the plan for its blocking constraint…")
    outcomes = {
        first.locator("#status-label").inner_text(),
        second.locator("#status-label").inner_text(),
    }
    assert "Conflict found" in outcomes
    errors = [
        page.locator("#action-error-copy").inner_text()
        for page in (first, second)
        if page.locator("#action-error").is_visible()
    ]
    assert errors == ["The plan changed before this action completed. Reload the decision and try again."]
    context.close()


def test_navigation_during_mutation_cancels_without_corrupting_state(browser, live_server):
    context, page = new_page(browser)
    page.goto(live_server)
    expect(page.locator("#operation-status")).to_have_text("Decision ready.")

    def delayed(route):
        time.sleep(0.1)
        route.continue_()

    page.route("**/api/session/*/diagnose", delayed)
    page.evaluate("document.querySelector('#inspect').click()")
    page.reload()
    expect(page.locator("#operation-status")).to_have_text("Decision ready.")
    expect(page.locator("#status-label")).to_have_text("Not inspected")
    expect(page.locator("#revision")).to_contain_text("R1")
    session_id = page.evaluate("localStorage.getItem('captains-table-session')")
    snapshot = page.request.get(f"{live_server}/api/session/{session_id}").json()
    assert snapshot["revision"] == 1
    assert snapshot["state"] == "draft"
    context.close()


def test_narrow_reduced_motion_layout_keeps_evidence_and_controls(browser, live_server):
    context = browser.new_context(viewport={"width": 680, "height": 900}, reduced_motion="reduce")
    context.add_init_script(MODEL_CONTEXT_MOCK)
    page = context.new_page()
    page.goto(live_server)
    expect(page.locator("#operation-status")).to_have_text("Decision ready.")
    assert page.locator("#proof-signals").evaluate("node => node.parentElement.id") == "narrow-proof-slot"
    assert page.locator("#technical-evidence").evaluate("node => node.parentElement.id") == "narrow-evidence-slot"
    expect(page.locator("#inspect")).to_be_visible()
    expect(page.locator("#workflow-stages")).to_be_visible()
    assert page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches") is True
    context.close()
