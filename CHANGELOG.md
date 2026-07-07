# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-07-06

### Fixed
- Fixed broken console script: the `jira-csv-upload` entry point now works after `pip install` (the CLI module was previously not packaged)
- A row with a Summary and Description but no Issue Type is no longer treated as a main issue; it now fails validation instead of failing at upload time with a confusing API error
- CSV rows that fail validation now fail the whole run instead of silently uploading the remaining rows and reporting success
- Retry logic now retries the operation it was asked to perform instead of always calling `issue_create`
- Version is now defined in one place (`jira_csv_upload.__version__`) instead of drifting across three files

### Added
- `upload --dry-run` flag: validate the CSV and show what would be created without calling Jira (works without Jira credentials)
- Created issue keys and errors are written to `upload_results.json` after each upload
- `JIRA_SUBTASK_ISSUE_TYPE` environment variable for instances where the subtask type is not named "Sub-task"
- `template --force` flag; `template` no longer silently overwrites an existing `template.csv`
- Clear error message when an integer environment variable (e.g. `RETRY_ATTEMPTS`) is not a number

### Changed
- **Breaking:** package restructured from `src/` + top-level `cli.py` to a proper `jira_csv_upload` package; run the CLI with `jira-csv-upload` (after install) or `python -m jira_csv_upload`
- Dependencies reduced to direct ones only (`atlassian-python-api`, `python-dotenv`, `click`, `pydantic`); `requirements.txt` and `dev-requirements.txt` removed in favor of `pip install -e ".[dev]"`
- mypy configuration tightened from effectively-disabled to a meaningful baseline
- Release workflow migrated from the archived `actions/create-release` to `softprops/action-gh-release`

### Removed
- Unused `JiraIssueData`/`JiraSubtaskData` models and `CSVRow.to_issue_data`/`to_subtask_data` methods
- Unused `BATCH_SIZE` configuration
- `constants.py` (subtask issue type moved to configuration)

## [1.2.0] - 2024-12-22

### Security
- Removed malicious `security==1.3.1` package flagged on PyPI
- Cleaned up dependency tree to improve security posture

### Fixed
- Fixed CSV validation to properly support subtask-only rows without requiring empty main issue fields
- Fixed logging setup with graceful error handling for log file creation failures
- Fixed CI workflow to properly exclude legacy test files

### Added
- Integration tests for end-to-end workflow
- `dev-requirements.txt` for development dependencies
- Constants module for hard-coded strings (e.g., `SUBTASK_ISSUE_TYPE`)

### Changed
- Streamlined README from 299 to 172 lines (43% reduction)
- Improved readability and focus on essential information
- Applied comprehensive type hints throughout the codebase
- Removed unused imports and duplicate configuration files
- Consolidated mypy configuration to `pyproject.toml`
- Fixed Python version inconsistencies (standardized to 3.9+)
- All 21 tests passing successfully

## [1.1.0] - 2024-12-01

### Changed
- Upgraded to Pydantic v2 with modern data validation
- Replaced deprecated `@validator` with `@field_validator` decorators
- Dropped Python 3.8 support (now requires Python 3.9+)
- Simplified GitHub Actions workflow
- Streamlined test matrix for more reliable CI runs

### Added
- `types-requests` dependency for improved type checking
- Comprehensive type hints across all modules
- 100% mypy compliance

### Fixed
- CSV structure validation in tests
- ApiError inheritance issues
- Mypy type annotation errors
- Exception handling in JiraClient

## [1.0.0] - 2024-11-15

Initial stable release - complete rewrite and modernization of the Jira CSV upload tool.

### Added
- Modern CLI interface built with Click
- Environment-based configuration with `.env` files
- Robust error handling with retry logic and exponential backoff
- Automatic CSV validation
- Comprehensive logging with file and console output
- Full test suite with mocking and validation
- Complete documentation and examples

### Features
- Upload issues and subtasks from CSV files
- Test Jira connection
- Validate CSV file format
- Generate CSV templates
- Show current configuration

### Technical
- Modular architecture with clean separation of concerns
- Pydantic models for data validation and type safety
- Automatic retry with exponential backoff for API failures
- Proper Python packaging with `pyproject.toml`

### Compatibility
- Jira Cloud (Atlassian Cloud)
- Jira Server (On-premise)
- Jira Data Center
- Python 3.8+
- Cross-platform (Windows, macOS, Linux)

[1.3.0]: https://github.com/star7js/jira-upload-csv/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/star7js/jira-upload-csv/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/star7js/jira-upload-csv/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/star7js/jira-upload-csv/releases/tag/v1.0.0
