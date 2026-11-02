"""Validate a complete public release, or the initial repository scaffold."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError, ValidationError

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {"data/projects.json"}


def validate(root: Path) -> None:
    schemas = {
        name: json.loads((ROOT / f"schemas/{name}.v1.schema.json").read_text())
        for name in ("projects", "profile", "manifest")
    }
    for schema in schemas.values():
        Draft202012Validator.check_schema(schema)
    if not (root / "manifest.json").exists():
        if (root / "data").exists() or (root / "resume").exists():
            raise ValueError("Partial release without manifest")
        print("Schemas valid; no project data has been published yet.")
        return
    if (root / "manifest.json").is_symlink():
        raise ValueError("Manifest symlink rejected")
    manifest = json.loads((root / "manifest.json").read_text())
    Draft202012Validator(schemas["manifest"]).validate(manifest)
    files = manifest["files"]
    actual = {
        path.relative_to(root).as_posix()
        for directory in ("data", "resume")
        for path in (root / directory).rglob("*")
        if path.is_file()
    }
    if actual != set(files):
        raise ValueError("Release contains missing or unlisted files")
    for name, digest in files.items():
        path = root / name
        if path.is_symlink() or any(
            parent.is_symlink() for parent in path.parents if parent != root
        ):
            raise ValueError("Symlink rejected")
        if path.stat().st_size > 10 * 1024 * 1024:
            raise ValueError("File exceeds limit")
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError("Release hash mismatch")
    records = {}
    for name in (
        ("projects", "profile") if "data/profile.json" in files else ("projects",)
    ):
        records[name] = json.loads((root / f"data/{name}.json").read_text())
        Draft202012Validator(schemas[name], format_checker=FormatChecker()).validate(
            records[name]
        )
    if records["projects"].get("preview") or records.get("profile", {}).get(
        "resume_draft", False
    ):
        raise ValueError("Draft data cannot be published")
    if "resume/resume.pdf" in files and not (
        root / "resume/resume.pdf"
    ).read_bytes().startswith(b"%PDF-"):
        raise ValueError("Invalid PDF")
    icons = {p["icon_url"] for p in records["projects"]["projects"] if p["icon_url"]}
    if icons != {name for name in files if name.startswith("data/icons/")}:
        raise ValueError("Icon references do not match release")
    print("Public release schemas, paths and hashes validated.")


if __name__ == "__main__":
    try:
        validate(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT)
    except (ValueError, OSError, KeyError, TypeError, SchemaError, ValidationError):
        # Do not echo input values into public CI logs.
        print("Public release validation failed.", file=sys.stderr)
        raise SystemExit(1) from None
