#!/usr/bin/env python3
"""Enforce the human-review status gates (the pipeline's core promise).

Two status vocabularies exist (deliberately independent):
  course.yaml chapter : planned -> scripted -> built -> rendered -> approved
  markdown layers     : draft -> reviewed -> approved   (front matter `status:`)

A chapter's course.yaml status must not be ahead of what its markdown layers
have actually been reviewed for:

  scripted+ : concept and script files exist; concept is at least `reviewed`
              (the script was generated from it)
  built+    : script is at least `reviewed` (the scene was generated from it);
              the target scene file exists
  rendered+ : script is `approved` (only approved narration gets rendered)

Exit code is nonzero on any violation, so it can gate a render or run in CI.

Usage:  python tools/check_status.py [--project DIR]
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from provenance import split_fm, fm_get
from _project import project_parser, resolve_project, load_course, warn_if_not_project

CHAPTER_ORDER = ["planned", "scripted", "built", "rendered", "approved"]
LAYER_ORDER = ["draft", "reviewed", "approved"]


def clean(value):
    """Strip an inline `# comment` from a front-matter scalar."""
    return value.split("#")[0].strip() if value else value


def layer_status(path):
    """(status, problem) for a markdown layer; status None when unusable."""
    if not os.path.exists(path):
        return None, "missing"
    fm, _ = split_fm(open(path, encoding="utf-8").read())
    if fm is None:
        return None, "no front matter"
    st = clean(fm_get(fm, "status"))
    if st not in LAYER_ORDER:
        return None, f"unknown status {st!r}"
    return st, None


def at_least(status, floor):
    return LAYER_ORDER.index(status) >= LAYER_ORDER.index(floor)


def main():
    args = project_parser(__doc__).parse_args()
    root = resolve_project(args.project)
    chapters = load_course(root).get("chapters") or []
    if not chapters:
        warn_if_not_project(root)
        print("No chapters in course.yaml — nothing to status-check.")
        sys.exit(0)

    problems = []
    for ch in chapters:
        slug = ch.get("slug", "?")
        st = ch.get("status", "planned")
        if st not in CHAPTER_ORDER:
            problems.append(f"{slug}: unknown chapter status {st!r}")
            continue
        rank = CHAPTER_ORDER.index(st)
        if rank < CHAPTER_ORDER.index("scripted"):
            continue

        cpath = os.path.join(root, "content", f"{slug}.md")
        spath = os.path.join(root, "content", f"{slug}-script.md")
        c_st, c_err = layer_status(cpath)
        s_st, s_err = layer_status(spath)
        if c_err:
            problems.append(f"{slug}: status `{st}` but concept {c_err}")
        if s_err:
            problems.append(f"{slug}: status `{st}` but script {s_err}")
        if c_err or s_err:
            continue

        if not at_least(c_st, "reviewed"):
            problems.append(
                f"{slug}: status `{st}` but concept is `{c_st}` (needs reviewed+)")
        if rank >= CHAPTER_ORDER.index("built"):
            if not at_least(s_st, "reviewed"):
                problems.append(
                    f"{slug}: status `{st}` but script is `{s_st}` (needs reviewed+)")
            sfm, _ = split_fm(open(spath, encoding="utf-8").read())
            target = clean(fm_get(sfm, "target_scene_file"))
            if not target:
                problems.append(f"{slug}: status `{st}` but script has no target_scene_file")
            elif not os.path.exists(os.path.join(root, target)):
                problems.append(f"{slug}: status `{st}` but scene file missing: {target}")
        if rank >= CHAPTER_ORDER.index("rendered") and s_st != "approved":
            problems.append(
                f"{slug}: status `{st}` but script is `{s_st}` (rendering requires approved)")

    if problems:
        for p in problems:
            print(p)
        print(f"\n{len(problems)} status-gate violation(s).")
        sys.exit(1)
    print(f"Status gates OK across {len(chapters)} chapters.")
    sys.exit(0)


if __name__ == "__main__":
    main()
