# tUilKit AI Quality Checklist

Use this checklist for every AI-assisted change in tUilKit.

## 1) Contract Safety
- Keep public API behavior backwards compatible unless the task explicitly approves a breaking change.
- If behavior changes, update interface definitions and implementations together.
- Do not add consuming-app logic into tUilKit modules.

## 2) Factory and Interface Usage
- Prefer factory-first imports: `get_logger`, `get_config_loader`, `get_file_system`, `get_colour_manager`.
- Use interface-driven patterns for core services and keep components independently testable.
- Avoid direct class construction when factory usage is the established path.

## 3) Config and Path Discipline
- Keep paths config-driven through `ROOTS`, `ROOT_MODES`, `PATHS`, and related config keys.
- Never hardcode machine-specific absolute paths.
- Ensure runtime, test, and generated output paths follow root-mode behavior.

## 4) Logging Quality
- Use semantic log keys (for example `!info`, `!warn`, `!error`, `!path`, `!test`, `!pass`, `!fail`, `!date`).
- Route logs through configured `LOG_FILES` targets.
- Use `logger.log_exception()` for caught exceptions.
- Include timestamps for entries that represent execution flow.

## 5) Tests and Determinism
- Add or update tests for changed behavior.
- Keep tests deterministic and aligned to existing bootstrap/path-resolution patterns.
- Run focused tests for touched modules before completion.

## 6) Documentation and Version Hygiene
- When behavior changes, update `README.md` and `CHANGELOG.md` in the same change.
- Keep changelog dates in `YYYY-MM-DD` format.
- If release metadata changes are required, keep `pyproject.toml` and related version fields aligned.

## 7) Definition of Done
Mark the task done only when all items below are true:
- Code follows factory/interface and config-driven policies.
- Relevant tests pass.
- Logging behavior remains policy-compliant.
- Documentation and versioning updates are complete when needed.

## 8) PR Evidence Snippet
Include a short implementation summary in PR notes:
- What contract was preserved or intentionally changed.
- What tests were run.
- Which docs/version files were updated.
