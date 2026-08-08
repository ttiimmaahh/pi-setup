# Pi extensions I use

This setup doubles as a curated index of public Pi extensions I use day to day. The config in [`../config/settings.json`](../config/settings.json) installs packages, while authored or vendored loose extensions live under [`../config/extensions/`](../config/extensions/) and are copied into Pi's global extension directory by the apply scripts.

## My public Pi extensions

| Extension | Install/reference | What it does |
| --- | --- | --- |
| [`pi-sap-aicore`](https://github.com/ttiimmaahh/pi-sap-aicore) | `npm:pi-sap-aicore` | SAP AI Core provider for Pi, including orchestration and foundation model support. |
| [`pi-usage-bar`](https://github.com/ttiimmaahh/pi-usage-bar) | `npm:pi-usage-bar` | Footer/statusline plus local usage ledger for per-session and per-project token/cost attribution. |

## Other Pi packages in this setup

These are third-party or separately maintained packages currently referenced by `config/settings.json`:

| Package | Purpose in this setup |
| --- | --- |
| `npm:@plannotator/pi-extension` | Plannotator integration, with package skills disabled in this config. |
| `npm:pi-hermes-memory` | Persistent memory tooling. Runtime memory data is **not** stored in this repo. |
| `npm:pi-mcp-adapter` | MCP integration support. MCP auth/token state is **not** stored in this repo. |
| `npm:pi-lens` | LSP/AST/code-intelligence tools. |
| `npm:pi-subagents` | Subagent orchestration tools. |
| [`npm:pi-skill-toggle`](https://github.com/Whamp/pi-skill-toggle) | `/skills-toggle` TUI for keeping skills enabled, hiding them from model auto-invocation, or disabling them completely. |
| [`npm:@codexstar/pi-listen@7.2.2`](https://github.com/codexstar69/pi-listen) | Local voice dictation, configured to use Parakeet TDT v3. |
| `npm:@juicesharp/rpiv-ask-user-question` | Structured question UI/tool support. |
| `npm:@juicesharp/rpiv-btw` | Additional Pi workflow/tooling package. |
| `npm:pi-intercom` | Live supervisor decisions, progress updates, and grouped result delivery for pi-subagents. |
| `npm:pi-prompt-template-model` | Reusable prompt-template workflows with model/thinking/skill/subagent frontmatter. |
| `npm:@juicesharp/rpiv-todo` | Persistent model-managed task lists with dependency tracking and a live Pi overlay. |
| `npm:@mobrienv/pi-tidy-tools` | Compact, reason-first rendering for Pi's built-in tools, with configurable layouts and diff summaries. |

## Authored loose extensions

| Extension | Inspiration | What it does |
| --- | --- | --- |
| [`terminal-status-title`](../config/extensions/terminal-status-title.js) | Pi's [`titlebar-spinner.ts`](https://github.com/earendil-works/pi-mono/blob/main/packages/coding-agent/examples/extensions/titlebar-spinner.ts) example | Owns the terminal title in TUI mode so concurrent sessions expose their state at a glance: `○` idle, an animated braille spinner while working, `✓` completed, `✗` failed, and `■` stopped. It uses the session name when present, falls back to the working-directory basename, refreshes after `/name`, and waits for `agent_settled` so retries and queued follow-ups do not briefly appear complete. |

The title extension is intentionally TUI-only. This avoids emitting high-frequency
`setTitle` requests in RPC mode. Pi's title API has no getter or keyed ownership, so
this extension replaces—not temporarily stacks on—the built-in title while Pi runs.

## Vendored loose extensions

| Extension | Source | What it does |
| --- | --- | --- |
| [`web-tools`](../config/extensions/web-tools/) | [dmmulroy/.dotfiles at `f450e808`](https://github.com/dmmulroy/.dotfiles/tree/f450e80819c08bbede9fd71b35d01dacc43499a2/home/.pi/agent/extensions/web-tools) | Registers `webfetch` and `websearch`. The apply workflows install its locked runtime dependencies after copying it into `~/.pi/agent/extensions/web-tools/`. |

## Generated and local-only integrations

Installer-managed loose extensions, such as Herdr's `herdr-agent-state.ts`, are
intentionally not exported. Their owning installer should recreate and update them
on each machine. Local package paths are also excluded; see
[`local-packages.md`](local-packages.md).

## Adding another extension here

1. Publish or make the extension repo public if you want others to use it.
2. Add its package spec to `config/settings.json` using an npm or git source when
   possible.
3. Add a row to this document.
4. Run:

   ```bash
   bash security-scan.sh
   ```
