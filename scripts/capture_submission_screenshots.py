"""Capture submission screenshots without creating or mutating production workflows."""

import json
from pathlib import Path

from playwright.sync_api import expect, sync_playwright


ROOT = Path(__file__).resolve().parent.parent
PRODUCTION_URL = "https://captains-table-webmcp-1017459622661.us-east1.run.app/"
VERIFIED_SESSION_ID = "UHxbrN-7PCXUU7kwmY2nCiNt"
VERIFIED_RECEIPT = "CT-79ECA1"
OUTPUT = ROOT / "docs/assets/devpost-03-durable-outcome-r6.png"
EVIDENCE_OUTPUT = ROOT / "docs/assets/devpost-04-protocol-evidence-r6.png"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

MODEL_CONTEXT_MOCK = """
(() => {
  Object.defineProperty(document, "modelContext", {
    configurable: true,
    value: { registerTool: async () => undefined },
  });
})();
"""


def main() -> None:
    with sync_playwright() as manager:
        browser = manager.chromium.launch(headless=True, executable_path=CHROME)
        context = browser.new_context(viewport={"width": 1440, "height": 1100})
        context.add_init_script(MODEL_CONTEXT_MOCK)
        context.add_init_script(
            "localStorage.setItem('captains-table-session', "
            f"{json.dumps(VERIFIED_SESSION_ID)});"
        )
        page = context.new_page()

        # Fail closed if the page ever attempts to create or mutate a workflow.
        page.route(
            "**/api/session",
            lambda route: route.abort() if route.request.method == "POST" else route.continue_(),
        )
        page.route(
            "**/api/session/*/protocol-events",
            lambda route: route.fulfill(status=201, content_type="application/json", body="{}"),
        )
        page.route(
            "**/api/session/*",
            lambda route: route.abort()
            if route.request.method not in {"GET", "HEAD", "OPTIONS"}
            else route.continue_(),
        )

        page.goto(PRODUCTION_URL, wait_until="networkidle")
        expect(page.locator("#status-label")).to_have_text("Reserved")
        expect(page.locator("#confirmation")).to_have_text(VERIFIED_RECEIPT)
        expect(page.locator("#revision")).to_contain_text("R6")
        expect(page.locator("#technical-evidence")).not_to_have_attribute("open", "")
        page.screenshot(path=str(OUTPUT), full_page=True)
        page.locator("#technical-evidence > summary").click()
        expect(page.locator("#technical-evidence")).to_have_attribute("open", "")
        page.screenshot(path=str(EVIDENCE_OUTPUT), full_page=True)

        context.close()
        browser.close()

    print(OUTPUT)
    print(EVIDENCE_OUTPUT)


if __name__ == "__main__":
    main()
