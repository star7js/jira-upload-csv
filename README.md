# Jira CSV Upload Tool

A robust Python tool for automating the creation of Jira issues and subtasks from CSV data. Features comprehensive error handling, validation, retry logic, and a command-line interface.

## 🚀 Features

- **CSV Data Processing**: Read and validate CSV files with automatic error detection
- **Jira Integration**: Create main issues and subtasks with proper linking
- **Error Handling**: Comprehensive error handling with retry logic and exponential backoff
- **Input Validation**: Validate CSV structure and data using Pydantic models
- **Configuration Management**: Environment-based configuration with validation
- **Logging**: Detailed logging with configurable levels
- **CLI Interface**: Easy-to-use command-line interface with multiple commands
- **Testing**: Comprehensive test suite with mocking

## 📋 Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [CSV Format](#csv-format)
- [API Reference](#api-reference)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## 🛠 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/star7js/jira-upload-csv.git
   cd jira-upload-csv
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root with your Jira credentials:

```bash
# Copy the example file
cp env.example .env

# Edit .env with your actual values
```

Required environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `JIRA_BASE_URL` | Your Jira instance URL | `https://your-company.atlassian.net` |
| `JIRA_USERNAME` | Your Jira email address | `user@example.com` |
| `JIRA_API_TOKEN` | Your Jira API token | `your-api-token-here` |

Optional environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` |
| `DEFAULT_CSV_PATH` | Default CSV file path | `data/main_and_subtasks_multiple.csv` |
| `BATCH_SIZE` | Number of issues to process in batch | `10` |
| `RETRY_ATTEMPTS` | Number of retry attempts for failed requests | `3` |
| `RETRY_DELAY` | Base delay between retries (seconds) | `5` |

### Getting Your Jira API Token

1. Go to [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click "Create API token"
3. Give it a name (e.g., "CSV Upload Tool")
4. Copy the generated token to your `.env` file

## 📖 Usage

### Command Line Interface

The tool provides a comprehensive CLI with multiple commands:

#### Upload Issues
```bash
# Upload using default CSV file
python cli.py upload

# Upload using specific CSV file
python cli.py upload --csv-file path/to/your/file.csv

# Upload with debug logging
python cli.py upload --log-level DEBUG
```

#### Test Configuration
```bash
# Test Jira connection and configuration
python cli.py test
```

#### Show Configuration
```bash
# Display current configuration
python cli.py config
```

#### Validate CSV
```bash
# Validate CSV file structure and data
python cli.py validate --csv-file path/to/your/file.csv
```

#### Generate Template
```bash
# Generate a template CSV file
python cli.py template
```

### Programmatic Usage

```python
from src.main import main

# Upload using default CSV file
success = main()

# Upload using specific CSV file
success = main('path/to/your/file.csv')

if success:
    print("Upload completed successfully!")
else:
    print("Upload failed. Check logs for details.")
```

## 📄 CSV Format

The tool expects CSV files with the following structure:

| Column | Required | Description |
|--------|----------|-------------|
| `ID` | Yes | Unique identifier for grouping related rows |
| `Project Key` | Yes | Jira project key (e.g., "PROJ") |
| `Summary` | Yes* | Issue summary (required for main issues) |
| `Description` | Yes* | Issue description (required for main issues) |
| `Issue Type` | Yes* | Issue type (required for main issues) |
| `Subtask Summary` | No | Subtask summary |
| `Subtask Description` | No | Subtask description |

### CSV Example

```csv
ID,Project Key,Summary,Description,Issue Type,Subtask Summary,Subtask Description
1,PROJ1,Main Issue 1,This is the first main issue,Task,Subtask 1.1,This is the first subtask for Main Issue 1
1,PROJ1,,,,Subtask 1.2,This is the second subtask for Main Issue 1
2,PROJ1,Main Issue 2,This is the second main issue,Task,Subtask 2.1,This is the first subtask for Main Issue 2
```

**Notes:**
- Rows with the same `ID` are grouped together
- Each group must have exactly one row with main issue data (Summary, Description, Issue Type)
- Additional rows in the same group can contain subtask data
- Empty subtask fields are ignored

## 🔧 API Reference

### Core Classes

#### `JiraClient`
Handles Jira API interactions with retry logic and error handling.

```python
from src.jira_client import JiraClient

client = JiraClient()
success = client.test_connection()
issue = client.create_issue(issue_data)
subtask = client.create_subtask(subtask_data)
```

#### `CSVProcessor`
Processes and validates CSV files.

```python
from src.csv_processor import CSVProcessor

processor = CSVProcessor('path/to/file.csv')
rows = processor.read_and_validate_csv()
groups = processor.get_issue_groups(rows)
```

#### `CSVRow`
Data model for CSV rows with validation.

```python
from src.models import CSVRow

row = CSVRow(
    id='1',
    project_key='TEST',
    summary='Test Issue',
    description='Test Description',
    issue_type='Task'
)
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_improved_modules.py

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

### Test Structure

- `tests/test_improved_modules.py`: Comprehensive tests for all new modules
- `tests/test_multi_issue_upload_with_subtasks.py`: Original tests (legacy)

## 🐛 Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Verify your Jira credentials in the `.env` file
   - Ensure your API token is correct and not expired
   - Check that your Jira instance URL is correct

2. **CSV Validation Errors**
   - Use `python cli.py validate --csv-file your-file.csv` to check for issues
   - Ensure all required columns are present
   - Check that each issue group has exactly one main issue row

3. **Permission Errors**
   - Ensure your Jira user has permission to create issues in the target project
   - Verify the project key exists and is accessible

4. **Rate Limiting**
   - The tool includes automatic retry logic with exponential backoff
   - Increase `RETRY_DELAY` in your `.env` file if you encounter rate limiting

### Logs

The tool creates detailed logs in `jira_upload.log`. Check this file for detailed error information:

```bash
tail -f jira_upload.log
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run the test suite: `python -m pytest tests/`
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt

# Install pre-commit hooks (optional)
pre-commit install

# Run linting
flake8 src/ tests/

# Run type checking
mypy src/
```

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Atlassian Python API](https://github.com/atlassian-api/atlassian-python-api) for Jira integration
- [Pydantic](https://pydantic-docs.helpmanual.io/) for data validation
- [Click](https://click.palletsprojects.com/) for CLI interface
