#!/usr/bin/env python3
"""Stamp content-hash provenance into the markdown layers.

For each chapter:
  content/{slug}.md         <- source_sha256 = hash of its vendored source
                               (+ companion_sha256 when a companion .md exists)
  content/{slug}-script.md  <- derived_from_sha256 = hash of {slug}.md

Run this once now, and again after regenerating any layer, so the recorded
hashes describe the current snapshot. check_sync.py then detects drift.

Usage:  python tools/stamp_provenance.py [--project DIR]
"""

import datetime
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from provenance import sha256_file, split_fm, rebuild, fm_get, fm_upsert
from _project import project_parser, resolve_project

DATE = datetime.date.today().isoformat()


def main():
    args = project_parser(__doc__).parse_args()
    root = resolve_project(args.project)
    concepts = sorted(
        f for f in glob.glob(os.path.join(root, "content", "*.md"))
        if not f.endswith("-script.md")
    )
    if not concepts:
        print("No concept files under content/ — nothing to stamp.")
        return
    stamped = 0
    for cpath in concepts:
        slug = os.path.basename(cpath)[:-3]
        fm, body = split_fm(open(cpath).read())
        if fm is None:
            print(f"  skip (no front matter): {slug}")
            continue

        src = fm_get(fm, "source")
        if not src:
            print(f"  WARN no `source:` in {slug}.md")
        else:
            sp = os.path.join(root, src)
            if not os.path.exists(sp):
                print(f"  WARN source missing for {slug}: {src}")
            else:
                fm = fm_upsert(fm, "source_sha256", sha256_file(sp), after="source")
                comp = fm_get(fm, "companion")
                if comp:
                    cp = os.path.join(root, comp)
                    if os.path.exists(cp):
                        fm = fm_upsert(fm, "companion_sha256", sha256_file(cp),
                                       after="companion")
                    else:
                        print(f"  WARN companion missing for {slug}: {comp}")
                fm = fm_upsert(fm, "provenance_stamped", DATE, after="source_sha256")
                open(cpath, "w").write(rebuild(fm, body))

        # Stamp the script layer against the (now updated) concept file.
        spath = os.path.join(root, "content", slug + "-script.md")
        if os.path.exists(spath):
            sfm, sbody = split_fm(open(spath).read())
            if sfm is not None:
                chash = sha256_file(cpath)
                sfm = fm_upsert(sfm, "derived_from_sha256", chash, after="derived_from")
                sfm = fm_upsert(sfm, "provenance_stamped", DATE, after="derived_from_sha256")
                open(spath, "w").write(rebuild(sfm, sbody))
        stamped += 1
        print(f"  stamped {slug}")
    print(f"Done: {stamped} chapters stamped ({DATE}).")


if __name__ == "__main__":
    main()
