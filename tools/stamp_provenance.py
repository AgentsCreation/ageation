#!/usr/bin/env python3
"""Stamp content-hash provenance into the markdown and scene layers.

For each chapter:
  content/{slug}.md         <- source_sha256 = hash of its vendored source
                               (+ companion_sha256 when a companion .md exists)
  content/{slug}-script.md  <- derived_from_sha256 = hash of {slug}.md
  scenes/{...}.py           <- `# derived_from_sha256:` header comment = hash of
                               the script (only refreshed when the scene already
                               carries the marker — the scene-from-script step
                               adds it at generation time; hand-built scenes
                               without it are reported by check_sync)

Each concept also records `framework_commit` — the git description of the
ageation checkout that performed the stamp — so a project (which lives
outside the framework repo) can tell which framework version built it.

Run this once now, and again after regenerating any layer, so the recorded
hashes describe the current snapshot. check_sync.py then detects drift.

Usage:  python tools/stamp_provenance.py [--project DIR]
"""

import datetime
import glob
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from provenance import sha256_file, sha256_script, split_fm, rebuild, fm_get, fm_upsert
from _project import project_parser, resolve_project

DATE = datetime.date.today().isoformat()

SCENE_SHA_RE = re.compile(r"(?m)^# derived_from_sha256:.*$")


def framework_version():
    """Git description of the framework checkout that performed this stamp.

    Projects live outside the framework repo (engine/content split), so the
    content hashes alone can't say which framework generated a snapshot. The
    `--dirty` suffix flags stamps made from an uncommitted framework tree.
    """
    fw_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try:
        r = subprocess.run(
            ["git", "-C", fw_root, "describe", "--always", "--dirty"],
            capture_output=True, text=True, timeout=10)
        return r.stdout.strip() or "unavailable"
    except Exception:
        return "unavailable"


FRAMEWORK = framework_version()


def stamp_scene(root, script_fm, script_path):
    """Refresh the scene's `# derived_from_sha256:` marker (when present).

    Only scenes that already carry the marker are touched: the marker is added
    by the scene-from-script step at generation time, so a hand-built scene is
    never silently claimed to derive from a script it predates.
    """
    target = fm_get(script_fm, "target_scene_file")
    if not target:
        return
    target = target.split("#")[0].strip()
    scene_abs = os.path.join(root, target)
    if not os.path.exists(scene_abs):
        return
    text = open(scene_abs, encoding="utf-8").read()
    if not SCENE_SHA_RE.search(text):
        if "# derived_from:" not in text:
            print(f"  WARN scene has no provenance marker: {target} "
                  f"(add `# derived_from:` lines; see PIPELINE.md)")
        return
    # sha256_script, not sha256_file: measured_* write-back lines are volatile
    # pipeline outputs and must not count as script drift.
    new = SCENE_SHA_RE.sub(
        f"# derived_from_sha256: {sha256_script(script_path)}", text, count=1)
    if new != text:
        open(scene_abs, "w", encoding="utf-8").write(new)


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
                fm = fm_upsert(fm, "framework_commit", FRAMEWORK,
                               after="provenance_stamped")
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
                stamp_scene(root, sfm, spath)
        stamped += 1
        print(f"  stamped {slug}")
    print(f"Done: {stamped} chapters stamped ({DATE}).")


if __name__ == "__main__":
    main()
