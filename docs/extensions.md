# Pi extensions I use

This setup doubles as a curated index of public Pi extensions I use day to day. The config in [`../config/settings.json`](../config/settings.json) installs or references these packages where appropriate.

## My public Pi extensions

| Extension | Install/reference | What it does |
|---|---|---|
| [`@ttiimmaahh/pi-handoff`](https://github.com/ttiimmaahh/pi-handoff) | `npm:@ttiimmaahh/pi-handoff` | Proactive context handoff for Pi. At a context-usage threshold, it can write a structured session handoff and offer to reload it in a new session. |
| [`pi-sap-aicore`](https://github.com/ttiimmaahh/pi-sap-aicore) | `npm:pi-sap-aicore` | SAP AI Core provider for Pi, including orchestration and foundation model support. |
| [`pi-usage-bar`](https://github.com/ttiimmaahh/pi-usage-bar) | `npm:pi-usage-bar` | Footer/statusline plus local usage ledger for per-session and per-project token/cost attribution. |

## Other Pi packages in this setup

These are third-party or separately maintained packages currently referenced by `config/settings.json`:

| Package | Purpose in this setup |
|---|---|
| `npm:@plannotator/pi-extension` | Plannotator integration, with package skills disabled in this config. |
| `npm:pi-hermes-memory` | Persistent memory tooling. Runtime memory data is **not** stored in this repo. |
| `npm:pi-mcp-adapter` | MCP integration support. MCP auth/token state is **not** stored in this repo. |
| `npm:pi-lens` | LSP/AST/code-intelligence tools. |
| `npm:pi-context` | Context checkpoint/timeline/compaction tools. |
| `npm:pi-subagents` | Subagent orchestration tools. |
| `npm:pi-bar` | Pi UI/status enhancement package. |
| `npm:@juicesharp/rpiv-ask-user-question` | Structured question UI/tool support. |
| `npm:@juicesharp/rpiv-btw` | Additional Pi workflow/tooling package. |
| `npm:pi-web-access` | Web access/research tools. |

## Adding another extension here

1. Publish or make the extension repo public if you want others to use it.
2. Add its package spec to `config/settings.json` using an npm or git source when possible.
3. Add a row to this document.
4. Run:

   ```bash
   bash security-scan.sh
   ```
