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
| --- | --- | --- |
| Voice toggle | No configured voice action | Tap to start; tap again to stop and insert transcript |
| Plan / mode | Cycle Manual, Auto, Accept Edits, and Plan | Toggle Plannotator planning mode |
| Submit | Submit prompt | Submit prompt |
| Escape | Cancel or close | Cancel or close |
| Interrupt | Interrupt current operation | Interrupt current operation |
| Details | Toggle verbose transcript | Expand or collapse tool output |
| Turn knob normally | Cycle permission mode (effort is only adjustable inside Model Picker) | Cycle effort/thinking level |
| Press knob | Open model selector | Open model selector |
| Turn knob in selector | Highlight previous/next model | Highlight previous/next model |
| Press knob in selector | Confirm highlighted model | Confirm highlighted model |

## Voice behavior

- Dictation never submits automatically; review or edit the transcript first.
- The controller sends `F13`; the terminal adapter translates it to `Ctrl+Alt+Shift+Up` for Pi toggle mode.
- Pi uses local Parakeet TDT v3 through `@codexstar/pi-listen`.
- Claude Code's native `/voice` mode is not triggered by this Pi-specific button.

## Configuration

- Controller profile: `~/.config/ch57x-keyboard-tool/coding-voice.yaml`
- Controller rollback: `~/.config/ch57x-keyboard-tool/coding-voice-ctrl-only-fallback.yaml`
- Ghostty adapter: `~/.config/ghostty/macropad-f13-adapter.conf`
- Alacritty adapter: `~/.config/alacritty/macropad-f13-adapter.toml` or `%APPDATA%\alacritty\macropad-f13-adapter.toml`
- Windows Terminal snippet: `config/macropad/windows-terminal-f13-adapter.json`
- This cheat sheet: `~/.config/ch57x-keyboard-tool/CHEATSHEET.md`
- Claude bindings: `~/.claude/keybindings.json`
- Pi bindings: `~/.pi/agent/keybindings.json`
