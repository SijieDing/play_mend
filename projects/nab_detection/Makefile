####

ROOT_DIR ?= $(shell git rev-parse --show-toplevel)
ALL_PY_FILES ?= $(shell git ls-files "*.py")
PYPI_REPO ?= sys-z-aiops-unite-team-snapshot-pypi-virtual
PYPI_REPO_LOCAL ?= sys-z-aiops-unite-team-snapshot-pypi-local
URL := https://${GLOBAL_ZAIOPS_READ_USER_ID}:${GLOBAL_ZAIOPS_READ_USER_TOKEN}@na.artifactory.swg-devops.com/artifactory/api/pypi/$(PYPI_REPO)/simple
URL_LOCAL := https://na.artifactory.swg-devops.com/artifactory/api/pypi/$(PYPI_REPO_LOCAL)/simple
BRANCH_NAME = ${TRAVIS_PULL_REQUEST_BRANCH}
ifeq ($(BRANCH_NAME),)
	BRANCH_NAME = ${TRAVIS_BRANCH}
endif
ifeq ($(BRANCH_NAME),)
	BRANCH_NAME = $(shell git rev-parse --abbrev-ref HEAD)
endif
ifeq ($(BRANCH_NAME),develop)
	BUILD_VERSION =
else ifneq ($(TRAVIS_BUILD_NUMBER),)
	BUILD_VERSION = "$(BRANCH_NAME).${TRAVIS_BUILD_NUMBER}"
else
	BUILD_VERSION = "$(BRANCH_NAME)"
endif
BUILD_VERSION_SANITIZED := $(shell echo $(BUILD_VERSION) | sed 's/[^0-9a-zA-Z.]/./g')
ifeq ($(BUILD_VERSION_SANITIZED),)
	BUILD_VERSION_FULL =
else
	BUILD_VERSION_FULL = .dev0+$(BUILD_VERSION_SANITIZED)
endif

.PHONY: requirements
requirements: requirements-dev requirements-projects

requirements-dev: tolerate-local-build
	@pip install -e './[lint]' --no-cache-dir --index-url $(URL) 

requirements-projects:
	@pip install -e '.' --no-cache-dir --index-url $(URL)

.PHONY: lint
lint: lint-typechecking lint-imports format-python lint-python lint-doc

tolerate-local-build:
	@cat pyproject.toml | sed 's/"aiops_nab_detection==\([0-9.]\+[0-9]\)\(\?:.dev0\)\?.*"/"aiops_nab_detection==\1$(BUILD_VERSION_FULL)"/' pyproject.toml > pyproject.toml.new
	@mv pyproject.toml.new pyproject.toml
	@cat pyproject.toml | sed 's/"aiops_unite==\([0-9.]\+[0-9]\)\(\?:.dev0\)\?.*"/"aiops_unite==\1$(BUILD_VERSION_FULL)"/' pyproject.toml > pyproject.toml.new
	@mv pyproject.toml.new pyproject.toml
	@cat pyproject.toml
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

clean:
	@rm -fr *.zip

build: clean
	@cd "$(CURDIR)/scripts" && ./packaging.sh