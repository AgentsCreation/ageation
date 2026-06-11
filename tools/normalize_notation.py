#!/usr/bin/env python3
"""Rewrite disallowed notation in the LOCAL working copies (sources/).

This is the payoff of vendoring: when an upstream source uses notation that
conflicts with the project convention (course.yaml: notation.rules), we fix it
on the editable copy — the read-only parent is never touched, and provenance
still records where the copy came from.

Only operates on sources/*.tex and sources/*.md. Run tools/check_notation.py
afterwards to confirm, and tools/stamp_provenance.py to refresh hashes (the
copies changed).

Usage:
  python tools/normalize_notation.py [--project DIR]           # dry-run report
  python tools/normalize_notation.py [--project DIR] --write   # apply
"""

import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _project import project_parser, resolve_project, load_course, notation_rules


def main():
    parser = project_parser(__doc__)
    parser.add_argument("--write", action="store_true", help="apply the rewrites")
    args = parser.parse_args()
    root = resolve_project(args.project)
    rules = notation_rules(load_course(root))
    if not rules:
        print("No notation rules configured (course.yaml: notation.rules); nothing to do.")
        return

    files = sorted(
        glob.glob(os.path.join(root, "sources", "*.tex"))
        + glob.glob(os.path.join(root, "sources", "*.md"))
    )
    if not files:
        print("No sources/ working copies yet. Run tools/vendor_sources.py first.")
        return
    total = 0
    for path in files:
        text = open(path, encoding="utf-8").read()
        new, n = text, 0
        for rule in rules:
            k = new.count(rule["avoid"])
            if k:
                new = new.replace(rule["avoid"], rule["use"])
                n += k
        if n:
            total += n
            rel = os.path.relpath(path, root)
            print(f"{rel}: {n} replacement(s)")
            if args.write:
                open(path, "w", encoding="utf-8").write(new)
    if total == 0:
        print(f"Notation already clean in {len(files)} working copies.")
    elif not args.write:
        print(f"\n{total} change(s) pending. Re-run with --write to apply.")
    else:
        print(f"\nApplied {total} change(s). Now run tools/stamp_provenance.py.")


if __name__ == "__main__":
    main()
