#!/usr/bin/env python3
"""Render the buildable chapters listed in course.yaml.

Replaces the old hand-maintained scene list: chapters whose status is
built/rendered/approved (and not marked `skip_render: true`) are rendered via
`uv run manim`. The scene file defaults to scenes/<slug minus its numeric
prefix, hyphens as underscores>.py and can be overridden per chapter with
`scene_file:`. Scene classes come from the chapter's videos[].scene_class
list; with no videos list the whole file is rendered (-a).

Rendering must run on a machine with a working manim (not a cloud sandbox
that cannot build manimpango).

Usage:
  python tools/render.py [--project DIR] [-q l|m|h|k] [slug ...]
  -q: l = 480p draft (default), m = 720p, h = 1080p60, k = 4K
"""

import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _project import project_parser, resolve_project, load_course

RENDERABLE = {"built", "rendered", "approved"}


def default_scene_file(slug: str) -> str:
    module = re.sub(r"^\d+-", "", slug).replace("-", "_")
    return f"scenes/{module}.py"


def main():
    parser = project_parser(__doc__)
    parser.add_argument("-q", "--quality", default="l", choices=list("lmhk"),
                        help="manim quality flag suffix (default: l, 480p draft)")
    parser.add_argument("slugs", nargs="*",
                        help="only these chapter slugs (default: all renderable)")
    parser.add_argument("--dry-run", action="store_true",
                        help="print the manim commands without running them")
    args = parser.parse_args()
    root = resolve_project(args.project)
    course = load_course(root)
    chapters = course.get("chapters") or []
    if not chapters:
        raise SystemExit("no chapters in course.yaml — nothing to render")

    selected = []
    for ch in chapters:
        slug = ch.get("slug", "")
        if args.slugs:
            if slug in args.slugs:
                selected.append(ch)
        elif ch.get("status") in RENDERABLE and not ch.get("skip_render"):
            selected.append(ch)
    if not selected:
        raise SystemExit("no renderable chapters (status built/rendered/approved, "
                         "or pass slugs explicitly)")

    failures = 0
    for ch in selected:
        slug = ch["slug"]
        scene_file = ch.get("scene_file") or default_scene_file(slug)
        if not os.path.exists(os.path.join(root, scene_file)):
            print(f"!!! {slug}: scene file missing: {scene_file}")
            failures += 1
            continue
        classes = [v["scene_class"] for v in ch.get("videos") or [] if v.get("scene_class")]
        cmd = ["uv", "run", "manim", f"-q{args.quality}", scene_file]
        cmd += classes if classes else ["-a"]
        if args.dry_run:
            print(f"would render {slug}: {' '.join(cmd)}")
            continue
        print(f">>> rendering {slug}: {' '.join(cmd)}")
        if subprocess.run(cmd, cwd=root).returncode != 0:
            print(f"!!! {slug}: render failed")
            failures += 1

    if not args.dry_run:
        print(f"Done: {len(selected) - failures}/{len(selected)} chapter(s) rendered; "
              f"videos under media/videos/.")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
