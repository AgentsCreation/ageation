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


def load_course(project_root: str) -> dict:
    """Parse <project>/course.yaml, or {} if it does not exist yet."""
    path = os.path.join(project_root, "course.yaml")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def notation_rules(course: dict) -> list[dict]:
    """The notation.rules list: dicts with literal `avoid`/`use`/`reason`."""
    return (course.get("notation") or {}).get("rules") or []
