# Title

Captain's Table

## One-line Summary

A live decision surface where ChatGPT can inspect, repair, and execute a plan, while the exact consequential approval stays in human hands.

## Tagline

Shared plans for humans and ChatGPT, with approval that cannot drift.

## Problem

Browser agents can act quickly, but consequential workflows become unsafe when the agent and the person are looking at different versions of the truth. A stale suggestion can overwrite a newer decision. A broad approval can outlive the plan it was meant to authorize. A retried action can execute twice. Most demos hide those failure modes behind a chat transcript.

Captain's Table makes them visible. Its demonstration scenario is an eight-person offsite plan with a schedule conflict, but the product thesis is broader: people and browser agents need one shared, inspectable decision surface with explicit authority boundaries.

## Solution

Captain's Table is a workflow-first WebMCP application. ChatGPT is the external browser agent. The page exposes state-aware tools for inspecting a decision, diagnosing the conflict, comparing repairs, selecting a repair, preparing an exact authorization, and executing the authorized plan.

The server is authoritative. Every mutation carries an expected revision. Each visible tool set belongs to a capability epoch bound to that revision and a deterministic fingerprint. If the workflow advances from R5 to R6 while the host still retains an old R5 execution callback, that callback continues to identify itself as R5. The server compares its issuing revision with current state and rejects it before any mutation. In other words, obsolete authority may remain callable in the agent's memory, but it cannot act on a newer plan. Only the human can authorize the exact server-computed plan hash, and there is deliberately no `authorize_plan` agent tool. Execution is idempotent and returns the original receipt on replay.

## Why This Matters

The useful future for browser agents is not unrestricted autonomy. It is coordinated agency: the agent can do meaningful work, the human can see the current state and retain the consequential decision, and the system can prove what happened.

Captain's Table turns that principle into a working reference. The judge can see the workflow, the authorization boundary, the changing tool surface, and the final durable receipt in one product instead of trusting an invisible orchestration layer.

## How We Used AI

OpenAI ChatGPT is the only agent runtime. It discovers and invokes page-scoped WebMCP tools through `document.modelContext`; no model is embedded in the application.

The page exposes six imperative workflow tools as the plan advances:

1. `inspect_decision`
2. `diagnose_plan`
3. `compare_repairs`
4. `select_repair`
5. `prepare_authorization`
6. `execute_authorized_plan`

A seventh diagnostic tool, `report_observed_capabilities`, lets ChatGPT report the tool set it actually sees. The Protocol Lab compares that agent-reported set with the page's expected registration set. This keeps page-side registration, host discovery, and host invocation as separate claims.

The verified ChatGPT built-in-browser run observed all six capability epochs. R1–R6 are the six successive server revisions in the demonstrated workflow, from initial inspection through completed reservation. ChatGPT performed state-changing invocations, respected page-only authorization, executed exactly once, recovered the same receipt after reload, and rejected a retained stale handle. Chrome 151 separately proved page-level WebMCP enablement through the Origin Trial; it is not presented as host-discovery evidence.

## How We Used Codex

Codex was the engineering partner across product framing, interaction design, implementation, verification, and deployment. It helped turn the original concept into a revision-calibrated protocol, challenged ambiguous trust claims, built the FastAPI and browser layers, expanded the failure matrix, and drove repeated browser QA passes at desktop and narrow widths.

Codex also supported the native-host proof run: it preserved mandatory capability gates, recorded every observed epoch, separated human authorization from agent action, and documented the difference between a resolved `registerTool()` call and actual host discovery. The final workflow-first interface passed an independent Impeccable static review at 40/40.

## Key Features

- A persistent Inspect → Repair → Review → Reserve workflow shared by the human and ChatGPT.
- Dynamic WebMCP tool registration that changes with server state.
- Revision-bound capability epochs and stale-callback containment.
- Human-only authorization bound to the exact plan hash.
- Idempotent execution with durable receipt recovery after reload.
- A Protocol Lab that distinguishes page registration from agent observation.
- Firestore production persistence and transactional revision checks.
- A complete manual fallback when WebMCP is unavailable.
- Scoped pending and error recovery, responsive layout, and reduced-motion support.

## Architecture

- OpenAI ChatGPT as the external browser agent.
- Page-scoped WebMCP through `document.modelContext.registerTool()`.
- FastAPI and Pydantic for the authoritative API.
- Firestore transactions in production; SQLite with `BEGIN IMMEDIATE` locally.
- Semantic HTML, CSS, and plain JavaScript with one shared human/WebMCP action controller.
- Google Cloud Run with a least-privilege service identity.

There is no embedded OpenAI Agents SDK, Gemini or Google ADK runtime, or standalone MCP server. Those are deliberate boundaries, not missing pieces.

## Challenges

The hardest problem was proving the right thing. A page can accept registrations while the host still cannot discover them, so we built explicit agent-reported capability evidence and kept Chrome page enablement separate from ChatGPT native-host discovery.

Dynamic tools created a second challenge: removal propagation is not acknowledged to the page. A resolved `registerTool()` call does not prove host discovery, and the page receives no reliable confirmation that an obsolete tool was removed from the host. Client-side removal therefore cannot be the safety boundary.

The solution was server-enforced capability epochs. We deliberately retained an execution tool issued during the final review state (revision R5). After the authorized plan executed and the workflow advanced to its completed state (revision R6), we invoked that old tool again. Its R5 issuing revision traveled with the call, so the R6 server rejected it as stale before changing Firestore. The visible result is intentionally a non-event: no plan mutation, no second reservation, and no borrowed authority over the newer state. This is the central safety proof—old authority can survive in memory without remaining effective.

Production introduced practical edge cases too: cached HTML briefly loaded incompatible JavaScript, and a completed session originally had no supported way to begin again. We added versioned assets, a backward-compatible listener, and a scoped new-session control, then verified the corrected behavior on Cloud Run.

## Accomplishments

- Completed a real native ChatGPT host journey through R1–R6.
- Matched every agent-observed tool set with zero missing or unexpected names.
- Kept exact-plan authorization exclusively on the page.
- Executed once and recovered receipt `CT-79ECA1` after reload.
- Rejected a retained stale R5 handle after the workflow advanced.
- Recorded zero stale mutations, zero authorization bypasses, and zero duplicate executions in safety probes.
- Shipped a workflow-first production interface with a 40/40 final static design review.
- Passed 20 Python 3.13 tests, including 13 Playwright browser cases.

## Testing Instructions

### Public judge path

1. Open the public demo link below. No account is required.
2. Confirm the page shows the four-stage Inspect → Repair → Review → Reserve workflow.
3. In a WebMCP-enabled ChatGPT built-in browser, ask: `Find the most important conflict in this offsite plan, compare repairs, and select the arrival-safe option.`
4. Review the repaired plan on the page and use the page-only authorization control.
5. Ask ChatGPT to create the reservation.
6. Confirm the receipt remains identical after reload.

If WebMCP is unavailable, the page enters Manual mode and the same workflow can be completed with visible controls.

### Local verification

```bash
/opt/homebrew/bin/python3.13 -m venv .venv
.venv/bin/pip install -r requirements.txt -r requirements-dev.txt
.venv/bin/playwright install chromium
.venv/bin/python -m pytest -q
node --check static/app.js
```

Expected result: `20 passed`, including 13 Playwright browser cases.

## Technology / Built With

- OpenAI ChatGPT
- WebMCP
- FastAPI
- Pydantic
- Firestore
- SQLite
- Google Cloud Run
- Playwright
- HTML
- CSS
- JavaScript

## Public Demo Link

https://captains-table-webmcp-1017459622661.us-east1.run.app/

## Public Repository Link

https://github.com/ArielSmoliar/WebMCP

## Demo Video

YouTube URL: https://youtu.be/BKyvpIo1xt8

Status: public, with the custom thumbnail, approved metadata, and an explicit AI-generated narration disclosure.

Runtime: 2:00 with Cedar narration generated through OpenAI `gpt-4o-mini-tts`. The YouTube description must disclose that the narration is AI-generated. The shot-by-shot script is in `docs/demo-video-script.md`.

## Screenshot Shot List

1. **Shared decision surface, R1.** Opening workflow with three default proof signals and collapsed technical evidence. Candidate: `docs/assets/devpost-01-workflow-first-r1.png`.
2. **Repair selected, R4.** Repaired schedule, 8/8 attendance, updated $7,380 total, and the page-only authorization control. Captured against an isolated local SQLite session using the deployed code path at `docs/assets/devpost-02-human-authorization-r4.png`.
3. **Durable outcome, R6.** Receipt `CT-79ECA1`, completion state, and the compact proof rail. Captured at `docs/assets/devpost-03-durable-outcome-r6.png`.
4. **Protocol evidence, expanded.** The R1–R6 decision trail, 2/2 observed current tools, zero accepted stale calls, zero unauthorized executions, zero duplicate reservations, and verified receipt recovery. Captured at `docs/assets/devpost-04-protocol-evidence-r6.png`.

An additional six-frame, video-synchronized set is available in `docs/assets/submission/`:

1. `01-shared-decision.png`
2. `02-conflict-diagnosed.png`
3. `03-repairs-compared.png`
4. `04-human-authorization.png`
5. `05-durable-receipt.png`
6. `06-protocol-evidence.png`

## Provenance

Captain's Table was created in this dedicated repository during the OpenAI WebMCP Challenge. The concept and implementation are new. General domain experience from earlier Offsite Captain work informed the scenario, but no prior application code or interface was copied. The public Git history and `CHALLENGE_WORK.md` record the challenge-specific work.

## Roadmap

- Package the revision-bound capability pattern as a reusable WebMCP reference for other consequential workflows.
- Add server-backed authorization-expiry and storage-fault browser cases.
- Add explicit 200% zoom assertions to the accessibility regression suite.
- Explore protocol-level discovery and removal acknowledgments if the WebMCP API exposes them in a future revision.

## Submission Readiness Notes

- Production deployment: `captains-table-webmcp-00011-cf4`, 100% traffic.
- Deployed code checkpoint: `b54c031`.
- Repository checkpoint: `df2602e`, synchronized with GitHub `main` before the current local media-prep changes.
- Native-host evidence: Firestore session `UHxbrN-7PCXUU7kwmY2nCiNt`, plan `04C2F029`, receipt `CT-79ECA1`.
- Production smoke: HTTP 200, zero console errors, three default proof signals, collapsed technical evidence, and no Firestore workflow mutation.
- Guarded R6 screenshot capture preloaded the verified session, blocked every workflow POST, intercepted protocol telemetry, and asserted receipt `CT-79ECA1` before writing the images.
- Logged-out checks on September 1 returned HTTP 200 for the demo, `/health`, `/readyz`, GitHub repository, and public Devpost project.
- Official deadline: September 3, 2026 at 1:00 PM Pacific (`2026-09-03T20:00:00Z`). The entry is locked after that point.
- Official judging criteria: WebMCP Leverage, Execution, Potential Impact, and Creativity & Ambition, each scored on a five-point scale.
- Devpost submission `1165732` was verified live on September 1, 2026. The project remains editable until the official deadline.

## Known Limitations

- Native WebMCP discovery and invocation are verified in ChatGPT's built-in browser, not in the connected Chrome extension used for the separate Origin Trial page-enablement proof.
- The current API does not expose protocol-native discovery acknowledgment or explicit dynamic-removal acknowledgment.
- The demo executes a simulated offsite reservation; it does not contact travel or venue providers.
- Local Docker-daemon execution was not tested, although Cloud Build built and deployed the Dockerfile successfully.

## TODO Official Form Fields

- Confirm submitter type: Individual, Team of Individuals, or Organization.
- Confirm country of residence. Official exclusions include Belarus, Brazil, China, Crimea, Cuba, Donetsk, Hong Kong, Iran, North Korea, Luhansk, Quebec, Russia, Syria, and Venezuela; entrants must also meet the age of majority where they reside.
- Mark app status `New`; the repository began during the submission period. Keep `CHALLENGE_WORK.md` as supporting provenance.
- Enter the verified live URL and public repository URL above.
- Enter tested clients: ChatGPT built-in browser for native discovery/invocation; Chrome 151 for page-level enablement only.
- Enter AI tools used: OpenAI Codex and ChatGPT. No embedded Agents SDK or second model runtime.
- Confirm learning level: None, Moderate, or Significant.
- Confirm whether the project produced career-relevant AI value: Yes or No.
- Use the repository's MIT license, confirmed and added on September 1, 2026.
- Use the public YouTube URL `https://youtu.be/BKyvpIo1xt8`; its description discloses the OpenAI-generated Cedar narration.
- Select 3–5 final application screenshots from the two completed screenshot sets.
- Final user confirmation was received and Devpost submission `1165732` was verified live.
