#!/usr/bin/env python3
"""Report whether the generated layers are in sync, by content hash.

Three links per chapter (content hashes, not git/mtime — robust across clones):
  upstream -> local   : did the read-only parent source move since we vendored
                        it? (compares hash of the upstream to the SHA recorded
                        in the local working copy's comment provenance header)
  local -> concept     : did the local working copy change since the concept?
                        (hash of sources/{slug}.tex vs concept's source_sha256;
                        when a companion .md is recorded, it is checked too and
                        the worse status wins)
  concept -> script    : did the concept change since the script?
                        (hash of concept .md vs script's derived_from_sha256)

A mismatch means that input changed since the layer was generated. Exit code is
nonzero if anything is stale/missing — usable as a pre-render gate.

Usage:  python tools/check_sync.py [--project DIR]
"""

import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from provenance import sha256_file, split_fm, fm_get
from _project import project_parser, resolve_project

OK, STALE, NOPROV, MISSING, NA = "in-sync", "STALE", "no-prov", "missing", "n/a"
NO_UP = "no-upstream"  # parent absent (e.g. input/ gitignored on a fresh clone)

# Worst-first ranking used when combining a source with its companion.
SEVERITY = [MISSING, NOPROV, STALE, NO_UP, OK, NA]


def worst(*statuses):
    return min(statuses, key=lambda s: SEVERITY.index(s) if s in SEVERITY else 0)


def header_field(local_abs, key):
    """Read a provenance-header field ('% key: v' or '<!-- key: v -->')."""
    txt = open(local_abs, encoding="utf-8").read()
    m = re.search(r"(?m)^(?:%|<!--)\s*" + re.escape(key) + r":\s*(.*?)\s*(?:-->)?$", txt)
    return m.group(1).strip() if m else None


def upstream_status(root, local_rel):
    local_abs = os.path.join(root, local_rel)
    if not os.path.exists(local_abs):
        return MISSING
    up = header_field(local_abs, "upstream")
    up_sha = header_field(local_abs, "upstream_sha256")
    if not up or not up_sha:
        return NOPROV
    up_abs = os.path.join(root, up)
    if not os.path.exists(up_abs):
        return NO_UP  # parent not present here; build still works from sources/
    return OK if sha256_file(up_abs) == up_sha else STALE


def hash_match(path, stored):
    if not stored:
        return NOPROV
    if not os.path.exists(path):
        return MISSING
    return OK if sha256_file(path) == stored else STALE


def main():
    args = project_parser(__doc__).parse_args()
    root = resolve_project(args.project)
    concepts = sorted(
        f for f in glob.glob(os.path.join(root, "content", "*.md"))
        if not f.endswith("-script.md")
    )
    if not concepts:
        print("No concept files under content/ — nothing to sync-check.")
        sys.exit(0)
    rows, bad = [], 0
    for cpath in concepts:
        slug = os.path.basename(cpath)[:-3]
        cfm, _ = split_fm(open(cpath).read())
        src = fm_get(cfm, "source") if cfm else None
        comp = fm_get(cfm, "companion") if cfm else None

        u2l = upstream_status(root, src) if (src and src.startswith("sources/")) else NA
        l2c = hash_match(os.path.join(root, src), fm_get(cfm, "source_sha256")) if src else NOPROV
        if comp:
            u2l = worst(u2l, upstream_status(root, comp))
            l2c = worst(l2c, hash_match(os.path.join(root, comp),
                                        fm_get(cfm, "companion_sha256")))

        spath = os.path.join(root, "content", slug + "-script.md")
        if os.path.exists(spath):
            sfm, _ = split_fm(open(spath).read())
            c2s = hash_match(cpath, fm_get(sfm, "derived_from_sha256")) if sfm else NOPROV
        else:
            c2s = "no-script"

        # A missing upstream is OK (input/ may be gitignored / absent); only a
        # genuine STALE/NOPROV upstream, or any downstream drift, counts.
        u_bad = u2l in (STALE, NOPROV, MISSING)
        d_bad = any(s in (STALE, NOPROV, MISSING) for s in (l2c, c2s))
        if u_bad or d_bad:
            bad += 1
        rows.append((slug, u2l, l2c, c2s))

    w = max(len(r[0]) for r in rows)
    print(f"{'chapter'.ljust(w)}   upstream->local  local->concept  concept->script")
    print("-" * (w + 50))
    for slug, u2l, l2c, c2s in rows:
        print(f"{slug.ljust(w)}   {u2l.ljust(15)}  {l2c.ljust(14)}  {c2s}")
    print("-" * (w + 50))
    print(f"{len(rows)} chapters, {bad} needing attention.")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
