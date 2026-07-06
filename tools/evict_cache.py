#!/usr/bin/env python3
"""Evict entries from a project's TTS voiceover cache so they re-synthesize.

manim-voiceover memoizes every synthesized line in
media/voiceovers/cache.json (keyed by text + service), pointing at an mp3
beside it. That is what saves TTS money on re-render. But occasionally a
final (nova/openai) take carries an artifact the text can't predict -- a
leading breath puff, or a near-homophone that runs together as a stutter
("three densi-ties"). The fix is to drop that one cached take and re-render
the beat, which synthesizes a fresh one.

Hand-editing cache.json is risky: it is a flat JSON list that corrupts under
concurrent writes, so a stray edit during a render can wedge the whole cache.
This tool does the surgical, safe version -- select entries, drop them, and
delete any now-orphaned mp3s -- with a --dry-run preview.

Select by any of:
  --text SUBSTR     entries whose spoken text contains SUBSTR (repeatable)
  --provider NAME   entries synthesized by this service (e.g. openai, gtts)
Combine them (AND). With no selector, nothing is evicted (use --all to mean
"every entry", i.e. a full cache reset).

Usage:
  python tools/evict_cache.py --project DIR --text "these densities" [--dry-run]
  python tools/evict_cache.py --project DIR --provider openai --text "..."
  python tools/evict_cache.py --project DIR --all          # full reset
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _project import project_parser, resolve_project

VOICE_DIR = os.path.join("media", "voiceovers")
CACHE_NAME = "cache.json"


def entry_text(entry: dict) -> str:
    return str(entry.get("input_text", ""))


def entry_provider(entry: dict) -> str:
    """Best-effort service name for an entry (the service class is recorded
    inside input_data; fall back to scanning the blob)."""
    blob = json.dumps(entry.get("input_data", {})).lower()
    if "openai" in blob:
        return "openai"
    if "gtts" in blob:
        return "gtts"
    return ""


def entry_audio(entry: dict) -> set:
    """The mp3 basenames an entry references."""
    out = set()
    for k in ("original_audio", "final_audio"):
        v = entry.get(k)
        if v:
            out.add(os.path.basename(v))
    return out


def selects(entry, texts, provider, take_all) -> bool:
    if take_all:
        return True
    if not texts and not provider:
        return False
    if texts and not any(t.lower() in entry_text(entry).lower() for t in texts):
        return False
    if provider and entry_provider(entry) != provider.lower():
        return False
    return True


def main():
    parser = project_parser(__doc__)
    parser.add_argument("--text", action="append", default=[],
                        help="evict entries whose text contains this substring "
                             "(repeatable; matched case-insensitively)")
    parser.add_argument("--provider",
                        help="restrict to entries from this service "
                             "(openai / gtts)")
    parser.add_argument("--all", action="store_true",
                        help="evict EVERY entry (full cache reset)")
    parser.add_argument("--dry-run", action="store_true",
                        help="report what would be evicted without changing anything")
    args = parser.parse_args()
    root = resolve_project(args.project)

    if not args.all and not args.text and not args.provider:
        raise SystemExit("no selector: pass --text, --provider, or --all "
                         "(refusing to do nothing)")

    cache_path = os.path.join(root, VOICE_DIR, CACHE_NAME)
    if not os.path.exists(cache_path):
        raise SystemExit(f"no voiceover cache at {os.path.relpath(cache_path, root)}")

    try:
        cache = json.load(open(cache_path, encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(
            f"cache.json is not valid JSON ({exc}); it may have corrupted under "
            f"a concurrent write -- truncate it to the longest valid prefix by "
            f"hand, or delete it to force a full re-synthesis.")

    evicted, kept = [], []
    for e in cache:
        (evicted if selects(e, args.text, args.provider, args.all)
         else kept).append(e)

    if not evicted:
        print("no cache entries matched; nothing to evict.")
        return

    # An mp3 is safe to delete only if no surviving entry still references it.
    kept_audio = set()
    for e in kept:
        kept_audio |= entry_audio(e)
    orphaned = set()
    for e in evicted:
        orphaned |= entry_audio(e)
    orphaned -= kept_audio

    voice_dir = os.path.join(root, VOICE_DIR)
    for e in evicted:
        print(f"  evict: {entry_text(e)[:70]!r}  [{entry_provider(e) or '?'}]")
    verb = "would remove" if args.dry_run else "removed"
    for name in sorted(orphaned):
        mp3 = os.path.join(voice_dir, name)
        if not args.dry_run and os.path.exists(mp3):
            os.remove(mp3)
        print(f"  {verb} {name}")

    if args.dry_run:
        print(f"\nwould evict {len(evicted)} entry(ies) and {len(orphaned)} "
              f"mp3(s); {len(kept)} entry(ies) kept. (--dry-run: no changes)")
        return

    # Compact rewrite: the re-render re-synthesizes only what it needs.
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(kept, f, indent=2, ensure_ascii=False)
    print(f"\nevicted {len(evicted)} entry(ies) and {len(orphaned)} mp3(s); "
          f"{len(kept)} kept. Re-render the affected beat(s) to re-synthesize.")


if __name__ == "__main__":
    main()
