# Release Notes v1.2.0

## Security Fixes

- **Removed malicious dependency**: Removed `security==1.3.1` package which was flagged as malicious on PyPI
- Cleaned up dependency tree to improve security posture

## Bug Fixes

- **Fixed CSV validation**: Corrected model validation to properly support subtask-only rows without requiring empty main issue fields
- **Fixed logging setup**: Added graceful error handling for log file creation failures
- **Fixed CI workflow**: Updated GitHub Actions to properly exclude legacy test files

## Improvements

### Code Quality
- Added comprehensive type hints throughout the codebase
- Created constants module for hard-coded strings (e.g., `SUBTASK_ISSUE_TYPE`)
- Removed unused imports and duplicate configuration files
- Enforced code quality with flake8 (0 errors) and mypy (0 errors)
- Applied black formatting consistently

### Testing
- Added integration tests for end-to-end workflow
- Added `dev-requirements.txt` for development dependencies
- Improved test coverage and reliability
- All 21 tests passing successfully

### Configuration
- Removed duplicate mypy configuration (consolidated to `pyproject.toml`)
- Fixed Python version inconsistencies (standardized to 3.9+)
- Synced CLI version with package version

### Documentation
- Streamlined README from 299 to 172 lines (43% reduction)
- Removed excessive emojis and redundant sections
- Improved readability and focus on essential information
- Better organized troubleshooting section

## Technical Details

### Files Changed
- 13 files modified with 380 insertions and 112 deletions
- 3 new files: `dev-requirements.txt`, `src/constants.py`, `tests/test_integration.py`
- 1 file removed: `mypy.ini` (duplicate configuration)

### Compatibility
- Python 3.9, 3.10, 3.11 tested and supported
- All dependencies updated and verified
- Backward compatible with v1.1.0 usage

## Migration Notes

No breaking changes. This release is a drop-in replacement for v1.1.0.

To upgrade:
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

## Contributors

- Josh Simnitt (@star7js)
