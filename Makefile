.PHONY: help install install-dev test lint format clean build publish docs

help: ## Show this help message
	@echo "X-Pull-Request-Reviewer - Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install the package in development mode
	pip install -e .

install-dev: ## Install the package with development dependencies
	pip install -e ".[dev]"

test: ## Run tests
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing

lint: ## Run linting checks
	flake8 src/ tests/
	mypy src/

format: ## Format code with black
	black src/ tests/

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: ## Build the package
	python setup.py sdist bdist_wheel

publish: ## Publish to PyPI (requires twine)
	twine upload dist/*

docs: ## Build documentation
	mkdocs build

run: ## Run the agent
	python src/xprr_agent.py --help

docker-build: ## Build Docker image
	docker build -t xprr-agent .

docker-run: ## Run Docker container
	docker run -it --rm xprr-agent

check: format lint test ## Run all checks (format, lint, test) 