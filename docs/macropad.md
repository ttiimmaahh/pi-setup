# Voice-dictation macro pad

This repository includes a profile for a CH57x 3×2 macro keyboard with one rotary knob. The tested device reports USB vendor/product IDs `1189:8890` and uses the `ch57x-2` model in `ch57x-keyboard-tool`.

The hardware used to develop the profile is available here:

- [Amazon: 3×2 macro keyboard with rotary knob](https://amzn.to/4pMdCj6)

> **Affiliate disclosure:** This is an Amazon affiliate link. The repository owner may earn a commission from qualifying purchases at no additional cost to you.

## What `pi-setup` installs

Applying this repository copies:

- `config/macropad/coding-voice.yaml` to `~/.config/ch57x-keyboard-tool/coding-voice.yaml`
- `config/macropad/CHEATSHEET.md` to `~/.config/ch57x-keyboard-tool/CHEATSHEET.md`
- `config/extensions/macropad-help.ts` to `~/.pi/agent/extensions/macropad-help.ts`
- the required Pi shortcuts through `config/keybindings.json`

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

## Current voice behavior

The voice button sends `Ctrl+Shift+V` on all three hardware layers:

1. Tap once to begin Pi recording immediately.
2. Tap again to stop recording and run local transcription.
3. Review or edit the inserted text; auto-submit remains disabled.

This avoids using a literal Space as hold-to-talk, which can add a space to the editor and requires a delay to distinguish typing from a held key.

The toggle mapping is currently Pi-specific. It does not invoke Claude Code's native `/voice hold` mode.

## Physical orientation

Use the controller with the USB cable facing away from you and the knob on the right. See `~/.config/ch57x-keyboard-tool/CHEATSHEET.md` or `/macropad` for the full layout.
