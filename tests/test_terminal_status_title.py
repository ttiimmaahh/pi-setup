import shutil
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXTENSION = ROOT / "config/extensions/terminal-status-title.js"


class TerminalStatusTitleTests(unittest.TestCase):
    def test_title_formatting_and_lifecycle(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js is required")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            shutil.copy2(EXTENSION, temp_path / "terminal-status-title.mjs")
            harness = temp_path / "test.mjs"
            harness.write_text(
                textwrap.dedent(
                    """
                    import assert from "node:assert/strict";
                    import terminalStatusTitle, {
                      basename,
                      formatTitle,
                      truncateTitle,
                    } from "./terminal-status-title.mjs";

                    let nextTimerId = 1;
                    const intervals = new Map();
                    const timeouts = new Map();

                    globalThis.setInterval = (callback, delay) => {
                      const timer = { id: nextTimerId++, callback, delay };
                      intervals.set(timer.id, timer);
                      return timer;
                    };
                    globalThis.clearInterval = (timer) => intervals.delete(timer.id);
                    globalThis.setTimeout = (callback, delay) => {
                      const timer = { id: nextTimerId++, callback, delay };
                      timeouts.set(timer.id, timer);
                      return timer;
                    };
                    globalThis.clearTimeout = (timer) => timeouts.delete(timer.id);

                    function runOnlyTimeout() {
                      assert.equal(timeouts.size, 1);
                      const timer = [...timeouts.values()][0];
                      timeouts.delete(timer.id);
                      timer.callback();
                    }

                    function runOnlyInterval() {
                      assert.equal(intervals.size, 1);
                      const timer = [...intervals.values()][0];
                      timer.callback();
                      return timer;
                    }

                    function createRuntime(mode = "tui") {
                      const handlers = new Map();
                      const titles = [];
                      let sessionName = "";
                      const pi = {
                        getSessionName: () => sessionName,
                        on: (event, handler) => handlers.set(event, handler),
                      };
                      const ctx = {
                        mode,
                        cwd: "/workspace/project",
                        ui: { setTitle: (title) => titles.push(title) },
                      };
                      terminalStatusTitle(pi);
                      return {
                        ctx,
                        handlers,
                        pi,
                        setSessionName: (name) => { sessionName = name; },
                        titles,
                      };
                    }

                    assert.equal(basename("C:\\\\repo\\\\project\\\\"), "project");
                    assert.equal(truncateTitle("🙂".repeat(41)), "🙂".repeat(37) + "...");
                    assert.equal(
                      formatTitle({ getSessionName: () => "x".repeat(41) }, { cwd: "/ignored" }, "idle"),
                      `○ | π | ${"x".repeat(37)}...`,
                    );

                    const runtime = createRuntime();
                    await runtime.handlers.get("session_start")({}, runtime.ctx);
                    assert.equal(runtime.titles.at(-1), "○ | π | project");
                    runOnlyTimeout();
                    assert.equal(runtime.titles.at(-1), "○ | π | project");

                    await runtime.handlers.get("agent_start")({}, runtime.ctx);
                    assert.equal(runtime.titles.at(-1), "⠋ | π | project");
                    assert.equal(runOnlyInterval().delay, 120);
                    assert.equal(runtime.titles.at(-1), "⠙ | π | project");

                    await runtime.handlers.get("agent_end")({
                      messages: [{ role: "assistant", stopReason: "error" }],
                    });
                    assert.equal(runtime.titles.at(-1), "⠙ | π | project");
                    await runtime.handlers.get("agent_settled")({}, runtime.ctx);
                    assert.equal(runtime.titles.at(-1), "✗ | π | project");
                    assert.equal(intervals.size, 0);

                    runtime.setSessionName(" Build\\n\\u009dAuth ");
                    await runtime.handlers.get("session_info_changed")({}, runtime.ctx);
                    assert.equal(runtime.titles.at(-1), "✗ | π | Build Auth");

                    await runtime.handlers.get("agent_start")({}, runtime.ctx);
                    await runtime.handlers.get("agent_end")({
                      messages: [{ role: "assistant", stopReason: "stop" }],
                    });
                    await runtime.handlers.get("agent_settled")({}, runtime.ctx);
                    assert.equal(runtime.titles.at(-1), "✓ | π | Build Auth");

                    await runtime.handlers.get("agent_start")({}, runtime.ctx);
                    await runtime.handlers.get("agent_end")({
                      messages: [{ role: "assistant", stopReason: "aborted" }],
                    });
                    await runtime.handlers.get("agent_settled")({}, runtime.ctx);
                    assert.equal(runtime.titles.at(-1), "■ | π | Build Auth");
                    await runtime.handlers.get("session_shutdown")();
                    assert.equal(intervals.size, 0);
                    assert.equal(timeouts.size, 0);

                    const startupRuntime = createRuntime();
                    await startupRuntime.handlers.get("session_start")({}, startupRuntime.ctx);
                    assert.equal(timeouts.size, 1);
                    await startupRuntime.handlers.get("agent_start")({}, startupRuntime.ctx);
                    assert.equal(timeouts.size, 0);
                    await startupRuntime.handlers.get("session_shutdown")();

                    const shutdownRuntime = createRuntime();
                    await shutdownRuntime.handlers.get("session_start")({}, shutdownRuntime.ctx);
                    assert.equal(timeouts.size, 1);
                    await shutdownRuntime.handlers.get("session_shutdown")();
                    assert.equal(timeouts.size, 0);

                    const rpcRuntime = createRuntime("rpc");
                    await rpcRuntime.handlers.get("session_start")({}, rpcRuntime.ctx);
                    await rpcRuntime.handlers.get("session_info_changed")({}, rpcRuntime.ctx);
                    await rpcRuntime.handlers.get("agent_start")({}, rpcRuntime.ctx);
                    await rpcRuntime.handlers.get("agent_end")({
                      messages: [{ role: "assistant", stopReason: "error" }],
                    });
                    await rpcRuntime.handlers.get("agent_settled")({}, rpcRuntime.ctx);
                    await rpcRuntime.handlers.get("session_shutdown")();
                    assert.deepEqual(rpcRuntime.titles, []);
                    assert.equal(intervals.size, 0);
                    assert.equal(timeouts.size, 0);
                    """
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [node, str(harness)],
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
