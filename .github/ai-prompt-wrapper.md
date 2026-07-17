# tUilKit Prompt Wrapper

Prepend this wrapper to any coding request when you want higher consistency from the agent.

## Quick Wrapper

```text
Project: tUilKit
Task: <describe task>

Constraints:
1. Keep public interfaces backwards compatible unless explicitly approved.
2. Use factory-first and interface-driven patterns.
3. Keep all paths and output locations config-driven; no hardcoded absolute paths.
4. Follow logging policy and LOG_FILES routing, including semantic keys and exception logging.
5. Add or update deterministic tests for changed behavior.
6. If behavior changes, update README.md and CHANGELOG.md in the same change.

Completion requirements:
- Summarize contract impact.
- List tests run and outcomes.
- List docs/version files updated.
```

## Feature Request Variant

```text
Implement a feature in tUilKit while preserving existing public contracts.
Use factory-first imports and interface-driven structure.
Any path handling must be ROOT_MODES/PATHS aware.
Add focused tests and keep them deterministic.
If user-visible behavior changes, update README.md and CHANGELOG.md.
Provide a short completion report with tests and contract impact.
```

## Bugfix Variant

```text
Fix the bug in tUilKit with the smallest safe change.
Do not introduce app-specific logic.
Keep logging policy-compliant and avoid hardcoded paths.
Add a regression test that fails before and passes after the fix.
Report contract impact, tests run, and doc updates.
```

## Refactor Variant

```text
Refactor for clarity/maintainability without changing public behavior.
Preserve interfaces and factory usage patterns.
Keep config-driven path behavior and logging policy compliance.
Run targeted tests to prove no regression.
```

## Tests-Only Variant

```text
Add or update tests in tUilKit for <target behavior> without changing public runtime behavior.
Follow existing deterministic test patterns and bootstrap/path rules.
Use policy-compliant logging in test output where applicable.
Summarize what behavior is now covered and provide commands and outcomes.
```

## Docs-Only Variant

```text
Update tUilKit documentation only (README/CHANGELOG/docs) for <topic>.
Do not change runtime behavior.
Keep terminology aligned with interfaces, factory-first usage, and config-driven path conventions.
Use YYYY-MM-DD date format for changelog entries.
Summarize what changed and why.
```

## Pre-Merge Gate Variant

```text
Before finalizing this change, run:
python scripts/ai_quality_gate.py

If warnings appear, explain whether they are expected or fix them.
If failures appear, fix them before completion.
Include gate output summary in the final report.
```
