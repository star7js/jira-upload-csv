# Jira CSV Upload Tool

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Python tool for automating the creation of Jira issues and subtasks from CSV data. Features robust error handling, validation, retry logic, and a command-line interface.

## Features

- CSV data processing with automatic validation
- Jira integration for creating issues and subtasks
- Retry logic with exponential backoff for API failures
- Input validation using Pydantic models
- Configurable logging and error handling
- Easy-to-use CLI with multiple commands

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/star7js/jira-upload-csv.git
   cd jira-upload-csv
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
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
| `BATCH_SIZE` | Issues per batch | `10` |
| `RETRY_ATTEMPTS` | Retry attempts for failed requests | `3` |
| `RETRY_DELAY` | Base delay between retries (seconds) | `5` |

**Get your Jira API token:** Visit [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens), create a new token, and add it to your `.env` file.

## Usage

### CLI Commands

```bash
# Upload issues from CSV
python cli.py upload --csv-file path/to/file.csv

# Test Jira connection
python cli.py test

# Validate CSV format
python cli.py validate --csv-file path/to/file.csv

# Generate CSV template
python cli.py template

# Show current configuration
python cli.py config
```

### Programmatic Usage

```python
from src.main import main

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
- Each group needs exactly one row with main issue data
- Additional rows in a group can contain subtask data
- Empty subtask fields are ignored

## Testing

Run tests:
```bash
# All tests
python -m pytest tests/

# With coverage
python -m pytest tests/ --cov=src --cov-report=html

# Development dependencies
pip install -r dev-requirements.txt
```

## Troubleshooting

**Authentication Failed**
- Verify credentials in `.env` file
- Check that API token is valid and not expired
- Confirm Jira instance URL is correct

**CSV Validation Errors**
- Run `python cli.py validate --csv-file your-file.csv`
- Ensure all required columns are present
- Check each issue group has exactly one main issue row

**Permission Errors**
- Verify Jira user has create permissions in the target project
- Confirm project key exists and is accessible

**Rate Limiting**
- Tool includes automatic retry logic with exponential backoff
- Increase `RETRY_DELAY` in `.env` if needed

**Logs**: Check `jira_upload.log` for detailed error information.

## Development

```bash
# Install dev dependencies
pip install -r dev-requirements.txt

# Run linting
flake8 src/ tests/

# Run type checking
mypy src/

# Format code
black src/ tests/
```

Pull requests are welcome. Please include tests for new features.

## License

MIT License. See [LICENSE](LICENSE) file for details.
