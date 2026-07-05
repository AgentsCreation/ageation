#!/usr/bin/env python3
"""Language/register lint: the spoken- and on-screen-text rules, at the source.

lint_style.py reads scene code for layout/style patterns; this tool reads the
*words* — script narration blockquotes and the strings a scene puts on screen
or into a voiceover. Every rule below is a repeated human review note from
the 2026-07-04 harvest (STYLE_BOOK 12/14):

  video-number    "video 26" / "video twenty-six" in narration or on-screen
                  text. Numbering is brittle (inserting one video breaks
                  every cross-reference); anchor callbacks in TOPICS
                  ("the video that introduced CDFs"). Structural forms —
                  "last video", "this video", "next video" — are fine and
                  not matched.
  bare-bell       "bell" not followed by "curve" for the Gaussian; the
                  register says "Gaussian density" / "PDF" / "distribution".
  bell-curve-n    the full phrase "bell curve" more than once in a file —
                  it is allowed only where the classic name is the point.
  ramp            "ramp(s)" for a continuous CDF; say "smooth progression"
                  or "continuous CDF".
  long-block      a narration segment (between bookmarks) or a voiceover
                  block over LONG_BLOCK_WORDS words — split it into
                  per-phrase sub-blocks so visuals land on their sentences.
  long-sentence   a spoken sentence over LONG_SENTENCE_WORDS words — split
                  it; TTS reads long sentences breathlessly.

Term rules (video-number / bare-bell / bell-curve-n / ramp) are violations;
length rules are advisories. Warning-only by default (exit 0) so it can sit
in `make check` without breaking history; `--strict` exits nonzero on any
VIOLATION (advisories never gate).

Usage:
  python tools/lint_language.py [--project DIR] [--chapter SLUG] [--strict]
"""

import ast
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _project import project_parser, resolve_project

LONG_BLOCK_WORDS = 70
LONG_SENTENCE_WORDS = 40

_ONES = "one|two|three|four|five|six|seven|eight|nine"
_TEENS = ("ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|"
          "eighteen|nineteen")
_TENS = "twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety"
_SPELLED = rf"(?:(?:{_TENS})(?:[-\s](?:{_ONES}))?|{_TEENS}|{_ONES})"
# The lookbehind spares "in this video one idea stands out" — the number
# belongs to the next clause, not to a video reference.
VIDEO_NUMBER = re.compile(
    rf"(?<!(?:this|last|next)\s)\bvideos?\s+(?:\d+|{_SPELLED})\b",
    re.IGNORECASE)
BARE_BELL = re.compile(r"\bbell\b(?!\s+curves?\b)", re.IGNORECASE)
BELL_CURVE = re.compile(r"\bbell\s+curves?\b", re.IGNORECASE)
RAMP = re.compile(r"\bramps?\b", re.IGNORECASE)
BOOKMARK = re.compile(r"<bookmark[^>]*/>")

# On-screen text enters scenes through these calls (module docstrings and
# comments are never scanned). MathTex is LaTeX and belongs to the notation
# lint — EXCEPT its \text{...} groups, which are prose and are scanned too
# (a "video 37" caption shipped inside one).
TEXT_CALLS = {"Text", "intro_card", "outro_bridge", "section_title",
              "caption_under"}
TEX_TEXT_GROUP = re.compile(r"\\text\s*\{([^{}]*)\}")


def term_findings(text: str, where: str) -> list[tuple[str, str, bool]]:
    """[(rule, message, is_violation)] for one chunk of prose."""
    out = []
    for m in VIDEO_NUMBER.finditer(text):
        out.append(("video-number",
                    f"{where}: {m.group(0)!r} — anchor the callback in a "
                    f"topic, not a number", True))
    for m in BARE_BELL.finditer(text):
        out.append(("bare-bell",
                    f"{where}: bare {m.group(0)!r} — say Gaussian density / "
                    f"PDF / distribution", True))
    for m in RAMP.finditer(text):
        out.append(("ramp",
                    f"{where}: {m.group(0)!r} — say smooth progression / "
                    f"continuous CDF", True))
    return out


def length_findings(text: str, where: str) -> list[tuple[str, str, bool]]:
    out = []
    clean = BOOKMARK.sub(" ", text)
    words = clean.split()
    if len(words) > LONG_BLOCK_WORDS:
        out.append(("long-block",
                    f"{where}: {len(words)} words in one block — split into "
                    f"per-phrase sub-blocks", False))
    for sent in re.split(r"[.!?]", clean):
        n = len(sent.split())
        if n > LONG_SENTENCE_WORDS:
            head = " ".join(sent.split()[:6])
            out.append(("long-sentence",
                        f"{where}: {n}-word sentence ({head!r}...) — split "
                        f"it for the ear", False))
    return out


def check_script(path: str) -> list[tuple[str, str, bool]]:
    """Lint a content/*-script.md: narration blockquotes only."""
    findings = []
    lines = open(path, encoding="utf-8").read().splitlines()
    beat, quote = "front", []

    def flush():
        if not quote:
            return
        text = " ".join(quote)
        findings.extend(term_findings(BOOKMARK.sub(" ", text), beat))
        # Bookmark markers bound the sync segments the scene will realize
        # as separate voiceover blocks — length is judged per segment.
        for seg in BOOKMARK.split(text):
            findings.extend(length_findings(seg, beat))
        quote.clear()

    for line in lines:
        if line.startswith("## Beat:"):
            flush()
            beat = line.removeprefix("## Beat:").strip().split()[0]
        elif line.startswith(">"):
            quote.append(line.lstrip("> ").strip())
        else:
            flush()
    flush()

    # "bell curve" is allowed once per video, not as a refrain.
    body = "\n".join(l.lstrip("> ") for l in lines if l.startswith(">"))
    hits = BELL_CURVE.findall(body)
    if len(hits) > 1:
        findings.append(("bell-curve-n",
                         f"narration: 'bell curve' appears {len(hits)} times "
                         f"— at most once per video", True))
    return findings


def _string_args(node: ast.Call):
    """Yield string constants passed to a call (positionals, kwargs, lists)."""
    values = list(node.args) + [kw.value for kw in node.keywords or []]
    for v in values:
        if isinstance(v, ast.Constant) and isinstance(v.value, str):
            yield v.value, v.lineno
        elif isinstance(v, (ast.List, ast.Tuple)):
            for elt in v.elts:
                if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                    yield elt.value, elt.lineno


def check_scene(path: str) -> list[tuple[str, str, bool]]:
    """Lint a scenes/*.py: voiceover text and on-screen Text strings."""
    findings = []
    try:
        tree = ast.parse(open(path, encoding="utf-8").read())
    except SyntaxError as exc:
        return [("syntax", f"line {exc.lineno}: does not parse: {exc.msg}", True)]

    spoken_bell_curve = 0
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        name = f.id if isinstance(f, ast.Name) else (
            f.attr if isinstance(f, ast.Attribute) else "")
        if name == "voiceover":
            for kw in node.keywords or []:
                if kw.arg == "text" and isinstance(kw.value, ast.Constant) \
                        and isinstance(kw.value.value, str):
                    where = f"voiceover@{kw.value.lineno}"
                    findings.extend(term_findings(kw.value.value, where))
                    findings.extend(length_findings(kw.value.value, where))
                    spoken_bell_curve += len(BELL_CURVE.findall(kw.value.value))
        elif name in TEXT_CALLS:
            for s, lineno in _string_args(node):
                findings.extend(term_findings(s, f"{name}@{lineno}"))
        elif name == "MathTex":
            for s, lineno in _string_args(node):
                for m in TEX_TEXT_GROUP.finditer(s):
                    findings.extend(
                        term_findings(m.group(1), f"MathTex-text@{lineno}"))
    if spoken_bell_curve > 1:
        findings.append(("bell-curve-n",
                         f"spoken 'bell curve' {spoken_bell_curve} times — "
                         f"at most once per video", True))
    return findings


def main():
    parser = project_parser(__doc__)
    parser.add_argument("--chapter", help="lint a single chapter slug")
    parser.add_argument("--strict", action="store_true",
                        help="exit nonzero on violations (advisories never gate)")
    args = parser.parse_args()
    root = resolve_project(args.project)

    scripts = sorted(glob.glob(os.path.join(root, "content", "*-script.md")))
    scenes = sorted(p for p in glob.glob(os.path.join(root, "scenes", "*.py"))
                    if not os.path.basename(p).startswith("_"))
    if args.chapter:
        scripts = [p for p in scripts
                   if os.path.basename(p) == f"{args.chapter}-script.md"]
        # Scope scenes via the script's target_scene_file when available.
        keep = set()
        for s in scripts:
            for line in open(s, encoding="utf-8"):
                if line.startswith("target_scene_file:"):
                    keep.add(os.path.basename(line.split(":", 1)[1].strip()))
        scenes = [p for p in scenes if os.path.basename(p) in keep]

    violations = advisories = 0
    for path in scripts + scenes:
        findings = (check_script if path.endswith(".md") else check_scene)(path)
        if not findings:
            continue
        print(f"\n{os.path.relpath(path, root)}")
        for rule, msg, is_violation in findings:
            tag = "VIOLATION" if is_violation else "advisory"
            print(f"  [{rule}] ({tag}) {msg}")
            if is_violation:
                violations += 1
            else:
                advisories += 1

    n_files = len(scripts) + len(scenes)
    if violations or advisories:
        print(f"\nlanguage lint: {violations} violation(s), "
              f"{advisories} advisory(ies) across {n_files} file(s)"
              + ("" if args.strict else " (warning-only; --strict to gate)"))
        sys.exit(1 if (args.strict and violations) else 0)
    print(f"language lint: clean across {n_files} file(s).")
    sys.exit(0)


if __name__ == "__main__":
    main()
