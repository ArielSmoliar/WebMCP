# New Session Prompt

Copy the prompt below into a new Codex session opened in the dedicated repository:

```text
Continue the OpenAI WebMCP Challenge demo in the dedicated repository:
/Users/arielsmoliar/Documents/ChatGPT/WebMCP

First, read HANDOFF.md completely, then read PRODUCT.md, DESIGN.md,
docs/engineering-plan.md, docs/interaction-design.md, docs/test-plan.md,
docs/protocol-observations.md, and CHALLENGE_WORK.md. Inspect git status, the current
commit, and remotes before changing anything. Preserve existing work and use Python
3.13, matching the Docker runtime.

Current checkpoint: commit a247d9e builds the complete shared decision demo. Six
Python domain/API tests pass. The full manual browser journey was visually tested at
760px and 680px through diagnosis, comparison, selection, human arrival edit,
exact-plan authorization, execution, and persisted receipt recovery.

Important distinction: the dedicated repository is named WebMCP. The interface is
currently named Captain's Table. The user questioned that product name, but no final
rename decision was made. Do not rename either one without asking. Also ask whether
the GitHub repository should be public or private before creating a remote or pushing.

The next objective is to publish and deploy safely, then verify actual WebMCP tool
discovery and invocation in a WebMCP-enabled ChatGPT browser. Do not treat Manual
mode browser QA as proof of WebMCP compatibility. Verify all six tools, state-aware
registration, visible mutations, the absence of an authorization tool, conditional
execution, and receipt replay. If dynamic tool propagation is unreliable, use the
documented compatibility mode and label it honestly.

After real-browser verification, add the missing browser/error-matrix tests, run a
post-implementation Impeccable critique/audit/polish pass, and prepare the Devpost
submission materials. Keep the product precise, quietly ambitious, and trustworthy.
Do not add Gemini, Google ADK, a standalone MCP server, or the OpenAI Agents SDK
without new evidence and explicit justification.
```

