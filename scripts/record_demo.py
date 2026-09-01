"""Record the complete two-minute Captain's Table browser demo locally."""

import os
import socket
import subprocess
import tempfile
import time
from pathlib import Path

from playwright.sync_api import expect, sync_playwright


ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "output/demo"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

MODEL_CONTEXT_MOCK = """
(() => {
  const registrations = [];
  Object.defineProperty(document, "modelContext", {
    configurable: true,
    value: {
      registerTool: async (tool, options = {}) => {
        const entry = { tool, aborted: Boolean(options.signal?.aborted) };
        options.signal?.addEventListener("abort", () => { entry.aborted = true; }, { once: true });
        registrations.push(entry);
      },
    },
  });
  window.__webmcp = {
    registrations,
    active: () => registrations.filter((entry) => !entry.aborted),
    invoke: async (name, args = {}) => {
      const entry = registrations.findLast(
        (candidate) => !candidate.aborted && candidate.tool.name === name
      );
      if (!entry) throw new Error(`tool_not_registered:${name}`);
      return entry.tool.execute(args);
    },
  };
})();
"""


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def pause(seconds: float) -> None:
    time.sleep(seconds)


def smooth_scroll(page, selector: str, block: str = "center") -> None:
    page.locator(selector).evaluate(
        "(element, block) => element.scrollIntoView({behavior: 'smooth', block})",
        block,
    )
    pause(1.2)


def show_overview(page) -> None:
    page.evaluate("window.scrollTo({top: 0, behavior: 'smooth'})")
    pause(1.2)


def wait_for_server(process: subprocess.Popen, port: int) -> None:
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError("Local demo server exited before becoming ready")
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                return
        except OSError:
            time.sleep(0.05)
    raise RuntimeError("Local demo server did not become ready")


def invoke(page, name: str, args: dict | None = None) -> None:
    page.evaluate(
        "([toolName, toolArgs]) => window.__webmcp.invoke(toolName, toolArgs)",
        [name, args or {}],
    )


def install_agent_panel(page) -> None:
    page.add_style_tag(
        content="""
        #demo-agent-panel {
          position: fixed;
          top: 54px;
          right: 26px;
          width: 360px;
          z-index: 9999;
          box-sizing: border-box;
          padding: 18px 20px;
          border: 1px solid rgba(255,255,255,.16);
          border-radius: 14px;
          background: rgba(19, 24, 23, .96);
          color: #f7f5ef;
          box-shadow: 0 18px 50px rgba(24, 34, 31, .24);
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }
        #demo-agent-panel .eyebrow {
          margin: 0 0 10px;
          color: #88d7c4;
          font-size: 11px;
          font-weight: 750;
          letter-spacing: .12em;
          text-transform: uppercase;
        }
        #demo-agent-panel .message {
          margin: 0 0 12px;
          font-size: 17px;
          font-weight: 650;
          line-height: 1.3;
        }
        #demo-agent-panel .tool {
          margin: 5px 0 0;
          padding: 10px 12px;
          border-radius: 8px;
          background: rgba(255,255,255,.08);
          color: #ffffff;
          font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
          font-size: 13px;
          line-height: 1.45;
          overflow-wrap: anywhere;
        }
        #demo-agent-panel .result {
          margin: 5px 0 0;
          color: #b9c6c2;
          font-size: 13px;
          line-height: 1.4;
        }
        #demo-agent-panel .field-label {
          margin: 12px 0 0;
          color: #88d7c4;
          font-size: 10px;
          font-weight: 750;
          letter-spacing: .09em;
          text-transform: uppercase;
        }
        #demo-agent-panel .result-label {
          padding-top: 10px;
          border-top: 1px solid rgba(255,255,255,.12);
        }
        """
    )
    page.evaluate(
        """
        () => {
          const panel = document.createElement('aside');
          panel.id = 'demo-agent-panel';
          panel.setAttribute('aria-label', 'ChatGPT WebMCP activity');
          document.body.appendChild(panel);
          window.__setAgentPanel = ({message, tool, result}) => {
            panel.innerHTML = `
              <p class="eyebrow">ChatGPT · WebMCP</p>
              <p class="message">${message}</p>
              <p class="field-label">ChatGPT action</p>
              <p class="tool">${tool}</p>
              <p class="field-label result-label">Server result</p>
              <p class="result">${result}</p>`;
          };
        }
        """
    )


def show_agent(page, message: str, tool: str, result: str) -> None:
    page.evaluate(
        "([message, tool, result]) => window.__setAgentPanel({message, tool, result})",
        [message, tool, result],
    )


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    port = free_port()
    with tempfile.TemporaryDirectory(prefix="captains-table-video-") as data_dir:
        env = os.environ.copy()
        env.update(
            {
                "CAPTAINS_TABLE_STORAGE": "sqlite",
                "CAPTAINS_TABLE_DB": str(Path(data_dir) / "demo.sqlite3"),
            }
        )
        process = subprocess.Popen(
            [
                os.sys.executable,
                "-m",
                "uvicorn",
                "app.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
            ],
            cwd=ROOT,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            wait_for_server(process, port)
            with sync_playwright() as manager:
                browser = manager.chromium.launch(headless=True, executable_path=CHROME)
                context = browser.new_context(
                    viewport={"width": 1440, "height": 900},
                    record_video_dir=str(OUTPUT_DIR),
                    record_video_size={"width": 1440, "height": 900},
                )
                context.add_init_script(MODEL_CONTEXT_MOCK)
                page = context.new_page()
                page.goto(f"http://127.0.0.1:{port}", wait_until="networkidle")
                expect(page.locator("#revision")).to_contain_text("R1")
                install_agent_panel(page)
                timeline_start = time.monotonic()

                def wait_until(second: float) -> None:
                    pause(max(0, second - (time.monotonic() - timeline_start)))

                show_agent(
                    page,
                    "Find what blocks this plan.",
                    "diagnose_plan()",
                    "Awaiting result · issuing revision R1",
                )
                wait_until(12.5)

                invoke(page, "diagnose_plan")
                expect(page.locator("#revision")).to_contain_text("R2")
                show_agent(
                    page,
                    "Conflict found",
                    "diagnose_plan()",
                    "Conflict found · R1 → R2. Two required attendees arrive after the roadmap session begins.",
                )
                smooth_scroll(page, "#finding")
                wait_until(20)

                show_agent(
                    page,
                    "Compare feasible repairs.",
                    "compare_repairs()",
                    "Awaiting result · issuing revision R2",
                )
                invoke(page, "compare_repairs")
                expect(page.locator("#revision")).to_contain_text("R3")
                show_agent(
                    page,
                    "Two repairs compared",
                    "compare_repairs()",
                    "Two repairs returned · R2 → R3. Explicit cost and attendance tradeoffs are now available.",
                )
                smooth_scroll(page, "#comparison")
                wait_until(29)

                show_agent(
                    page,
                    "Select the arrival-safe option.",
                    "select_repair({repair_id: 'shift'})",
                    "Awaiting result · issuing revision R3",
                )
                invoke(page, "select_repair", {"repair_id": "shift"})
                expect(page.locator("#revision")).to_contain_text("R4")
                show_overview(page)
                wait_until(35)
                smooth_scroll(page, "#review", "center")
                show_agent(
                    page,
                    "Human authorization required",
                    "select_repair({repair_id: 'shift'})",
                    "Arrival-safe repair selected · R3 → R4. Only the person on the page can approve its hash.",
                )
                wait_until(57)

                page.locator("#authorize").click()
                expect(page.locator("#revision")).to_contain_text("R5")
                show_agent(
                    page,
                    "Exact plan authorized by the human",
                    "None · page-only human action",
                    "Authorization recorded · R4 → R5. It is bound to this revision and plan hash.",
                )
                show_overview(page)
                wait_until(59)
                smooth_scroll(page, "#review", "center")
                wait_until(60)

                show_agent(
                    page,
                    "Create the reservation.",
                    "execute_authorized_plan()",
                    "Awaiting result · issuing revision R5 · idempotency key devpost-video-002",
                )
                wait_until(61)
                invoke(page, "execute_authorized_plan", {"idempotency_key": "devpost-video-002"})
                expect(page.locator("#confirmation")).to_contain_text("CT-")
                show_agent(
                    page,
                    "Executed exactly once",
                    "execute_authorized_plan()",
                    "Reservation created · R5 → R6. A durable receipt can be recovered after reload.",
                )
                show_overview(page)
                wait_until(64)
                smooth_scroll(page, "#receipt", "center")
                wait_until(69)

                page.locator("#technical-evidence > summary").click()
                show_agent(
                    page,
                    "An outdated tool cannot reuse approval",
                    "retained execute_authorized_plan() [R5]",
                    "Rejected at R6. The organizer's approval cannot authorize a second reservation or a newer plan state.",
                )
                smooth_scroll(page, "#technical-evidence", "start")
                wait_until(79)
                smooth_scroll(page, "#events", "center")
                wait_until(89)

                page.reload(wait_until="networkidle")
                expect(page.locator("#confirmation")).to_contain_text("CT-")
                install_agent_panel(page)
                show_agent(
                    page,
                    "Same outcome after reload",
                    "None · receipt recovery",
                    "Original receipt recovered · remains R6. No duplicate reservation was created.",
                )
                show_overview(page)
                wait_until(98)
                smooth_scroll(page, "#receipt", "center")
                wait_until(105)

                video = page.video
                context.close()
                if video is None:
                    raise RuntimeError("Playwright did not create a video")
                video.save_as(str(OUTPUT_DIR / "captains-table-demo-silent.webm"))
                browser.close()
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

    print(OUTPUT_DIR / "captains-table-demo-silent.webm")


if __name__ == "__main__":
    main()
