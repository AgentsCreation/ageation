# Convenience targets for the video pipeline.  Run `make help`.
# All targets act on PROJECT (default: the repo root). Point them at another
# project dir with e.g. `make check PROJECT=examples/probability`.
# (Recipe lines are TAB-indented, as Make requires.)

PROJECT ?= .

.PHONY: help setup init sync notation status check stamp test render render-draft render-4k clean

help: ## List targets
	@grep -E '^[a-zA-Z0-9_-]+:.*?## ' $(MAKEFILE_LIST) | \
		awk 'BEGIN{FS=":.*?## "}{printf "  %-14s %s\n", $$1, $$2}'

setup: ## Install system deps (brew bundle) + Python env (uv sync)
	brew bundle
	uv sync

init: ## Bootstrap a draft course.yaml from INPUT (e.g. make init INPUT=input/MySubject)
	uv run python tools/init_course.py $(INPUT) --project $(PROJECT)

sync: ## Report upstream<->local<->concept<->script drift
	uv run python tools/check_sync.py --project $(PROJECT)

notation: ## Enforce the notation convention (course.yaml: notation.rules)
	uv run python tools/check_notation.py --project $(PROJECT)

status: ## Enforce the human-review status gates
	uv run python tools/check_status.py --project $(PROJECT)

check: sync notation status ## Run all gates (provenance + notation + review status)

stamp: ## Re-record provenance hashes after regenerating a layer
	uv run python tools/stamp_provenance.py --project $(PROJECT)

test: ## Run the tool test suite (no rendering involved)
	uv run python -m pytest tests/ -q

render: ## Render built chapters at 1080p60
	uv run python tools/render.py -q h --project $(PROJECT)

render-draft: ## Render built chapters at 480p (fast)
	uv run python tools/render.py -q l --project $(PROJECT)

render-4k: ## Render built chapters at 4K
	uv run python tools/render.py -q k --project $(PROJECT)

clean: ## Remove rendered output (regenerable from scenes/)
	rm -rf $(PROJECT)/media
