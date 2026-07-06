#!/usr/bin/env python3
"""Bootstrap a draft project.yaml from upstream source(s).

Shape-aware (see PIPELINE.md "Project shapes"):

  --shape article   single .tex input  -> one chapter, one video.  *Default
                    when input is a file.*
  --shape book      directory of .tex  -> one chapter per file, multi-video.
  --shape course    directory of .tex  -> many chapters, optional videos[] per
                    chapter. Default when input is a directory.
  --shape session   (planned) synthesize a Claude Code session into a video;
                    not yet supported here — hand-author project.yaml.

The shape binds these manifest defaults (consult `_project.PROJECT_SHAPES`):

  voice.rate                 article 1.25 / book 1.15 / course 1.0
  pedagogy.recap_prior       false for article/session; true for book/course
  pedagogy.target_minutes_*  article 10 / book 8 / course 6  (overridden by
                             --target-minutes; prompted when interactive)

If --shape is omitted, the shape is inferred from the input type (file ->
article, directory -> course). Explicit --shape overrides the inference and
errors when the input type doesn't match.

Companion notes: when an upstream .tex has a sibling pandoc .md (high-level
characterization), it's detected and recorded so the concept stage can use
both. With --scaffold-concepts: also emit content/{slug}.md stubs.

Usage:
  # article (file)
  python tools/init_project.py paper.tex [--project DIR] [--shape article]
                              [--title T] [--target-minutes N]
                              [--scaffold-concepts] [--force]

  # book or course (directory)
  python tools/init_project.py input/MySubject --shape course [...]
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _project import (
    project_parser, resolve_project,
    PROJECT_SHAPES, DEFAULT_SHAPE, shape_defaults,
)
from render import default_scene_file

TITLE_PATTERNS = [
    r"\\title\{([^}]*)\}",
    r"\\chapter\*?\{([^}]*)\}",
    r"\\section\*?\{([^}]*)\}",
]

TARGET_MINUTES_MIN = 5
TARGET_MINUTES_MAX = 20

CONCEPT_SECTIONS = [
    "What", "Why", "How", "What else", "Conceptual progression",
    "Visual opportunities", "Deliberately out of scope",
]


# --- Slug + title helpers (unchanged from the course-era bootstrap) ----------

def slugify(stem: str) -> str:
    """'5Discrete_Random_Variables' -> '05-discrete-random-variables'.

    A leading chapter number is zero-padded to two digits so listings sort in
    course order. The number is a permanent accession ID, not a position:
    playback order lives in the project.yaml spine, and a chapter inserted
    later takes the next free number (see PIPELINE.md, "Chapter numbering").
    """
    s = re.sub(r"^(\d+)", r"\1-", stem)
    s = re.sub(r"[_\s]+", "-", s)
    s = re.sub(r"(?<=[a-z])(?=[A-Z])", "-", s)
    s = re.sub(r"-+", "-", s).strip("-").lower()
    s = re.sub(r"^(\d)(?=-)", r"0\1", s)
    return s


def title_from_tex(path: str, stem: str) -> str:
    try:
        txt = open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        txt = ""
    for pat in TITLE_PATTERNS:
        m = re.search(pat, txt)
        if m and m.group(1).strip():
            return re.sub(r"\s+", " ", m.group(1)).strip()
    human = re.sub(r"^\d+\s*", "", re.sub(r"[_-]+", " ", stem))
    human = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", human).strip()
    return human.title() if human else stem


def sort_key(name: str):
    m = re.match(r"(\d+)", name)
    return (0, int(m.group(1)), name.lower()) if m else (1, 0, name.lower())


def detect_collisions(chapters):
    """Duplicate slugs / derived scene files — each must map 1:1."""
    problems = []
    seen = {}
    for ch in chapters:
        if ch["slug"] in seen:
            problems.append(
                f"duplicate slug {ch['slug']!r}: {seen[ch['slug']]} and {ch['upstream']}")
        seen[ch["slug"]] = ch["upstream"]
    scenes = {}
    for ch in chapters:
        sf = default_scene_file(ch["slug"])
        if sf in scenes:
            problems.append(
                f"scene-file collision {sf!r}: slugs {scenes[sf]!r} and {ch['slug']!r} "
                f"(set an explicit scene_file: for one of them)")
        scenes[sf] = ch["slug"]
    return problems


# --- Chapter generation per shape -------------------------------------------

def chapters_for_article(tex_abs: str) -> list[dict]:
    """One chapter, representing the article as a whole."""
    stem = os.path.splitext(os.path.basename(tex_abs))[0]
    slug = slugify(stem) or "article"
    sib = os.path.splitext(tex_abs)[0] + ".md"
    return [{
        "slug": slug,
        "title": title_from_tex(tex_abs, stem),
        "upstream": os.path.basename(tex_abs),
        "companion": os.path.basename(sib) if os.path.exists(sib) else None,
        "prereq": None,
    }]


def chapters_for_directory(input_dir: str) -> list[dict]:
    """One chapter per .tex file in input_dir, linear prereq chain."""
    tex_files = sorted(
        (f for f in os.listdir(input_dir) if f.endswith(".tex")),
        key=sort_key,
    )
    if not tex_files:
        raise SystemExit(f"no .tex files in {input_dir}")
    chapters = []
    prev_slug = None
    for name in tex_files:
        stem = name[:-4]
        slug = slugify(stem)
        companion = stem + ".md"
        has_companion = os.path.exists(os.path.join(input_dir, companion))
        chapters.append({
            "slug": slug,
            "title": title_from_tex(os.path.join(input_dir, name), stem),
            "upstream": name,
            "companion": companion if has_companion else None,
            "prereq": prev_slug,
        })
        prev_slug = slug
    return chapters


# --- Interactive prompting --------------------------------------------------

def prompt_target_minutes(suggestion: int) -> int:
    """Ask for a per-video time budget. Falls back to suggestion when stdin
    isn't a TTY (e.g. piped / CI)."""
    msg = (f"Target minutes per video [{TARGET_MINUTES_MIN}-{TARGET_MINUTES_MAX}, "
           f"default {suggestion}]: ")
    if not sys.stdin.isatty():
        print(f"{msg.rstrip()} {suggestion} (non-interactive)")
        return suggestion
    while True:
        try:
            raw = input(msg).strip()
        except EOFError:
            return suggestion
        if not raw:
            return suggestion
        try:
            n = int(raw)
        except ValueError:
            print(f"  not a number: {raw!r}")
            continue
        if not (TARGET_MINUTES_MIN <= n <= TARGET_MINUTES_MAX):
            print(f"  outside the {TARGET_MINUTES_MIN}-{TARGET_MINUTES_MAX} range "
                  "(edit project.yaml by hand if you really need to)")
            continue
        return n


# --- Housekeeping scaffold ---------------------------------------------------

GITIGNORE = """\
# Renders, per-beat clips, and the TTS voiceover cache are all regenerable
# from the tracked layers (project.yaml + content/ + scenes/ + sources/) via
# tools/render.py + tools/assemble.py. Re-renders are approximate: TTS audio
# is re-synthesized, so beat durations drift within the runtime tolerance.
media/

# Secrets (OPENAI_API_KEY); document the shape in .env.example, not here.
.env

__pycache__/
.DS_Store
"""


def scaffold_gitignore(root: str) -> bool:
    """Emit a .gitignore that keeps media/ and .env out of git.

    The single biggest footgun in an embedded project is committing the 8 GB
    media/ tree or the .env secret; the tracked text layers regenerate the
    videos, so neither belongs in history. Skips an existing .gitignore.
    """
    path = os.path.join(root, ".gitignore")
    if os.path.exists(path):
        print("  .gitignore exists, skipping")
        return False
    with open(path, "w", encoding="utf-8") as f:
        f.write(GITIGNORE)
    print("  wrote .gitignore (media/, .env, __pycache__/, .DS_Store)")
    return True


# --- Concept scaffold (unchanged) -------------------------------------------

def scaffold_concept(root, in_rel, ch):
    path = os.path.join(root, "content", f"{ch['slug']}.md")
    if os.path.exists(path):
        print(f"  concept exists, skipping: content/{ch['slug']}.md")
        return False
    lines = [
        "---",
        f"slug: {ch['slug']}",
        f"title: {ch['title']}",
        "stage: concept            # tex -> [concept] -> script -> scene -> render",
        "status: draft             # draft | reviewed | approved  (human gate)",
        f"source: {in_rel}/{ch['upstream']}",
    ]
    if ch["companion"]:
        lines.append(f"# companion upstream: {in_rel}/{ch['companion']} "
                     "(vendored + recorded by tools/vendor_sources.py)")
    if ch["prereq"]:
        lines += ["prereqs:", f"  - {ch['prereq']}"]
    lines += ["---", ""]
    for section in CONCEPT_SECTIONS:
        lines += [f"## {section}", "", "TODO", ""]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines).rstrip() + "\n")
    return True


# --- Shape resolution + validation ------------------------------------------

def resolve_shape(explicit_shape: str | None, in_abs: str) -> str:
    """Return the validated shape for this invocation.

    If --shape was given, validate it matches the input type. Else infer
    from input type: file -> article, dir -> course (back-compat with the
    course-era bootstrap)."""
    is_file = os.path.isfile(in_abs)
    is_dir = os.path.isdir(in_abs)

    if explicit_shape is None:
        if is_file:
            return "article"
        if is_dir:
            return "course"
        raise SystemExit(f"input not found (neither file nor directory): {in_abs}")

    if explicit_shape == "article" and not is_file:
        raise SystemExit(
            f"--shape article expects a single .tex file; got: {in_abs}\n"
            f"(use --shape book or --shape course for a directory of .tex files)")
    if explicit_shape in ("book", "course") and not is_dir:
        raise SystemExit(
            f"--shape {explicit_shape} expects a directory of .tex files; got: {in_abs}\n"
            f"(use --shape article for a single .tex file)")
    if explicit_shape == "session":
        raise SystemExit(
            "--shape session is recognized but not yet supported by "
            "init_project.py. Hand-author project.yaml for now "
            "(see PIPELINE.md 'Project shapes').")
    return explicit_shape


# --- Manifest writer --------------------------------------------------------

def write_manifest(out, in_rel, shape, title, target_minutes, defaults, chapters):
    lines = [
        "# Project manifest -- the ordering spine for this project's video(s).",
        "# DRAFT generated by tools/init_project.py — review before running the",
        "# pipeline: set the title, fix the chapter spine for your content, fill",
        "# in notation rules. Per-shape defaults come from PROJECT_SHAPES in",
        "# tools/_project.py; override them by editing the YAML below.",
        "",
        "project:",
        f"  title: {title}",
        f"  shape: {shape}            # {defaults['summary']}",
        "  # Read-only parent source(s). Editable working copies are vendored",
        "  # to sources/ (tools/vendor_sources.py); the pipeline builds from those.",
        f"  upstream_dir: {in_rel}",
        "  render:",
        "    quality: ql            # ql = 480p draft; qh = 1080p final",
        "  voice:",
        "    provider: gtts         # gtts (free draft) -> openai (final)",
        f"    rate: {defaults['voice_rate']}",
        "  pedagogy:",
        f"    target_minutes_per_video: {target_minutes}   "
        f"# {TARGET_MINUTES_MIN}-{TARGET_MINUTES_MAX}; shape default = {defaults['target_minutes_per_video']}",
        "    open_with_objective: true",
        "    close_with_key_idea: true",
        f"    recap_prior: {str(defaults['recap_prior']).lower()}",
        "",
        "# Notation convention as data: literal LaTeX strings, not regexes.",
        "# Enforced by tools/check_notation.py; tools/normalize_notation.py",
        "# rewrites `avoid` -> `use` in the sources/ working copies.",
        "notation:",
        "  rules: []",
        "  # - avoid: '\\mathbb{P}'",
        "  #   use: '\\Pr'",
        "  #   reason: probability",
        "",
        "# status:  planned -> scripted -> built -> rendered -> approved",
        "",
        "chapters:",
    ]
    for ch in chapters:
        lines.append(f"  - slug: {ch['slug']}")
        lines.append(f"    title: {ch['title']}")
        lines.append(f"    upstream: {ch['upstream']}")
        if ch["companion"]:
            lines.append(f"    companion: {ch['companion']}   # pandoc high-level notes")
        lines.append("    status: planned")
        if ch["prereq"]:
            lines.append(f"    prereqs: [{ch['prereq']}]")
        lines.append("")

    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines).rstrip() + "\n")


# --- Entry point ------------------------------------------------------------

def main():
    parser = project_parser(__doc__)
    parser.add_argument("input",
                        help="upstream .tex file (article) or directory of .tex "
                             "files (book/course)")
    parser.add_argument("--shape", default=None, choices=list(PROJECT_SHAPES),
                        help=f"project shape; inferred from input if omitted "
                             f"(file -> article, dir -> course). "
                             f"Default project default = {DEFAULT_SHAPE}.")
    parser.add_argument("--title", default=None,
                        help="project title (default: derived from input)")
    parser.add_argument("--target-minutes", type=int, default=None,
                        help=f"target minutes per video "
                             f"({TARGET_MINUTES_MIN}-{TARGET_MINUTES_MAX}); "
                             f"prompts if omitted, shape default used non-interactively")
    parser.add_argument("--scaffold-concepts", action="store_true",
                        help="also emit content/{slug}.md concept stubs")
    parser.add_argument("--force", action="store_true",
                        help="overwrite an existing project.yaml")
    args = parser.parse_args()
    root = resolve_project(args.project)

    out = os.path.join(root, "project.yaml")
    if os.path.exists(out) and not args.force:
        raise SystemExit(f"refusing to overwrite {out} (use --force)")

    in_abs = args.input if os.path.isabs(args.input) \
        else os.path.join(root, args.input)
    in_abs = os.path.normpath(in_abs)

    shape = resolve_shape(args.shape, in_abs)
    defaults = shape_defaults(shape)

    if shape == "article":
        chapters = chapters_for_article(in_abs)
        upstream_root = os.path.dirname(in_abs)
        title_default = chapters[0]["title"]
    else:  # book or course
        chapters = chapters_for_directory(in_abs)
        upstream_root = in_abs
        title_default = os.path.basename(os.path.normpath(in_abs))

    in_rel = os.path.relpath(upstream_root, root) or "."

    problems = detect_collisions(chapters)
    if problems:
        for p in problems:
            print(f"ERROR: {p}")
        raise SystemExit(f"{len(problems)} naming collision(s) — rename the "
                         "input files or curate project.yaml by hand")

    if args.target_minutes is None:
        target_minutes = prompt_target_minutes(defaults["target_minutes_per_video"])
    elif not (TARGET_MINUTES_MIN <= args.target_minutes <= TARGET_MINUTES_MAX):
        raise SystemExit(f"--target-minutes {args.target_minutes} outside "
                         f"the {TARGET_MINUTES_MIN}-{TARGET_MINUTES_MAX} range")
    else:
        target_minutes = args.target_minutes

    title = args.title or title_default

    write_manifest(out, in_rel, shape, title, target_minutes, defaults, chapters)

    n_comp = sum(1 for c in chapters if c["companion"])
    print(f"Wrote {os.path.relpath(out, root)}: shape={shape}, "
          f"{len(chapters)} chapter(s) ({n_comp} with companion .md) "
          f"from {in_rel}.")

    scaffold_gitignore(root)

    if args.scaffold_concepts:
        os.makedirs(os.path.join(root, "content"), exist_ok=True)
        n = sum(scaffold_concept(root, in_rel, ch) for ch in chapters)
        print(f"Scaffolded {n} concept stub(s) in content/.")
        print("Next: flesh out + review the concepts, then run "
              "tools/vendor_sources.py and tools/stamp_provenance.py.")
    else:
        print("Review the draft, then scaffold concepts in content/ "
              "(or re-run with --scaffold-concepts) and run tools/vendor_sources.py.")


if __name__ == "__main__":
    main()
