# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[1.2.0]: https://github.com/star7js/jira-upload-csv/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/star7js/jira-upload-csv/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/star7js/jira-upload-csv/releases/tag/v1.0.0
