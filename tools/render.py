#!/usr/bin/env python3
"""Render the buildable chapters listed in project.yaml.

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

import io
import os
import re
import subprocess
import sys
import tokenize

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _project import project_parser, resolve_project, load_project, parse_dotenv
from provenance import split_fm, fm_get

RENDERABLE = {"built", "rendered", "approved"}

# A scene that constructs OpenAIService directly ignores the AGEATION_TTS=gtts
# draft switch and tries to reach OpenAI; with no key, manim-voiceover drops
# into an interactive input() that a background render can't answer, hanging
# the whole run. Voice is configuration -- scenes must call
# _style.speech_service(). This preflight turns that latent hang into a clear
# up-front error on the free draft path.


def constructs_openai_service(source: str) -> bool:
    """True iff `source` actually calls OpenAIService(...) in code.

    Tokenized rather than regex-matched so a mention inside a comment or
    docstring (e.g. a "switch to OpenAIService" render note) never
    false-positives -- only a real NAME `OpenAIService` immediately followed
    by `(` counts. A bare `import OpenAIService` (no call) is also ignored.
    Falls back to a conservative textual scan if the file won't tokenize.
    """
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(source).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return bool(re.search(r"\bOpenAIService\s*\(", source))
    for cur, nxt in zip(toks, toks[1:]):
        if (cur.type == tokenize.NAME and cur.string == "OpenAIService"
                and nxt.type == tokenize.OP and nxt.string == "("):
            return True
    return False

# The engine repo (containing pyproject.toml and the manim-bearing venv)
# is the parent directory of tools/. When a consumer project lives outside
# this repo, `uv run` invoked with cwd=<project> can't find a venv to use;
# passing --project <ENGINE_ROOT> points uv at the engine's venv instead.
ENGINE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def script_status(root, slug):
    """The review status of content/{slug}-script.md, or None when unreadable."""
    path = os.path.join(root, "content", f"{slug}-script.md")
    if not os.path.exists(path):
        return None
    fm, _ = split_fm(open(path, encoding="utf-8").read())
    if fm is None:
        return None
    st = fm_get(fm, "status")
    return st.split("#")[0].strip() if st else None


def default_scene_file(slug: str) -> str:
    module = re.sub(r"^\d+-", "", slug).replace("-", "_")
    return f"scenes/{module}.py"


def main():
    parser = project_parser(__doc__)
    parser.add_argument("-q", "--quality", default=None, choices=list("lmhk"),
                        help="manim quality flag suffix "
                             "(default: project.yaml render.quality, else l)")
    parser.add_argument("slugs", nargs="*",
                        help="only these chapter slugs (default: all renderable)")
    parser.add_argument("--dry-run", action="store_true",
                        help="print the manim commands without running them")
    parser.add_argument("--force", action="store_true",
                        help="render even when the script is not `approved`")
    args = parser.parse_args()
    root = resolve_project(args.project)
    manifest = load_project(root)
    if args.quality is None:
        cfg = ((manifest.get("project") or {}).get("render") or {}).get("quality", "ql")
        args.quality = cfg.lstrip("q") if cfg.lstrip("q") in list("lmhk") else "l"
    chapters = manifest.get("chapters") or []
    if not chapters:
        raise SystemExit("no chapters in project.yaml — nothing to render")

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

    # Environment for the manim subprocesses. The scene-side speech_service()
    # reads AGEATION_PROJECT to find project.yaml and AGEATION_TTS as the
    # draft/final voice switch: -ql drafts default to the free gtts voice so a
    # draft render never spends TTS money or needs an API key. Keys in the
    # project's .env (the doctor.py convention) are lifted in because
    # manim-voiceover only reads the process environment -- exporting in the
    # shell must not be a prerequisite doctor can't see.
    env = os.environ.copy()
    for key, val in parse_dotenv(os.path.join(root, ".env")).items():
        env.setdefault(key, val)
    env.setdefault("AGEATION_PROJECT", root)
    if args.quality == "l":
        env.setdefault("AGEATION_TTS", "gtts")

    failures = 0
    for ch in selected:
        slug = ch["slug"]
        # The status gate: only approved narration gets rendered (TTS costs
        # money and un-vetted narration should never reach a final video).
        st = script_status(root, slug)
        if st != "approved" and not args.force:
            print(f"!!! {slug}: script status is {st!r}, not `approved` "
                  f"(--force to override)")
            failures += 1
            continue
        scene_file = ch.get("scene_file") or default_scene_file(slug)
        scene_path = os.path.join(root, scene_file)
        if not os.path.exists(scene_path):
            print(f"!!! {slug}: scene file missing: {scene_file}")
            failures += 1
            continue
        # Draft preflight: a hard-coded OpenAIService would hang the free
        # gtts render on an interactive key prompt. Fail fast with the fix.
        if env.get("AGEATION_TTS") == "gtts" and constructs_openai_service(
                open(scene_path, encoding="utf-8").read()):
            print(f"!!! {slug}: {scene_file} constructs OpenAIService directly "
                  f"-- the gtts draft render would hang on a key prompt. "
                  f"Return _style.speech_service() from make_speech_service() "
                  f"(the AGEATION_TTS env var then picks the draft/final voice).")
            failures += 1
            continue
        classes = [v["scene_class"] for v in ch.get("videos") or [] if v.get("scene_class")]
        cmd = ["uv", "run", "--project", ENGINE_ROOT,
               "manim", f"-q{args.quality}", scene_file]
        cmd += classes if classes else ["-a"]
        if args.dry_run:
            print(f"would render {slug}: {' '.join(cmd)}")
            continue
        print(f">>> rendering {slug}: {' '.join(cmd)}")
        if subprocess.run(cmd, cwd=root, env=env).returncode != 0:
            print(f"!!! {slug}: render failed")
            failures += 1

    if not args.dry_run:
        print(f"Done: {len(selected) - failures}/{len(selected)} chapter(s) rendered; "
              f"videos under media/videos/.")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
