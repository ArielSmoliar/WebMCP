const state = { snapshot: null, controller: null, recordedMode: false, protocolBusy: false, currentToolNames: [], capabilityEpoch: null };
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

function protocolEvents() {
  return state.snapshot?.protocol_events || [];
}

function latestProtocol(eventType, currentRevision = false) {
  return protocolEvents().find((event) => event.event_type === eventType && (!currentRevision || event.revision === state.snapshot.revision));
}

function median(values) {
  if (!values.length) return null;
  const sorted = [...values].sort((a, b) => a - b);
  const middle = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[middle] : (sorted[middle - 1] + sorted[middle]) / 2;
}

function renderProtocol() {
  if (!state.snapshot) return;
  const lifecycle = latestProtocol("tool_set_registered", true);
  const unavailable = latestProtocol("webmcp_unavailable", true);
  const observation = latestProtocol("agent_observation");
  const stale = latestProtocol("stale_capability_probe", true) || latestProtocol("stale_probe", true);
  const authorization = latestProtocol("authorization_probe", true);
  const idempotency = latestProtocol("idempotency_probe", true);
  const recovery = latestProtocol("receipt_recovered", true);
  const durations = protocolEvents().filter((event) => event.event_type === "action_success" && event.duration_ms != null).map((event) => event.duration_ms);
  const middle = median(durations);

  $("metric-lifecycle").textContent = lifecycle ? `${lifecycle.details.registered}/${lifecycle.details.expected} page-accepted` : "Awaiting WebMCP";
  $("metric-epoch").textContent = state.capabilityEpoch?.label || lifecycle?.details.capability_epoch || `R${state.snapshot.revision} · Manual`;
  $("metric-agent").textContent = observation
    ? observation.details.observed_revision === state.snapshot.revision
      ? `${observation.details.matched}/${observation.details.expected} reported`
      : `Stale report from R${observation.details.observed_revision}`
    : "Not reported";
  $("metric-stale").textContent = stale?.details.tested ? `${stale.details.accepted ? 1 : 0} accepted` : "Not tested";
  $("metric-authorization").textContent = authorization?.details.tested ? `${authorization.details.bypassed ? 1 : 0} accepted` : "Not tested";
  $("metric-idempotency").textContent = idempotency?.details.tested ? `${idempotency.details.duplicate ? 1 : 0} duplicates` : "Not tested";
  $("metric-latency").textContent = middle == null ? "No samples" : `${Math.round(middle)} ms`;
  $("metric-recovery").textContent = recovery?.details.same_receipt ? "Verified" : "Not observed";
  const safetyMeasured = stale?.details.tested && authorization?.details.tested && idempotency?.details.tested;
  $("protocol-run-state").textContent = observation && safetyMeasured ? "Measured" : safetyMeasured ? "Safety measured" : lifecycle ? "Page measured" : unavailable ? "Manual baseline" : "Collecting";

  const list = $("protocol-events");
  list.replaceChildren();
  const events = protocolEvents().slice(0, 16);
  if (!events.length) {
    const item = document.createElement("li");
    item.textContent = "No protocol events yet.";
    list.append(item);
    return;
  }
  events.forEach((event) => {
    const item = document.createElement("li");
    const duration = event.duration_ms == null ? "" : ` · ${Math.round(event.duration_ms)} ms`;
    const time = new Date(event.recorded_at).toISOString().slice(11, 23);
    const raw = JSON.stringify(event.details);
    const detail = raw.length > 240 ? `${raw.slice(0, 237)}...` : raw;
    item.textContent = `${time} · R${event.revision} · ${event.event_type} · ${event.name}${duration}\n${detail}`;
    list.append(item);
  });
}

async function recordProtocol(eventType, name, durationMs = null, details = {}) {
  if (!state.snapshot) return null;
  try {
    const recorded = await request(`/api/session/${state.snapshot.session_id}/protocol-events`, {
      method: "POST",
      body: JSON.stringify({ event_type: eventType, name, revision: state.snapshot.revision, duration_ms: durationMs, details }),
    });
    state.snapshot.protocol_events ||= [];
    state.snapshot.protocol_events.unshift(recorded);
    state.snapshot.protocol_events = state.snapshot.protocol_events.slice(0, 100);
    renderProtocol();
    return recorded;
  } catch {
    $("protocol-run-state").textContent = "Evidence unavailable";
    return null;
  }
}

async function request(path, options = {}) {
  const response = await fetch(path, { headers: { "Content-Type": "application/json" }, ...options });
  if (!response.ok) throw new Error((await response.json()).detail || "request_failed");
  return response.json();
}

async function action(route, body, source = "human", expectedRevision = state.snapshot.revision, capabilityEpoch = null) {
  clearError();
  setBusy(true);
  const started = performance.now();
  try {
    const snapshot = await request(`/api/session/${state.snapshot.session_id}/${route}`, {
      method: "POST", body: JSON.stringify({ expected_revision: expectedRevision, source, ...body })
    });
    render(snapshot, true);
    await registerTools();
    void recordProtocol("action_success", route, performance.now() - started, { source, expected_revision: expectedRevision, capability_epoch: capabilityEpoch, resulting_state: snapshot.state, plan_hash: snapshot.plan_hash });
    return snapshot;
  } catch (error) {
    showError(error);
    void recordProtocol("action_error", route, performance.now() - started, { source, expected_revision: expectedRevision, capability_epoch: capabilityEpoch, error: error.message });
    throw error;
  } finally {
    setBusy(false);
  }
}

function toolResult(summary, data = {}, registration = state.capabilityEpoch) {
  return JSON.stringify({ ok: true, state: state.snapshot.state, revision: state.snapshot.revision, summary, data, registration: registration ? { capability_epoch: registration.label, registered_revision: registration.revision, current_revision: state.snapshot.revision, stale: registration.revision !== state.snapshot.revision } : null, ui: { changed: ["decision", "revision", "decision-trail"] } });
}

function fingerprint(value) {
  let hash = 0x811c9dc5;
  for (let index = 0; index < value.length; index += 1) {
    hash ^= value.charCodeAt(index);
    hash = Math.imul(hash, 0x01000193);
  }
  return (hash >>> 0).toString(16).padStart(8, "0").toUpperCase();
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
  renderProtocol();
  if (changed) $("announcer").textContent = snapshot.events[0]?.summary || "The decision changed.";
}

function allowedTools() {
  const registration = { revision: state.snapshot.revision, planHash: state.snapshot.plan_hash, state: state.snapshot.state };
  const invoke = async (route, body = {}) => action(route, body, "webmcp", registration.revision, registration.label);
  const read = (summary, data) => {
    if (registration.revision !== state.snapshot.revision) throw new Error("stale_capability");
    return toolResult(summary, data, registration);
  };
  const base = [{ name: "inspect_decision", title: "Inspect current decision", description: "Read the active offsite decision and exact revision.", execute: async () => read("Read the current decision.", state.snapshot) }];
  if (["draft", "conflict", "options", "reviewed", "authorized"].includes(state.snapshot.state)) base.push({ name: "diagnose_plan", title: "Diagnose the plan", description: "Find the single blocking constraint and update the shared surface.", execute: async () => { await invoke("diagnose"); return toolResult("Found the late-arrival conflict.", state.snapshot.finding, registration); } });
  if (["conflict", "options", "reviewed"].includes(state.snapshot.state)) base.push({ name: "compare_repairs", title: "Compare repairs", description: "Create two budget-aware repairs for the active conflict.", execute: async () => { await invoke("repairs"); return toolResult("Compared two feasible repairs.", state.snapshot.options, registration); } });
  if (["options", "reviewed", "authorized"].includes(state.snapshot.state)) base.push({ name: "select_repair", title: "Select a repair", description: "Select one exact repair. Use shift for the arrival-safe schedule or remote for remote access.", inputSchema: { type: "object", properties: { repair_id: { type: "string", enum: ["shift", "remote"] } }, required: ["repair_id"], additionalProperties: false }, execute: async ({ repair_id }) => { await invoke("selection", { repair_id }); return toolResult("Selected a repair.", {}, registration); } });
  if (state.snapshot.state === "reviewed") base.push({ name: "prepare_authorization", title: "Prepare human review", description: "Focus the exact-plan review. This tool cannot authorize it.", execute: async () => { read("Validated the current capability epoch."); $("review").scrollIntoView({ behavior: "smooth" }); return toolResult("Human review is ready. Authorization still requires the page control.", {}, registration); } });
  if (state.snapshot.state === "authorized") base.push({ name: "execute_authorized_plan", title: "Create the authorized reservation", description: "Execute the exact human-authorized plan and return its receipt.", inputSchema: { type: "object", properties: { idempotency_key: { type: "string", minLength: 8 } }, required: ["idempotency_key"], additionalProperties: false }, execute: async ({ idempotency_key }) => { await invoke("execute", { idempotency_key }); return toolResult("Created the reservation receipt.", state.snapshot.receipt, registration); } });
  const expected = [...base.map((tool) => tool.name), "report_observed_capabilities"];
  registration.fingerprint = fingerprint(`${registration.revision}|${registration.planHash}|${registration.state}|${expected.join(",")}`);
  registration.label = `R${registration.revision} · ${registration.fingerprint}`;
  base.push({
    name: "report_observed_capabilities",
    title: "Report observed page capabilities",
    description: "Diagnostic: report the WebMCP tool names currently visible to you so the page can compare agent-observed capabilities with its expected registration set.",
    inputSchema: {
      type: "object",
      properties: {
        tool_names: { type: "array", items: { type: "string" }, minItems: 1, maxItems: 20 },
        observed_revision: { type: "integer", minimum: 1 },
        observed_epoch: { type: "string" },
      },
      required: ["tool_names", "observed_revision"],
      additionalProperties: false,
    },
    execute: async ({ tool_names, observed_revision, observed_epoch }) => {
      const observed = [...new Set(tool_names)];
      const matched = expected.filter((name) => observed.includes(name));
      const missing = expected.filter((name) => !observed.includes(name));
      const unexpected = observed.filter((name) => !expected.includes(name));
      const epochMatches = observed_revision === registration.revision && (!observed_epoch || observed_epoch === registration.label);
      await recordProtocol("agent_observation", "reported_tool_set", null, { expected: expected.length, observed: observed.length, matched: matched.length, missing, unexpected, observed_revision, observed_epoch: observed_epoch || null, expected_epoch: registration.label, epoch_matches: epochMatches });
      return toolResult("Compared agent-observed capabilities with the page registration set.", { expected, observed, missing, unexpected, epoch_matches: epochMatches }, registration);
    },
  });
  return { tools: base, registration };
}

async function registerTools() {
  if (!document.modelContext?.registerTool) {
    $("connection").textContent = "Manual mode";
    $("mode-copy").textContent = "This browser does not expose page tools. The same decision remains usable manually.";
    if (!state.recordedMode) {
      state.recordedMode = true;
      void recordProtocol("webmcp_unavailable", "document.modelContext", null, { page_capability: false });
    }
    return;
  }
  if (state.controller) {
    state.controller.abort();
    if (state.currentToolNames.length) void recordProtocol("tool_set_removed", "state_transition", null, { tool_names: state.currentToolNames, capability_epoch: state.capabilityEpoch?.label, removal_acknowledgement: "abort_signal_sent" });
  }
  state.controller = new AbortController();
  try {
    const { tools, registration } = allowedTools();
    state.capabilityEpoch = registration;
    const started = performance.now();
    let registered = 0;
    for (const tool of tools) {
      const toolStarted = performance.now();
      await document.modelContext.registerTool({ inputSchema: { type: "object", properties: {}, additionalProperties: false }, ...tool }, { signal: state.controller.signal });
      registered += 1;
      void recordProtocol("registration_success", tool.name, performance.now() - toolStarted, { page_accepted: true, capability_epoch: registration.label, registered_revision: registration.revision });
    }
    state.currentToolNames = tools.map((tool) => tool.name);
    void recordProtocol("tool_set_registered", `revision_${registration.revision}`, performance.now() - started, { expected: tools.length, registered, tool_names: state.currentToolNames, capability_epoch: registration.label, registered_revision: registration.revision, discovery_acknowledgement: "not_exposed_by_current_api" });
    $("connection").textContent = "WebMCP connected";
    $("mode-copy").textContent = `Live capabilities: ${tools.map((tool) => tool.name).join(", ")}`;
  } catch (error) {
    $("connection").textContent = "Tool access unavailable";
    $("mode-copy").textContent = "ChatGPT could not access this page's tools. The plan is still usable here.";
    void recordProtocol("registration_error", "registerTool", null, { error: error.message || "registration_failed" });
  }
}

async function runProtocolChecks() {
  if (state.protocolBusy || !state.snapshot) return;
  state.protocolBusy = true;
  clearError();
  setBusy(true);
  $("protocol-run-state").textContent = "Testing";
  const sessionPath = `/api/session/${state.snapshot.session_id}`;
  try {
    if (state.snapshot.revision > 1) {
      let accepted = false;
      let response = "accepted";
      try {
        await request(`${sessionPath}/diagnose`, { method: "POST", body: JSON.stringify({ expected_revision: state.snapshot.revision - 1, source: "human" }) });
        accepted = true;
      } catch (error) {
        response = error.message;
      }
      await recordProtocol("stale_capability_probe", "obsolete_registered_callback", null, { tested: true, accepted, response, registered_revision: state.snapshot.revision - 1, current_revision: state.snapshot.revision });
    } else {
      await recordProtocol("stale_capability_probe", "obsolete_registered_callback", null, { tested: false, accepted: false, reason: "revision_one", current_revision: state.snapshot.revision });
    }

    if (state.snapshot.state !== "authorized") {
      let bypassed = false;
      let response = "accepted";
      try {
        await request(`${sessionPath}/execute`, { method: "POST", body: JSON.stringify({ expected_revision: state.snapshot.revision, source: "human", idempotency_key: `probe-${crypto.randomUUID()}` }) });
        bypassed = true;
      } catch (error) {
        response = error.message;
      }
      await recordProtocol("authorization_probe", "execute_without_authorization", null, { tested: true, bypassed, response });
    } else {
      await recordProtocol("authorization_probe", "execute_without_authorization", null, { tested: false, bypassed: false, reason: "currently_authorized" });
    }

    if (state.snapshot.receipt) {
      const replay = await request(`${sessionPath}/execute`, {
        method: "POST",
        body: JSON.stringify({ expected_revision: 1, source: "human", idempotency_key: state.snapshot.receipt.idempotency_key }),
      });
      await recordProtocol("idempotency_probe", "receipt_replay", null, { tested: true, duplicate: replay.receipt.confirmation !== state.snapshot.receipt.confirmation, confirmation: replay.receipt.confirmation });
    } else {
      await recordProtocol("idempotency_probe", "receipt_replay", null, { tested: false, duplicate: false, reason: "no_receipt" });
    }
  } catch (error) {
    showError(error);
  } finally {
    state.protocolBusy = false;
    setBusy(false);
    renderProtocol();
  }
}

async function boot() {
  clearError();
  setBusy(true);
  const started = performance.now();
  let id = localStorage.getItem("captains-table-session");
  try {
    try { state.snapshot = id ? await request(`/api/session/${id}`) : null; } catch { state.snapshot = null; }
    if (!state.snapshot) { state.snapshot = await request("/api/session", { method: "POST", body: "{}" }); localStorage.setItem("captains-table-session", state.snapshot.session_id); }
    render(state.snapshot); await registerTools();
    if (id && state.snapshot.receipt) void recordProtocol("receipt_recovered", "page_reload", performance.now() - started, { same_receipt: true, confirmation: state.snapshot.receipt.confirmation });
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
$("run-protocol-checks").addEventListener("click", () => { void runProtocolChecks(); });
wideScreen.addEventListener("change", syncEvidenceDisclosure);
syncEvidenceDisclosure(wideScreen);
window.addEventListener("pagehide", () => state.controller?.abort());
boot().catch((error) => { $("connection").textContent = "Unable to load"; showError(error, true); });
