import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PortableApplyTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.workdir = Path(self.tempdir.name)
        self.bin_dir = self.workdir / "bin"
        self.bin_dir.mkdir()
        self.npm_log = self.workdir / "npm-args.txt"
        self.pi_lens_config = self.workdir / "pi-lens/config.json"
        self.home = self.workdir / "home"
        self.home.mkdir()

    def write_command(self, name: str, body: str) -> Path:
        command = self.bin_dir / name
        command.write_text(f"#!/bin/sh\n{body}\n", encoding="utf-8")
        command.chmod(0o755)
        return command

    def environment(self) -> dict[str, str]:
        env = os.environ.copy()
        env["PATH"] = f"{self.bin_dir}{os.pathsep}{env['PATH']}"
        env["NPM_LOG"] = str(self.npm_log)
        env["PI_LENS_CONFIG_PATH"] = str(self.pi_lens_config)
        env["HOME"] = str(self.home)
        env["XDG_CONFIG_HOME"] = str(self.home / ".config")
        return env

    def read_json(self, path: Path):
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            self.fail(f"{path} is unreadable: {error}")

    def install_successful_fake_npm(self) -> None:
        self.write_command("npm", 'printf "%s\\n" "$@" > "$NPM_LOG"')

    def assert_npm_ci_arguments(self, extension_dir: Path) -> None:
        self.assertEqual(
            self.npm_log.read_text(encoding="utf-8").splitlines(),
            [
                "ci",
                "--omit=dev",
                "--omit=peer",
                "--ignore-scripts",
                "--prefix",
                str(extension_dir),
            ],
        )

    def test_node_apply_copies_web_tools_and_installs_dependencies(self):
        self.install_successful_fake_npm()
        target = self.workdir / "target with spaces"

        result = subprocess.run(
            ["node", str(ROOT / "bin/pi-setup.js"), "--target", str(target), "--no-update"],
            cwd=ROOT,
            env=self.environment(),
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        extension_dir = target / "extensions/web-tools"
        self.assertTrue((extension_dir / "index.ts").is_file())
        self.assertTrue((extension_dir / "package-lock.json").is_file())
        self.assertTrue((target / "extensions/terminal-status-title.js").is_file())
        settings = self.read_json(target / "settings.json")
        self.assertNotIn("npm:pi-web-access", settings["packages"])
        self.assertEqual(self.read_json(self.pi_lens_config), {"format": {"enabled": False}})
        review_skill = target / "skills/review-global-agents"
        self.assertTrue((review_skill / "SKILL.md").is_file())
        self.assertTrue((review_skill / "references/AGENTS.example.md").is_file())
        self.assertTrue((review_skill / "references/ORCHESTRATION_REVIEW.md").is_file())
        self.assert_npm_ci_arguments(extension_dir)
        self.assertTrue((self.home / ".config/ch57x-keyboard-tool/coding-voice.yaml").is_file())
        self.assertTrue(
            (self.home / ".config/ch57x-keyboard-tool/coding-voice-ctrl-only-fallback.yaml").is_file()
        )
        ghostty_config = self.home / ".config/ghostty/config"
        self.assertIn(
            "config-file = macropad-f13-adapter.conf",
            ghostty_config.read_text(encoding="utf-8"),
        )
        self.assertTrue((self.home / ".config/ghostty/macropad-f13-adapter.conf").is_file())
        alacritty_config = self.home / ".config/alacritty/alacritty.toml"
        self.assertTrue((self.home / ".config/alacritty/macropad-f13-adapter.toml").is_file())
        self.assertIn(
            'import = ["macropad-f13-adapter.toml"]',
            alacritty_config.read_text(encoding="utf-8"),
        )
        self.assertTrue((self.home / ".claude/keybindings.json").is_file())

    def test_node_dry_run_does_not_write_or_invoke_npm(self):
        self.install_successful_fake_npm()
        target = self.workdir / "dry-run-target"

        result = subprocess.run(
            ["node", str(ROOT / "bin/pi-setup.js"), "--target", str(target), "--dry-run", "--no-update"],
            cwd=ROOT,
            env=self.environment(),
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(target.exists())
        self.assertFalse(self.pi_lens_config.exists())
        self.assertFalse(self.npm_log.exists())
        self.assertFalse((self.home / ".config/ghostty/config").exists())
        self.assertFalse((self.home / ".config/alacritty/alacritty.toml").exists())
        self.assertFalse((self.home / ".claude/keybindings.json").exists())
        self.assertIn("install Pi Lens config", result.stdout)
        self.assertIn("install extensions/web-tools dependencies", result.stdout)

    def test_node_apply_fails_when_dependency_install_fails(self):
        self.write_command("npm", "exit 23")
        target = self.workdir / "failed-target"

        result = subprocess.run(
            ["node", str(ROOT / "bin/pi-setup.js"), "--target", str(target), "--no-update"],
            cwd=ROOT,
            env=self.environment(),
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("failed to install the web-tools extension dependencies", result.stderr)

    def test_shell_apply_installs_web_tools_dependencies(self):
        self.install_successful_fake_npm()
        self.write_command("pi", "exit 1")
        target = self.workdir / "shell target with spaces"
        env = self.environment()
        env["PI_CODING_AGENT_DIR"] = str(target)

        result = subprocess.run(
            ["bash", str(ROOT / "apply.sh")],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        extension_dir = target / "extensions/web-tools"
        self.assertTrue((extension_dir / "index.ts").is_file())
        self.assertEqual(self.read_json(self.pi_lens_config), {"format": {"enabled": False}})
        self.assert_npm_ci_arguments(extension_dir)
        self.assertTrue((self.home / ".config/ghostty/macropad-f13-adapter.conf").is_file())
        self.assertTrue((self.home / ".config/alacritty/macropad-f13-adapter.toml").is_file())
        self.assertTrue((self.home / ".claude/keybindings.json").is_file())

    def test_alacritty_installer_preserves_config_and_is_idempotent(self):
        config_dir = self.workdir / "alacritty"
        config_dir.mkdir()
        config = config_dir / "alacritty.toml"
        config.write_text("[window]\nopacity = 0.9\n", encoding="utf-8")
        adapter = config_dir / "macropad-f13-adapter.toml"
        backup = self.workdir / "alacritty-backup"
        command = [
            "node",
            str(ROOT / "scripts/install_alacritty_macropad_adapter.js"),
            "--source",
            str(ROOT / "config/macropad/alacritty-f13-adapter.toml"),
            "--adapter",
            str(adapter),
            "--config",
            str(config),
            "--backup-dir",
            str(backup),
        ]
        for _ in range(2):
            result = subprocess.run(command, text=True, capture_output=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)

        text = config.read_text(encoding="utf-8")
        self.assertEqual(text.count("macropad-f13-adapter.toml"), 1)
        self.assertIn("[window]\nopacity = 0.9", text)
        self.assertTrue(adapter.is_file())

    def test_node_apply_backs_up_existing_pi_lens_config(self):
        self.install_successful_fake_npm()
        target = self.workdir / "backup-target"
        self.pi_lens_config.parent.mkdir(parents=True)
        self.pi_lens_config.write_text('{"format":{"enabled":true}}\n', encoding="utf-8")

        result = subprocess.run(
            ["node", str(ROOT / "bin/pi-setup.js"), "--target", str(target), "--no-update"],
            cwd=ROOT,
            env=self.environment(),
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        backups = list((target / "backups").glob("*/pi-lens/config.json"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(self.read_json(backups[0]), {"format": {"enabled": True}})
        self.assertEqual(self.read_json(self.pi_lens_config), {"format": {"enabled": False}})


if __name__ == "__main__":
    unittest.main()
