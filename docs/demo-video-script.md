# Captain's Table Two-Minute Demo

Target runtime: 1:40–1:50. Record the full 1440×900 browser viewport. Use a compact agent-activity panel for tool names and results; do not add sentence-by-sentence captions. Narration should sound calm, precise, quietly ambitious, and trustworthy.

## Narration

Watch ChatGPT call the page's Web M C P tool. In seconds, the live plan changes from uninspected to conflict found: two required attendees arrive after the roadmap session begins.

Captain's Table gives Chat G P T and a human one decision surface. Instead of clicking through screens or guessing from a screenshot, the agent works through explicit, page-scoped tools bound to current server state.

ChatGPT compares two feasible repairs and selects the arrival-safe option: move the roadmap decision to twelve fifteen. Everyone can attend, and the updated plan costs seven thousand, three hundred eighty dollars.

Now the authority boundary becomes visible. ChatGPT can prepare this exact version for review, but it cannot approve it. No authorize-plan agent tool exists. Only the person on the page can authorize the server-computed plan hash. Any later mutation invalidates that approval.

After the human authorizes, the execution tool appears. ChatGPT creates the simulated reservation exactly once and receives a durable receipt. Reloading recovers that same receipt instead of creating a duplicate.

The final proof is intentionally a non-event. We retained an execution tool from the final review state, advanced the workflow to completion, and invoked the old tool again. The server rejected its stale revision before changing Firestore: no plan mutation, no second reservation, and no borrowed authority over newer state.

That is what Web M C P enables here: meaningful agent action, exact human authority, and evidence both sides can inspect.

## Timed Visual Run

| Time | Browser action |
|---|---|
| 0:00–0:10 | Start on the working product. Show `ChatGPT · WebMCP` calling `diagnose_plan()` and the page advancing to Conflict found. |
| 0:10–0:27 | Show `compare_repairs()` and both repair tradeoffs. |
| 0:27–0:43 | Show `select_repair({repair_id: 'shift'})`, the repaired plan, and 8/8 attendance. |
| 0:43–1:00 | Show that no `authorize_plan` tool exists; the human authorizes the exact plan on the page. |
| 1:00–1:19 | Show `execute_authorized_plan()`, the R6 receipt, and exactly-once outcome. |
| 1:19–1:38 | Expand Technical evidence and explain the retained R5 handle rejected at R6. |
| 1:38–1:48 | Reload and finish on the recovered receipt. |

## Production Notes

- Use a temporary local SQLite session with the deployed code path; do not create another production Firestore session.
- Record the complete browser viewport at 1440×900 and scroll smoothly to relevant sections.
- Do not show account identity, bookmarks, unrelated tabs, desktop notifications, or credentials.
- Do not imply that ChatGPT performed the human authorization click.
- Use ChatGPT built-in-browser evidence for native host claims. Chrome 151 is page-enablement evidence only.
- Generate narration with OpenAI `gpt-4o-mini-tts` through `v1/audio/speech`.
- Upload the final MP4 publicly to YouTube and add the URL to Devpost.
