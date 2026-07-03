#!/usr/bin/env python3
"""Write measured beat durations back into each chapter's script front matter.

The script layer carries a timing contract (`target_runtime_sec`,
`tolerance_sec`) and placeholders the render stage was always meant to fill
(`measured_sec` per beat, `measured_runtime_sec` total). This tool closes
that loop: it ffprobes each beat's rendered per-scene .mp4 and rewrites the
placeholder lines in place, so check_status can enforce the tolerance
instead of a human eyeballing the runtime.

The write-back is a targeted line rewrite, not a YAML round-trip: the beats
block is machine-templated, and re-dumping the whole front matter would
destroy its hand-written comments. Provenance stays green because scripts
are hashed with sha256_script (measured_* lines removed) -- see
provenance.py.

Runs automatically after a successful assemble (tools/assemble.py); also
available standalone as `make measure`.

Usage:
  python tools/measure_runtime.py [--project DIR] [-q l|m|h|k] [slug ...]
"""

import os
import re
import subprocess
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _project import project_parser, resolve_project, load_project
from provenance import split_fm, rebuild
from assemble import QUALITY_DIR, RENDERABLE, default_scene_file, scene_module_stem


def probe_duration(path: str) -> float | None:
    """Container duration in seconds via ffprobe, or None when unreadable."""
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True)
    if r.returncode != 0:
        return None
    try:
        return float(r.stdout.strip())
    except ValueError:
        return None


def script_beat_list(root: str, slug: str):
    """Full beat dicts from the script front matter (yaml-parsed), or None."""
    spath = os.path.join(root, "content", f"{slug}-script.md")
    if not os.path.exists(spath):
        return None, spath
    fm_text, _ = split_fm(open(spath, encoding="utf-8").read())
    if fm_text is None:
        return None, spath
    fm = yaml.safe_load(fm_text)
    if not isinstance(fm, dict):
        return None, spath
    beats = [b for b in (fm.get("beats") or []) if isinstance(b, dict)]
    return beats, spath


def upsert_measured(fm_text: str, per_beat: dict[str, float], total: float) -> str:
    """Rewrite measured_sec per beat (keyed by beat id) + measured_runtime_sec.

    Line-targeted so every hand-written comment in the front matter survives.
    A beat block runs from its `- id:` line to the next `- ` item at the same
    indent or the next top-level key.
    """
    lines = fm_text.split("\n")

    def beat_bounds(beat_id: str):
        start = None
        item_re = re.compile(r"^(\s*)- id:\s*" + re.escape(beat_id) + r"\s*(#.*)?$")
        for i, line in enumerate(lines):
            m = item_re.match(line)
            if m:
                start = i
                indent = m.group(1)
                break
        if start is None:
            return None, None
        end = len(lines)
        boundary = re.compile(r"^(" + indent + r"- |\S)")
        for j in range(start + 1, len(lines)):
            if boundary.match(lines[j]):
                end = j
                break
        return start, end

    for beat_id, sec in per_beat.items():
        start, end = beat_bounds(beat_id)
        if start is None:
            print(f"  WARN beat id {beat_id!r} not found in front matter")
            continue
        value = f"{sec:.1f}"
        for j in range(start, end):
            m = re.match(r"^(\s*)measured_sec:", lines[j])
            if m:
                lines[j] = f"{m.group(1)}measured_sec: {value}"
                break
        else:
            # No placeholder in this beat: insert after est_sec, else after
            # the scene_class line, matching the item's field indentation.
            insert_at, indent = start + 1, "    "
            for j in range(start, end):
                m = re.match(r"^(\s*)(est_sec|scene_class):", lines[j])
                if m:
                    insert_at, indent = j + 1, m.group(1)
            lines.insert(insert_at, f"{indent}measured_sec: {value}")

    total_line = f"measured_runtime_sec: {total:.1f}"
    for i, line in enumerate(lines):
        if re.match(r"^measured_runtime_sec:", line):
            lines[i] = total_line
            break
    else:
        for anchor in ("estimated_runtime_sec", "target_runtime_sec"):
            idx = next((i for i, line in enumerate(lines)
                        if re.match(r"^" + anchor + r":", line)), None)
            if idx is not None:
                lines.insert(idx + 1, total_line)
                break
        else:
            lines.append(total_line)

    return "\n".join(lines)


def measure_chapter(root: str, ch: dict, quality: str,
                    dry_run: bool = False) -> bool:
    """Measure one chapter's beats and update its script. True on success."""
    slug = ch.get("slug", "")
    beats, spath = script_beat_list(root, slug)
    if not beats:
        print(f"!!! {slug}: no beats[] in content/{slug}-script.md "
              f"-- nothing to measure")
        return False

    scene_file = ch.get("scene_file") or default_scene_file(slug)
    media_dir = os.path.join(root, "media", "videos",
                             scene_module_stem(scene_file), QUALITY_DIR[quality])

    per_beat, missing = {}, []
    for b in beats:
        cls, beat_id = b.get("scene_class"), b.get("id")
        if not cls or not beat_id:
            continue
        mp4 = os.path.join(media_dir, f"{cls}.mp4")
        dur = probe_duration(mp4) if os.path.exists(mp4) else None
        if dur is None:
            missing.append(mp4)
        else:
            per_beat[beat_id] = dur
    if missing:
        print(f"!!! {slug}: {len(missing)} rendered scene(s) missing/unreadable:")
        for p in missing:
            print(f"      {os.path.relpath(p, root)}")
        return False

    total = sum(per_beat.values())
    if dry_run:
        print(f"would measure {slug}: total {total:.1f}s "
              f"({', '.join(f'{k}={v:.1f}' for k, v in per_beat.items())})")
        return True

    text = open(spath, encoding="utf-8").read()
    fm_text, body = split_fm(text)
    new = rebuild(upsert_measured(fm_text, per_beat, total), body)
    if new != text:
        open(spath, "w", encoding="utf-8").write(new)
    print(f">>> measured {slug}: {total:.1f}s across {len(per_beat)} beat(s) "
          f"-> {os.path.relpath(spath, root)}")
    return True


def main():
    parser = project_parser(__doc__)
    parser.add_argument("-q", "--quality", default=None, choices=list("lmhk"),
                        help="which rendered quality to probe "
                             "(default: project.yaml render.quality, else l)")
    parser.add_argument("slugs", nargs="*",
                        help="only these chapter slugs (default: all renderable)")
    parser.add_argument("--dry-run", action="store_true",
                        help="print measurements without writing them back")
    args = parser.parse_args()
    root = resolve_project(args.project)
    manifest = load_project(root)
    if args.quality is None:
        cfg = ((manifest.get("project") or {}).get("render") or {}).get("quality", "ql")
        args.quality = cfg.lstrip("q") if cfg.lstrip("q") in list("lmhk") else "l"

    chapters = manifest.get("chapters") or []
    if args.slugs:
        targets = [ch for ch in chapters if ch.get("slug") in args.slugs]
    else:
        targets = [ch for ch in chapters if ch.get("status") in RENDERABLE]
    if not targets:
        raise SystemExit("no chapters selected for measurement")

    failures = sum(
        not measure_chapter(root, ch, args.quality, dry_run=args.dry_run)
        for ch in targets)
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
