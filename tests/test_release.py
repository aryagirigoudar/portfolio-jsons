"""Public validation tests use a synthetic profile and no private source data."""

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "release_validator", Path(__file__).parents[1] / "scripts/validate.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)

    def bundle(self, *, draft=False):
        profile = {
            "schema_version": 1,
            "name": "Example Engineer",
            "title": "Engineer",
            "summary": "Synthetic test profile.",
            "email": "engineer@example.org",
            "location": "Example",
            "github": None,
            "linkedin": None,
            "skills": {},
            "experience": [],
            "education": [],
            "resume_url": "resume/resume.pdf",
            "resume_draft": draft,
        }
        files = {
            "data/projects.json": json.dumps(
                {
                    "schema_version": 1,
                    "generated_at": "2026-11-02T00:00:00Z",
                    "projects": [],
                }
            ).encode(),
            "data/profile.json": json.dumps(profile).encode(),
            "resume/resume.pdf": b"%PDF-synthetic-test",
        }
        for name, raw in files.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        (self.root / "manifest.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "files": {
                        name: hashlib.sha256(raw).hexdigest()
                        for name, raw in files.items()
                    },
                }
            )
        )

    def test_empty_scaffold(self):
        module.validate(self.root)

    def test_complete_release(self):
        self.bundle()
        module.validate(self.root)

    def test_draft_rejected(self):
        self.bundle(draft=True)
        with self.assertRaises(ValueError):
            module.validate(self.root)

    def test_partial_release_rejected(self):
        (self.root / "data").mkdir()
        with self.assertRaises(ValueError):
            module.validate(self.root)

    def test_corruption_rejected(self):
        self.bundle()
        (self.root / "resume/resume.pdf").write_bytes(b"%PDF-corruption")
        with self.assertRaises(ValueError):
            module.validate(self.root)

    def test_manifest_symlink_rejected(self):
        self.bundle()
        (self.root / "manifest.json").unlink()
        (self.root / "manifest.json").symlink_to("/etc/hostname")
        with self.assertRaises(ValueError):
            module.validate(self.root)


if __name__ == "__main__":
    unittest.main()
