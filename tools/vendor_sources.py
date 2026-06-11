#!/usr/bin/env python3
"""Vendor each upstream source into an editable local working copy.

Why: the upstream notes are read-only (a co-authored, possibly externally-synced
folder). To normalize notation or fix typos without touching the parent, we keep
an editable copy under sources/ and make THAT the pipeline's input. The copy
carries a comment provenance header recording where it came from — upstream
path, upstream SHA-256, and git origin/commit/tag when available (gracefully
"unavailable" when not, e.g. a detached clone).

Companion notes: when the upstream .tex has a sibling .md (a pandoc-style
high-level characterization of the same document), it is vendored too, as
sources/{slug}.md with an HTML-comment provenance header, and recorded in the
concept's front matter as `companion:`. The concept stage should read both —
the .md for intent/structure, the .tex for the authoritative content.

Effect per chapter:
  - create sources/{slug}.tex (header + verbatim upstream body) if absent
  - create sources/{slug}.md when an upstream companion exists
  - repoint content/{slug}.md front matter: source -> sources/{slug}.tex,
    recording upstream: <original path> (and companion/companion_upstream)

Run tools/stamp_provenance.py afterwards to refresh the hashes.

Usage:  python tools/vendor_sources.py [--project DIR]
"""

import datetime
import glob
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from provenance import sha256_file, split_fm, rebuild, fm_get, fm_upsert
from _project import project_parser, resolve_project

DATE = datetime.date.today().isoformat()


def git_info(file_abs):
    """Capture origin/commit/tag for the repo containing file_abs, or {}."""
    d = os.path.dirname(file_abs)

    def run(args):
        try:
            r = subprocess.run(["git", "-C", d] + args,
                               capture_output=True, text=True, timeout=10)
            return r.stdout.strip()
        except Exception:
            return ""

    if run(["rev-parse", "--is-inside-work-tree"]) != "true":
        return {}
    return {
        "git_origin": run(["config", "--get", "remote.origin.url"]) or "none",
        "git_commit": run(["rev-parse", "HEAD"]) or "none",
        "git_tag": run(["describe", "--tags", "--always", "--dirty"]) or "none",
    }


def header(upstream_rel, up_sha, gi, style="%"):
    """Provenance header. style '%' for .tex, 'html' for .md companions."""
    fields = [
        ("--- provenance (auto-added by tools/vendor_sources.py) ---", None),
        ("upstream", upstream_rel),
        ("upstream_sha256", up_sha),
    ]
    if gi:
        fields += [
            ("git_origin", gi["git_origin"]),
            ("git_commit", gi["git_commit"]),
            ("git_tag", gi["git_tag"]),
        ]
    else:
        fields += [("git", "unavailable (no repo / detached history)")]
    fields += [
        ("vendored_at", DATE),
        ("EDITABLE working copy. Normalize notation here; the parent stays read-only.", None),
        ("----------------------------------------------------------------", None),
    ]
    lines = []
    for key, val in fields:
        text = key if val is None else f"{key}: {val}"
        lines.append(f"<!-- {text} -->" if style == "html" else f"% {text}")
    return "\n".join(lines) + "\n"


def vendor_file(root, upstream_rel, local_rel):
    """Copy upstream into sources/ with a provenance header. True if usable."""
    up_abs = os.path.join(root, upstream_rel)
    if not os.path.exists(up_abs):
        print(f"  WARN upstream missing: {upstream_rel}")
        return False
    local_abs = os.path.join(root, local_rel)
    if not os.path.exists(local_abs):
        style = "html" if local_rel.endswith(".md") else "%"
        up_sha = sha256_file(up_abs)
        gi = git_info(up_abs)
        with open(local_abs, "w", encoding="utf-8") as f:
            f.write(header(upstream_rel, up_sha, gi, style))
            f.write(open(up_abs, encoding="utf-8").read())
    return True


def companion_upstream(upstream_rel):
    """Sibling .md next to an upstream .tex (the pandoc characterization)."""
    base, ext = os.path.splitext(upstream_rel)
    return base + ".md" if ext == ".tex" else None


def main():
    args = project_parser(__doc__).parse_args()
    root = resolve_project(args.project)
    os.makedirs(os.path.join(root, "sources"), exist_ok=True)
    concepts = sorted(
        f for f in glob.glob(os.path.join(root, "content", "*.md"))
        if not f.endswith("-script.md")
    )
    vendored = 0
    for cpath in concepts:
        slug = os.path.basename(cpath)[:-3]
        fm, body = split_fm(open(cpath).read())
        if fm is None:
            continue
        cur = fm_get(fm, "source")
        if not cur:
            print(f"  WARN no source in {slug}.md")
            continue
        if cur.startswith("sources/"):
            print(f"  already vendored: {slug}")
            continue

        local_rel = f"sources/{slug}.tex"
        if not vendor_file(root, cur, local_rel):
            continue

        # Repoint the concept to the local working copy.
        fm = fm_upsert(fm, "upstream", cur, after="source")
        fm = fm_upsert(fm, "source", local_rel)

        # Vendor a companion .md when the upstream has one.
        comp_up = companion_upstream(cur)
        if comp_up and os.path.exists(os.path.join(root, comp_up)):
            comp_rel = f"sources/{slug}.md"
            vendor_file(root, comp_up, comp_rel)
            fm = fm_upsert(fm, "companion_upstream", comp_up, after="upstream")
            fm = fm_upsert(fm, "companion", comp_rel, after="upstream")
            print(f"  companion {slug}  ->  {comp_rel}")

        open(cpath, "w").write(rebuild(fm, body))
        vendored += 1
        print(f"  vendored {slug}  ->  {local_rel}")

    print(f"Done: {vendored} sources vendored. Now run tools/stamp_provenance.py.")


if __name__ == "__main__":
    main()
