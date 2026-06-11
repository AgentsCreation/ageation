"""Shared project-directory resolution and course.yaml loading.

Every pipeline tool operates on a *project directory* — a folder containing
course.yaml and the input/, sources/, content/, scenes/ layout. Tools take
--project <dir> (default: the current directory), so the same tools drive the
root workspace or any project under examples/.
"""

import argparse
import os

import yaml


def project_parser(description: str) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=description)
    p.add_argument(
        "--project",
        default=".",
        help="project directory containing course.yaml (default: current dir)",
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
    has_course = os.path.exists(os.path.join(project_root, "course.yaml"))
    has_content = os.path.isdir(os.path.join(project_root, "content"))
    if not has_course and not has_content:
        print(f"WARNING: {project_root} has no course.yaml or content/ — "
              "fresh workspace, or wrong --project dir?")


def load_course(project_root: str) -> dict:
    """Parse <project>/course.yaml, or {} if it does not exist yet."""
    path = os.path.join(project_root, "course.yaml")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def notation_rules(course: dict) -> list[dict]:
    """The notation.rules list: dicts with literal `avoid`/`use`/`reason`.

    Validates the shape so a malformed course.yaml fails with a clear message
    instead of a KeyError deep inside a checker.
    """
    rules = (course.get("notation") or {}).get("rules") or []
    if not isinstance(rules, list):
        raise SystemExit("course.yaml: notation.rules must be a list")
    for i, rule in enumerate(rules):
        if (not isinstance(rule, dict)
                or not isinstance(rule.get("avoid"), str) or not rule["avoid"]
                or not isinstance(rule.get("use"), str) or not rule["use"]):
            raise SystemExit(
                f"course.yaml: notation.rules[{i}] needs non-empty string "
                f"`avoid` and `use` keys (got: {rule!r})")
    return rules
