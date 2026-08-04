# Voice-dictation macro pad

This repository includes a profile for a CH57x 3×2 macro keyboard with one rotary knob. The tested device reports USB vendor/product IDs `1189:8890` and uses the `ch57x-2` model in `ch57x-keyboard-tool`.

The hardware used to develop the profile is available here:

- [Amazon: 3×2 macro keyboard with rotary knob](https://amzn.to/4pMdCj6)

> **Affiliate disclosure:** This is an Amazon affiliate link. The repository owner may earn a commission from qualifying purchases at no additional cost to you.

## What `pi-setup` installs

Applying this repository copies:

- `config/macropad/coding-voice.yaml` to `~/.config/ch57x-keyboard-tool/coding-voice.yaml`
- the confirmed rollback profile and cheat sheet beside the installed CH57x profile
- `config/macropad/ghostty-f13-adapter.conf` into Ghostty's config and includes it idempotently on macOS/Linux
- `config/macropad/alacritty-f13-adapter.toml` into Alacritty and imports it idempotently on Windows/Linux/macOS
- `config/macropad/claude-keybindings.json` to `~/.claude/keybindings.json`
- `config/extensions/macropad-help.ts` and the Plannotator alias wrapper to Pi's extensions
- the required Pi shortcuts and voice setting through `config/keybindings.json` and `config/settings.json`

It does not upload anything to USB hardware automatically. Flashing remains an explicit step so applying a general Pi configuration cannot overwrite an attached controller unexpectedly.

## Install and flash

Install `ch57x-keyboard-tool` using the method appropriate for your platform, then validate the installed profile:

```bash
ch57x-keyboard-tool validate ~/.config/ch57x-keyboard-tool/coding-voice.yaml
```

Connect the controller and upload only after validation succeeds:

```bash
ch57x-keyboard-tool upload ~/.config/ch57x-keyboard-tool/coding-voice.yaml
```

Flashing replaces the mappings currently stored on the controller; the device cannot read its previous mappings back. Keep a copy of any profile you may want to restore.

Restart Pi or run `/reload`, then run `/macropad` to display the controller cheat sheet.

## Portable F13 Ghostty adapter

The production mapping is defined by:

- `config/macropad/coding-voice.yaml`
- `config/macropad/ghostty-f13-adapter.conf`
- `config/macropad/claude-keybindings.json`

All three stored mappings emit `F13` and `F16`–`F19` for Voice, Plan/mode, and the three knob events. The connected unit has no physical layer switch, so the profile does not depend on selecting a layer. `F14` and `F15` are skipped because macOS uses them for display-brightness controls before Ghostty can translate them. Ghostty 1.3+ consumes the remaining uncommon keys and emits explicit xterm sequences for documented modified navigation keys:

| Hardware key | Ghostty emits | Intended role |
| --- | --- | --- |
| `F13` | `Ctrl+Alt+Shift+Up` (`CSI 1;8A`) | Voice toggle |
| `F16` | `Ctrl+Alt+Shift+Down` (`CSI 1;8B`) | Plan / mode |
| `F17` | `Ctrl+Alt+Shift+Left` (`CSI 1;8D`) | Knob counterclockwise |
| `F18` | `Ctrl+Alt+Shift+Delete` (`CSI 3;8~`) | Knob press |
| `F19` | `Ctrl+Alt+Shift+Right` (`CSI 1;8C`) | Knob clockwise |

These application-facing keys avoid global F5–F9 behavior and stay within the documented modifier/special-key vocabulary of both Pi and Claude Code.

This adapter is Ghostty configuration, not a background daemon or agent script. It acts before tmux, SSH, Pi, or Claude Code receives the input. The measured Ctrl-only mapping is preserved separately as `config/macropad/coding-voice-ctrl-only-fallback.yaml` and can be reflashed if rollback is needed.

Install the adapter without flashing the controller:

```bash
mkdir -p ~/.config/ghostty
cp config/macropad/ghostty-f13-adapter.conf \
  ~/.config/ghostty/macropad-f13-adapter.conf
grep -Fqx 'config-file = macropad-f13-adapter.conf' ~/.config/ghostty/config || \
  printf '\n# pi-setup CH57x portable adapter\nconfig-file = macropad-f13-adapter.conf\n' \
    >> ~/.config/ghostty/config
ghostty +validate-config
```

Reload Ghostty's configuration with its `reload_config` action (Command+Shift+, by default on macOS). If a newly added `config-file` include is not applied to an existing process, start a fresh Ghostty instance; the isolated startup path is the acceptance test. Upload only after validation and explicit approval to replace the controller profile:

```bash
ch57x-keyboard-tool validate config/macropad/coding-voice.yaml
ch57x-keyboard-tool upload config/macropad/coding-voice.yaml
```

### Windows and Linux terminal adapters

Alacritty uses the same translation bytes on Windows and Linux. `npx ... pi-setup`, `apply.sh`, and `Apply.ps1` install `macropad-f13-adapter.toml` and add its import idempotently. This is the preferred zero-daemon Windows path because the existing Windows testing already uses Alacritty.

Linux Ghostty uses the same `ghostty-f13-adapter.conf` as macOS. Linux Alacritty is installed as an alternative. Neither adapter changes the application bindings or firmware.

For Windows Terminal, merge the `actions` and `keybindings` arrays from `config/macropad/windows-terminal-f13-adapter.json` into Terminal's `settings.json`. Windows Terminal officially accepts `F1`–`F24` keybindings and `sendInput` actions with `\u001b` ANSI sequences. Its JSON fragment mechanism cannot install global actions/keybindings, so this optional Terminal integration remains a settings merge rather than an unsafe automated JSONC rewrite.

The first test after upload is raw terminal capture of all five translated events. Pi and Claude bindings should be changed only after the five modified-navigation sequences are proven through the required terminal/Herdr path. To restore the previous Ctrl-only firmware:

```bash
ch57x-keyboard-tool validate config/macropad/coding-voice-ctrl-only-fallback.yaml
ch57x-keyboard-tool upload config/macropad/coding-voice-ctrl-only-fallback.yaml
```

## Current application behavior

The Voice button emits hardware `F13`; Ghostty translates it to `Ctrl+Alt+Shift+Up`, and Pi uses that chord for toggle dictation:

1. Tap once to begin Pi recording immediately.
2. Tap again to stop recording and run local transcription.
3. Review or edit the inserted text; auto-submit remains disabled.

Voice remains Pi-specific and does not invoke Claude Code's native `/voice` mode.

In Pi, turning the knob in the editor cycles effort/thinking. In Claude Chat, the closest exposed action is `chat:cycleMode`, which cycles permission modes. Claude exposes effort adjustment only inside the `ModelPicker` context through `modelPicker:decreaseEffort` and `modelPicker:increaseEffort`; it has no Chat-context effort-cycle action. The current selector mapping prioritizes model navigation and confirmation over effort adjustment.

## Physical orientation

Use the controller with the USB cable facing away from you and the knob on the right. See `~/.config/ch57x-keyboard-tool/CHEATSHEET.md` or `/macropad` for the full layout.
