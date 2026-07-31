import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "config" / "skills" / "review-global-agents"
SKILL = SKILL_DIR / "SKILL.md"


class ReviewGlobalAgentsSkillTests(unittest.TestCase):
    def test_skill_references_existing_review_materials(self):
        content = SKILL.read_text(encoding="utf-8")
        for relative_path in (
            "references/AGENTS.example.md",
            "references/ORCHESTRATION_REVIEW.md",
        ):
            self.assertIn(relative_path, content)
            self.assertTrue((SKILL_DIR / relative_path).is_file())


if __name__ == "__main__":
    unittest.main()
