# Video Pipeline

A file-based, stage-gated pipeline that turns a LaTeX chapter into a narrated
Manim video. Each stage reads files and writes files, so every stage is
re-runnable, diffable, and reviewable in isolation. The pipeline is
subject-agnostic: everything project-specific (title, input dir, notation
rules, chapter spine) lives in `course.yaml`.

## The layers

```
input/<Subject>/{Slug}.tex       (1) SOURCE      read-only, authored by humans
  (+ {Slug}.md sibling            optional pandoc high-level characterization)
        |  concept skill
        v
content/{slug}.md                (2) CONCEPT     meta description: what/why/how
        |  script skill
        v
content/{slug}-script.md         (3) SCRIPT      narration + beats + sync points
        |  scene skill
        v
scenes/{slug}.py                 (4) SCENE       Manim code (manim-voiceover)
        |  render skill (real machine / Claude Code CLI only)
        v
build/{slug}/                    (5) BUILD       audio + video + timing report
```

Layers 2 and 3 are **prose you can review and edit**. Layer 4 is generated from
layer 3 and treated as a build artifact — edit the script, regenerate the scene,
don't hand-patch the `.py`.

### Scaffolded source pairs (.tex + .md)

Some source sets ship each `.tex` with a sibling pandoc `.md`: the `.tex` is
the intended/authoritative output, the `.md` a high-level characterization of
the same document. When the pair exists, the pipeline vendors **both**
(`sources/{slug}.tex` + `sources/{slug}.md`, recorded as `companion:` in the
concept's front matter) and the concept stage should read both — the `.md`
for intent and structure, the `.tex` for the precise content.

## Bootstrapping a new project

`tools/init_course.py input/<Subject>` scans the input folder and emits a
draft `course.yaml`: one chapter per `.tex` (numeric-prefix order), slugs,
titles, a linear prereq chain, detected companions, and an empty
notation-rules skeleton. Review and curate it before running the stages.

## File conventions

- `slug`: lowercase, hyphenated, chapter-numbered — e.g. `5-discrete-random-variables`.
- Concept layer: `content/{slug}.md`.
- Script layer: `content/{slug}-script.md`.
- Scene code: `scenes/{slug}.py`.
- Build output: `build/{slug}/` (git-ignored; regenerable).
- Every markdown layer carries a self-describing **YAML front matter** with at
  least: `slug`, `stage`, `status`, and provenance (`source` / `derived_from`,
  plus `companion` when a pandoc sibling exists).

## Status gates (human in the loop)

`status: draft | reviewed | approved`. A downstream stage refuses to run unless
its input is at least `reviewed`. This keeps the agent from racing tex -> video
unattended and burning TTS credits on un-vetted narration. You approve the
concept, then the script; only an approved script gets rendered.

## The timing strategy (the hard part)

Use **manim-voiceover**. Narration drives animation length, not the reverse.

- Pre-render estimate (cheap): `est_sec = narration_words / words_per_minute * 60`,
  summed across beats. Lets you catch a too-long chapter before any TTS spend.
- Render-time truth: each beat is
  ```python
  with self.voiceover(text=NARRATION) as tracker:
      self.play(some_animation, run_time=tracker.duration)
  ```
  `tracker.duration` is measured from the generated audio, so the visuals always
  match the voice.
- Sync points: `<bookmark mark="id"/>` in the narration + `tracker.time_until_bookmark("id")`
  in the scene fire a specific animation on a specific word.
- Reconciliation: the render stage writes `measured_sec` back into the script's
  YAML. If `|measured_runtime_sec - target_runtime_sec| > tolerance_sec`, the
  build is flagged and you consult the script's **cut list**.
- Cost control: manim-voiceover caches audio by a hash of the narration text, so
  unchanged beats are never re-synthesized. Draft with `gtts` (free), switch the
  `voice.provider` to `openai`/`elevenlabs` only for finals.

## Local working copies + provenance (is production in sync with the source?)

The upstream notes are **read-only** (co-authored, possibly externally synced).
To normalize notation or fix a typo without touching the parent, each source is
**vendored** into an editable working copy under `sources/` — and that copy is
what the pipeline builds from. The copy carries a comment provenance header
(`%` in `.tex`, `<!-- -->` in `.md`) recording the upstream path, the upstream
SHA-256, and git origin/commit/tag when available (gracefully "unavailable" on
a detached clone). `tools/vendor_sources.py` creates the copies (including the
companion `.md` when present) and repoints each concept's `source:` to
`sources/{slug}.tex` (recording `upstream:` / `companion:`).

Every derived file then records the SHA-256 of its immediate input, so drift is
detectable by content hash (not git/mtime — those don't survive a clone):

- `sources/{slug}.tex` header : `upstream` + `upstream_sha256` (the parent).
- `content/{slug}.md` (concept): `source` (the local copy) + `source_sha256`,
  plus `companion` + `companion_sha256` when a pandoc sibling exists.
- `content/{slug}-script.md` (script): `derived_from` + `derived_from_sha256`.

`tools/check_sync.py` re-hashes and reports three links per chapter:
`upstream→local` (did the parent move? decide when to re-vendor), `local→concept`,
and `concept→script` (companion hashes fold into the first two — the worse
status wins). It exits nonzero on any drift, so it can gate a render.
Re-run `tools/stamp_provenance.py` after regenerating any layer. Section-level
hashing is a future refinement (localizes drift to a single section video).

Because the working copies are editable, `tools/normalize_notation.py` can
rewrite disallowed notation (per the project's rules) in `sources/*` only —
the read-only parent is never modified, and provenance still records its origin.

## Notation convention

Defined per project as data in `course.yaml` (`notation.rules`: literal
`avoid`/`use`/`reason` triples) and enforced by `tools/check_notation.py`,
which scans `content/`, `scenes/`, and `sources/` and fails on the avoided
forms. Manim has no access to a book's LaTeX macros, so scenes use the
expanded forms via `scenes/_style.py` helpers. See NOTATION.md for the full
model and `examples/probability/` for a populated rule set.

## Script bookmarks are authoring markers (not Whisper bookmarks)

`script.md` narration may contain `<bookmark mark="..."/>` tags. These are
**authoring sync markers** only -- they label the points where an animation
should fire. The `scene-from-script` step realizes each marked segment as a
*separate sequential* `with self.voiceover(...)` block (see the timing strategy
above), so NO word-level transcription (Whisper/PyTorch) is ever required. Do
not interpret script bookmarks as manim-voiceover `<bookmark>` calls.

## Overflow safety (graphs never spill off-frame)

Every chart/graph must fit inside the visible frame at any resolution. This is
enforced in code, not by eyeballing: `_style.fit_to_frame(mobj)` scales a
mobject down (never up) until it sits inside `config.frame_*` minus a margin.
`make_pmf_chart` already calls it, and any axes/long formula a scene builds
should be passed through it too. Because the guard is resolution-independent,
the same code is safe at 480p draft or 4K final.

## Rendering resolution

Drafts: `-ql` (480p15, fast, free gTTS). Finals: `-qh` (1080p60) or `-qk` (4K).
`tools/render.py` reads `course.yaml` and renders every chapter whose status is
built/rendered/approved (skip with `skip_render: true`); `render_all.sh` wraps
it: `./render_all.sh` for 1080p60, `./render_all.sh k` for 4K, optional second
arg = project dir. Rendering runs on a real machine only (cloud sandboxes
can't build manimpango).

## Skills (the workflow processors)

| Skill            | Input                      | Output                      | Runs in        |
|------------------|----------------------------|-----------------------------|----------------|
| `concept-from-tex` | `{Slug}.tex` (+ companion `.md`) | `content/{slug}.md`   | Cowork or CLI  |
| `script-from-concept` | `{slug}.md` (+ tex)  | `content/{slug}-script.md`  | Cowork or CLI  |
| `scene-from-script` | `{slug}-script.md`     | `scenes/{slug}.py`          | Cowork or CLI  |
| `render-verify`  | `scenes/{slug}.py` + script | `build/{slug}/` + timing  | **CLI / real machine only** |

Each skill is a thin, deterministic transform with a fixed contract (named
inputs/outputs, YAML schema it must emit). That is what makes the pipeline
robust and testable.

## Where each tool runs (learned empirically)

Rendering **cannot** happen in the Cowork cloud sandbox: no Mac Python, no
prebuilt `manimpango` wheel, no pango dev headers. So:

- **Cowork (cloud):** layers 1-3 — read the tex, author and review the concept
  and script markdown, generate scene code. Text-in, text-out work that thrives
  in the cloud and benefits from conversation.
- **Claude Code CLI (your machine):** layer 4-5 — the real `uv run manim`
  render, TTS calls, the self-correcting render loop, and frame screenshots for
  visual QA.

Hand off via the repo: Cowork commits the markdown + scene code, you pull on
the machine and run `render-verify`.

## Linking videos into a course (not one film)

The output is **short, self-contained section videos (~5-6 min)** that cohere
into a course through structure -- not a single concatenated film, and not
disconnected snippets. Five mechanisms, all file-driven:

1. **`course.yaml` -- the ordering spine.** One ordered list of chapters (each
   split into section videos) with `status` and `prereqs`. Single source of
   truth for sequence; the template and any assembly step read it for neighbour
   titles.
2. **Recap / bridge.** Each `script.md` carries a `linking:` block
   (`objective`, `recap`, `key_idea`, `bridge`). The open reactivates the prior
   video; the close states the takeaway and teases the next.
3. **Shared open/close template.** `_style.py` provides `intro_card`,
   `outro_bridge`, and `progress_tag` so every video begins and ends with the
   same grammar. Combined with the house style, this is the visual + structural
   continuity.
4. **Concept DAG.** `concept.md` `concepts[].id` + `prereqs` form a graph across
   chapters. It generates accurate callbacks and catches the #1 continuity bug:
   using an idea before it's been taught. (To build.)
5. **Assembly (optional).** Per-chapter videos stay separate for easy updates;
   an ffmpeg pass can also emit a stitched cut with uniform encode, audio
   loudness-normalization, and crossfades. (To build.)

**Why this shape:** learner engagement drops past ~6 minutes, so videos are kept
short and focused. Each opens by stating its objective and reactivating the last
video (spacing), and closes with a one-line key idea (retrieval cue) -- loosely
following multimedia-learning and spaced-retrieval guidance.

## Suggested repo layout

```
input/          # layer 1 UPSTREAM (read-only parent sources; gitignored)
sources/        # layer 1 LOCAL editable working copies (vendored, normalizable)
content/        # layers 2 & 3 (markdown, reviewed)
scenes/         # layer 4 (generated Manim, + _style.py shared house style)
build/          # layer 5 (git-ignored)
.claude/        # skills + a /animate-chapter command (CLI)
course.yaml     # per-project config: title, input dir, notation rules,
                #   chapters, render/voice/pedagogy defaults
tools/          # init_course, vendor_sources, stamp_provenance, check_sync,
                #   check_notation, normalize_notation, render
                #   (all take --project DIR, default `.`)
examples/       # complete worked example project(s), e.g. probability
NOTATION.md     # how the notation-rule system works
PIPELINE.md     # this file
```
