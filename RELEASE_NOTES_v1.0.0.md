# Release v1.0.0 - First Stable Release

🎉 **Jira CSV Upload Tool** is now production-ready with a modern, robust architecture!

## 🚀 What's New

This release represents a complete rewrite and modernization of the Jira CSV upload tool, transforming it from a simple script into a professional-grade application.

### ✨ Major Features

- **🔧 Modern CLI Interface**: Built with Click for intuitive command-line usage
- **⚙️ Environment-based Configuration**: Secure credential management via `.env` files
- **🛡️ Robust Error Handling**: Comprehensive error handling with retry logic and exponential backoff
- **📊 CSV Validation**: Automatic validation of CSV structure and data integrity
- **📝 Detailed Logging**: Configurable logging with file and console output
- **🧪 Comprehensive Testing**: Full test suite with mocking and validation
- **📚 Complete Documentation**: Extensive README with examples and troubleshooting

### 🔧 Technical Improvements

- **Modular Architecture**: Clean separation of concerns with dedicated modules
- **Type Safety**: Pydantic models for data validation and type checking
- **Retry Logic**: Automatic retry with exponential backoff for API failures
- **Input Validation**: Comprehensive validation of CSV data and Jira responses
- **Configuration Management**: Environment variables with validation
- **Package Structure**: Proper Python packaging with `pyproject.toml`

### 🎯 New Commands

```bash
# Upload issues from CSV
python cli.py upload --csv-file data/issues.csv

# Test Jira connection
python cli.py test

# Validate CSV file
python cli.py validate --csv-file data/issues.csv

# Show configuration
python cli.py config

# Generate template CSV
python cli.py template
```

### 🔒 Security & Reliability

- **Secure Credentials**: Environment variables instead of hardcoded credentials
- **API Token Support**: Proper authentication for both Jira Cloud and Server
- **Error Recovery**: Graceful handling of network issues and API errors
- **Data Validation**: Prevents invalid data from reaching Jira

### 📋 Compatibility

- ✅ **Jira Cloud** (Atlassian Cloud)
- ✅ **Jira Server** (On-premise)
- ✅ **Jira Data Center**
- ✅ **Python 3.8+**
- ✅ **Cross-platform** (Windows, macOS, Linux)

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/star7js/jira-upload-csv.git
cd jira-upload-csv

# Install dependencies
pip install -r requirements.txt

# Set up configuration
cp env.example .env
# Edit .env with your Jira credentials
```

## 🚀 Quick Start

1. **Configure your Jira credentials**:
   ```bash
   cp env.example .env
   # Edit .env with your Jira URL, username, and API token
   ```

2. **Test your connection**:
   ```bash
   python cli.py test
   ```

3. **Generate a template**:
   ```bash
   python cli.py template
   ```

4. **Upload your issues**:
   ```bash
   python cli.py upload --csv-file template.csv
   ```

## 📄 CSV Format

The tool expects CSV files with this structure:

| Column | Required | Description |
|--------|----------|-------------|
| `ID` | Yes | Unique identifier for grouping related rows |
| `Project Key` | Yes | Jira project key (e.g., "PROJ") |
| `Summary` | Yes* | Issue summary (required for main issues) |
| `Description` | Yes* | Issue description (required for main issues) |
| `Issue Type` | Yes* | Issue type (required for main issues) |
| `Subtask Summary` | No | Subtask summary |
| `Subtask Description` | No | Subtask description |

## 🔧 Configuration

Environment variables in `.env`:

```bash
# Required
JIRA_BASE_URL=https://your-company.atlassian.net
JIRA_USERNAME=your-email@example.com
JIRA_API_TOKEN=your-api-token

# Optional
LOG_LEVEL=INFO
DEFAULT_CSV_PATH=data/main_and_subtasks_multiple.csv
BATCH_SIZE=10
RETRY_ATTEMPTS=3
RETRY_DELAY=5
```

## 🧪 Testing

```bash
# Run basic functionality test
PYTHONPATH=src python test_basic_functionality.py

# Run full test suite
PYTHONPATH=src pytest tests/

# Run with coverage
PYTHONPATH=src pytest tests/ --cov=src --cov-report=html
```

## 🐛 Bug Fixes & Improvements

- Fixed SSL compatibility issues with urllib3
- Improved error messages and logging
- Added comprehensive input validation
- Enhanced CSV processing with better error handling
- Added retry logic for network failures
- Improved documentation and examples

## 📈 Performance

- Faster CSV processing with optimized validation
- Reduced API calls through better batching
- Improved error recovery reduces manual intervention
- Better memory usage with streaming CSV processing

## 🔮 What's Next

Future releases will include:
- GitHub Actions for automated testing and releases
- Docker containerization
- PyPI package distribution
- Advanced CSV templates and validation rules
- Bulk operations and progress tracking
- Integration with other Atlassian tools

## 🙏 Acknowledgments

- [Atlassian Python API](https://github.com/atlassian-api/atlassian-python-api) for Jira integration
- [Pydantic](https://pydantic-docs.helpmanual.io/) for data validation
- [Click](https://click.palletsprojects.com/) for CLI interface
- [Python community](https://www.python.org/community/) for best practices

---

**Download**: [Source code (zip)](https://github.com/star7js/jira-upload-csv/archive/v1.0.0.zip) | [Source code (tar.gz)](https://github.com/star7js/jira-upload-csv/archive/v1.0.0.tar.gz)

**Documentation**: [README.md](https://github.com/star7js/jira-upload-csv/blob/v1.0.0/README.md)

**Issues**: [Report a bug](https://github.com/star7js/jira-upload-csv/issues)

---

*This release represents a significant milestone in the project's development. Thank you for using Jira CSV Upload Tool! 🎉* 