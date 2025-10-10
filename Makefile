# ---------------------- Project Config ---------------------- #
PROJECT_NAME := fastapi_genai_boilerplate
ENV_FILE := .env
PORT := $(shell grep ^PORT= $(ENV_FILE) | cut -d '=' -f2)
PYTHON := uv run python
UVICORN := uv run python main.py
PRECOMMIT := uv run pre-commit

.DEFAULT_GOAL := help

# ---------------------- Local Development ---------------------- #
.PHONY: run
run: ## Run FastAPI app in local dev mode (auto reload)
	uv run python main.py --env-file $(ENV_FILE)

.PHONY: shell
shell: ## Open Python shell inside uv virtual env
	$(PYTHON)

# ---------------------- Linting & Formatting ---------------------- #
.PHONY: format
format: ## Auto-fix imports, lint, and format code (isort + ruff + black)
	@echo "✨ Auto-formatting imports (isort)..."
	uv run isort . --profile black --line-length 88
	@echo "🧹 Auto-fixing lint issues (ruff)..."
	uv run ruff check . --fix
	@echo "🎨 Formatting code (black)..."
	uv run black . --line-length 88

.PHONY: lint
lint: ## Run static checks (ruff + mypy)
	@echo "🔍 Running Ruff lint checks..."
	uv run ruff check .
	@echo "🧠 Running Mypy type checks..."
	uv run mypy --config-file mypy.ini .

.PHONY: check
check: ## Run all pre-commit hooks on all files
	$(PRECOMMIT) run --all-files

.PHONY: install-hooks
install-hooks: ## Install pre-commit hooks
	$(PRECOMMIT) install

.PHONY: reinstall-hooks
reinstall-hooks: ## Reinstall and update pre-commit hooks
	uv run pre-commit uninstall
	uv run pre-commit install --install-hooks
	uv run pre-commit autoupdate

# ---------------------- Testing ---------------------- #
.PHONY: test
test: ## Run pytest suite if available
	@echo "🧪 Checking for tests..."
	@if ls tests/test_*.py >/dev/null 2>&1; then \
		echo "✅ Running pytest..."; \
		uv run pytest --disable-warnings -q; \
	else \
		echo "⚠️  No test files found. Skipping pytest."; \
	fi

# ---------------------- Cleanup ---------------------- #
.PHONY: clean
clean: ## Remove caches and temporary files
	@echo "🧽 Cleaning up build and cache files..."
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage dist build

# ---------------------- Docker ---------------------- #
.PHONY: docker-build
docker-build: ## Build the Docker image
	@echo "🐳 Building Docker image for $(PROJECT_NAME)..."
	docker build -t $(PROJECT_NAME):latest .

.PHONY: docker-run
docker-run: ## Run the Docker container
	@echo "🐳 Running Docker container on port $(PORT)..."
	docker run --rm -p $(PORT):$(PORT) $(PROJECT_NAME):latest

# ---------------------- Help ---------------------- #
.PHONY: help
help: ## Show all available Make targets
	@echo ""
	@echo "📘 Available Commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
