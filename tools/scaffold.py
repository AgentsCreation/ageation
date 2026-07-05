#!/usr/bin/env python3
"""Emit the mechanical skeleton of a pipeline layer for one chapter.

The four layer transforms (tex -> concept -> script -> scene) are agent
work, but most of each output file is mechanical: front matter, provenance
fields, section headings, beat scaffolding, voiceover-block plumbing. This
tool pre-fills everything deterministic so the agent (or human) only writes
the parts that need judgment -- concept prose, narration, animations.

  --layer concept : content/{slug}.md with provenance-ready front matter,
                    the seven concept sections, and the vendored source's
                    \\section headings as an outline aid.
  --layer script  : content/{slug}-script.md derived from the concept:
                    linking block (neighbour titles from project.yaml),
                    voice/timing contract, one beat per concept entry, and
                    a narration section per beat.
  --layer scene   : scenes/{module}.py derived from the script: sha-stamped
                    header, _style imports, speech_service wiring, one
                    VoiceoverScene per beat with the script's narration
                    split into sequential voiceover blocks at <bookmark/>
                    markers (the settled bookmark-free timing model) and
                    TODO animation bodies.

Each layer refuses to overwrite an existing file unless --force is given.

Usage:
  python tools/scaffold.py --layer concept|script|scene --chapter SLUG
                           [--project DIR] [--force]
"""

import os
import re
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _project import project_parser, resolve_project, load_project, project_shape, shape_defaults
from provenance import sha256_file, sha256_script, split_fm
from render import default_scene_file

CONCEPT_SECTIONS = [
    "What", "Why (motivation for the viewer)", "How (the spine of the chapter)",
    "What else (connections, to seed callbacks in narration)",
    "Conceptual progression (drives the storyboard)",
    "Visual opportunities", "Deliberately out of scope",
]


def find_chapter(manifest: dict, slug: str) -> tuple[dict, dict | None, dict | None]:
    """(chapter, previous, next) entries from project.yaml, by slug."""
    chapters = manifest.get("chapters") or []
    for i, ch in enumerate(chapters):
        if ch.get("slug") == slug:
            prev = chapters[i - 1] if i > 0 else None
            nxt = chapters[i + 1] if i + 1 < len(chapters) else None
            return ch, prev, nxt
    raise SystemExit(f"slug {slug!r} not found in project.yaml chapters")


def tex_section_headings(path: str) -> list[str]:
    r"""Every \section/\subsection heading in a .tex file, in order."""
    if not os.path.exists(path):
        return []
    text = open(path, encoding="utf-8").read()
    return [m.group(2) for m in
            re.finditer(r"\\(section|subsection)\*?\{([^}]*)\}", text)]


def class_name_for(beat_id: str) -> str:
    """'rv-mapping' -> 'RvMapping' (a starting point; rename freely)."""
    return "".join(part.capitalize() for part in re.split(r"[-_]+", beat_id))


def refuse_existing(path: str, force: bool):
    if os.path.exists(path) and not force:
        raise SystemExit(f"refusing to overwrite {path} (use --force)")


# --- concept ------------------------------------------------------------------

def scaffold_concept(root: str, manifest: dict, slug: str, force: bool) -> str:
    ch, _, _ = find_chapter(manifest, slug)
    out = os.path.join(root, "content", f"{slug}.md")
    refuse_existing(out, force)

    # Vendor on demand: tools/vendor_sources.py works off existing concept
    # files, so a chapter added to an established project has no vendored
    # copy yet when its concept is first scaffolded. Reuse the same vendoring
    # machinery here (provenance header, companion sibling).
    source = f"sources/{slug}.tex"
    source_abs = os.path.join(root, source)
    upstream = ch.get("upstream")
    companion_rel = None
    if not os.path.exists(source_abs):
        if not upstream:
            raise SystemExit(
                f"{source} not found and chapter {slug} declares no "
                f"`upstream:` in project.yaml -- nothing to vendor from")
        from vendor_sources import vendor_file, find_companion
        vendor_file(root, upstream, source)
        print(f"  vendored {slug}  ->  {source}")
        by_slug = {c.get("slug"): c for c in manifest.get("chapters") or []}
        upstream_dir = (manifest.get("project") or {}).get("upstream_dir")
        comp_up = find_companion(root, slug, upstream, by_slug, upstream_dir)
        if comp_up:
            companion_rel = f"sources/{slug}.md"
            vendor_file(root, comp_up, companion_rel)
            print(f"  companion {slug}  ->  {companion_rel}")
    elif os.path.exists(os.path.join(root, "sources", f"{slug}.md")):
        companion_rel = f"sources/{slug}.md"

    shape = shape_defaults(project_shape(manifest))
    pedagogy = (manifest.get("project") or {}).get("pedagogy") or {}
    minutes = pedagogy.get("target_minutes_per_video",
                           shape["target_minutes_per_video"])

    lines = [
        "---",
        f"slug: {slug}",
        f"title: {ch.get('title', slug)}",
        "stage: concept            # tex -> [concept] -> script -> scene -> render",
        "status: draft             # draft | reviewed | approved  (human gate)",
        f"source: {source}",
        f"source_sha256: {sha256_file(source_abs)}",
    ]
    if upstream:
        lines.append(f"upstream: {upstream}")
    if companion_rel:
        lines.append(f"companion: {companion_rel}")
    if ch.get("prereqs"):
        lines.append("prereqs:")
        lines += [f"  - {p}" for p in ch["prereqs"]]
    lines += [
        "audience: TODO",
        "concepts:                 # one entry per idea worth a beat",
        "  - id: TODO-kebab-id",
        "    name: TODO",
        "    importance: core      # core | highlight | optional",
        "    one_liner: TODO",
        f"estimated_runtime_sec: {minutes * 60}",
        "---",
        "",
        f"# {ch.get('title', slug)} — Concept Map",
        "",
    ]
    headings = tex_section_headings(source_abs)
    if headings:
        lines += ["<!-- Source sections (from the vendored .tex), an outline aid:"]
        lines += [f"       {h}" for h in headings]
        lines += ["-->", ""]
    for section in CONCEPT_SECTIONS:
        lines += [f"## {section}", "", "TODO", ""]
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines).rstrip() + "\n")
    return out


# --- script -------------------------------------------------------------------

def scaffold_script(root: str, manifest: dict, slug: str, force: bool) -> str:
    ch, prev, nxt = find_chapter(manifest, slug)
    out = os.path.join(root, "content", f"{slug}-script.md")
    refuse_existing(out, force)

    cpath = os.path.join(root, "content", f"{slug}.md")
    if not os.path.exists(cpath):
        raise SystemExit(f"concept file missing: {cpath} "
                         f"(scaffold + write the concept layer first)")
    cfm_text, _ = split_fm(open(cpath, encoding="utf-8").read())
    cfm = yaml.safe_load(cfm_text) if cfm_text else {}
    if (str(cfm.get("status", "draft")).split("#")[0].strip()) == "draft":
        print("  NOTE: concept status is still `draft` -- the script layer "
              "normally starts after human review of the concept.")

    concepts = [c for c in (cfm.get("concepts") or []) if isinstance(c, dict)]
    beat_ids = [c.get("id") for c in concepts if c.get("id")] or ["overview"]
    if "overview" not in beat_ids:
        beat_ids.insert(0, "overview")

    voice = (manifest.get("project") or {}).get("voice") or {}
    target_sec = cfm.get("estimated_runtime_sec") or 360

    lines = [
        "---",
        f"slug: {slug}",
        f"title: {ch.get('title', slug)}",
        "stage: script             # tex -> concept -> [script] -> scene -> render",
        "status: draft             # draft | reviewed | approved  (human gate)",
        f"derived_from: {slug}.md",
        f"derived_from_sha256: {sha256_file(cpath)}",
        f"target_scene_file: {default_scene_file(slug)}",
        "",
        "# --- Narrative glue (links this video to its neighbours) ----------",
        "linking:",
        '  objective: "TODO -- the learning goal, spoken in the intro_card"',
        f'  recap: "TODO -- reactivate the previous chapter'
        f'{(": " + prev["title"]) if prev and prev.get("title") else ""}"',
        '  key_idea: "TODO -- one-line takeaway spoken in outro_bridge"',
        f'  bridge: "TODO -- tease the next chapter'
        f'{(": " + nxt["title"]) if nxt and nxt.get("title") else ""}"',
        "",
        "# --- Voice + timing config ----------------------------------------",
        "voice:",
        f"  provider: {voice.get('provider', 'gtts')}   # scenes read this via _style.speech_service()",
    ]
    if voice.get("name"):
        lines.append(f"  name: {voice['name']}")
    lines += [
        f"  rate: {voice.get('rate', 1.0)}",
        "words_per_minute: 150     # used only for the pre-TTS estimate",
        f"target_runtime_sec: {target_sec}",
        "tolerance_sec: 30         # check_status fails rendered+ chapters outside this",
        "",
        "# --- Estimates vs measured ------------------------------------------",
        "# est_sec: narration_words / wpm (cheap, pre-render).",
        "# measured_sec: written back by assemble / make measure (ffprobe).",
        "estimated_runtime_sec: null",
        "measured_runtime_sec: null",
        "",
        "beats:",
    ]
    for beat_id in beat_ids:
        lines += [
            f"  - id: {beat_id}",
            f"    scene_class: {class_name_for(beat_id)}",
            "    narration_words: null",
            "    est_sec: null",
            "    measured_sec: null",
            "    sync_points: []",
        ]
    lines += ["---", "", f"# Video Script — {ch.get('title', slug)}", "",
              "Narration is the source of truth for timing. Each `<bookmark "
              'mark="id"/>` is an authoring marker: the generated scene splits '
              "the narration into *sequential* voiceover blocks at each marker "
              "(bookmark-free timing; no Whisper).", ""]
    for beat_id in beat_ids:
        lines += [
            "---", "",
            f"## Beat: {beat_id}  (scene: {class_name_for(beat_id)})",
            "",
            "> TODO narration.",
            "",
            "Animation cues: TODO",
            "",
        ]
    lines += ["---", "", "## Cut list (if over budget)", "",
              "1. TODO -- what to drop first, and what it saves.", ""]
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines).rstrip() + "\n")
    return out


# --- scene --------------------------------------------------------------------

def beat_narrations(body: str) -> dict[str, list[str]]:
    """{beat_id: [narration chunk, ...]} from '## Beat: <id>' blockquotes.

    Consecutive `> ` lines under a beat heading are one narration; it is
    split into chunks at <bookmark .../> markers -- each chunk becomes one
    sequential voiceover block in the generated scene.
    """
    out: dict[str, list[str]] = {}
    current = None
    quote: list[str] = []

    def flush():
        if current is None or not quote:
            return
        text = " ".join(q.strip() for q in quote).strip()
        chunks = [c.strip() for c in re.split(r"<bookmark[^>]*/>", text)]
        out[current] = [c for c in chunks if c]

    for line in body.split("\n"):
        m = re.match(r"^## Beat:\s*(\S+)", line)
        if m:
            flush()
            current, quote = m.group(1), []
            continue
        if line.startswith(">"):
            quote.append(line.lstrip("> "))
        elif quote and line.strip() == "":
            continue
        elif quote:
            flush()
            quote = []
    flush()
    return out


def scaffold_scene(root: str, manifest: dict, slug: str, force: bool) -> str:
    ch, _, nxt = find_chapter(manifest, slug)
    spath = os.path.join(root, "content", f"{slug}-script.md")
    if not os.path.exists(spath):
        raise SystemExit(f"script file missing: {spath} "
                         f"(scaffold + write the script layer first)")
    text = open(spath, encoding="utf-8").read()
    fm_text, body = split_fm(text)
    fm = yaml.safe_load(fm_text) if fm_text else {}
    target = (fm.get("target_scene_file") or default_scene_file(slug))
    target = str(target).split("#")[0].strip()
    out = os.path.join(root, target)
    refuse_existing(out, force)
    os.makedirs(os.path.dirname(out), exist_ok=True)

    beats = [b for b in (fm.get("beats") or []) if isinstance(b, dict)]
    if not beats:
        raise SystemExit(f"{spath} has no beats[] in its front matter")
    narrations = beat_narrations(body)
    linking = fm.get("linking") or {}
    title = ch.get("title", slug)

    lines = [
        f"# derived_from: content/{slug}-script.md",
        f"# derived_from_sha256: {sha256_script(spath)}",
        f'"""{title} (narrated with manim-voiceover).',
        "",
        f"Script: content/{slug}-script.md",
        "",
        "Timing model: bookmark-free. Each narration chunk (split at",
        "<bookmark/> markers in the script) is its own sequential",
        "`with self.voiceover(text=...)` block; animations fill",
        "`run_time=tracker.duration`. See STYLE_BOOK.md for the house rules",
        "(one ACCENT at a time, five font sizes, fit_to_frame everything,",
        "mark_intended_overlap for deliberate overlaps).",
        '"""',
        "",
        "import os",
        "import sys",
        "",
        "sys.path.insert(0, os.path.dirname(__file__))",
        "",
        "from manim import *  # noqa: F401,F403",
        "from manim_voiceover import VoiceoverScene",
        "",
        "from _style import (",
        "    ACCENT,",
        "    MUTED,",
        "    BAR,",
        "    INK,",
        "    TITLE,",
        "    SECTION,",
        "    BODY,",
        "    SMALL,",
        "    CAPTION,",
        "    section_title,",
        "    intro_card,",
        "    outro_bridge,",
        "    progress_tag,",
        "    fit_to_frame,",
        "    mark_intended_overlap,",
        "    speech_service,",
        "    # Predictable layout (STYLE_BOOK 6) -- use these, don't hand-place:",
        "    two_column,",
        "    eq_chain,",
        "    even_stack,",
        "    caption_under,",
        "    chart_tag,",
        ")",
        "",
        "",
        "def make_speech_service():",
        '    """Voice comes from project.yaml (project.voice); AGEATION_TTS',
        '    is the draft/final switch (render.py sets gtts for -ql)."""',
        "    return speech_service()",
        "",
    ]
    for i, beat in enumerate(beats):
        beat_id = beat.get("id", f"beat{i}")
        cls = beat.get("scene_class") or class_name_for(beat_id)
        chunks = narrations.get(beat_id) or ["TODO narration."]
        lines += [
            "",
            f"class {cls}(VoiceoverScene):",
            f'    """Beat: {beat_id}."""',
            "",
            "    def construct(self):",
            "        self.set_speech_service(make_speech_service())",
            "",
        ]
        if i == 0:
            objective = linking.get("objective", "TODO objective")
            lines += [
                "        intro = intro_card(",
                f"            {title!r},",
                f"            {objective!r},",
                f"            kicker={('Chapter — ' + title)!r},  # TODO kicker",
                "        )",
                "",
            ]
        for chunk in chunks:
            lines += [
                "        with self.voiceover(",
                f"            text={chunk!r}",
                "        ) as tracker:",
                "            pass  # TODO animations, run_time=tracker.duration",
                "",
            ]
        if i == len(beats) - 1:
            key_idea = linking.get("key_idea", "TODO key idea")
            nxt_title = nxt.get("title") if nxt else None
            lines += [
                "        outro = outro_bridge(",
                f"            {key_idea!r},",
                f"            next_title={nxt_title!r},",
                "        )",
                "        # TODO: FadeIn(outro) inside the final voiceover block",
                "",
            ]
        lines += ["        self.play(*[FadeOut(m) for m in self.mobjects])", ""]

    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines).rstrip() + "\n")
    return out


def main():
    parser = project_parser(__doc__)
    parser.add_argument("--layer", required=True,
                        choices=["concept", "script", "scene"])
    parser.add_argument("--chapter", required=True, help="chapter slug")
    parser.add_argument("--force", action="store_true",
                        help="overwrite an existing output file")
    args = parser.parse_args()
    root = resolve_project(args.project)
    manifest = load_project(root)
    if not manifest:
        raise SystemExit(f"no project.yaml in {root}")

    fn = {"concept": scaffold_concept, "script": scaffold_script,
          "scene": scaffold_scene}[args.layer]
    out = fn(root, manifest, args.chapter, args.force)
    print(f"scaffolded {args.layer}: {os.path.relpath(out, root)}")
    print("Fill in the TODOs, then: make stamp && make check "
          f"--  (project {root})")


if __name__ == "__main__":
    main()
