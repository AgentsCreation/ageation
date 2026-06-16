#!/usr/bin/env bash
# Render every buildable chapter listed in project.yaml (see tools/render.py)
# AND assemble each chapter's per-beat clips into a single reviewable .mp4
# (see tools/assemble.py). This matches `make video` and is the standard
# final step of the creation workflow.
#
# IMPORTANT: this must run on a machine with a working manim install — a cloud
# sandbox that cannot build manimpango cannot render. See PIPELINE.md.
#
# Usage:
#   ./render_all.sh              # high quality, 1080p60 (default)
#   ./render_all.sh k            # 4K, 2160p60   (overnight / final masters)
#   ./render_all.sh l            # 480p15 draft  (fast iteration)
#   ./render_all.sh l examples/probability   # render another project dir
#
# Per-beat clips land in <project>/media/videos/<scene_file>/<resolution>/.
# The reviewable deliverable lands at
# <project>/media/videos/<scene_file>/<resolution>/_assembled/<slug>.mp4.

set -euo pipefail
cd "$(dirname "$0")"

Q="${1:-h}"          # h = -qh (1080p60), k = -qk (4K), l = -ql (480p), m = 720p
PROJECT="${2:-.}"

uv run python tools/render.py -q "$Q" --project "$PROJECT"
uv run python tools/assemble.py -q "$Q" --project "$PROJECT"
