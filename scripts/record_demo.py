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


def smooth_scroll(page, selector: str) -> None:
    page.locator(selector).scroll_into_view_if_needed()
    pause(1.5)


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
                pause(10)

                invoke(page, "diagnose_plan")
                expect(page.locator("#revision")).to_contain_text("R2")
                smooth_scroll(page, "#finding")
                pause(11)

                invoke(page, "compare_repairs")
                expect(page.locator("#revision")).to_contain_text("R3")
                smooth_scroll(page, "#comparison")
                pause(13)

                invoke(page, "select_repair", {"repair_id": "shift"})
                expect(page.locator("#revision")).to_contain_text("R4")
                smooth_scroll(page, "#review")
                pause(16)

                page.locator("#authorize").click()
                expect(page.locator("#revision")).to_contain_text("R5")
                pause(10)

                invoke(page, "execute_authorized_plan", {"idempotency_key": "devpost-video-001"})
                expect(page.locator("#confirmation")).to_contain_text("CT-")
                smooth_scroll(page, "#receipt")
                pause(15)

                page.locator("#technical-evidence > summary").click()
                smooth_scroll(page, "#technical-evidence")
                pause(14)

                page.reload(wait_until="networkidle")
                expect(page.locator("#confirmation")).to_contain_text("CT-")
                smooth_scroll(page, "#receipt")
                pause(8)

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
