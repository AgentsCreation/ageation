# Convenience targets for the video pipeline.  Run `make help`.
# All targets act on PROJECT (default: the repo root). Point them at another
# project dir with e.g. `make check PROJECT=examples/probability`.
# (Recipe lines are TAB-indented, as Make requires.)

PROJECT ?= .
SPEED   ?= 1.0    # playback speed multiplier for assemble (1.0 = native)

.PHONY: help setup install-skills init sync notation status check stamp measure doctor lint-scene lint-style lint-language test render render-draft render-4k assemble assemble-draft assemble-4k video video-draft video-4k clean clean-cache

help: ## List targets
	@grep -E '^[a-zA-Z0-9_-]+:.*?## ' $(MAKEFILE_LIST) | \
		awk 'BEGIN{FS=":.*?## "}{printf "  %-14s %s\n", $$1, $$2}'

setup: ## Install system deps (brew bundle) + Python env (uv sync)
	brew bundle
	uv sync

install-skills: ## Copy the versioned processor skills into .claude/skills (Claude Code loads them from there)
	mkdir -p .claude/skills
	cp -R skills/ .claude/skills/

init: ## Bootstrap a draft project.yaml from INPUT (e.g. make init INPUT=input/MySubject)
	uv run python tools/init_project.py $(INPUT) --project $(PROJECT)

sync: ## Report upstream<->local<->concept<->script drift
	uv run python tools/check_sync.py --project $(PROJECT)

notation: ## Enforce the notation convention (project.yaml: notation.rules)
	uv run python tools/check_notation.py --project $(PROJECT)

status: ## Enforce the human-review status gates
	uv run python tools/check_status.py --project $(PROJECT)

check: sync notation status lint-style lint-language ## Run all gates (provenance + notation + review status + style/language warnings)

lint-style: ## Static STYLE_BOOK lint over scenes/*.py (warning-only; --strict gates)
	uv run python tools/lint_style.py --project $(PROJECT)

lint-language: ## Register lint over narration + on-screen text (video numbers, terminology, sentence length)
	uv run python tools/lint_language.py --project $(PROJECT)

stamp: ## Re-record provenance hashes after regenerating a layer
	uv run python tools/stamp_provenance.py --project $(PROJECT)

measure: ## ffprobe rendered beats, write measured_sec back into script front matter
	uv run python tools/measure_runtime.py --project $(PROJECT)

test: ## Run the tool test suite (no rendering involved)
	uv run python -m pytest tests/ -q

doctor: ## Preflight: project.yaml, env, ffmpeg, latex, OPENAI_API_KEY when needed
	uv run python tools/doctor.py --project $(PROJECT)

lint-scene: ## Geometric scene lint — bbox overlaps after every play(); gates `video`, not `render`
	uv run python tools/lint_scene.py --project $(PROJECT)

# Each render target preflights at the SAME quality it renders, so the doctor
# key check matches reality: a draft (-q l) forces the free gtts voice and
# needs no OPENAI_API_KEY, while finals do (see tools/doctor.py, render.py).
render: ## Render built chapters at 1080p60
	uv run python tools/doctor.py -q h --project $(PROJECT)
	uv run python tools/render.py -q h --project $(PROJECT)

render-draft: ## Render built chapters at 480p (fast)
	uv run python tools/doctor.py -q l --project $(PROJECT)
	uv run python tools/render.py -q l --project $(PROJECT)

render-4k: ## Render built chapters at 4K
	uv run python tools/doctor.py -q k --project $(PROJECT)
	uv run python tools/render.py -q k --project $(PROJECT)

assemble: ## Stitch per-scene .mp4 files of each chapter into one video (1080p60). SPEED= overrides 1.0x.
	uv run python tools/assemble.py -q h --speed $(SPEED) --project $(PROJECT)

assemble-draft: ## Stitch per-scene .mp4 files of each chapter into one video (480p). SPEED= overrides 1.0x.
	uv run python tools/assemble.py -q l --speed $(SPEED) --project $(PROJECT)

assemble-4k: ## Stitch per-scene .mp4 files of each chapter into one video (4K). SPEED= overrides 1.0x.
	uv run python tools/assemble.py -q k --speed $(SPEED) --project $(PROJECT)

# `video`, `video-draft`, `video-4k`: render every scene AND stitch them into
# one .mp4 per chapter. The per-scene clips remain on disk (under
# media/videos/.../<quality>/<SceneClass>.mp4) so iterating on a single beat
# is still cheap; the deliverable single video lives next to them under
# .../<quality>/_assembled/<slug>.mp4.

video: lint-scene render assemble ## Render + assemble: one .mp4 per chapter at 1080p60
	@echo
	@echo "Single-video output(s) at:"
	@find $(PROJECT)/media/videos -path '*/1080p60/_assembled/*.mp4' 2>/dev/null

video-draft: lint-scene render-draft assemble-draft ## Render + assemble at 480p (fast)
	@echo
	@echo "Single-video output(s) at:"
	@find $(PROJECT)/media/videos -path '*/480p15/_assembled/*.mp4' 2>/dev/null

video-4k: lint-scene render-4k assemble-4k ## Render + assemble at 4K
	@echo
	@echo "Single-video output(s) at:"
	@find $(PROJECT)/media/videos -path '*/2160p60/_assembled/*.mp4' 2>/dev/null

clean: ## Remove rendered output (regenerable from scenes/)
	rm -rf $(PROJECT)/media

clean-cache: ## Prune partial_movie_files render fragments; keeps per-scene mp4s, _assembled/, voiceovers
	uv run python tools/clean_cache.py --project $(PROJECT)
