#!/usr/bin/env python3
"""Prune manim's intermediate render cache from a project's media/ tree.

Manim keeps every per-animation fragment under
media/videos/<module>/<quality>/partial_movie_files/<SceneClass>/ so an
unchanged animation is not re-rendered next time. Across a whole series the
fragments dwarf everything else (the live probability project accumulated
5,385 of them). They are safe to delete: the per-scene .mp4 files, the
_assembled/ deliverables, and the voiceover cache (which is what actually
saves TTS money) are all kept; the only cost is that the next render of a
scene re-renders all its animations.

Usage:
  python tools/clean_cache.py [--project DIR] [--dry-run]
"""

import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _project import project_parser, resolve_project


def partial_dirs(media_root: str):
    """Every .../partial_movie_files directory under media/videos."""
    videos = os.path.join(media_root, "videos")
    if not os.path.isdir(videos):
        return
    for dirpath, dirnames, _ in os.walk(videos):
        if "partial_movie_files" in dirnames:
            yield os.path.join(dirpath, "partial_movie_files")
            dirnames.remove("partial_movie_files")  # no need to walk into it


def dir_stats(path: str) -> tuple[int, int]:
    """(file count, total bytes) under `path`."""
    count = size = 0
    for dirpath, _, filenames in os.walk(path):
        for name in filenames:
            count += 1
            try:
                size += os.path.getsize(os.path.join(dirpath, name))
            except OSError:
                pass
    return count, size


def main():
    parser = project_parser(__doc__)
    parser.add_argument("--dry-run", action="store_true",
                        help="report what would be deleted without deleting")
    args = parser.parse_args()
    root = resolve_project(args.project)

    total_files = total_bytes = 0
    targets = list(partial_dirs(os.path.join(root, "media")))
    for path in targets:
        count, size = dir_stats(path)
        total_files += count
        total_bytes += size
        rel = os.path.relpath(path, root)
        if args.dry_run:
            print(f"would remove {rel}  ({count} files, {size / 1e6:.1f} MB)")
        else:
            shutil.rmtree(path)
            print(f"removed {rel}  ({count} files, {size / 1e6:.1f} MB)")

    verb = "would free" if args.dry_run else "freed"
    print(f"{verb} {total_bytes / 1e6:.1f} MB across {total_files} cached "
          f"fragment(s) in {len(targets)} partial_movie_files dir(s); "
          f"per-scene mp4s, _assembled/ and voiceover cache untouched.")


if __name__ == "__main__":
    main()
