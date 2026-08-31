const state = { snapshot: null, controller: null };
const $ = (id) => document.getElementById(id);
const wideScreen = window.matchMedia("(min-width: 1100px)");

const errorCopy = {
  stale_state: "The plan changed before this action completed. Reload the decision and try again.",
  invalid_state: "This action is no longer available for the current plan state.",
  plan_changed: "The authorized version no longer matches the current plan. Review it again.",
  authorization_required: "Review and authorize this exact plan before creating the reservation.",
  authorization_expired: "Authorization expired. Review and authorize the current plan again.",
  storage_error: "Persistent storage is temporarily unavailable. Try again in a moment.",
};

function setBusy(busy) {
  $("decision").setAttribute("aria-busy", String(busy));
  document.querySelectorAll("button").forEach((button) => { button.disabled = busy; });
}

function showError(error, bootFailure = false) {
  const key = error?.message || "request_failed";
  $("action-error-copy").textContent = errorCopy[key] || "The service could not complete this action. Check the connection and try again.";
  $("retry-load").hidden = !bootFailure;
  $("action-error").hidden = false;
}

function clearError() {
  $("action-error").hidden = true;
  $("retry-load").hidden = true;
}

function syncEvidenceDisclosure(event) {
  $("technical-evidence").open = event.matches;
}

async function request(path, options = {}) {
  const response = await fetch(path, { headers: { "Content-Type": "application/json" }, ...options });
  if (!response.ok) throw new Error((await response.json()).detail || "request_failed");
  return response.json();
}

async function action(route, body, source = "human") {
  clearError();
  setBusy(true);
  try {
    const snapshot = await request(`/api/session/${state.snapshot.session_id}/${route}`, {
      method: "POST", body: JSON.stringify({ expected_revision: state.snapshot.revision, source, ...body })
    });
    render(snapshot, true);
    await registerTools();
    return snapshot;
  } catch (error) {
    showError(error);
    throw error;
  } finally {
    setBusy(false);
  }
}

function toolResult(summary, data = {}) {
  return JSON.stringify({ ok: true, state: state.snapshot.state, revision: state.snapshot.revision, summary, data, ui: { changed: ["decision", "revision", "decision-trail"] } });
}

function comparisonRows(options) {
  const rows = [["Time", "time"], ["Added cost", "cost"], ["Attendance", "attendance"], ["Tradeoff", "tradeoff"]];
  return rows.map(([label, key]) => `<tr><th scope="row">${label}</th>${options.map((item) => `<td>${key === "cost" ? `$${item[key]}` : item[key]}${label === "Tradeoff" ? `<button class="secondary select-repair" data-repair="${item.id}">Select ${item.name.toLowerCase()}</button>` : ""}</td>`).join("")}</tr>`).join("");
}

function render(snapshot, changed = false) {
  state.snapshot = snapshot;
  $("revision").textContent = `R${snapshot.revision} · ${snapshot.plan_hash}`;
  $("revision-notch").style.inlineSize = `${8 + Math.min(snapshot.revision, 8) * 4}px`;
  $("plan-budget").textContent = `$${snapshot.plan.budget.toLocaleString()}`;
  $("plan-arrival").textContent = snapshot.plan.arrival;
  $("roadmap-time").textContent = snapshot.plan.agenda[0].time;
  const rank = { draft: 0, conflict: 1, options: 2, reviewed: 3, authorized: 4, completed: 5 }[snapshot.state];
  $("first-run").hidden = rank > 0;
  $("finding").hidden = rank < 1;
  $("comparison").hidden = rank < 1 || rank === 5;
  $("review").hidden = rank < 3 || rank === 5;
  $("receipt").hidden = rank !== 5;
  $("execute").hidden = rank !== 4;
  $("compare").hidden = rank !== 1;
  $("status-label").textContent = ({ draft: "Not inspected", conflict: "Conflict found", options: "Repairs ready", reviewed: "Ready for review", authorized: "Authorized", completed: "Reserved" })[snapshot.state];

  if (snapshot.finding) {
    $("finding-label").textContent = rank >= 3 ? "Original conflict" : "Conflict found";
    $("finding-title").textContent = rank >= 3 ? "The late arrival conflict is repaired" : snapshot.finding.title;
    $("finding-detail").textContent = rank >= 3
      ? `Originally, the 09:30 session began before two required attendees arrived. The selected plan starts it at ${snapshot.plan.agenda[0].time}.`
      : snapshot.finding.detail;
    $("conflict-jump").hidden = rank >= 3;
    $("roadmap").classList.toggle("changed", changed);
  }
  if (snapshot.options) {
    $("comparison-body").innerHTML = comparisonRows(snapshot.options);
    document.querySelectorAll(".select-repair").forEach((button) => button.addEventListener("click", () => { void action("selection", { repair_id: button.dataset.repair }).catch(() => {}); }));
  }
  if (rank >= 3 && rank < 5) {
    const selected = snapshot.options?.find((item) => item.id === snapshot.selection);
    $("review-change").textContent = selected?.name || "Updated arrival constraint";
    $("review-cost").textContent = `$${snapshot.plan.budget.toLocaleString()}`;
    $("arrival").value = snapshot.plan.arrival;
    $("auth-hash").textContent = `R${snapshot.revision} · ${snapshot.plan_hash}`;
    $("auth-expiry").textContent = snapshot.authorization ? new Date(snapshot.authorization.expires_at).toLocaleString() : "Created after authorization";
    $("authorize").hidden = rank === 4;
    $("revert").hidden = rank === 4 || !snapshot.previous_plan;
    $("review-note").textContent = rank === 4 ? "Authorized. Execution is now available to ChatGPT and on this page." : "ChatGPT can prepare this review but cannot authorize it.";
  }
  if (snapshot.receipt) $("confirmation").textContent = snapshot.receipt.confirmation;
  $("events").innerHTML = snapshot.events.length ? snapshot.events.map((event) => `<li><code>${event.action}</code><span>${event.summary}</span><small>R${event.revision} · ${event.source}</small></li>`).join("") : "<li>No structured actions yet.</li>";
  if (changed) $("announcer").textContent = snapshot.events[0]?.summary || "The decision changed.";
}

function allowedTools() {
  const base = [{ name: "inspect_decision", title: "Inspect current decision", description: "Read the active offsite decision and exact revision.", execute: async () => toolResult("Read the current decision.", state.snapshot) }];
  if (["draft", "conflict", "options", "reviewed", "authorized"].includes(state.snapshot.state)) base.push({ name: "diagnose_plan", title: "Diagnose the plan", description: "Find the single blocking constraint and update the shared surface.", execute: async () => { await action("diagnose", {}, "webmcp"); return toolResult("Found the late-arrival conflict.", state.snapshot.finding); } });
  if (["conflict", "options", "reviewed"].includes(state.snapshot.state)) base.push({ name: "compare_repairs", title: "Compare repairs", description: "Create two budget-aware repairs for the active conflict.", execute: async () => { await action("repairs", {}, "webmcp"); return toolResult("Compared two feasible repairs.", state.snapshot.options); } });
  if (["options", "reviewed", "authorized"].includes(state.snapshot.state)) base.push({ name: "select_repair", title: "Select a repair", description: "Select one exact repair. Use shift for the arrival-safe schedule or remote for remote access.", inputSchema: { type: "object", properties: { repair_id: { type: "string", enum: ["shift", "remote"] } }, required: ["repair_id"], additionalProperties: false }, execute: async ({ repair_id }) => { await action("selection", { repair_id }, "webmcp"); return toolResult("Selected a repair."); } });
  if (state.snapshot.state === "reviewed") base.push({ name: "prepare_authorization", title: "Prepare human review", description: "Focus the exact-plan review. This tool cannot authorize it.", execute: async () => { $("review").scrollIntoView({ behavior: "smooth" }); return toolResult("Human review is ready. Authorization still requires the page control."); } });
  if (state.snapshot.state === "authorized") base.push({ name: "execute_authorized_plan", title: "Create the authorized reservation", description: "Execute the exact human-authorized plan and return its receipt.", inputSchema: { type: "object", properties: { idempotency_key: { type: "string", minLength: 8 } }, required: ["idempotency_key"], additionalProperties: false }, execute: async ({ idempotency_key }) => { await action("execute", { idempotency_key }, "webmcp"); return toolResult("Created the reservation receipt.", state.snapshot.receipt); } });
  return base;
}

async function registerTools() {
  if (!document.modelContext?.registerTool) {
    $("connection").textContent = "Manual mode";
    $("mode-copy").textContent = "This browser does not expose page tools. The same decision remains usable manually.";
    return;
  }
  state.controller?.abort(); state.controller = new AbortController();
  try {
    const tools = allowedTools();
    for (const tool of tools) await document.modelContext.registerTool({ inputSchema: { type: "object", properties: {}, additionalProperties: false }, ...tool }, { signal: state.controller.signal });
    $("connection").textContent = "WebMCP connected";
    $("mode-copy").textContent = `Live capabilities: ${tools.map((tool) => tool.name).join(", ")}`;
  } catch {
    $("connection").textContent = "Tool access unavailable";
    $("mode-copy").textContent = "ChatGPT could not access this page's tools. The plan is still usable here.";
  }
}

async function boot() {
  clearError();
  setBusy(true);
  let id = localStorage.getItem("captains-table-session");
  try {
    try { state.snapshot = id ? await request(`/api/session/${id}`) : null; } catch { state.snapshot = null; }
    if (!state.snapshot) { state.snapshot = await request("/api/session", { method: "POST", body: "{}" }); localStorage.setItem("captains-table-session", state.snapshot.session_id); }
    render(state.snapshot); await registerTools();
  } finally {
    setBusy(false);
  }
}

$("inspect").addEventListener("click", () => { void action("diagnose", {}).catch(() => {}); });
$("compare").addEventListener("click", () => { void action("repairs", {}).catch(() => {}); });
$("save-arrival").addEventListener("click", () => { void action("constraint", { arrival: $("arrival").value }).catch(() => {}); });
$("authorize").addEventListener("click", () => { void action("authorize", { plan_hash: state.snapshot.plan_hash, consent: true }).catch(() => {}); });
$("revert").addEventListener("click", () => { void action("revert", {}).catch(() => {}); });
$("execute").addEventListener("click", () => { void action("execute", { idempotency_key: crypto.randomUUID() }).catch(() => {}); });
$("copy-prompt").addEventListener("click", async () => { try { await navigator.clipboard.writeText("Find the most important conflict in this offsite plan."); $("copy-prompt").textContent = "Copied"; } catch (error) { showError(error); } });
$("retry-load").addEventListener("click", () => { window.location.reload(); });
wideScreen.addEventListener("change", syncEvidenceDisclosure);
syncEvidenceDisclosure(wideScreen);
window.addEventListener("pagehide", () => state.controller?.abort());
boot().catch((error) => { $("connection").textContent = "Unable to load"; showError(error, true); });
