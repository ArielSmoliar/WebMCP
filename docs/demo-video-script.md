# Captain's Table Two-Minute Demo

Target runtime: 1:55–2:00. Record the full 1440×900 browser viewport. No captions. Narration should sound calm, precise, quietly ambitious, and trustworthy.

## Narration

Browser agents can move quickly, but consequential work breaks when the person and the agent act on different versions of a plan. Captain's Table gives ChatGPT and a human one live decision surface.

The scenario is an eight-person offsite. Two required attendees arrive after the roadmap session begins. ChatGPT inspects the live plan through page-scoped WebMCP tools and identifies that conflict without guessing through the interface.

The available tools change with the workflow. ChatGPT compares two feasible repairs, then selects the arrival-safe option: move the roadmap session to twelve fifteen. Everyone can attend, and the updated plan costs seven thousand, three hundred eighty dollars.

Now the authority boundary becomes visible. ChatGPT can prepare this exact version for review, but it cannot approve it. There is deliberately no authorize-plan agent tool. Only the person on the page can authorize the server-computed plan hash, and any later mutation invalidates that approval.

After the human authorizes, ChatGPT receives the execution tool and creates the simulated reservation. The server executes exactly once and returns receipt C T, seven nine E C A one. Reloading recovers the same receipt instead of creating a duplicate.

The evidence rail shows why this is more than a staged workflow. Every tool set belongs to a capability epoch bound to one server revision and fingerprint. The verified ChatGPT host observed the current tools. Retained stale callbacks were rejected. Safety probes recorded zero stale mutations, zero authorization bypasses, and zero duplicate reservations.

Captain's Table is a reference for coordinated agency: meaningful agent action, exact human authority, and evidence both sides can inspect.

## Timed Visual Run

| Time | Browser action |
|---|---|
| 0:00–0:12 | Full-screen R1 opening: title, decision, four-stage workflow, and three proof signals. |
| 0:12–0:27 | Invoke diagnosis; hold on the repaired-conflict explanation and R2 tool state. |
| 0:27–0:44 | Invoke repair comparison; scroll to both repair options and their tradeoffs. |
| 0:44–1:03 | Select the shift option; scroll to R4 human authorization and hold on the exact-plan summary. |
| 1:03–1:16 | Click the page-only authorization control; show R5 and the changed tool state. |
| 1:16–1:35 | Invoke execution; scroll to the R6 receipt and completed workflow. |
| 1:35–1:52 | Expand Technical evidence; show current capabilities, safety results, receipt recovery, and decision trail. |
| 1:52–2:00 | Reload; finish on the same recovered receipt. |

## Production Notes

- Use a temporary local SQLite session with the deployed code path; do not create another production Firestore session.
- Record the complete browser viewport at 1440×900 and scroll smoothly to relevant sections.
- Do not show account identity, bookmarks, unrelated tabs, desktop notifications, or credentials.
- Do not imply that ChatGPT performed the human authorization click.
- Use ChatGPT built-in-browser evidence for native host claims. Chrome 151 is page-enablement evidence only.
- Generate narration with OpenAI `gpt-4o-mini-tts` through `v1/audio/speech`.
- Upload the final MP4 publicly to YouTube and add the URL to Devpost.
