#!/usr/bin/env python3
"""
Command-line interface for Jira CSV upload tool.
"""

import click
import sys
from pathlib import Path

from src.main import main as run_main
from src.config import jira_config, app_config


@click.group()
@click.version_option(version="1.1.0")
def cli():
    """Jira CSV Upload Tool - Create Jira issues and subtasks from CSV data."""
    pass


@cli.command()
@click.option(
    "--csv-file",
    "-f",
    type=click.Path(exists=True, path_type=Path),
    help="Path to CSV file (default: data/main_and_subtasks_multiple.csv)",
)
@click.option(
    "--log-level",
    "-l",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    default="INFO",
    help="Logging level (default: INFO)",
)
def upload(csv_file, log_level):
    """Upload issues and subtasks from CSV to Jira."""
    # Set log level
    app_config.log_level = log_level

    # Run the main process
    success = run_main(str(csv_file) if csv_file else None)

    if not success:
        click.echo("❌ Upload failed. Check the logs for details.", err=True)
        sys.exit(1)
    else:
        click.echo("✅ Upload completed successfully!")


@cli.command()
def test():
    """Test Jira connection and configuration."""
    click.echo("Testing Jira configuration...")

    try:
        # Validate configuration
        jira_config.validate()
        click.echo("✅ Configuration is valid")

        # Test connection
        from src.jira_client import JiraClient

        jira_client = JiraClient()

        if jira_client.test_connection():
            click.echo("✅ Successfully connected to Jira")
        else:
            click.echo("❌ Failed to connect to Jira")
            sys.exit(1)

    except Exception as e:
        click.echo(f"❌ Configuration error: {e}", err=True)
        sys.exit(1)


@cli.command()
def config():
    """Show current configuration."""
    click.echo("Current Configuration:")
    click.echo("=" * 30)

    click.echo(f"Jira Base URL: {jira_config.base_url}")
    click.echo(f"Jira Username: {jira_config.username}")
    token_display = (
        "*" * len(jira_config.password) if jira_config.password else "Not set"
    )
    click.echo(f"Jira API Token: {token_display}")
    click.echo(f"Log Level: {app_config.log_level}")
    click.echo(f"Default CSV Path: {app_config.default_csv_path}")
    click.echo(f"Batch Size: {app_config.batch_size}")
    click.echo(f"Retry Attempts: {app_config.retry_attempts}")
    click.echo(f"Retry Delay: {app_config.retry_delay} seconds")


@cli.command()
@click.option(
    "--csv-file",
    "-f",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to CSV file to validate",
)
def validate(csv_file):
    """Validate CSV file structure and data."""
    click.echo(f"Validating CSV file: {csv_file}")

    try:
        from src.csv_processor import CSVProcessor

        processor = CSVProcessor(str(csv_file))

        # Read and validate CSV
        rows = processor.read_and_validate_csv()
        click.echo(f"✅ CSV file is valid. Found {len(rows)} valid rows.")

        # Group and validate issue groups
        issue_groups = processor.get_issue_groups(rows)
        if processor.validate_issue_groups(issue_groups):
            click.echo(
                f"✅ Issue groups are valid. Found {len(issue_groups)} issue groups."
            )
        else:
            click.echo("❌ Issue groups validation failed.")
            sys.exit(1)

    except Exception as e:
        click.echo(f"❌ CSV validation failed: {e}", err=True)
        sys.exit(1)


@cli.command()
def template():
    """Generate a template CSV file."""
    # fmt: off
    template_content = """ID,Project Key,Summary,Description,Issue Type,Subtask Summary,Subtask Description
1,PROJ1,Main Issue 1,This is the first main issue,Task,Subtask 1.1,This is the first subtask for Main Issue 1
1,PROJ1,,,,Subtask 1.2,This is the second subtask for Main Issue 1
2,PROJ1,Main Issue 2,This is the second main issue,Task,Subtask 2.1,This is the first subtask for Main Issue 2
"""  # noqa: E501
    # fmt: on

    template_file = Path("template.csv")
    template_file.write_text(template_content)
    click.echo(f"✅ Template CSV file created: {template_file}")
    click.echo("Edit this file with your data and use the upload command.")


if __name__ == "__main__":
    cli()
