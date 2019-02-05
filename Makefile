.DEFAULT_GOAL := help

.PHONY: test
test:		## Invoke tests
	@echo "===[ bash --version ]==="
	@bash --version
	@echo
	@echo "===[ tests ]==="
	@tests/test_wb.py

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'
