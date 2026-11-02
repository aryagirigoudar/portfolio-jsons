# Public portfolio project data

This repository contains the reusable public metadata specification and validation checks. Approved releases are prepared by private portfolio automation through owner-reviewed PRs. The initial repository intentionally has no project dataset or resume yet.

## Release layout

```text
manifest.json
data/
  projects.json
  profile.json
  icons/<sha256>.png
resume/
  resume.pdf
```

The versioned manifest hashes every release file. JSON schemas are under schemas/. No private repository names/IDs, credentials, raw source files, raw resume YAML or private collection reports belong here. Descriptions and icons are explicit public disclosures; review before merging because PR branches are already public.

Private automation writes only these release paths on codex/portfolio-sync and never merges. Published projects opt in using a root port_info.json in an authorized source repository; the reusable input schema is schemas/port_info.v1.schema.json. The internal port_info/info.json maintenance catalog does not authorize disclosure.

The public website resolves the approved main branch to a single commit, validates the manifest/files, then copies them into a complete static build. No Pages hosting, browser access token, or separate server is needed for this data repository. Merged data reaches the site on its next scheduled/manual website refresh.

## Validation

```bash
python -m pip install -r requirements.txt
python scripts/validate.py
```

A schema-only scaffold passes. Partial releases, extra/missing files, unsafe paths, symlinks, corrupted hashes, invalid schemas, inconsistent icon references, or draft resume/profile data fail. The real resume is currently draft by owner instruction and is not included here.

Project-only releases require just manifest.json, data/projects.json and any referenced icons. Profile JSON and resume PDF are optional but must appear together and be approved. The live project sync deliberately omits both while the owner's resume remains draft.
