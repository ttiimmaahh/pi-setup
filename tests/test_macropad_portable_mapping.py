"""Regression tests for the portable CH57x identity and adapter contract."""

import json
import re
import tomllib
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = REPO_ROOT / "config" / "macropad" / "coding-voice.yaml"
FALLBACK_PATH = REPO_ROOT / "config" / "macropad" / "coding-voice-ctrl-only-fallback.yaml"
ADAPTER_PATH = REPO_ROOT / "config" / "macropad" / "ghostty-f13-adapter.conf"
ALACRITTY_ADAPTER_PATH = REPO_ROOT / "config" / "macropad" / "alacritty-f13-adapter.toml"
WINDOWS_TERMINAL_ADAPTER_PATH = (
    REPO_ROOT / "config" / "macropad" / "windows-terminal-f13-adapter.json"
)
PI_KEYBINDINGS_PATH = REPO_ROOT / "config" / "keybindings.json"
PI_SETTINGS_PATH = REPO_ROOT / "config" / "settings.json"
PLANNOTATOR_WRAPPER_PATH = (
    REPO_ROOT / "config" / "extensions" / "macropad-plannotator-shortcut.ts"
)
CLAUDE_KEYBINDINGS_PATH = REPO_ROOT / "config" / "macropad" / "claude-keybindings.json"
APPLY_SH_PATH = REPO_ROOT / "apply.sh"
APPLY_PS1_PATH = REPO_ROOT / "Apply.ps1"

PORTABLE_BUTTON_ROWS = [
    ["f13", "f16"],
    ["enter", "escape"],
    ["ctrl-c", "ctrl-o"],
]
FALLBACK_BUTTON_ROWS = [
    ["ctrl-g", "ctrl-p"],
    ["enter", "escape"],
    ["ctrl-c", "ctrl-o"],
]
PORTABLE_KNOB = {"ccw": "f17", "press": "f18", "cw": "f19"}
FALLBACK_KNOB = {"ccw": "ctrl-r", "press": "ctrl-l", "cw": "ctrl-n"}
EXPECTED_ADAPTER = {
    "f13": "csi:1;8A",  # Ctrl+Alt+Shift+Up
    "f16": "csi:1;8B",  # Ctrl+Alt+Shift+Down
    "f17": "csi:1;8D",  # Ctrl+Alt+Shift+Left
    "f18": "csi:3;8~",  # Ctrl+Alt+Shift+Delete
    "f19": "csi:1;8C",  # Ctrl+Alt+Shift+Right
}
EXPECTED_TERMINAL_BYTES = {
    key: f"\x1b[{action.removeprefix('csi:')}" for key, action in EXPECTED_ADAPTER.items()
}


def parse_button_rows(text: str) -> list[list[str]]:
    return [
        [match.group(1), match.group(2)]
        for match in re.finditer(r'-\s*\["([^"]+)",\s*"([^"]+)"\]', text)
    ]


def parse_knobs(text: str) -> list[dict[str, str]]:
    return [
        {"ccw": match.group(1), "press": match.group(2), "cw": match.group(3)}
        for match in re.finditer(
            r'ccw:\s*"([^"]+)"\s*\n\s*press:\s*"([^"]+)"\s*\n\s*cw:\s*"([^"]+)"',
            text,
        )
    ]


def parse_adapter(text: str) -> dict[str, str]:
    return dict(re.findall(r"^keybind\s*=\s*(f\d+)=(\S+)\s*$", text, re.MULTILINE))


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise AssertionError(f"unable to read JSON from {path}: {error}") from error


class PortableProfileTests(unittest.TestCase):
    def setUp(self):
        text = PROFILE_PATH.read_text(encoding="utf-8")
        self.rows = parse_button_rows(text)
        self.knobs = parse_knobs(text)

    def test_all_stored_layers_use_the_portable_mapping(self):
        self.assertEqual(len(self.rows), 9)
        self.assertEqual(len(self.knobs), 3)
        for layer_start in (0, 3, 6):
            self.assertEqual(self.rows[layer_start : layer_start + 3], PORTABLE_BUTTON_ROWS)
        for knob in self.knobs:
            self.assertEqual(knob, PORTABLE_KNOB)

    def test_standard_buttons_keep_their_terminal_semantics(self):
        for layer_start in (0, 3, 6):
            self.assertEqual(self.rows[layer_start + 1], ["enter", "escape"])
            self.assertEqual(self.rows[layer_start + 2], ["ctrl-c", "ctrl-o"])

    def test_ctrl_only_rollback_profile_is_complete(self):
        text = FALLBACK_PATH.read_text(encoding="utf-8")
        rows = parse_button_rows(text)
        knobs = parse_knobs(text)
        self.assertEqual(len(rows), 9)
        self.assertEqual(len(knobs), 3)
        for layer_start in (0, 3, 6):
            self.assertEqual(rows[layer_start : layer_start + 3], FALLBACK_BUTTON_ROWS)
        for knob in knobs:
            self.assertEqual(knob, FALLBACK_KNOB)


class GhosttyAdapterTests(unittest.TestCase):
    def test_all_hardware_identities_have_one_translation(self):
        text = ADAPTER_PATH.read_text(encoding="utf-8")
        self.assertEqual(parse_adapter(text), EXPECTED_ADAPTER)

    def test_adapter_uses_no_modifier_chords_or_global_bindings(self):
        text = ADAPTER_PATH.read_text(encoding="utf-8")
        bindings = "\n".join(
            line for line in text.splitlines() if line.strip().startswith("keybind")
        )
        self.assertNotIn("global:", bindings)
        self.assertNotRegex(bindings, r"(?:ctrl|alt|shift|super|cmd)\+")


class CrossPlatformAdapterTests(unittest.TestCase):
    def test_alacritty_emits_the_same_bytes(self):
        config = tomllib.loads(ALACRITTY_ADAPTER_PATH.read_text(encoding="utf-8"))
        actual = {
            binding["key"].lower(): binding["chars"]
            for binding in config["keyboard"]["bindings"]
        }
        self.assertEqual(actual, EXPECTED_TERMINAL_BYTES)

    def test_windows_terminal_emits_the_same_bytes(self):
        config = read_json(WINDOWS_TERMINAL_ADAPTER_PATH)
        action_inputs = {
            action["id"]: action["command"]["input"] for action in config["actions"]
        }
        actual = {
            binding["keys"].lower(): action_inputs[binding["id"]]
            for binding in config["keybindings"]
        }
        self.assertEqual(actual, EXPECTED_TERMINAL_BYTES)


class PiApplicationMappingTests(unittest.TestCase):
    def test_knob_chords_are_bound_in_every_required_context(self):
        bindings = read_json(PI_KEYBINDINGS_PATH)
        self.assertIn("ctrl+alt+shift+left", bindings["tui.select.up"])
        self.assertIn("ctrl+alt+shift+right", bindings["tui.select.down"])
        self.assertIn("ctrl+alt+shift+delete", bindings["tui.select.confirm"])
        self.assertIn("ctrl+alt+shift+delete", bindings["app.model.select"])
        self.assertIn("ctrl+alt+shift+left", bindings["app.thinking.cycle"])
        self.assertIn("ctrl+alt+shift+right", bindings["app.thinking.cycle"])

    def test_voice_and_plannotator_use_adapter_chords(self):
        settings = read_json(PI_SETTINGS_PATH)
        self.assertEqual(settings["voice"]["toggleShortcut"], "ctrl+alt+shift+up")
        packages = [
            entry
            for entry in settings["packages"]
            if isinstance(entry, dict)
            and entry.get("source") == "npm:@plannotator/pi-extension"
        ]
        self.assertEqual(len(packages), 1)
        self.assertEqual(packages[0].get("extensions"), [])

        wrapper = PLANNOTATOR_WRAPPER_PATH.read_text(encoding="utf-8")
        self.assertRegex(wrapper, r'SOURCE_SHORTCUT\s*=\s*"ctrl\+alt\+p"')
        self.assertRegex(
            wrapper,
            r'MACROPAD_SHORTCUT\s*=\s*"ctrl\+alt\+shift\+down"',
        )
        self.assertIn("real.registerShortcut(shortcut, options)", wrapper)
        self.assertIn("real.registerShortcut(MACROPAD_SHORTCUT, options)", wrapper)


class ClaudeApplicationMappingTests(unittest.TestCase):
    def test_translated_keys_are_bound_by_context(self):
        config = read_json(CLAUDE_KEYBINDINGS_PATH)
        contexts = {entry["context"]: entry["bindings"] for entry in config["bindings"]}
        chat = contexts["Chat"]
        select = contexts["Select"]
        self.assertEqual(chat["ctrl+alt+shift+down"], "chat:cycleMode")
        self.assertEqual(chat["ctrl+alt+shift+left"], "chat:cycleMode")
        self.assertEqual(chat["ctrl+alt+shift+delete"], "chat:modelPicker")
        self.assertEqual(chat["ctrl+alt+shift+right"], "chat:cycleMode")
        self.assertEqual(select["ctrl+alt+shift+left"], "select:previous")
        self.assertEqual(select["ctrl+alt+shift+delete"], "select:accept")
        self.assertEqual(select["ctrl+alt+shift+right"], "select:next")


class ApplyScriptTests(unittest.TestCase):
    def test_bash_apply_installs_terminal_claude_and_rollback_files(self):
        script = APPLY_SH_PATH.read_text(encoding="utf-8")
        self.assertIn("coding-voice-ctrl-only-fallback.yaml", script)
        self.assertIn("ghostty-f13-adapter.conf", script)
        self.assertIn("config-file = macropad-f13-adapter.conf", script)
        self.assertIn("alacritty-f13-adapter.toml", script)
        self.assertIn("claude-keybindings.json", script)

    def test_powershell_apply_installs_claude_and_rollback_files(self):
        script = APPLY_PS1_PATH.read_text(encoding="utf-8")
        self.assertIn("coding-voice-ctrl-only-fallback.yaml", script)
        self.assertIn("alacritty-f13-adapter.toml", script)
        self.assertIn("claude-keybindings.json", script)


if __name__ == "__main__":
    unittest.main()
