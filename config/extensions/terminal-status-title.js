const DEFAULT_TITLE = "π";
const PREFIX = "π";
const MAX_TITLE_LENGTH = 40;
const SPINNER_INTERVAL_MS = 120;
const SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"];

function sanitizeTitlePart(value) {
  return value
    .replace(/[\x00-\x1f\x7f-\x9f]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

export function truncateTitle(title) {
  const characters = Array.from(title);
  if (characters.length <= MAX_TITLE_LENGTH) return title;
  return characters.slice(0, MAX_TITLE_LENGTH - 3).join("") + "...";
}

export function basename(path) {
  if (!path) return DEFAULT_TITLE;

  const trimmed = path.replace(/[\\/]+$/, "");
  if (!trimmed) return DEFAULT_TITLE;

  return sanitizeTitlePart(trimmed.split(/[\\/]/).pop() || DEFAULT_TITLE) || DEFAULT_TITLE;
}

function getSessionName(pi) {
  const name = pi.getSessionName?.();
  return typeof name === "string" ? sanitizeTitlePart(name) : "";
}

function getRawTitle(pi, ctx) {
  return getSessionName(pi) || basename(ctx.cwd);
}

function isSpinningStatus(status) {
  return status === "working";
}

function statusIndicator(status, spinnerFrame) {
  if (isSpinningStatus(status)) {
    return SPINNER_FRAMES[spinnerFrame % SPINNER_FRAMES.length];
  }

  if (status === "done") return "✓";
  if (status === "error") return "✗";
  if (status === "stopped") return "■";
  return "○";
}

export function formatTitle(pi, ctx, status, spinnerFrame = 0) {
  const rawTitle = getRawTitle(pi, ctx);
  const suffix = rawTitle === DEFAULT_TITLE ? DEFAULT_TITLE : `${PREFIX} | ${truncateTitle(rawTitle)}`;

  return `${statusIndicator(status, spinnerFrame)} | ${suffix}`;
}

function getRunOutcome(event) {
  const assistantMessages = event.messages?.filter((message) => message.role === "assistant") || [];
  const lastAssistantMessage = assistantMessages.at(-1);

  if (lastAssistantMessage?.stopReason === "error") return "error";
  if (lastAssistantMessage?.stopReason === "aborted") return "stopped";
  return "done";
}

export default function terminalStatusTitle(pi) {
  let status = "idle";
  let runOutcome = "done";
  let spinnerFrame = 0;
  let spinnerInterval;
  let deferredWrite;
  let lastCtx;

  function isTuiContext(ctx) {
    return ctx?.mode === "tui";
  }

  function clearDeferredWrite() {
    if (!deferredWrite) return;

    clearTimeout(deferredWrite);
    deferredWrite = undefined;
  }

  function writeTitle(ctx = lastCtx) {
    if (!isTuiContext(ctx)) return;

    lastCtx = ctx;
    ctx.ui.setTitle(formatTitle(pi, ctx, status, spinnerFrame));
  }

  function stopSpinner() {
    if (spinnerInterval) {
      clearInterval(spinnerInterval);
      spinnerInterval = undefined;
    }
    spinnerFrame = 0;
  }

  function startSpinner(ctx) {
    if (!isTuiContext(ctx) || spinnerInterval) return;

    spinnerFrame = 0;
    spinnerInterval = setInterval(() => {
      if (!isSpinningStatus(status)) {
        stopSpinner();
        return;
      }

      spinnerFrame = (spinnerFrame + 1) % SPINNER_FRAMES.length;
      writeTitle();
    }, SPINNER_INTERVAL_MS);
    spinnerInterval.unref?.();
  }

  function setStatus(nextStatus, ctx) {
    if (!isTuiContext(ctx)) return;

    clearDeferredWrite();
    status = nextStatus;
    lastCtx = ctx;

    if (isSpinningStatus(status)) {
      startSpinner(ctx);
    } else {
      stopSpinner();
    }

    writeTitle(ctx);
  }

  function scheduleWrite(ctx) {
    if (!isTuiContext(ctx)) return;

    clearDeferredWrite();
    deferredWrite = setTimeout(() => {
      deferredWrite = undefined;
      writeTitle(ctx);
    }, 0);
    deferredWrite.unref?.();
  }

  pi.on("session_start", async (_event, ctx) => {
    runOutcome = "done";
    setStatus("idle", ctx);
    // Pi writes its built-in title after extensions bind during startup.
    scheduleWrite(ctx);
  });

  pi.on("session_info_changed", async (_event, ctx) => {
    writeTitle(ctx);
  });

  pi.on("agent_start", async (_event, ctx) => {
    runOutcome = "done";
    setStatus("working", ctx);
  });

  pi.on("agent_end", async (event) => {
    runOutcome = getRunOutcome(event);
  });

  pi.on("agent_settled", async (_event, ctx) => {
    setStatus(runOutcome, ctx);
  });

  pi.on("session_shutdown", async () => {
    clearDeferredWrite();
    stopSpinner();
    lastCtx = undefined;
  });
}
