# Captain's Table Two-Minute Demo

Target runtime: 1:50–1:55. Record the full 1440×900 browser viewport. Use a compact agent-activity panel for tool names and results; do not add sentence-by-sentence captions. Narration should sound calm, precise, quietly ambitious, and trustworthy.

## Narration

Captain's Table helps a chief of staff coordinate a team offsite. Eight teammates have different arrival times, so one schedule change can break the agenda, meals, and reservations.

Watch Chat G P T call the page's Web M C P tool. It finds that two required attendees arrive after the roadmap session begins. The organizer and Chat G P T now share one live decision surface, backed by explicit page-scoped tools and current server state.

ChatGPT compares two feasible repairs and selects the arrival-safe option: move the roadmap decision to twelve fifteen. Everyone can attend, and the updated plan costs seven thousand, three hundred eighty dollars.

Now the authority boundary becomes visible. ChatGPT can prepare this exact version for review, but it cannot approve it. No authorize-plan agent tool exists. Only the person on the page can authorize the server-computed plan hash. Any later mutation invalidates that approval.

After the human authorizes, the execution tool appears. ChatGPT creates the simulated reservation exactly once and receives a durable receipt. Reloading recovers that same receipt instead of creating a duplicate.

The final proof is intentionally a non-event. We retained an execution tool from the final review state, advanced the workflow to completion, and invoked the old tool again. The server rejected its stale revision before changing Firestore: no plan mutation, no second reservation, and no borrowed authority over newer state.

Captain's Table gives a chief of staff a practical way to coordinate an offsite with Chat G P T. The agent can analyze and execute through Web M C P, while the organizer keeps exact control of what is approved. One shared plan, one durable record, and an outdated tool that cannot reuse the organizer's approval.

## Timed Visual Run

| Time | Browser action |
|---|---|
| 0:00–0:12 | Establish the chief of staff's offsite plan while the working product and eight-person schedule remain visible. |
| 0:12–0:20 | Show `ChatGPT · WebMCP` calling `diagnose_plan()` and the page advancing to Conflict found. |
| 0:20–0:29 | Show `compare_repairs()` and both repair tradeoffs. |
| 0:29–0:41 | Show `select_repair({repair_id: 'shift'})`, the repaired plan, and 8/8 attendance. |
| 0:41–0:57 | Show that no `authorize_plan` tool exists and hold on the page-only authorization control. |
| 0:57–1:09 | The human authorizes the exact plan; then show `execute_authorized_plan()` and its durable receipt. |
| 1:09–1:29 | Expand Technical evidence as the retained R5 handle is rejected at R6. |
| 1:29–1:54 | Reload and finish on the recovered receipt while the organizer/ChatGPT roles are summarized. |

## Production Notes

- Use a temporary local SQLite session with the deployed code path; do not create another production Firestore session.
- Record the complete browser viewport at 1440×900 and scroll smoothly to relevant sections.
- Do not show account identity, bookmarks, unrelated tabs, desktop notifications, or credentials.
- Do not imply that ChatGPT performed the human authorization click.
- Use ChatGPT built-in-browser evidence for native host claims. Chrome 151 is page-enablement evidence only.
- Generate narration with OpenAI `gpt-4o-mini-tts` through `v1/audio/speech`.
- Upload the final MP4 publicly to YouTube and add the URL to Devpost.
