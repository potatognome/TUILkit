# Version Bumping Guidelines

Purpose
- Employ standardized versioning.
- Ensure project versions are properly synced across workspace

## Current Version Syncing

 Ensure Current Version is included/updated in any or all of the following locations, where available.
 - \$PROJECT_ROOT\config\($PROJECT_NAME)_CONFIG.json
 - \$PROJECT_ROOT\CHANGELOG.md
 - \$PROJECT_ROOT\pyproject.toml
 - \$PROJECT_ROOT\README.md


## Changelog Updates

Include all updates in Project's change log file \$PROJECT_ROOT\CHANGELOG.md and automatically bump version by 0.0.1 on incremental updates.
Include date in CHANGELOG entries, limit automatic reversioning to 3 times per day.
Ensure all locations have synced versioning after all CHANGELOG updates.
When asked to manually reversion (by 0.1.0 or more), round down after the update. (e.g. 0.9.3 -> 1.0.0) and include an entry in the CHANGELOG stating 'VERSION UPDATED MANUALLY: $OLD_VERSION -> $NEW_VERSION'

## Version Disputes

In the case of disputed version numbers, always sync to the higher version number, (Highest to Lowest, Left to Right)

