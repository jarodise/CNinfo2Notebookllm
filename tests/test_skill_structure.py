import unittest
import os
import json
import yaml


class TestSkillStructure(unittest.TestCase):
    def setUp(self):
        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def test_required_files_exist(self):
        """Test that all required files for a standard skill exist"""
        required_files = [
            "skill.yaml",
            "package.json",
            "SKILL.md",
            "scripts/run.py",
            "scripts/upload.py",
            "scripts/download.py",
            "assets/financial_analyst_prompt.txt",
            "assets/stocks.json",
        ]

        for file_path in required_files:
            full_path = os.path.join(self.root_dir, file_path)
            self.assertTrue(
                os.path.exists(full_path), f"Missing required file: {file_path}"
            )

    def test_no_forbidden_dirs(self):
        """Test that data/ directory is gone (renamed to assets/)"""
        data_dir = os.path.join(self.root_dir, "data")
        self.assertFalse(
            os.path.exists(data_dir),
            "Forbidden directory 'data/' still exists (should be 'assets/')",
        )

    def test_skill_yaml_valid(self):
        """Test that skill.yaml is valid YAML and has required fields"""
        yaml_path = os.path.join(self.root_dir, "skill.yaml")
        with open(yaml_path, "r") as f:
            data = yaml.safe_load(f)

        self.assertIn("name", data)
        self.assertIn("commands", data)
        self.assertEqual(data["name"], "cninfo-to-notebooklm")

    def test_package_json_valid(self):
        """Test that package.json is valid JSON"""
        json_path = os.path.join(self.root_dir, "package.json")
        with open(json_path, "r") as f:
            data = json.load(f)

        self.assertIn("name", data)
        self.assertIn("scripts", data)
        self.assertEqual(data["name"], "cninfo-to-notebooklm")


if __name__ == "__main__":
    unittest.main()
