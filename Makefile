DEPS_MANAGER := uv
EXECUTOR := $(DEPS_MANAGER) run

.PHONY: help pc pre-commit pci pre-commit-install lint format lx fx lint-fix format-fix test

help: ## Show this help.
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z0-9_.-]+:.*##/ {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

pc: pre-commit ## Run pre-commit on all files
pre-commit:
	$(EXECUTOR) pre-commit run --all-files $(ARGS)

pci: pre-commit-install ## Install pre-commit hooks
pre-commit-install:
	$(EXECUTOR) pre-commit install $(ARGS)
	$(EXECUTOR) pre-commit install -t commit-msg $(ARGS)

lint: ## Lint code with ruff
	$(EXECUTOR) ruff check $(ARGS)

format: ## Check formatting with ruff
	$(EXECUTOR) ruff format --check $(ARGS)

x: lx fx ## Fix lint and formatting (ruff)

lx: lint-fix
lint-fix:
	$(EXECUTOR) ruff check --fix $(ARGS)

fx: format-fix
format-fix:
	$(EXECUTOR) ruff format $(ARGS)

test:
	$(EXECUTOR) pytest
