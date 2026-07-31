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

    def test_example_and_skill_define_model_matrix_workflow(self):
        example = (SKILL_DIR / "references/AGENTS.example.md").read_text(encoding="utf-8")
        skill = SKILL.read_text(encoding="utf-8")

        self.assertIn("| model | cost | intelligence | taste |", example)
        self.assertIn("### Selection algorithm", example)
        self.assertIn("gpt-5.6-sol", example)
        self.assertIn("opus-5", example)
        self.assertIn("adopt the example matrix", skill)
        self.assertIn("customize the matrix", skill)
        self.assertIn("capability roles only", skill)


if __name__ == "__main__":
    unittest.main()
