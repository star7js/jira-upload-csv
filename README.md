# Jira CSV Upload Tool

[![Test](https://github.com/star7js/jira-upload-csv/actions/workflows/test.yml/badge.svg)](https://github.com/star7js/jira-upload-csv/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/star7js/jira-upload-csv/graph/badge.svg)](https://codecov.io/gh/star7js/jira-upload-csv)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Python tool for automating the creation of Jira issues and subtasks from CSV data. Features error handling, validation, retry logic, and a command-line interface.

## Features

- CSV data processing with automatic validation
- Jira integration for creating issues and subtasks
- Dry-run mode to preview what would be created
- Retry logic with exponential backoff for API failures
- Input validation using Pydantic models
- Results file recording every created issue key
- Configurable logging and error handling
- Easy-to-use CLI with multiple commands

## Installation

```bash
git clone https://github.com/star7js/jira-upload-csv.git
cd jira-upload-csv
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

## Configuration

Create a `.env` file in the project root:

```bash
cp env.example .env
```

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `JIRA_BASE_URL` | Your Jira instance URL | `https://your-company.atlassian.net` |
| `JIRA_USERNAME` | Your Jira email address | `user@example.com` |
| `JIRA_API_TOKEN` | Your Jira API token | `your-api-token-here` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Logging level | `INFO` |
| `DEFAULT_CSV_PATH` | Default CSV file path | `data/main_and_subtasks_multiple.csv` |
| `JIRA_SUBTASK_ISSUE_TYPE` | Subtask issue type name | `Sub-task` |
| `RETRY_ATTEMPTS` | Retry attempts for failed requests | `3` |
| `RETRY_DELAY` | Base delay between retries (seconds) | `5` |

**Get your Jira API token:** Visit [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens), create a new token, and add it to your `.env` file.

## Usage

### CLI Commands

```bash
# Upload issues from CSV
jira-csv-upload upload --csv-file path/to/file.csv

# Preview what would be created without touching Jira
jira-csv-upload upload --csv-file path/to/file.csv --dry-run

# Test Jira connection
jira-csv-upload test

# Validate CSV format
jira-csv-upload validate --csv-file path/to/file.csv

# Generate CSV template
jira-csv-upload template

# Show current configuration
jira-csv-upload config
```

`python -m jira_csv_upload <command>` works too if you prefer not to use the entry point.

After each upload, the created issue keys, URLs, and any errors are written to `upload_results.json`.

### Programmatic Usage

```python
from jira_csv_upload.main import main

success = main('path/to/file.csv')
if success:
    print("Upload completed successfully!")
```

## CSV Format

Required columns:

| Column | Required | Description |
|--------|----------|-------------|
| `ID` | Yes | Unique identifier for grouping rows |
| `Project Key` | Yes | Jira project key |
| `Summary` | Yes* | Issue summary (main issues only) |
| `Description` | Yes* | Issue description (main issues only) |
| `Issue Type` | Yes* | Issue type (main issues only) |
| `Subtask Summary` | No | Subtask summary |
| `Subtask Description` | No | Subtask description |

### Example

```csv
ID,Project Key,Summary,Description,Issue Type,Subtask Summary,Subtask Description
1,PROJ1,Main Issue 1,Description,Task,Subtask 1.1,Subtask description
1,PROJ1,,,,Subtask 1.2,Another subtask
2,PROJ1,Main Issue 2,Description,Task,,
```

**Key points:**
- Rows with the same `ID` are grouped together
- Each group needs exactly one row with main issue data (`Summary`, `Description`, and `Issue Type`)
- Additional rows in a group can contain subtask data
- Empty subtask fields are ignored
- If any row fails validation, the whole run fails — nothing is uploaded partially

## Troubleshooting

**Authentication Failed**
- Verify credentials in `.env` file
- Check that API token is valid and not expired
- Confirm Jira instance URL is correct

**CSV Validation Errors**
- Run `jira-csv-upload validate --csv-file your-file.csv`
- Ensure all required columns are present
- Check each issue group has exactly one main issue row

**Permission Errors**
- Verify Jira user has create permissions in the target project
- Confirm project key exists and is accessible

**Subtask Creation Fails**
- Your instance may use a different subtask type name; set `JIRA_SUBTASK_ISSUE_TYPE` in `.env`

**Rate Limiting**
- Tool includes automatic retry logic with exponential backoff
- Increase `RETRY_DELAY` in `.env` if needed

**Logs**: Check `jira_upload.log` for detailed error information.

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
python -m pytest tests/

# Run tests with coverage
python -m pytest tests/ --cov=jira_csv_upload --cov-report=html

# Run linting
flake8 jira_csv_upload/ tests/

# Run type checking
mypy jira_csv_upload/

# Format code
black jira_csv_upload/ tests/
```

Pull requests are welcome. Please include tests for new features.

## License

MIT License. See [LICENSE](LICENSE) file for details.
