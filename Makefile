.PHONY: help install install-dev test test-cov lint format type-check clean build publish

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install pytest pytest-cov black flake8 mypy pre-commit

test: ## Run tests
	python -m pytest tests/ -v

test-cov: ## Run tests with coverage
	python -m pytest tests/ --cov=src --cov-report=html --cov-report=term

lint: ## Run linting
	flake8 src/ tests/
	black --check src/ tests/

format: ## Format code
	black src/ tests/

type-check: ## Run type checking
	mypy src/

clean: ## Clean up build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

build: ## Build package
	python -m build

publish: ## Publish to PyPI (requires twine)
	twine upload dist/*

setup-hooks: ## Setup pre-commit hooks
	pre-commit install

run-example: ## Run the tool with example data
	python cli.py upload --csv-file data/main_and_subtasks_multiple.csv

validate-example: ## Validate the example CSV file
	python cli.py validate --csv-file data/main_and_subtasks_multiple.csv

test-connection: ## Test Jira connection
	python cli.py test

show-config: ## Show current configuration
	python cli.py config

generate-template: ## Generate a template CSV file
	python cli.py template

all: format lint type-check test ## Run all checks (format, lint, type-check, test) 