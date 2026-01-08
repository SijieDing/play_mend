####

ROOT_DIR ?= $(shell git rev-parse --show-toplevel)
ALL_PY_FILES ?= $(shell git ls-files "*.py")

.PHONY: requirements
requirements: requirements-dev

requirements-dev:
	@pip install -e './[test,lint]' --index-url https://${GLOBAL_ZAIOPS_READ_USER_ID}:${GLOBAL_ZAIOPS_READ_USER_TOKEN}@na.artifactory.swg-devops.com/artifactory/api/pypi/${PYPI_REPO}/simple

.PHONY: lint
lint: lint-typechecking lint-imports format-python lint-python lint-doc

lint-typechecking:
	@pyright $(ALL_PY_FILES)
lint-imports:
	@isort --check-only $(ALL_PY_FILES)
format-python:
	@black --check $(ALL_PY_FILES)
lint-python:
	@flake8 $(ALL_PY_FILES)
lint-doc:
	@pylint $(ALL_PY_FILES)
