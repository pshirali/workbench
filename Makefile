.DEFAULT_GOAL := help

.PHONY: test
test:                               ## Invoke tests
	@tests/test_wb.py -v

.PHONY: docs
docs:                               ## Open last built html docs
	@open docs/build/html/index.html

.PHONY: install-deps
install-deps:                       ## Install build tools and dependencies
	@pip3 install sphinx
	@pip3 install sphinx_rtd_theme

.PHONY: clean-docs
clean-docs:                         ## Remove docs/build folder
	@echo "Removing docs/build"
	@rm -rf docs/build

.PHONY: clean
clean: clean-docs                   ## Clean up all built data
	@echo "Done."

.PHONY: build-docs
build-docs: clean-docs              ## Build html documentation
	@cd docs && make html

.PHONY: build
build: install-deps build-docs      ## Install build dependencies and build
	@echo "Done."

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'
