# ag-devops plugin — convenience targets
#
# Usage:
#   make restore-symlinks   Restore all plugin symlinks from manifest
#   make test               Run the full test suite
#   make test-watch         Run tests in watch mode (requires pytest-watch)

PYTHON      := python
PYTEST      := pytest
SYMLINK_MGR := .agents/skills/symlink-manager/scripts/symlink_manager.py
SYMLINKS_JSON := plugins/ag-devops/symlinks.json
TESTS_DIR   := tests

.PHONY: restore-symlinks test test-watch

restore-symlinks:
	@echo "Restoring symlinks from $(SYMLINKS_JSON)..."
	$(PYTHON) $(SYMLINK_MGR) restore --manifest $(SYMLINKS_JSON)
	@echo "Done."

test:
	$(PYTEST) $(TESTS_DIR) -v

test-watch:
	$(PYTEST) $(TESTS_DIR) -v --watch
