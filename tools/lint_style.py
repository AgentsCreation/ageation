#!/usr/bin/env python3
"""Static style lint: the mechanizable STYLE_BOOK rules, checked at the source.

The geometric lint (lint_scene.py) replays scenes; this one just reads them.
It flags the STYLE_BOOK violations that show up as source-code patterns --
each rule below earned its place by being a *repeated* human review note
(STYLE_BOOK 12):

  text-newline      \\n inside a Text(...) literal renders garbled; build one
                    Text per line (intro_card/outro_bridge accept lists).
  text-emdash       em-dashes in on-screen captions (fine in narration).
  raw-font-size     a numeric font_size above CAPTION (24) where a type-scale
                    constant (TITLE/SECTION/BODY/SMALL/CAPTION) belongs.
                    Sub-caption sizes (chart tick fonts etc.) are allowed.
  raw-accent        literal YELLOW/GRAY_B color -- the palette names ACCENT
                    and MUTED carry the accent-discipline intent.
  local-helper      redefinition of a promoted _style helper (omega_box,
                    ball, die_face, coin, intro_card, outro_bridge,
                    make_pmf_chart, fit_to_frame) -- a chapter drawing its
                    own glyphs reads as a different series.
  hardcoded-voice   direct GTTSService/OpenAIService construction -- voice is
                    configuration; call _style.speech_service().

Warning-only by default (exit 0) so it can sit in `make check` without
breaking history; `--strict` exits nonzero on any finding, for gating.

Usage:
  python tools/lint_style.py [--project DIR] [--strict]
"""

import ast
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _project import project_parser, resolve_project

TYPE_SCALE_MAX_FREE = 24   # CAPTION; smaller sizes are chart internals
PROMOTED_HELPERS = {
    "omega_box", "ball", "die_face", "coin", "intro_card", "outro_bridge",
    "make_pmf_chart", "fit_to_frame", "progress_tag", "speech_service",
}
ACCENT_LITERALS = {"YELLOW": "ACCENT", "GRAY_B": "MUTED"}
VOICE_CLASSES = {"GTTSService", "OpenAIService"}


def call_name(node: ast.Call) -> str:
    f = node.func
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        return f.attr
    return ""


def check_file(path: str) -> list[tuple[int, str, str]]:
    """[(line, rule, message)] for one scene source file."""
    text = open(path, encoding="utf-8").read()
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return [(exc.lineno or 0, "syntax", f"does not parse: {exc.msg}")]

    findings = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in PROMOTED_HELPERS:
            findings.append((node.lineno, "local-helper",
                             f"def {node.name}(...) shadows the _style helper; "
                             f"import it instead"))
        if not isinstance(node, ast.Call):
            continue
        name = call_name(node)
        if name == "Text" and node.args:
            arg = node.args[0]
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                if "\n" in arg.value:
                    findings.append((node.lineno, "text-newline",
                                     "\\n inside Text() renders garbled; one "
                                     "Text per line (cards accept lists)"))
                if "—" in arg.value:
                    findings.append((node.lineno, "text-emdash",
                                     "em-dash in an on-screen caption "
                                     "(STYLE_BOOK 12, narration hygiene)"))
        if name in VOICE_CLASSES:
            findings.append((node.lineno, "hardcoded-voice",
                             f"{name}(...) constructed directly; voice is "
                             f"config -- return _style.speech_service()"))
        for kw in node.keywords or []:
            if (kw.arg == "font_size" and isinstance(kw.value, ast.Constant)
                    and isinstance(kw.value.value, (int, float))
                    and kw.value.value > TYPE_SCALE_MAX_FREE):
                findings.append((node.lineno, "raw-font-size",
                                 f"font_size={kw.value.value}: use the type "
                                 f"scale (TITLE/SECTION/BODY/SMALL/CAPTION)"))
            if kw.arg in ("color", "fill_color", "stroke_color"):
                v = kw.value
                if isinstance(v, ast.Name) and v.id in ACCENT_LITERALS:
                    findings.append((node.lineno, "raw-accent",
                                     f"{v.id} used literally; the palette "
                                     f"name is {ACCENT_LITERALS[v.id]}"))
    return findings


def main():
    parser = project_parser(__doc__)
    parser.add_argument("--strict", action="store_true",
                        help="exit nonzero on any finding (default: warn only)")
    args = parser.parse_args()
    root = resolve_project(args.project)

    scene_files = sorted(
        p for p in glob.glob(os.path.join(root, "scenes", "*.py"))
        if not os.path.basename(p).startswith("_"))
    if not scene_files:
        print("No scene files under scenes/ — nothing to style-lint.")
        sys.exit(0)

    total = 0
    for path in scene_files:
        findings = check_file(path)
        if not findings:
            continue
        print(f"\n{os.path.relpath(path, root)}")
        for line, rule, msg in sorted(findings):
            print(f"  {line:4d}  [{rule}]  {msg}")
        total += len(findings)

    if total:
        print(f"\nstyle lint: {total} finding(s) across "
              f"{len(scene_files)} scene file(s)"
              + ("" if args.strict else " (warning-only; --strict to gate)"))
        sys.exit(1 if args.strict else 0)
    print(f"style lint: clean across {len(scene_files)} scene file(s).")
    sys.exit(0)


if __name__ == "__main__":
    main()
