# Qt Framework - Project Makefile
# Modern Python project management with uv

# Detect if uv is available, fallback to pip for IDE compatibility
PYTHON := python
UV_EXISTS := $(shell uv --version 2>/dev/null)
ifdef UV_EXISTS
    INSTALLER := uv pip
    SYNC_CMD := uv pip sync
    RUN_PREFIX := uv run
else
    INSTALLER := $(PYTHON) -m pip
    SYNC_CMD := $(PYTHON) -m pip install -r
    RUN_PREFIX :=
endif

.PHONY: help
help:  ## Show this help message
	@echo "Qt Framework - Available Commands"
	@echo "================================="
	@echo ""
	@echo "Package Manager: $(if $(UV_EXISTS),uv detected ✓,pip fallback)"
	@echo ""
	@echo "Commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Usage: make [command]"

# === Installation ===

.PHONY: install
install:  ## Install project in development mode with all dependencies
ifdef UV_EXISTS
	uv pip install -e ".[dev,docs]"
	@echo "✓ Installed with uv (fast mode)"
else
	pip install -e ".[dev,docs]"
	@echo "✓ Installed with pip (compatibility mode)"
endif
	-pre-commit install 2>/dev/null

.PHONY: install-dev
install-dev:  ## Install only development dependencies
	$(INSTALLER) install -e ".[dev]"

.PHONY: install-docs
install-docs:  ## Install only documentation dependencies
	$(INSTALLER) install -e ".[docs]"

.PHONY: install-uv
install-uv:  ## Install/upgrade uv package manager
	curl -LsSf https://astral.sh/uv/install.sh | sh || \
	pip install --upgrade uv

.PHONY: sync
sync:  ## Sync dependencies with lock file (uv only)
ifdef UV_EXISTS
	uv pip sync requirements.txt 2>/dev/null || \
	uv pip install -e ".[dev,docs]"
else
	@echo "⚠ uv not found, using standard install instead"
	$(MAKE) install
endif

# === Code Quality ===

.PHONY: format
format:  ## Format code with ruff
	$(RUN_PREFIX) ruff format src tests examples

.PHONY: lint
lint:  ## Lint code with ruff
	$(RUN_PREFIX) ruff check src tests examples

.PHONY: lint-fix
lint-fix:  ## Lint and auto-fix issues with ruff
	$(RUN_PREFIX) ruff check --fix src tests examples

.PHONY: typecheck
typecheck:  ## Type check with mypy
	$(RUN_PREFIX) mypy src

.PHONY: check
check: format lint typecheck  ## Run all code quality checks

.PHONY: pre-commit
pre-commit:  ## Run pre-commit hooks on all files
	$(RUN_PREFIX) pre-commit run --all-files

# === Testing ===

.PHONY: test
test:  ## Run all tests
	$(RUN_PREFIX) pytest tests -v

.PHONY: test-fast
test-fast:  ## Run tests in parallel (faster)
	$(RUN_PREFIX) pytest tests -v -n auto

.PHONY: test-cov
test-cov:  ## Run tests with coverage report
	$(RUN_PREFIX) pytest tests \
		--cov=src/qtframework \
		--cov-report=term-missing \
		--cov-report=html \
		--cov-report=xml

.PHONY: test-watch
test-watch:  ## Run tests in watch mode
	$(RUN_PREFIX) pytest-watch tests

.PHONY: test-gui
test-gui:  ## Run GUI tests only
	$(RUN_PREFIX) pytest tests -v -m gui

.PHONY: test-unit
test-unit:  ## Run unit tests only (no GUI)
	$(RUN_PREFIX) pytest tests -v -m "not gui"

.PHONY: test-failed
test-failed:  ## Re-run only failed tests
	$(RUN_PREFIX) pytest tests -v --lf

# === Documentation ===

SPHINXOPTS    ?=
SPHINXBUILD   := $(RUN_PREFIX) sphinx-build
SOURCEDIR     := docs
BUILDDIR      := docs/_build

.PHONY: docs
docs:  ## Build HTML documentation
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)
	@echo "✓ Documentation built at docs/_build/html/index.html"

.PHONY: docs-live
docs-live:  ## Serve documentation with live reload
	$(RUN_PREFIX) sphinx-autobuild "$(SOURCEDIR)" "$(BUILDDIR)/html" \
		--ignore "*~" \
		--ignore "*.swp" \
		--ignore ".git/*" \
		--ignore "_build/*" \
		--ignore "*.pyc" \
		--open-browser

.PHONY: docs-api
docs-api:  ## Generate API documentation from source
	$(RUN_PREFIX) sphinx-apidoc -o docs/api/generated src/qtframework \
		--force \
		--module-first \
		--separate \
		--implicit-namespaces

.PHONY: docs-clean
docs-clean:  ## Clean documentation build files
	rm -rf $(BUILDDIR)
	rm -rf docs/api/generated
	@echo "✓ Documentation cleaned"

.PHONY: docs-linkcheck
docs-linkcheck:  ## Check all external links in documentation
	@$(SPHINXBUILD) -M linkcheck "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)

.PHONY: docs-pdf
docs-pdf:  ## Build PDF documentation (requires LaTeX)
	@$(SPHINXBUILD) -M latexpdf "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)

.PHONY: docs-changes
docs-changes:  ## Show documentation changes
	@$(SPHINXBUILD) -M changes "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)

# === Running the Application ===

.PHONY: run
run:  ## Run the example Qt application
	$(RUN_PREFIX) $(PYTHON) examples/features/main.py

.PHONY: run-dev
run-dev:  ## Run with development settings (hot reload)
	QTFRAMEWORK_ENV=development \
	QTFRAMEWORK_DEBUG=1 \
	$(RUN_PREFIX) $(PYTHON) examples/features/main.py --reload

.PHONY: demo
demo: run  ## Alias for 'run' - start the demo application

# === Build & Distribution ===

.PHONY: build
build:  ## Build distribution packages (wheel and sdist)
ifdef UV_EXISTS
	uv build
else
	$(PYTHON) -m build
endif

.PHONY: build-wheel
build-wheel:  ## Build wheel distribution only
ifdef UV_EXISTS
	uv build --wheel
else
	$(PYTHON) -m build --wheel
endif

.PHONY: build-sdist
build-sdist:  ## Build source distribution only
ifdef UV_EXISTS
	uv build --sdist
else
	$(PYTHON) -m build --sdist
endif

.PHONY: publish-test
publish-test:  ## Publish to TestPyPI (test distribution)
ifdef UV_EXISTS
	uv publish --publish-url https://test.pypi.org/legacy/
else
	$(PYTHON) -m twine upload --repository testpypi dist/*
endif

.PHONY: publish
publish:  ## Publish to PyPI (requires credentials)
ifdef UV_EXISTS
	uv publish
else
	$(PYTHON) -m twine upload dist/*
endif

# === Cleaning ===

.PHONY: clean
clean: clean-pyc clean-test clean-build docs-clean  ## Clean all generated files
	@echo "✓ All clean!"

.PHONY: clean-pyc
clean-pyc:  ## Clean Python cache files
	find . -type f -name '*.py[co]' -delete
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '*egg-info' -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Python cache cleaned"

.PHONY: clean-test
clean-test:  ## Clean test and coverage files
	rm -rf .coverage coverage.xml htmlcov
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	rm -rf .hypothesis
	@echo "✓ Test artifacts cleaned"

.PHONY: clean-build
clean-build:  ## Clean build artifacts
	rm -rf build dist *.egg-info
	rm -rf src/*.egg-info
	@echo "✓ Build artifacts cleaned"

# === Internationalization (i18n) ===

.PHONY: i18n-extract
i18n-extract:  ## Extract translatable strings
	$(RUN_PREFIX) pybabel extract -F babel.cfg -o locales/messages.pot src/qtframework

.PHONY: i18n-update
i18n-update:  ## Update translation files
	$(RUN_PREFIX) pybabel update -i locales/messages.pot -d locales

.PHONY: i18n-compile
i18n-compile:  ## Compile translation files
	$(RUN_PREFIX) pybabel compile -d locales

.PHONY: i18n-init
i18n-init:  ## Initialize new language (use LANG=xx_XX)
	$(RUN_PREFIX) pybabel init -i locales/messages.pot -d locales -l $(LANG)

# === Development Utilities ===

.PHONY: shell
shell:  ## Open interactive Python shell with project context
	$(RUN_PREFIX) $(PYTHON) -c "from qtframework import *; import IPython; IPython.embed()"

.PHONY: repl
repl:  ## Open Python REPL with qtframework imported
	$(RUN_PREFIX) $(PYTHON) -i -c "from qtframework import *; print('Qt Framework loaded')"

.PHONY: tree
tree:  ## Show project structure
	tree -I '__pycache__|*.pyc|.git|.pytest_cache|.mypy_cache|*.egg-info|htmlcov|dist|build|.ruff_cache' --dirsfirst

.PHONY: todo
todo:  ## Find all TODO/FIXME/HACK comments
	@grep -r "TODO\|FIXME\|HACK" src tests examples \
		--exclude-dir=__pycache__ \
		--exclude-dir=.git \
		--exclude="*.pyc" || echo "No TODOs found ✓"

# === Continuous Integration ===

.PHONY: ci
ci: check test docs  ## Run full CI pipeline locally
	@echo "✓ CI pipeline passed!"

.PHONY: ci-fast
ci-fast: lint test-unit  ## Run fast CI checks (no GUI tests)
	@echo "✓ Fast CI checks passed!"

.PHONY: ci-full
ci-full: install check test-cov docs  ## Run complete CI with coverage
	@echo "✓ Full CI pipeline passed!"

# === Dependencies Management ===

.PHONY: deps-upgrade
deps-upgrade:  ## Upgrade all dependencies to latest versions
ifdef UV_EXISTS
	uv pip install --upgrade -e ".[dev,docs]"
	uv pip list --outdated
else
	$(INSTALLER) install --upgrade -e ".[dev,docs]"
	$(INSTALLER) list --outdated
endif

.PHONY: deps-tree
deps-tree:  ## Show dependency tree
ifdef UV_EXISTS
	uv pip tree
else
	$(INSTALLER) install pipdeptree
	$(PYTHON) -m pipdeptree
endif

.PHONY: deps-check
deps-check:  ## Check for security vulnerabilities
ifdef UV_EXISTS
	uv pip audit || echo "Install 'pip-audit' for security scanning"
else
	$(INSTALLER) install pip-audit
	$(PYTHON) -m pip_audit
endif

# === Git Hooks ===

.PHONY: hooks-install
hooks-install:  ## Install pre-commit hooks
	$(RUN_PREFIX) pre-commit install
	$(RUN_PREFIX) pre-commit install --hook-type commit-msg

.PHONY: hooks-update
hooks-update:  ## Update pre-commit hooks to latest versions
	$(RUN_PREFIX) pre-commit autoupdate

.PHONY: hooks-run
hooks-run:  ## Run pre-commit hooks on all files
	$(RUN_PREFIX) pre-commit run --all-files

# === Performance ===

.PHONY: profile
profile:  ## Profile the application (requires py-spy)
	$(RUN_PREFIX) py-spy record -o profile.svg -- \
		$(PYTHON) examples/features/main.py

.PHONY: bench
bench:  ## Run performance benchmarks
	$(RUN_PREFIX) pytest tests -v --benchmark-only 2>/dev/null || \
		echo "No benchmarks found. Add pytest-benchmark to run benchmarks."

# === Project Info ===

.PHONY: info
info:  ## Show project information
	@echo "Qt Framework Project Information"
	@echo "================================"
	@echo "Python:      $$($(PYTHON) --version)"
	@echo "Location:    $$(pwd)"
	@echo "Package:     src/qtframework"
ifdef UV_EXISTS
	@echo "UV Version:  $$(uv --version)"
	@echo "Installer:   uv (fast mode)"
else
	@echo "Installer:   pip (compatibility mode)"
endif
	@echo ""
	@echo "Quick Start:"
	@echo "  make install  - Install all dependencies"
	@echo "  make run      - Run the demo application"
	@echo "  make test     - Run all tests"
	@echo "  make docs     - Build documentation"

# === Default target ===
.DEFAULT_GOAL := help
