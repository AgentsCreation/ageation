#!/usr/bin/env python3
"""Generate ``site/data/site.json`` for the ageation site.

Mirrors the probability repo's site workflow: a deterministic generator turns
repo content into a single JSON file the static site loads. Here the content
is the engine itself — the toolbox (every public tool under tools/ with the
first line of its docstring) and the engine version — so the "under the hood"
strip on the site stays current with the repo automatically.

Stdlib only (no third-party deps), idempotent and diff-friendly: same inputs
produce byte-identical output.

Run:  python3 scripts/site_data.py   (or ``just web-data``)
"""

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = REPO_ROOT / "tools"
SITE_DATA = REPO_ROOT / "site" / "data" / "site.json"

# The pipeline's layer spine, as documented in PIPELINE.md. Kept here (not
# parsed from prose) because it is the engine's stable public contract.
LAYERS = [
    {"name": "source", "summary": "the upstream LaTeX notes, vendored into an editable copy with a provenance header"},
    {"name": "concept", "summary": "what is worth animating — a reviewed concept map per chapter"},
    {"name": "script", "summary": "narration, beats, and a runtime contract; the source of truth for timing"},
    {"name": "scene", "summary": "generated Manim code — one voiceover scene per beat"},
    {"name": "build", "summary": "render, assemble, and measure: one reviewable .mp4 per chapter"},
]


def engine_version() -> str:
    try:
        r = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "describe", "--always"],
            capture_output=True, text=True, timeout=10,
        )
        return r.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def tool_summary(path: Path) -> str | None:
    """First line of the module docstring, or None when there is none."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return None
    doc = ast.get_docstring(tree)
    if not doc:
        return None
    first = doc.strip().splitlines()[0].strip()
    return first.rstrip(".") + "." if first else None


# Shared libraries that live in tools/ without a leading underscore.
INTERNAL = {"provenance"}


def collect_tools() -> list[dict]:
    tools = []
    for path in sorted(TOOLS_DIR.glob("*.py")):
        if path.name.startswith("_") or path.stem in INTERNAL:
            continue  # shared libraries, not user-facing tools
        summary = tool_summary(path)
        if summary:
            tools.append({"name": path.stem, "summary": summary})
    return tools


def main() -> int:
    data = {
        "version": engine_version(),
        "layers": LAYERS,
        "tools": collect_tools(),
    }
    SITE_DATA.parent.mkdir(parents=True, exist_ok=True)
    SITE_DATA.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"wrote {SITE_DATA.relative_to(REPO_ROOT)}  "
          f"layers: {len(LAYERS)}  tools: {len(data['tools'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
