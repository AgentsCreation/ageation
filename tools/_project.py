"""Shared project-directory resolution and project.yaml loading.

Every pipeline tool operates on a *project directory* — a folder containing
project.yaml and the sources/, content/, scenes/ layout (plus input/ in the
standalone posture, or an `auto_manim/` subdirectory of a base repo in the
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
