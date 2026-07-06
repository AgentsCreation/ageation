"""Shared project-directory resolution and project.yaml loading.

Every pipeline tool operates on a *project directory* — a folder containing
project.yaml and the sources/, content/, scenes/ layout (plus input/ in the
standalone posture, or an `ageation/` subdirectory of a base repo in the
embedded posture). Tools take --project <dir> (default: the current
directory), so the same tools drive the root workspace, any project under
examples/, or a sibling/base repo.
"""

import argparse
import os

import yaml


def project_parser(description: str) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=description)
    p.add_argument(
        "--project",
        default=".",
        help="project directory containing project.yaml (default: current dir)",
    )
    return p


def resolve_project(path: str) -> str:
    root = os.path.abspath(path)
    if not os.path.isdir(root):
        raise SystemExit(f"project directory not found: {root}")
    return root


def warn_if_not_project(project_root: str) -> None:
    """Loud warning when a gate runs somewhere that has no project layout.

    The gates pass vacuously on an empty directory (correct for a fresh
    workspace), but that also makes a mistyped-yet-existing --project pass
    silently — so make the situation visible.
    """
    has_manifest = os.path.exists(os.path.join(project_root, "project.yaml"))
    has_content = os.path.isdir(os.path.join(project_root, "content"))
    if not has_manifest and not has_content:
        print(f"WARNING: {project_root} has no project.yaml or content/ — "
              "fresh workspace, or wrong --project dir?")


def load_project(project_root: str) -> dict:
    """Parse <project>/project.yaml, or {} if it does not exist yet."""
    path = os.path.join(project_root, "project.yaml")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def yaml_scalar(value) -> str:
    r"""Render `value` as a YAML scalar safe to drop into a mapping-value slot.

    The manifests and layer front matter are hand-interpolated (kept readable,
    with inline comments) rather than emitted through yaml.safe_dump, so a
    content-derived string like ``Graphical Models: A Quick Tour`` would slip an
    unescaped ``:`` into the YAML and break every later yaml.safe_load. This
    quotes exactly the values a plain scalar would misparse -- colons, leading
    indicators, and bool/number/null look-alikes -- single-quoting and doubling
    any embedded quote; safe strings (the common case) pass through unquoted so
    generated files stay readable.
    """
    s = "" if value is None else str(value)
    try:
        plain_ok = (yaml.safe_load(s) == s) and s == s.strip() and "\n" not in s
    except yaml.YAMLError:
        plain_ok = False
    if plain_ok:
        return s
    return "'" + s.replace("'", "''") + "'"


def parse_dotenv(path: str) -> dict:
    """Minimal .env parser: KEY=VALUE per line, # comments and blanks skipped.

    Avoids adding python-dotenv as a dep; the file format is simple enough.
    Quoted values (single or double) are stripped of their surrounding quotes.
    """
    if not os.path.exists(path):
        return {}
    out = {}
    for raw in open(path, encoding="utf-8"):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in {"'", '"'}:
            val = val[1:-1]
        if key:
            out[key] = val
    return out


def notation_rules(manifest: dict) -> list[dict]:
    """The notation.rules list: dicts with literal `avoid`/`use`/`reason`.

    Validates the shape so a malformed project.yaml fails with a clear message
    instead of a KeyError deep inside a checker.
    """
    rules = (manifest.get("notation") or {}).get("rules") or []
    if not isinstance(rules, list):
        raise SystemExit("project.yaml: notation.rules must be a list")
    for i, rule in enumerate(rules):
        if (not isinstance(rule, dict)
                or not isinstance(rule.get("avoid"), str) or not rule["avoid"]
                or not isinstance(rule.get("use"), str) or not rule["use"]):
            raise SystemExit(
                f"project.yaml: notation.rules[{i}] needs non-empty string "
                f"`avoid` and `use` keys (got: {rule!r})")
    return rules


# --- Project shapes ----------------------------------------------------------
# A "shape" is the kind of source the project distills into video. It binds
# planning conventions: how the chapter spine is structured, default
# narration pace, whether a recap line belongs in the intro_card. Tools and
# skills branch on it. See PIPELINE.md "Project shapes" for the full table.

PROJECT_SHAPES = {
    "article": {"voice_rate": 1.25, "recap_prior": False,
                "target_minutes_per_video": 10,
                "default_chapter_count": 1,
                "summary": "single video distilling an article (e.g. arXiv paper)"},
    "book":    {"voice_rate": 1.15, "recap_prior": True,
                "target_minutes_per_video": 8,
                "default_chapter_count": None,  # one per book chapter
                "summary": "one video per book chapter, multi-video series"},
    "course":  {"voice_rate": 1.0,  "recap_prior": True,
                "target_minutes_per_video": 6,
                "default_chapter_count": None,
                "summary": "many chapters with optional videos[] sublists"},
    "session": {"voice_rate": 1.25, "recap_prior": False,
                "target_minutes_per_video": 10,
                "default_chapter_count": 1,
                "summary": "(planned) synthesize a Claude Code session into a video"},
}
DEFAULT_SHAPE = "article"  # the most common case — single video distilling one source


def project_shape(manifest: dict) -> str:
    """Return the validated shape string for a project manifest.

    Falls back to DEFAULT_SHAPE when `project.shape` is absent. `article` is
    the default because single-video standalone is the most common case;
    declare `shape: book` or `shape: course` only when the project really
    fans out into a series. An unknown explicit shape is a hard error.
    """
    shape = (manifest.get("project") or {}).get("shape")
    if shape is None:
        return DEFAULT_SHAPE
    if shape not in PROJECT_SHAPES:
        known = ", ".join(sorted(PROJECT_SHAPES))
        raise SystemExit(
            f"project.yaml: unknown project.shape {shape!r} (known: {known})")
    return shape


def shape_defaults(shape: str) -> dict:
    """The default convention bundle for a shape; explicit YAML wins over these."""
    return PROJECT_SHAPES[shape]
