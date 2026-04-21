# Documentation Guidelines

This document outlines best practices for creating and organizing documentation in Syncbot and other projects in this workspace.

## Documentation Structure

All package and project documentation and user/planning guides should be organized as follows relative to the package root folder:

```
ProjectRoot/
├── docs/
│   ├── README.md                 # Project overview and quick start
│   ├── DOCUMENTATION_GUIDELINES.md  # This file
│   ├── CHANGELOG.md              # Version history and changes
│   ├── QUICK_START.md            # Getting started guide
│   ├── user-guides/
│   │   ├── installation.md
│   │   ├── configuration.md
│   │   └── troubleshooting.md
│   ├── developer-guides/
│   │   ├── architecture.md
│   │   ├── contributing.md
│   │   └── testing.md
│   └── planning/
│       ├── design-decisions.md
│       ├── roadmap.md
│       └── architecture-notes.md
├── src/
├── tests/
└── config/
```

## Documentation Types

Use this priority model:

### 1) Core Documentation (required for all projects)

#### `README.md`
Purpose: First-stop guide for users and contributors.

Required sections:
- Project purpose (1-2 sentences)
- Installation / setup
- Quick usage example
- Link to docs folder and key files

Guidelines:
- Keep concise and task-oriented
- Prefer copy/paste-ready examples
- Update whenever startup or usage changes

#### `CHANGELOG.md`
Purpose: Track what changed per release.

Required rules:
- One section per version
- Use date format `YYYY-MM-DD`
- Group by: Added, Changed, Fixed, Removed (as applicable)
- Flag breaking changes explicitly

Guidelines:
- Write from user impact perspective
- Keep entries short and specific

#### `ROADMAP.md` (or `planning/roadmap.md`)
Purpose: Capture planned work and priorities.

Required sections:
- Near-term priorities
- Mid-term goals
- Deferred / backlog ideas

Guidelines:
- Use short bullet points
- Mark items as Planned / In Progress / Done
- Review at each release milestone

### 2) Supporting Documentation (recommended)

#### User Documentation
Location: `docs/user-guides/`

Guidelines:
- Focus on installation, configuration, troubleshooting
- Use plain language and examples
- Keep one workflow per file where possible

#### Developer Documentation
Location: `docs/developer-guides/`

Guidelines:
- Document architecture, testing, and contribution flow
- Link to relevant code paths
- Keep implementation details aligned with current code

#### Planning / Design Documentation
Location: `docs/planning/`

Guidelines:
- Capture decisions, trade-offs, and rationale
- Include decision date and context
- Update when priorities or architecture changes

### 3) Optional Documentation (larger projects)

Add these only when project complexity justifies them:
- `CONTRIBUTING.md`
- `ARCHITECTURE.md`
- `API_REFERENCE.md`
- Migration guides
- Feature-specific deep dives

Rule of thumb: start with `README.md`, `CHANGELOG.md`, and `ROADMAP.md`; expand only as the project grows.

## Maintenance Rules

- Keep documentation in `docs/` under project root
- Tag any documentation guidelines files by appending either "Summary/Detailed/Comprehensive" to the filename.
- Any or all developer guides (where applicable) should always have a Summary version.
- Include last updated date in top section of each file
- Update docs in the same change set as related code updates
- Remove stale docs instead of letting them drift
- Prefer short, scannable markdown over long narrative text

## Links to Related Guides

- [Syncbot README (v2)](../../Applications/Syncbot/docs/README_V2.md)
- [Syncbot Quick Start](../../Applications/Syncbot/docs/QUICK_START.md)
- [Syncbot Changelog](../../Applications/Syncbot/docs/CHANGELOG.md)
- [tUilKit Development](../../Core/tUilKit/docs/)
- [H3l3n Project Scaffolding](../../SuiteTools/H3l3n/docs/)
- [Workspace Copilot Instructions](../copilot-instructions.md)
- [Testing Policy](building_tests_policy.md)
