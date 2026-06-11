#!/usr/bin/env python3
"""Flag notation that violates the project convention.

The rules live as data in the project's course.yaml under `notation.rules`
(each rule: a literal LaTeX string to `avoid`, the form to `use`, and a short
`reason`). This scans content/*.md, scenes/*.py, and sources/*.{tex,md} for the
avoided forms and prints file:line: message for each. Exit code is nonzero if
any violation is found, so it can gate a render or run in CI.

Usage:  python tools/check_notation.py [--project DIR]
"""

import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _project import project_parser, resolve_project, load_course, notation_rules


def main():
    args = project_parser(__doc__).parse_args()
    root = resolve_project(args.project)
    rules = notation_rules(load_course(root))
    if not rules:
        print("No notation rules configured (course.yaml: notation.rules); nothing to check.")
        sys.exit(0)

    targets = sorted(
        glob.glob(os.path.join(root, "content", "*.md"))
        + glob.glob(os.path.join(root, "scenes", "*.py"))
        + glob.glob(os.path.join(root, "sources", "*.tex"))
        + glob.glob(os.path.join(root, "sources", "*.md"))
    )
    violations = 0
    for path in targets:
        rel = os.path.relpath(path, root)
        with open(path, encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                for rule in rules:
                    if rule["avoid"] in line:
                        msg = f"use {rule['use']} for {rule.get('reason', '?')}"
                        print(f"{rel}:{i}: {msg}  ->  {line.strip()[:70]}")
                        violations += 1
    if violations:
        print(f"\n{violations} notation violation(s). See the notation rules in course.yaml.")
        sys.exit(1)
    print(f"Notation OK across {len(targets)} files ({len(rules)} rules).")
    sys.exit(0)


if __name__ == "__main__":
    main()
