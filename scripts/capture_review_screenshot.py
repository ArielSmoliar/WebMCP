"""Capture the R4 human-authorization boundary against a temporary local store."""

import os
import socket
import subprocess
import tempfile
import time
from pathlib import Path

from playwright.sync_api import expect, sync_playwright


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "docs/assets/devpost-02-human-authorization-r4.png"
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


def wait_for_server(process: subprocess.Popen, port: int) -> None:
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError("Local capture server exited before becoming ready")
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                return
        except OSError:
            time.sleep(0.05)
    raise RuntimeError("Local capture server did not become ready")


def main() -> None:
    port = free_port()
    with tempfile.TemporaryDirectory(prefix="captains-table-capture-") as data_dir:
        env = os.environ.copy()
        env.update(
            {
                "CAPTAINS_TABLE_STORAGE": "sqlite",
                "CAPTAINS_TABLE_DB": str(Path(data_dir) / "capture.sqlite3"),
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
                context = browser.new_context(viewport={"width": 1440, "height": 1100})
                context.add_init_script(MODEL_CONTEXT_MOCK)
                page = context.new_page()
                page.goto(f"http://127.0.0.1:{port}", wait_until="networkidle")

                page.evaluate("window.__webmcp.invoke('diagnose_plan')")
                expect(page.locator("#revision")).to_contain_text("R2")
                page.evaluate("window.__webmcp.invoke('compare_repairs')")
                expect(page.locator("#revision")).to_contain_text("R3")
                page.evaluate("window.__webmcp.invoke('select_repair', {repair_id: 'shift'})")
                expect(page.locator("#revision")).to_contain_text("R4")
                expect(page.locator("#status-label")).to_have_text("Ready for review")
                expect(page.locator("#authorize")).to_be_visible()
                expect(page.locator("#authorize")).to_be_enabled()
                expect(page.locator("#plan-budget")).to_have_text("$7,380")
                expect(page.locator("#roadmap-time")).to_have_text("12:15")
                page.screenshot(path=str(OUTPUT), full_page=True)

                context.close()
                browser.close()
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

    print(OUTPUT)


if __name__ == "__main__":
    main()
