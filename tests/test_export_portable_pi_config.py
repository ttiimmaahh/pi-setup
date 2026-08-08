import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPORTER = REPO_ROOT / "scripts" / "export_portable_pi_config.py"


class PortableExportTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(self.temp_dir.name)
        self.pi_dir = root / "agent"
        self.out_dir = root / "snapshot"
        self.pi_dir.mkdir()

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_json(self, relative_path, value):
        path = self.pi_dir / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def run_export(self):
        env = os.environ.copy()
        for name in (
            "PI_SETUP_INCLUDE_LOCAL_PACKAGES",
            "PI_SETUP_INCLUDE_MCP",
            "PI_SETUP_INCLUDE_MODELS",
        ):
            env.pop(name, None)
        return subprocess.run(
            [sys.executable, str(EXPORTER), str(self.pi_dir), str(self.out_dir)],
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )

    def read_exported_json(self, relative_path):
        path = self.out_dir / relative_path
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            self.fail(f"Could not read exported JSON {path}: {exc}")

    def remove_fixture_tree(self, path):
        try:
            shutil.rmtree(path)
        except OSError as exc:
            self.fail(f"Could not remove fixture directory {path}: {exc}")

    def test_exports_only_portable_settings_and_authored_resources(self):
        self.write_json(
            "settings.json",
            {
                "lastChangelogVersion": "0.80.6",
                "defaultProvider": "private-provider",
                "defaultModel": "private-model",
                "trackingId": "private-tracking-id",
                "packages": [
                    "npm:portable-extension",
                    "../../Developer/local-extension",
                    ".\\relative\\local-extension",
                    "C:\\Users\\developer\\local-extension",
                    "\\\\server\\share\\local-extension",
                    {"source": "npm:filtered-extension", "skills": []},
                ],
                "theme": "dark",
            },
        )
        self.write_json("models.json", {"providers": {"private": {"apiKey": "secret"}}})
        self.write_json("mcp.json", {"mcpServers": {"private": {"token": "secret"}}})

        extensions = self.pi_dir / "extensions"
        extensions.mkdir()
        (extensions / "portable.ts").write_text("export default function () {}\n", encoding="utf-8")
        (extensions / "herdr-agent-state.ts").write_text("// managed by herdr\n", encoding="utf-8")

        prompts = self.pi_dir / "prompts"
        prompts.mkdir()
        (prompts / "review.md").write_text("Review this.\n", encoding="utf-8")
        (prompts / "apex-private.md").write_text("Private workflow.\n", encoding="utf-8")

        result = self.run_export()

        settings = self.read_exported_json("settings.json")
        self.assertEqual(
            settings,
            {
                "packages": [
                    "npm:portable-extension",
                    {"source": "npm:filtered-extension", "skills": []},
                ],
                "theme": "dark",
            },
        )
        self.assertIn("Excluded local package paths", result.stdout)
        self.assertEqual(self.read_exported_json("models.json"), {"providers": {}})
        self.assertEqual(
            self.read_exported_json("mcp.json"),
            {"imports": [], "mcpServers": {}},
        )
        self.assertTrue((self.out_dir / "extensions" / "portable.ts").is_file())
        self.assertFalse((self.out_dir / "extensions" / "herdr-agent-state.ts").exists())
        self.assertTrue((self.out_dir / "prompts" / "review.md").is_file())
        self.assertFalse((self.out_dir / "prompts" / "apex-private.md").exists())

    def test_removes_stale_portable_files_but_keeps_public_placeholders(self):
        self.write_json("settings.json", {"packages": []})
        stale_files = (
            "keybindings.json",
            "pi-handoff-config.json",
            "pi-usage-bar/config.json",
        )
        for relative_path in stale_files:
            path = self.out_dir / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("{}\n", encoding="utf-8")

        self.run_export()

        for relative_path in stale_files:
            self.assertFalse((self.out_dir / relative_path).exists())
        self.assertEqual(self.read_exported_json("models.json"), {"providers": {}})
        self.assertEqual(
            self.read_exported_json("mcp.json"),
            {"imports": [], "mcpServers": {}},
        )

    def test_removes_snapshot_directory_when_every_resource_is_ignored(self):
        self.write_json("settings.json", {"packages": []})
        extensions = self.pi_dir / "extensions"
        extensions.mkdir()
        (extensions / "herdr-agent-state.ts").write_text(
            "// managed by herdr\n",
            encoding="utf-8",
        )
        stale_extensions = self.out_dir / "extensions"
        stale_extensions.mkdir(parents=True)
        (stale_extensions / "old.ts").write_text("// stale\n", encoding="utf-8")

        self.run_export()

        self.assertFalse(stale_extensions.exists())

    def test_removes_stale_snapshot_directories_when_live_resources_are_removed(self):
        self.write_json("settings.json", {"packages": []})
        extensions = self.pi_dir / "extensions"
        extensions.mkdir()
        (extensions / "portable.ts").write_text("export default function () {}\n", encoding="utf-8")

        self.run_export()
        self.assertTrue((self.out_dir / "extensions" / "portable.ts").is_file())

        self.remove_fixture_tree(extensions)
        self.run_export()

        self.assertFalse((self.out_dir / "extensions").exists())


if __name__ == "__main__":
    unittest.main()
