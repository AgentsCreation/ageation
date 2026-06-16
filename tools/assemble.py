#!/usr/bin/env python3
"""Concatenate the per-scene .mp4 outputs of a chapter into one video.

Manim renders each Scene class to its own file under
``media/videos/{scene_module}/{quality_dir}/{SceneClass}.mp4``. For a chapter
whose script has multiple beats (and so multiple Scene classes), the
deliverable is usually one combined video, not N small ones. This tool reads
the script's ``beats[]`` list in order, locates each per-beat .mp4 in the
quality-specific subdirectory, and uses ffmpeg's concat demuxer to stitch
them into one chapter video under ``media/videos/{scene_module}/{quality_dir}/
_assembled/{slug}.mp4``.

The concat demuxer uses ``-c copy`` -- no re-encoding -- which works because
every scene came out of the same manim quality preset (identical codec, frame
rate, audio sample rate). If a future scene set ever mixes presets, fall back
to ``-c:v libx264 -c:a aac``.

Usage:
  python tools/assemble.py [--project DIR] [-q l|m|h|k] [slug ...]
  --dry-run   print what would be assembled without invoking ffmpeg
"""

import os
import re
import subprocess
import sys
import tempfile

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _project import project_parser, resolve_project, load_project
from provenance import split_fm

# Manim's -q flag -> output subdirectory name (current manim convention).
QUALITY_DIR = {
    "l": "480p15",
    "m": "720p30",
    "h": "1080p60",
    "k": "2160p60",
}


def default_scene_file(slug: str) -> str:
    """Mirror of tools/render.py: strip leading digits, hyphens -> underscores."""
    module = re.sub(r"^\d+-", "", slug).replace("-", "_")
    return f"scenes/{module}.py"


def scene_module_stem(scene_file: str) -> str:
    return os.path.splitext(os.path.basename(scene_file))[0]


def atempo_chain(speed: float) -> str:
    """ffmpeg atempo filter, chained if needed (per-filter range is 0.5-2.0).

    For a 1.25x speed-up a single ``atempo=1.25`` suffices; for 4x we need
    ``atempo=2.0,atempo=2.0``. We greedily split factors of 2 (or 0.5) until
    the residual lies within atempo's per-filter range.
    """
    if speed <= 0:
        raise ValueError("speed must be > 0")
    factors = []
    s = speed
    while s > 2.0:
        factors.append(2.0)
        s /= 2.0
    while s < 0.5:
        factors.append(0.5)
        s /= 0.5
    factors.append(s)
    return ",".join(f"atempo={f}" for f in factors)


def assemble_one(list_file: str, out_path: str, speed: float) -> int:
    """Concat then (optionally) time-stretch. Returns ffmpeg's exit code.

    1.0x  -> single pass concat with -c copy (no re-encode).
    other -> two-pass: concat -c copy to a temp .mp4, then re-encode the
             temp with setpts + atempo to ``out_path``. The two-pass approach
             keeps the concat lossless and confines the re-encode to one
             pass over an already-concatenated stream.
    """
    if speed == 1.0:
        return subprocess.run([
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-f", "concat", "-safe", "0", "-i", list_file,
            "-c", "copy", out_path,
        ]).returncode

    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
        temp_concat = f.name
    try:
        rc = subprocess.run([
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-f", "concat", "-safe", "0", "-i", list_file,
            "-c", "copy", temp_concat,
        ]).returncode
        if rc != 0:
            return rc
        filter_complex = (
            f"[0:v]setpts=PTS/{speed}[v];"
            f"[0:a]{atempo_chain(speed)}[a]"
        )
        return subprocess.run([
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", temp_concat,
            "-filter_complex", filter_complex,
            "-map", "[v]", "-map", "[a]",
            out_path,
        ]).returncode
    finally:
        try:
            os.unlink(temp_concat)
        except OSError:
            pass


def script_beats(root: str, slug: str):
    """Return the ordered list of scene_class names from a chapter's script.

    Parses the script's YAML front matter directly (provenance.fm_get is
    regex-based for top-level scalars and can't read nested lists like
    ``beats:``). We use ``split_fm`` to extract the front matter cleanly
    (its regex requires the closing ``---`` at line boundaries, so inline
    ``---`` inside YAML comments doesn't confuse it).
    """
    spath = os.path.join(root, "content", f"{slug}-script.md")
    if not os.path.exists(spath):
        return None
    fm_text, _ = split_fm(open(spath, encoding="utf-8").read())
    if fm_text is None:
        return None
    fm = yaml.safe_load(fm_text)
    if not isinstance(fm, dict):
        return None
    beats = fm.get("beats") or []
    return [b.get("scene_class") for b in beats
            if isinstance(b, dict) and b.get("scene_class")]


def main():
    parser = project_parser(__doc__)
    parser.add_argument("-q", "--quality", default=None, choices=list("lmhk"),
                        help="manim quality flag suffix "
                             "(default: project.yaml render.quality, else l)")
    parser.add_argument("slugs", nargs="*",
                        help="only these chapter slugs (default: all chapters)")
    parser.add_argument("--speed", type=float, default=1.0,
                        help="playback speed multiplier (default 1.0); "
                             "uses ffmpeg setpts for video and atempo for "
                             "audio (atempo preserves pitch). Range 0.5-2.0 "
                             "in one pass; outside that, atempo is chained.")
    parser.add_argument("--dry-run", action="store_true",
                        help="print what would be assembled without invoking ffmpeg")
    args = parser.parse_args()
    if args.speed <= 0:
        raise SystemExit(f"--speed must be > 0 (got {args.speed})")
    root = resolve_project(args.project)
    manifest = load_project(root)
    if args.quality is None:
        cfg = ((manifest.get("project") or {}).get("render") or {}).get("quality", "ql")
        args.quality = cfg.lstrip("q") if cfg.lstrip("q") in list("lmhk") else "l"
    qdir = QUALITY_DIR[args.quality]

    chapters = manifest.get("chapters") or []
    targets = [ch for ch in chapters
               if not args.slugs or ch.get("slug") in args.slugs]
    if not targets:
        raise SystemExit("no chapters selected for assembly")

    failures = 0
    for ch in targets:
        slug = ch.get("slug", "")
        scene_file = ch.get("scene_file") or default_scene_file(slug)
        module = scene_module_stem(scene_file)
        media_dir = os.path.join(root, "media", "videos", module, qdir)
        scene_classes = script_beats(root, slug)
        if not scene_classes:
            print(f"!!! {slug}: no beats[] in content/{slug}-script.md "
                  f"-- nothing to assemble")
            failures += 1
            continue

        mp4_paths, missing = [], []
        for cls in scene_classes:
            p = os.path.join(media_dir, f"{cls}.mp4")
            (mp4_paths if os.path.exists(p) else missing).append(p)
        if missing:
            print(f"!!! {slug}: {len(missing)} rendered scene(s) missing:")
            for p in missing:
                print(f"      {os.path.relpath(p, root)}")
            print(f"      (render first: tools/render.py -q {args.quality})")
            failures += 1
            continue

        out_dir = os.path.join(media_dir, "_assembled")
        out_path = os.path.join(out_dir, f"{slug}.mp4")
        if args.dry_run:
            print(f"would assemble {slug}  ({len(mp4_paths)} scenes)")
            for p in mp4_paths:
                print(f"   in {os.path.relpath(p, root)}")
            print(f"  out {os.path.relpath(out_path, root)}")
            continue

        os.makedirs(out_dir, exist_ok=True)
        # ffmpeg concat demuxer reads a list file with one `file '...'` line
        # per input. Absolute paths are required because the concat demuxer
        # resolves them relative to the list file's location.
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False,
                                         encoding="utf-8") as f:
            list_file = f.name
            for p in mp4_paths:
                f.write(f"file '{os.path.abspath(p)}'\n")

        speed_suffix = f" @ {args.speed}x" if args.speed != 1.0 else ""
        print(f">>> assembling {slug} ({len(mp4_paths)} scenes){speed_suffix} "
              f"-> {os.path.relpath(out_path, root)}")
        rc = assemble_one(list_file, out_path, args.speed)
        try:
            os.unlink(list_file)
        except OSError:
            pass
        if rc != 0:
            print(f"!!! {slug}: ffmpeg failed (exit {rc})")
            failures += 1

    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
