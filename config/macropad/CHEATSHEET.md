# Macro Pad Cheat Sheet

```text
┌──────────────┬──────────────┬──────────────┐      ◉ KNOB
│ Voice toggle │ Plan / mode  │ Submit       │      Turn: navigate or cycle
├──────────────┼──────────────┼──────────────┤      Press: open / confirm model
│ Escape       │ Interrupt    │ Details      │
└──────────────┴──────────────┴──────────────┘
```

Physical orientation: USB cable away from you, knob on the right.

| Control | Claude Code | Pi |
|---|---|---|
| Voice toggle | No configured voice action | Tap to start; tap again to stop and insert transcript |
| Plan / mode | Cycle Manual, Auto, Accept Edits, and Plan | Toggle Plannotator planning mode |
| Submit | Submit prompt | Submit prompt |
| Escape | Cancel or close | Cancel or close |
| Interrupt | Interrupt current operation | Interrupt current operation |
| Details | Toggle verbose transcript | Expand or collapse tool output |
| Turn knob normally | Cycle permission mode | Cycle effort/thinking level |
| Press knob | Open model selector | Open model selector |
| Turn knob in selector | Highlight previous/next model | Highlight previous/next model |
| Press knob in selector | Confirm highlighted model | Confirm highlighted model |

## Voice behavior

- Dictation never submits automatically; review or edit the transcript first.
- The voice button now sends `Ctrl+Shift+V` for a Pi toggle-mode trial.
- Pi uses local Parakeet TDT v2 through `@codexstar/pi-listen`.
- Claude Code's native `/voice hold` is not triggered by this temporary mapping.

## Configuration

- Controller profile: `~/.config/ch57x-keyboard-tool/coding-voice.yaml`
- This cheat sheet: `~/.config/ch57x-keyboard-tool/CHEATSHEET.md`
- Claude bindings: `~/.claude/keybindings.json`
- Pi bindings: `~/.pi/agent/keybindings.json`
