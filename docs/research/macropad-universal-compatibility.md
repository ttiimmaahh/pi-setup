# CH57x macropad universal-compatibility report

**Status:** macOS implementation physically verified; Windows/Linux terminal adapters remain to be exercised on their target hosts.  
**Scope:** the CH57x 3×2+knob profile used with Pi and Claude Code on macOS, Windows, Linux, terminal emulators, tmux, and SSH.  
**Repository state examined:** current checkout plus the unmerged snapshot at `~/Downloads/pi-setup-d287be4`.  
**Tool/application versions observed locally:** `ch57x-keyboard-tool` 1.7.0, Pi 0.83.0, Claude Code 2.1.220, Ghostty 1.3.1.

## Executive conclusion

The original macOS regression was a **confirmed configuration-generation mismatch**: raw Ghostty/Herdr PTY capture showed that the pad emitted the downloaded snapshot's Ctrl-only generation while the live applications expected the older `Ctrl+Shift`/`Ctrl+Alt` generation.

The implemented architecture now separates stable hardware identity from application meaning:

| Control | Firmware identity | Ghostty application chord |
| --- | --- | --- |
| Voice | `F13` | `Ctrl+Alt+Shift+Up` (`CSI 1;8A`) |
| Plan/mode | `F16` | `Ctrl+Alt+Shift+Down` (`CSI 1;8B`) |
| Knob CCW | `F17` | `Ctrl+Alt+Shift+Left` (`CSI 1;8D`) |
| Knob press | `F18` | `Ctrl+Alt+Shift+Delete` (`CSI 3;8~`) |
| Knob CW | `F19` | `Ctrl+Alt+Shift+Right` (`CSI 1;8C`) |

`F14` and `F15` are deliberately skipped because macOS consumes them as display-brightness controls before Ghostty receives them. Enter, Escape, Ctrl+C, and Ctrl+O retain their normal firmware meanings. The connected unit has no physical layer switch, so all three stored mappings are identical.

The complete macOS path was physically verified:

- all five firmware identities reached a fresh Ghostty instance and produced the exact expected xterm sequences;
- all Pi actions passed, including voice, Plannotator plan mode, thinking/selection navigation, model picker, and confirmation;
- all configured Claude actions passed, including mode cycling, model navigation, picker opening, and confirmation;
- Claude Code validates F6–F9 user bindings but does not dispatch them, so the final design uses only Claude's documented modifiers and special keys;
- Ghostty's native configuration works without a background daemon, but a newly added include may require a fresh Ghostty process instead of relying on hot reload.

The firmware is now host-neutral. Each terminal adapter must translate the same hardware identities into the same five documented application chords. This keeps Pi and Claude configuration identical across hosts while allowing Ghostty, Windows Terminal, Alacritty, or another terminal to implement the local HID-to-terminal boundary. A SwiftUI menu-bar utility remains a macOS fallback only if native terminal configuration later proves unreliable.

Do **not** copy only a firmware file between generations. Firmware, terminal adapter, Pi bindings/settings, Plannotator wrapper, Claude bindings, tests, and documentation form one atomic configuration contract.

## Evidence labels

- **Verified fact** means supported by an owning specification, project source, or official documentation cited here.
- **Repository observation** means directly observed in this checkout, installed configuration, git history, or the downloaded snapshot. It is evidence about this setup, not a general upstream guarantee.
- **Uncertainty** means physical or cross-product behavior was not measured here.
- **Recommendation** is a design judgment based on the verified facts and observations.

## What the two pre-migration generations configured

### Pre-migration checkout and live macOS generation

**Repository observation:** `config/macropad/coding-voice.yaml` repeats this mapping on all three layers:

| Physical control | Current firmware profile | Current Pi/extension expectation | Current Claude expectation |
| --- | --- | --- | --- |
| Voice | `Ctrl+Shift+V` | `Ctrl+Shift+V` | no configured voice action |
| Plan/mode | `Ctrl+Alt+P` | Plannotator directly registers `Ctrl+Alt+P` | live binding is `Ctrl+Meta+P` (`Meta` means Alt/Option in Claude) |
| Submit | `Enter` | `Enter` | `Enter` |
| Escape | `Escape` | `Escape` | `Escape` |
| Interrupt | `Ctrl+C` | `Ctrl+C` | `Ctrl+C` |
| Details | `Ctrl+O` | `Ctrl+O` | `Ctrl+O` |
| Knob CCW | `Ctrl+Shift+Left` | selection up / thinking cycle | mode cycle in Chat / previous in Select |
| Knob press | `Ctrl+Shift+M` | model select / selection confirm | model picker / selection accept |
| Knob CW | `Ctrl+Shift+Right` | selection down / thinking cycle | mode cycle in Chat / next in Select |

The plan/mode row is not a static macOS modifier mismatch. Claude defines `meta`, `alt`, `opt`, and `option` as the same modifier family—Alt on Windows/Linux and Option on macOS—while `cmd`, `command`, `super`, and `win` denote the GUI/Command family ([Claude keybindings](https://code.claude.com/docs/en/keybindings#modifiers)). CH57x likewise aliases `alt`/`opt` separately from its `cmd`/`win` GUI modifier ([CH57x actions](https://github.com/kriomant/ch57x-keyboard-tool/blob/996255ec6bdf852d92359f0116af72f5128c23d6/doc/actions.md), [CH57x key parser](https://raw.githubusercontent.com/kriomant/ch57x-keyboard-tool/996255ec6bdf852d92359f0116af72f5128c23d6/src/keyboard/mod.rs)). The binding can still fail if the terminal does not encode Option/Alt as Meta or another layer consumes it, but the firmware and Claude names describe the same modifier.

**Repository observation:** git commit `239b6ed` introduced the current profile wholesale. The available history does not contain an earlier macOS profile, so history cannot establish exactly what a previously working physical mapping emitted.

### Downloaded Windows-working generation

**Repository observation:** `~/Downloads/pi-setup-d287be4` is a source snapshot with no `.git` directory, so its commit ancestry cannot be independently established. Its files are internally consistent and materially differ from the current checkout:

| Physical control | Snapshot firmware | Snapshot companion change |
| --- | --- | --- |
| Voice | `Ctrl+G` | voice `toggleShortcut` becomes `ctrl+g` |
| Plan/mode | `Ctrl+P` | wrapper converts Plannotator's `ctrl+alt+p` registration to `ctrl+p` |
| Knob CCW | `Ctrl+R` | Pi selection up and thinking cycle use `ctrl+r` |
| Knob press | `Ctrl+L` | Pi model select and selection confirm use `ctrl+l` |
| Knob CW | `Ctrl+N` | Pi selection down and thinking cycle use `ctrl+n` |
| Submit / Escape / Interrupt / Details | unchanged | `Enter`, `Escape`, `Ctrl+C`, `Ctrl+O` remain |

The snapshot also:

- clears Pi actions that otherwise use `Ctrl+G`, `Ctrl+P`, `Ctrl+R`, or `Ctrl+N`;
- disables direct autoload of the pinned Plannotator extension and loads it through `config/extensions/macropad-plannotator-shortcut.ts`;
- tests the firmware, Pi bindings, voice setting, package setting, and wrapper as one synchronized contract in `tests/test_macropad_portable_mapping.py`;
- describes the profile as Pi-specific rather than installing matching Claude Code bindings.

**Repository observation:** the snapshot documentation records that `Ctrl+Alt+letter` produced no PTY input in Windows Alacritty 0.17.0 through Herdr—even from a normal keyboard—and that earlier shifted-letter tests lost distinctions in Windows Terminal. Those are useful first-party test notes from this setup, but they were not reproduced during this macOS investigation and should not be generalized to every Windows terminal configuration.

This is stronger evidence than a standalone YAML file: it shows that the Ctrl-only mapping was intentionally designed as a coordinated migration, not as a drop-in replacement for the current firmware profile.

### Measured live macOS output

**Repository observation:** before migration, a raw-mode capture in Ghostty under Herdr measured the controller's effective mapping as follows:

| Physical control | Captured hex | Decoded key |
| --- | ---: | --- |
| Voice | `07` | `Ctrl+G` |
| Plan/mode | `10` | `Ctrl+P` |
| Submit | `0d` | `Enter` / carriage return |
| Escape | `1b` | `Escape` |
| Interrupt | `03` | `Ctrl+C` |
| Details | `0f` | `Ctrl+O` |
| Knob CCW | `12` | `Ctrl+R` |
| Knob press | `0c` | `Ctrl+L` |
| Knob CW | `0e` | `Ctrl+N` |

This exactly matched the downloaded Ctrl-only profile at the terminal boundary. The unit has no physical layer control; after migration all three stored slots were programmed identically.

### Confirmed immediate failure mapping

| Pad emits | macOS configuration listens for | Immediate result |
| --- | --- | --- |
| `Ctrl+G` | voice: `Ctrl+Shift+V` | voice does not toggle; Pi may perform its ordinary `Ctrl+G` action instead |
| `Ctrl+P` | plan: `Ctrl+Alt+P`; Claude mode: `Ctrl+Meta+P` | neither custom plan/mode binding matches |
| `Ctrl+R` / `Ctrl+N` | knob: `Ctrl+Shift+Left` / `Ctrl+Shift+Right` | knob rotation does not drive the configured custom actions |
| `Ctrl+L` | knob press: `Ctrl+Shift+M` for confirmation; Pi also accepts `Ctrl+L` for opening model select | opening Pi's model selector may work, but pressing again need not confirm it |
| `Enter`, `Escape`, `Ctrl+C`, `Ctrl+O` | same keys | these controls can continue to work, which can make the failure look partial or application-specific |

**Recommendation:** restore generation consistency before debugging terminal modifier behavior. Either reflash the current YAML, or merge/apply the complete Ctrl-only generation. The former restores the old macOS setup but reintroduces known Windows terminal problems; the latter restores the tested Windows behavior but retains the Ctrl-only design's application collisions and Pi-specific scope. Neither should be mistaken for the long-term universal design.

## The five interpretation layers

A useful model is:

1. **USB HID usage and modifier bits.** The device reports keyboard usages; it does not report “Pi action,” “paste,” or “Command.” The USB HID Usage Tables define keyboard usages including `F1`–`F24` and separate modifier usages ([USB HID Usage Tables 1.5, Keyboard/Keypad page](https://usb.org/sites/default/files/hut1_5.pdf)). CH57x 1.7.0 exposes `F13`–`F24`, decimal custom HID codes, multi-modifier chords, and left/right Ctrl, Shift, Alt, and GUI modifiers ([actions](https://github.com/kriomant/ch57x-keyboard-tool/blob/996255ec6bdf852d92359f0116af72f5128c23d6/doc/actions.md), [parser source](https://raw.githubusercontent.com/kriomant/ch57x-keyboard-tool/996255ec6bdf852d92359f0116af72f5128c23d6/src/keyboard/mod.rs), [device encoder](https://raw.githubusercontent.com/kriomant/ch57x-keyboard-tool/996255ec6bdf852d92359f0116af72f5128c23d6/src/keyboard/k8890.rs)).
2. **Host OS interpretation.** The host maps GUI to its platform convention and may reserve system shortcuts. On macOS, user-facing shortcuts distinguish Command, Control, Option, and Shift; Option-as-Meta is a separate terminal setting, not an alias for Command ([Apple Terminal shortcuts](https://support.apple.com/guide/terminal/keyboard-shortcuts-trmlshtcts/mac), [Apple Terminal keyboard profile settings](https://support.apple.com/guide/terminal/change-profiles-keyboard-settings-trmlkbrd/mac)).
3. **Terminal interception and encoding.** A terminal may execute a local action such as Paste, or encode the key into bytes. Legacy terminal input cannot represent all modern modifier combinations distinctly; enhanced protocols add explicit key/modifier reporting ([kitty keyboard protocol](https://sw.kovidgoyal.net/kitty/keyboard-protocol/), [xterm control sequences](https://invisible-island.net/xterm/ctlseqs/ctlseqs.html)).
4. **Multiplexer and remoting.** tmux receives terminal bytes, not USB reports, and documents the resulting modifier limitations; its extended-keys support depends on terminal capability and configuration ([tmux modifier keys](https://github.com/tmux/tmux/wiki/Modifier-Keys), [tmux manual](https://raw.githubusercontent.com/tmux/tmux/master/tmux.1)). SSH carries the resulting terminal data in channel data and communicates terminal modes; it does not reconstruct a lost HID modifier ([RFC 4254, sections 6.2–6.5](https://www.rfc-editor.org/rfc/rfc4254.html)).
5. **Application parsing and binding.** Pi or Claude Code parses the received sequence and applies a context-specific binding. Pi documents modifiers and named keys through `F1`–`F12`, not `F13`–`F24` ([Pi keybindings](https://github.com/earendil-works/pi/blob/845d6ff1f6643aba440341cce877ce1c43ebbc39/packages/coding-agent/docs/keybindings.md)); its terminal parser shows the sequences it recognizes ([Pi keys](https://raw.githubusercontent.com/earendil-works/pi/845d6ff1f6643aba440341cce877ce1c43ebbc39/packages/tui/src/keys.ts), [Pi terminal](https://raw.githubusercontent.com/earendil-works/pi/845d6ff1f6643aba440341cce877ce1c43ebbc39/packages/tui/src/terminal.ts)). Claude Code likewise has context-scoped, user-configurable keybindings and documents terminal-specific setup limitations ([Claude keybindings](https://code.claude.com/docs/en/keybindings), [terminal configuration](https://code.claude.com/docs/en/terminal-config), [interactive mode](https://code.claude.com/docs/en/interactive-mode)).

A later layer cannot recover information consumed or collapsed by an earlier one.

## Collision and failure analysis of the current controls

| Current signal | Principal failure modes | Assessment |
| --- | --- | --- |
| `Ctrl+Shift+V` | GNOME Terminal and WezTerm document it as Paste; Windows Terminal commonly binds Paste as an action; a legacy path may not preserve Shift distinctly from `Ctrl+V` | **Unsafe as a universal application key** ([GNOME](https://help.gnome.org/users/gnome-terminal/stable/adv-keyboard-shortcuts.html.en), [WezTerm defaults](https://wezterm.org/config/default-keys.html), [Windows Terminal actions](https://learn.microsoft.com/en-us/windows/terminal/customize-settings/actions), [kitty protocol](https://sw.kovidgoyal.net/kitty/keyboard-protocol/)) |
| `Ctrl+Alt+P` | Alt/Option must survive OS and terminal handling; Apple Terminal exposes Option-as-Meta as profile configuration; Claude's `Meta` spelling means Alt/Option, so the application names align but transport is configuration-dependent | **Semantically aligned in Claude, not universally delivered by terminals** ([Apple profile settings](https://support.apple.com/guide/terminal/change-profiles-keyboard-settings-trmlkbrd/mac), [Claude keybindings](https://code.claude.com/docs/en/keybindings#modifiers), [Claude terminal config](https://code.claude.com/docs/en/terminal-config)) |
| `Enter` | Contextually submits, confirms, inserts, or activates; `Ctrl+M` may be the same legacy carriage-return control | **Portable transport, inherently contextual meaning** ([kitty protocol](https://sw.kovidgoyal.net/kitty/keyboard-protocol/), [Claude interactive mode](https://code.claude.com/docs/en/interactive-mode)) |
| `Escape` | Also begins many terminal escape sequences; timing can matter through terminal/multiplexer paths | **Portable as a key, contextual and sequence-sensitive** ([xterm sequences](https://invisible-island.net/xterm/ctlseqs/ctlseqs.html), [tmux manual](https://raw.githubusercontent.com/tmux/tmux/master/tmux.1)) |
| `Ctrl+C` | Conventional interrupt/control character; shell terminal modes can generate an interrupt, while full-screen apps may handle it themselves | **Intentionally semantic, not an unused identity** ([RFC 4254 terminal modes](https://www.rfc-editor.org/rfc/rfc4254.html), [Claude interactive mode](https://code.claude.com/docs/en/interactive-mode)) |
| `Ctrl+O` | A legacy C0 control byte with application-specific meaning | **Reliable transport in many paths, collision-prone identity** ([xterm sequences](https://invisible-island.net/xterm/ctlseqs/ctlseqs.html)) |
| `Ctrl+Shift+Left/Right` | Often expressible as modified cursor sequences, but exact encoding/capability must survive the terminal and tmux; terminals may bind modified arrows locally | **Better than shifted letters, still capability/configuration dependent** ([xterm sequences](https://invisible-island.net/xterm/ctlseqs/ctlseqs.html), [tmux modifier keys](https://github.com/tmux/tmux/wiki/Modifier-Keys)) |
| `Ctrl+Shift+M` | Konsole documents this as its Show Menubar shortcut; without distinct Shift reporting it can collapse toward `Ctrl+M`, which is carriage return/Enter | **Especially unsafe** ([Konsole command reference](https://docs.kde.org/trunk_kf6/en/konsole/konsole/commandreference.html), [kitty protocol](https://sw.kovidgoyal.net/kitty/keyboard-protocol/)) |

The downloaded Ctrl-only signals solve modifier *transport* but consume scarce control characters:

| Ctrl-only signal | Legacy byte | Local cost observed in the snapshot |
| --- | ---: | --- |
| `Ctrl+G` | `07` | Pi's existing action must be cleared; voice becomes Pi-specific |
| `Ctrl+P` | `10` | Pi's model-cycle action must be cleared; Plannotator requires a wrapper |
| `Ctrl+R` | `12` | Pi resume-picker behavior must be cleared/reinterpreted |
| `Ctrl+L` | `0c` | conventionally redraw/clear in terminal software; made model/confirm here |
| `Ctrl+N` | `0e` | Pi resume-picker behavior must be cleared/reinterpreted |

This design is defensible for a controlled Pi environment, but calling it universal would confuse reliable one-byte transport with globally collision-free meaning.

## Terminal and transport matrix

Legend: **Good candidate** means the architecture is supported in principle, not physically certified here; **configure** means a terminal/host mapping is required; **risk** means a documented local shortcut or legacy ambiguity exists.

| Environment | Old modified chords | Ctrl-only snapshot | Bare `F5`–`F9` | `F13`–`F21` identity |
| --- | --- | --- | --- | --- |
| Apple Terminal | Option/Meta setup and legacy modifier ambiguity; `Ctrl+Alt+P` is not Command | likely transported, but C0/app collisions remain | **Good candidate**; verify the active profile's function-key mappings | **Configure** its keyboard profile or an OS remapper to send supported app keys ([settings](https://support.apple.com/guide/terminal/change-profiles-keyboard-settings-trmlkbrd/mac)) |
| iTerm2 | key mappings and protocol mode can alter delivery; must test | likely transported, with C0/app collisions | **Good candidate**; verify no profile key mapping consumes it | **Configure** an iTerm2 key mapping or OS remapper; do not assume Pi accepts raw F13+ |
| WezTerm | `Ctrl+Shift+V` is a documented default Paste binding | likely transported after removing conflicting bindings | **Good candidate**; inspect defaults | **Configure** `SendKey`/`SendString` or an OS remapper ([keys](https://wezterm.org/config/keys.html), [defaults](https://wezterm.org/config/default-keys.html), [SendKey](https://wezterm.org/config/lua/keyassignment/SendKey.html), [SendString](https://wezterm.org/config/lua/keyassignment/SendString.html)) |
| Windows Terminal | terminal actions may consume chords; legacy input cannot be assumed to preserve shifted letters | likely transported after action conflicts are resolved | **Good candidate**; bind applications explicitly | **Configure** a Terminal action/remapper and unbind conflicts ([actions](https://learn.microsoft.com/en-us/windows/terminal/customize-settings/actions), [interaction](https://learn.microsoft.com/en-us/windows/terminal/customize-settings/interaction)) |
| GNOME Terminal | `Ctrl+Shift+V` is Paste | likely transported, with C0/app collisions | **Good candidate**; verify desktop/terminal shortcuts | **Configure** a desktop or terminal remapper ([shortcuts](https://help.gnome.org/users/gnome-terminal/stable/adv-keyboard-shortcuts.html.en)) |
| Konsole | `Ctrl+Shift+M` is Show Menubar; other terminal shortcuts can intercept | likely transported, with C0/app collisions | **Good candidate**; verify the active key-binding scheme | **Configure** the key-binding scheme or OS remapper ([key bindings](https://docs.kde.org/trunk_kf6/en/konsole/konsole/key-bindings.html), [commands](https://docs.kde.org/trunk_kf6/en/konsole/konsole/commandreference.html)) |
| tmux | only receives what the outer terminal encoded; extended keys require compatible configuration | one-byte C0 controls are robust, but tmux/apps still assign meanings | standard function-key sequences are a good legacy candidate; test nested contexts | raw F13+ cannot be assumed to match Pi; translate before or at the outer terminal ([modifier keys](https://github.com/tmux/tmux/wiki/Modifier-Keys), [manual](https://raw.githubusercontent.com/tmux/tmux/master/tmux.1)) |
| SSH | cannot restore an intercepted/collapsed modifier | transports the bytes sent by the local terminal | transports terminal function-key sequences; remote `$TERM`/app must agree | translate locally before SSH unless the entire remote stack explicitly supports the chosen sequence ([RFC 4254](https://www.rfc-editor.org/rfc/rfc4254.html)) |

## Pre-migration application matrix

| Application | Old generation | Ctrl-only generation | Bare `F5`–`F9` | F13+ direct |
| --- | --- | --- | --- | --- |
| Pi | current repo bindings align except for terminal losses | works only with the snapshot's companion keybindings, settings, and wrapper | **Recommended direct binding:** Pi documents `F1`–`F12` | **Not a documented direct binding:** translate to `F1`–`F12` or another supported key ([Pi keybindings](https://github.com/earendil-works/pi/blob/845d6ff1f6643aba440341cce877ce1c43ebbc39/packages/coding-agent/docs/keybindings.md)) |
| Claude Code | live knob bindings aligned; plan firmware Alt matched Claude's Meta/Alt family if the terminal delivered it | snapshot intentionally installed no matching Claude bindings | **Rejected after test:** bindings loaded without warnings but actions did not dispatch | use host/terminal translation to a documented Claude binding ([keybindings](https://code.claude.com/docs/en/keybindings)) |
| Shell/readline-like input | several chords may be intercepted or collapse | each Ctrl letter already has terminal/editor semantics | F-key sequence may be unbound or have an editor function; less destructive than arbitrary C0 reuse but still verify | usually requires mapping before the shell/application |

Claude voice is a separate application feature with its own documented interaction and terminal requirements; this repository's Pi voice toggle should not be described as invoking Claude voice ([Claude voice dictation](https://code.claude.com/docs/en/voice-dictation)).

## Architecture options by operational tradeoff

### Bare F5–F9 plus explicit application bindings

**Rejected for the shared baseline after physical testing.** Pi accepted the bindings, but Claude Code 2.1.220 loaded F6–F9 user bindings with zero warnings and did not dispatch them. Global F5–F9 behavior would also create avoidable application collisions.

Suggested mapping for the five custom controls:

| Control | Firmware identity | Pi | Claude Code |
| --- | --- | --- | --- |
| Voice | `F5` | Pi voice toggle | optional Claude voice/custom action, or deliberately unbound |
| Plan/mode | `F6` | Plannotator toggle via a small binding bridge if required | cycle/toggle configured mode |
| Knob CCW | `F7` | selection up / thinking cycle | mode cycle in Chat / previous in Select |
| Knob press | `F8` | model selector / confirm | model picker / accept |
| Knob CW | `F9` | selection down / thinking cycle | mode cycle in Chat / next in Select |

Keep `Enter`, `Escape`, `Ctrl+C`, and `Ctrl+O` only if their ordinary semantics are intentionally desired. Otherwise give all nine controls distinct identities and translate them.

Why this was considered as a no-remapper prototype:

- no Ctrl/Shift/Alt/GUI combination must survive;
- F5–F9 are inside the keyboard HID table and Pi's documented F-key range;
- the terminal can encode them using established function-key sequences;
- Pi can own the final contextual meaning; Claude can do so only if the exact parser accepts the keys and its available actions match the intended behavior. Neither app currently documents a reverse cycle action, so opposite knob directions both cycle in the same direction outside selectors.

Observed result:

- CH57x and Pi accepted the function keys;
- Claude loaded the configuration without warnings but ignored the F-key actions;
- ordinary F-key meanings remain visible outside terminal-scoped adapters.

### F13 identities plus host-local terminal translation

**Implemented.** Collision avoidance and stable physical identities justify a small terminal configuration installed by the repository.

CH57x and HID support these usages, but Pi's documented key names stop at F12. Treat F13–F21 as *device identities*, not as guaranteed end-to-end terminal keys. Translate them near the host boundary:

- macOS: a maintained OS remapper or terminal keyboard profile;
- Windows: a maintained OS remapper or Windows Terminal action where adequate;
- Linux: desktop/input remapper or terminal configuration;
- WezTerm: explicit key assignment that sends the app-supported key/sequence.

Translate before tmux/SSH where possible. That makes remoting carry an ordinary, known terminal sequence and avoids requiring every remote Pi version and `$TERM` database to understand F13+.

The verified macOS adapter uses Ghostty-native bindings and no daemon. It maps `F13`, `F16`, `F17`, `F18`, and `F19` to explicit xterm sequences for `Ctrl+Alt+Shift+Up`, Down, Left, Delete, and Right. Windows/Linux adapters should emit those same sequences so Pi and Claude files remain identical.

Costs:

- one terminal configuration per host/terminal family;
- a fresh terminal process may be required after first installing an include;
- troubleshooting must record both the HID identity and translated output.

### App/OS-specific hardware layers

**Unavailable on this physical unit.** The controller exposes three stored mapping slots but has no physical layer switch. All three are programmed identically so behavior cannot depend on an inaccessible active layer.

### Ctrl-only snapshot

**Recommended only for:** a controlled Pi-first environment where the cleared defaults and wrapper are acceptable.

It is robust through legacy terminal transport because each custom chord reduces to one C0 byte, but it reassigns globally meaningful control characters, requires a Plannotator wrapper, removes Pi defaults, and does not configure Claude Code. It is a targeted Windows/Pi compatibility design, not a universal one.

### Existing Ctrl+Shift/Ctrl+Alt direct chords

**Not recommended as the portable baseline.** They have documented terminal-owned collisions, lossy legacy representations, and Alt/Option terminal-configuration dependencies. They may also be involved in a configuration-generation mismatch if the downloaded Ctrl-only profile is what the pad currently emits.

## Implemented migration

1. Captured and preserved the original Ctrl-only generation as `coding-voice-ctrl-only-fallback.yaml`.
2. Programmed every stored mapping slot with the same host-neutral identities: `F13` and `F16`–`F19`.
3. Skipped macOS-reserved `F14`/`F15` after physical tests showed they were consumed before Ghostty.
4. Rejected F5–F9 application bindings after Claude loaded but did not dispatch them.
5. Installed Ghostty translation to documented modified-navigation chords shared by Pi and Claude.
6. Added synchronized regression tests covering firmware, terminal adapter, Pi, Claude, voice, Plannotator, installers, and rollback artifacts.

## Verification protocol

Record OS, terminal and version, local/SSH, tmux version, `$TERM` outside and inside tmux, application/version, and expected hardware identity for every run.

### A. Physical HID stage

1. Connect the pad directly and confirm USB ID/model.
2. Capture each button, knob direction, and knob press with an OS-level HID/event viewer.
3. Record key usage and modifier bits; do not record only the rendered character.
4. Because this unit has no layer control, program all three stored mapping slots identically.
5. Compare with the chosen YAML. A schema validation proves only that the tool accepts the profile, not that this physical device currently contains it.

### B. Raw terminal stage

From a plain shell, outside tmux, put the terminal in raw mode and print received bytes. For example:

```bash
python3 - <<'PY'
import os, select, sys, termios, tty
fd = sys.stdin.fileno()
old = termios.tcgetattr(fd)
try:
    tty.setraw(fd)
    print("Press one control within 5 seconds...", end="\r\n")
    ready, _, _ = select.select([fd], [], [], 5)
    data = os.read(fd, 64) if ready else b""
finally:
    termios.tcsetattr(fd, termios.TCSADRAIN, old)
print("bytes:", data.hex() or "<no input>", end="\r\n")
PY
```

Test both the physical pad and the nominally identical normal-keyboard input. `<no input>` means an earlier layer consumed the key. Equal bytes from two intended identities mean the terminal path collapsed them.

### C. tmux and SSH stages

Repeat the raw capture:

1. inside local tmux;
2. over SSH without tmux;
3. over SSH inside remote tmux;
4. if relevant, through nested local and remote multiplexers.

Compare bytes at every boundary. Do not attribute an outer-terminal loss to SSH or Pi.

### D. Application stage

For Pi and Claude Code separately:

1. verify the applied keybinding file, not only the repository copy;
2. test in the main editor, selector/model picker, running-operation state, and any resume/scoped-model context;
3. verify press, repeat, and rapid knob rotation;
4. verify all stored mapping slots are identical because this unit has no layer control;
5. verify ordinary keyboard access to any default action displaced by the design.

### E. Pass criteria

A design passes a target path only when:

- all nine physical events are distinct at the intended interpretation boundary;
- no required terminal action consumes them;
- tmux/SSH preserve the intended sequence;
- Pi and Claude perform the documented action in every required context;
- displaced defaults have explicit alternatives;
- results survive restart and configuration re-application.

## Remaining uncertainties

- Windows and Linux terminal adapters have not yet been physically exercised on their target hosts. They must emit the same five xterm sequences verified in Ghostty.
- tmux, SSH, and nested remote tmux acceptance still needs to be repeated on each required host path.
- The downloaded snapshot is not a git checkout, so its exact ancestry remains unknown even though its Ctrl-only output was measured and preserved as rollback firmware.
- Terminal configurations are user-modifiable. Setup re-application and a fresh-terminal smoke test remain part of acceptance.
- Pi publicly documents F1–F12 only. The production design deliberately translates F13+ before Pi rather than relying on unsupported raw handling.
- The locally installed `@codexstar/pi-listen` reports version 7.2.2, but no matching public upstream git tag was found during the bounded research. Voice-binding statements here are repository observations.

## Bottom line

The macOS solution is physically verified end to end: **F13/F16–F19 stable firmware identities, Ghostty-native translation to documented modified-navigation sequences, and synchronized Pi/Claude bindings**. It requires no macOS daemon and avoids global F-key or C0-control collisions. The same firmware and application bindings should remain unchanged across computers; only the terminal adapter is host-specific. Windows/Linux adapters and remote terminal paths are the remaining acceptance work.
