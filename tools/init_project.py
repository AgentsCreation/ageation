#!/usr/bin/env python3
"""Bootstrap a draft project.yaml from a folder of LaTeX sources.

The "launch on any input" entry point. Point it at an input directory of .tex
files (e.g. input/MySubject) and it emits a draft project.yaml at the project
root: one chapter per .tex in numeric-prefix-then-alphabetical order, with a
slug, a title (from \\title/\\chapter/\\section when present, else the
filename), a linear prereq chain, status: planned, and an empty notation-rules
skeleton. Companion pandoc .md files sitting next to a .tex (a high-level
characterization of the same document) are detected and recorded so the
concept stage can leverage both.

With --scaffold-concepts it also emits a minimal content/{slug}.md stub per
chapter (front matter + the seven prose section headings), so the next steps
(vendor_sources, stamp_provenance, check_sync) are mechanical — without it,
nothing creates the concept files that vendor_sources is driven by.

Everything it writes is a DRAFT for human review — reorder chapters, fix the
prereq DAG, set the project title, and fill in notation rules before running
the pipeline.

Usage:
  python tools/init_project.py input/MySubject [--project DIR] [--title T]
                              [--scaffold-concepts] [--force]
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _project import project_parser, resolve_project
from render import default_scene_file

TITLE_PATTERNS = [
    r"\\title\{([^}]*)\}",
    r"\\chapter\*?\{([^}]*)\}",
    r"\\section\*?\{([^}]*)\}",
]


def slugify(stem: str) -> str:
    """'5Discrete_Random_Variables' -> '5-discrete-random-variables'."""
    s = re.sub(r"^(\d+)", r"\1-", stem)
    s = re.sub(r"[_\s]+", "-", s)
    s = re.sub(r"(?<=[a-z])(?=[A-Z])", "-", s)
    s = re.sub(r"-+", "-", s).strip("-").lower()
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
    """Duplicate slugs / derived scene files — each must map 1:1.

    Returns a list of human-readable problems (empty when clean).
    """
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


CONCEPT_SECTIONS = [
    "What", "Why", "How", "What else", "Conceptual progression",
    "Visual opportunities", "Deliberately out of scope",
]


def scaffold_concept(root, in_rel, ch):
    """Write a minimal content/{slug}.md stub. Returns True when written."""
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


def main():
    parser = project_parser(__doc__)
    parser.add_argument("input_dir", help="folder of .tex sources, e.g. input/MySubject")
    parser.add_argument("--title", default=None, help="project title (default: input folder name)")
    parser.add_argument("--scaffold-concepts", action="store_true",
                        help="also emit content/{slug}.md concept stubs")
    parser.add_argument("--force", action="store_true", help="overwrite an existing project.yaml")
    args = parser.parse_args()
    root = resolve_project(args.project)

    out = os.path.join(root, "project.yaml")
    if os.path.exists(out) and not args.force:
        raise SystemExit(f"refusing to overwrite {out} (use --force)")

    in_abs = args.input_dir if os.path.isabs(args.input_dir) \
        else os.path.join(root, args.input_dir)
    if not os.path.isdir(in_abs):
        raise SystemExit(f"input directory not found: {in_abs}")
    in_rel = os.path.relpath(in_abs, root)

    tex_files = sorted(
        (f for f in os.listdir(in_abs) if f.endswith(".tex")),
        key=sort_key,
    )
    if not tex_files:
        raise SystemExit(f"no .tex files in {in_abs}")

    title = args.title or os.path.basename(os.path.normpath(in_abs))
    chapters = []
    prev_slug = None
    for name in tex_files:
        stem = name[:-4]
        slug = slugify(stem)
        companion = stem + ".md"
        has_companion = os.path.exists(os.path.join(in_abs, companion))
        chapters.append({
            "slug": slug,
            "title": title_from_tex(os.path.join(in_abs, name), stem),
            "upstream": name,
            "companion": companion if has_companion else None,
            "prereq": prev_slug,
        })
        prev_slug = slug

    problems = detect_collisions(chapters)
    if problems:
        for p in problems:
            print(f"ERROR: {p}")
        raise SystemExit(f"{len(problems)} naming collision(s) — rename the "
                         "input files or curate project.yaml by hand")

    lines = [
        "# Project manifest -- the ordering spine for the whole video series.",
        "# DRAFT generated by tools/init_project.py — review before running the",
        "# pipeline: reorder chapters, fix the prereq DAG (a linear chain is",
        "# assumed), set the title, and fill in notation rules.",
        "",
        "project:",
        f"  title: {title}",
        "  # Read-only parent sources. Editable working copies are vendored to",
        "  # sources/ (tools/vendor_sources.py); the pipeline builds from those.",
        f"  upstream_dir: {in_rel}",
        "  render:",
        "    quality: ql            # ql = 480p draft; qh = 1080p final",
        "  voice:",
        "    provider: gtts         # gtts (free draft) -> openai (final)",
        "    rate: 1.0",
        "  pedagogy:",
        "    target_minutes_per_video: 6",
        "    open_with_objective: true",
        "    close_with_key_idea: true",
        "    recap_prior: true",
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

    n_comp = sum(1 for c in chapters if c["companion"])
    print(f"Wrote {os.path.relpath(out, root)}: {len(chapters)} chapters "
          f"({n_comp} with companion .md) from {in_rel}.")

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
