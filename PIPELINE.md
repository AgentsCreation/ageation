# Video Pipeline

A file-based, stage-gated pipeline that turns a LaTeX chapter into a narrated
Manim video. Each stage reads files and writes files, so every stage is
re-runnable, diffable, and reviewable in isolation. The pipeline is
subject-agnostic: everything project-specific (title, input dir, notation
rules, chapter spine) lives in `project.yaml`.

## The layers

```
upstream {Slug}.tex              (1) SOURCE      read-only, authored by humans
  (host-repo files, or input/     (+ optional {Slug}.md sibling: pandoc
   <Subject>/ when standalone)     high-level characterization)
        |  concept skill
        v
content/{slug}.md                (2) CONCEPT     meta description: what/why/how
        |  script skill
        v
content/{slug}-script.md         (3) SCRIPT      narration + beats + sync points
        |  scene skill
        v
scenes/{slug}.py                 (4) SCENE       Manim code (manim-voiceover)
        |  render (tools/render.py; real machine / Claude Code CLI only)
        v
media/videos/.../<SceneClass>.mp4    per-beat renders + .srt subtitles
        |  assemble (tools/assemble.py)
        v
media/videos/.../_assembled/         (5) BUILD   one stitched .mp4 per chapter
  {slug}.mp4                                     (the reviewable deliverable)
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

## Project shapes

Every project declares its **shape** in `project.yaml` (`project.shape`).
The shape is a planning anchor: it binds how the chapter spine is structured,
the default narration pace, and whether the intro_card includes a recap of
the prior chapter. Tools and skills branch on it.

| `shape`   | chapter spine                          | voice.rate | recap_prior | example                                            |
|-----------|----------------------------------------|------------|-------------|----------------------------------------------------|
| `article` | one chapter (the article as a whole)   | 1.25       | false       | arXiv preprint → single 8–12 min explainer         |
| `book`    | one video per book chapter             | 1.15       | true        | textbook → multi-video series                      |
| `course`  | many chapters, optional `videos[]`     | 1.0        | true        | `examples/probability/` (12 chapters)              |
| `session` | *(planned)* synthesize a CC session    | 1.25       | false       | Claude Code transcript → retrospective video       |

The table values are *defaults*; explicit fields in `project.yaml` always win.
`session` is recognized but tooling for it is not built yet — declare it now
if you have a transcript you want to distil, and the per-shape conventions
will fill in as the support lands.

When `project.shape` is absent, the framework defaults to `article` —
single-video standalone is the common case. Declare `shape: book` or
`shape: course` explicitly when the project fans out into a series.

## Bootstrapping a new project

`tools/init_project.py input/<Subject>` scans the input folder and emits a
draft `project.yaml`: one chapter per `.tex` (numeric-prefix order), slugs,
titles, a linear prereq chain, detected companions, and an empty
notation-rules skeleton. Review and curate it before running the stages.

`init_project` is a convenience, not the only entry point. Inputs whose
chapter boundaries are not encoded in numbered filenames — an article whose
order lives in `main.tex` `\input` lines, a software repo whose chapters must
be designed from the documentation's logical structure — start from a
**hand-authored `project.yaml`**, which is fully first-class: every downstream
tool reads the spine from the file, never from the input layout.

## Consumer projects (engine / content split)

The framework repo is an **engine** that drives any number of external
*project* directories. A project contains only `project.yaml` + the layer
folders (`sources/`, `content/`, `scenes/`, `media/`); the engine owns the
tools, the single Python venv, and `_style.py`. Two postures:

- **Embedded** (preferred when the videos are about a base repo — an article,
  a book, a software project): the project is the reserved subdirectory
  `ageation/` inside the host repo, and `project.yaml`'s `upstream_dir`
  points back into the host (e.g. `../sections`). No `input/` folder exists;
  vendoring still snapshots the host files into `ageation/sources/` with
  full provenance. `ageation/` is the single name the framework claims in a
  host repo — keep it disjoint from host layouts (the canonical article
  template uses `sections/`, `figures/`, `templates/`, `output/`,
  `resources/`, `misc/`).
- **Standalone**: the project is its own directory and the read-only upstream
  is dropped under `input/` — the only posture that uses `input/`.

Conventions, in either posture:

- Run `uv sync` / `uv run` in the engine repo; projects have no
  `pyproject.toml`.
- Target a project with `--project DIR` (all tools) or
  `make check PROJECT=DIR` / `./render_all.sh h DIR`.
- Version the project with the host repo (or as its own git repo when
  standalone); gitignore `.env`, `media/`, `__pycache__/`. The engine repo
  never absorbs project content.
- The stamp records which engine built the project (`framework_commit`, see
  provenance below), so engine evolution is detectable per project.

## Environment + secrets

Secrets (chiefly `OPENAI_API_KEY` for final renders) live in **`<project>/.env`**
— a flat `KEY=VALUE` file at the project root, next to `project.yaml`. The
framework's conventions:

- The file is **gitignored** in every project (`.env` is on the standard
  ignore list documented under "Consumer projects" above).
- `tools/doctor.py` reads `<project>/.env` and verifies that the secrets
  required by the project's selected `voice.provider` are present (so a
  missing key fails LOUD before manim spins up, not several minutes into
  a render). `make doctor PROJECT=…` runs this preflight; every
  `make render*` and `make video*` target depends on it.
- The engine repo ships `.env.example` as a template — copy it into the
  project root and fill in the key. Never commit the filled copy.

Provider-specific:

- `voice.provider: gtts` (free, no key) needs no secrets — doctor reports
  the OPENAI_API_KEY check as "not required."
- `voice.provider: openai` requires `OPENAI_API_KEY`. The scene's
  `make_speech_service()` constructs `OpenAIService(...)`, which reads the
  key from the process environment via the openai SDK — so source `.env`
  in your shell (or use a tool like `direnv`) before invoking `make render`.

## File conventions

- `slug`: lowercase, hyphenated, chapter-numbered — e.g. `05-discrete-random-variables`.
- Concept layer: `content/{slug}.md`.
- Script layer: `content/{slug}-script.md`.
- Scene code: `scenes/{module}.py`, where `{module}` is the slug minus its
  numeric prefix, hyphens to underscores (Python module names cannot start
  with a digit or contain hyphens) — e.g. `scenes/discrete_random_variables.py`.
- Build output: `media/` (git-ignored; regenerable — Manim's native layout).
- Every markdown layer carries a self-describing **YAML front matter** with at
  least: `slug`, `stage`, `status`, and provenance (`source` / `derived_from`,
  plus `companion` when a pandoc sibling exists).

### Chapter numbering

Chapter numbers are **permanent accession IDs, not positions**. Playback
order is defined solely by the chapter order in the `project.yaml` spine;
the numeric prefix exists so listings sort in course order and so humans
have a short, unambiguous handle ("video 25") during review and upload.
Three rules keep the numbers insertion-proof:

- **Zero-pad to two digits** (`01-sets`, not `1-sets`) so lexicographic
  sort matches course order. `tools/init_project.py` does this for you.
- **Never renumber.** A chapter inserted later takes the next free number
  and is slotted into the spine wherever it belongs — a `44-` chapter may
  legitimately sit between `20-` and `21-` in the playback order. Filenames,
  provenance chains, and published deliverable names never cascade.
- **Numbers never leak into content.** Narration and on-screen text refer to
  neighbouring topics, never to video numbers (STYLE_BOOK §0) — the viewer's
  artifact stays number-free, so the series is robust to later insertions.

## Status gates (human in the loop)

`status: draft | reviewed | approved`. A downstream stage must not run unless
its input is at least `reviewed`. This keeps the agent from racing tex -> video
unattended and burning TTS credits on un-vetted narration. You approve the
concept, then the script; only an approved script gets rendered.

**Enforcement** (not just convention):
- `tools/check_status.py` (part of `make check`) fails when a chapter's
  `project.yaml` status is ahead of its layers' review status — `scripted+`
  needs the concept `reviewed`, `built+` needs the script `reviewed` and the
  scene file present, `rendered+` needs the script `approved`.
- `tools/render.py` refuses to render a chapter whose script is not
  `approved` (override consciously with `--force`).

## Geometric scene lint

`tools/lint_scene.py` (`make lint-scene PROJECT=…`) replays each scene's
`construct()` with TTS stubbed and `Scene.play` monkey-patched, snapshots
mobject bounding boxes when each animation comes to rest, and flags pairwise
overlaps between leaf mobjects. Parent-child pairs are skipped (a label
inside its container box is intentional), as are heuristic connections: a
line/arrow whose *real endpoint* (not bbox corner — matters for CurvedArrow)
lands on a node or inside a container shape is anchored there by
construction. Tolerance is in **scene units**, not pixels, so 480p and
1080p lint identically.

**Declaring intent.** When an overlap is the point of the composition (Venn
ellipses, a fan of crossing arrows, bars over ghost bars), call
`_style.mark_intended_overlap(a, b, ..., reason=...)` on the mobjects or
groups in the scene. The mark rides every family member, so it survives
regrouping, `Transform`, and `LaggedStartMap` re-parenting — unlike the
legacy index-addressed `scenes/<scene>.lint-allow.yaml` sidecars, which
break on any structural edit (still honored, but deprecated; new scenes
should not create them). `--verbose` lists what the marks suppressed so
declared intent stays auditable.

**Gating rule.** `make video*` (final-quality stitched output) depends on
`lint-scene`; `make render*` (per-scene draft frames) does **not**. False
positives blocking *drafts* are worse than missed catches during iteration;
final renders are where clean layout actually has to ship.

**Scope.** The lint catches ~44% of typical review rounds (spatial overlaps
+ near-misses with `--buffer`). It does NOT catch animation-logic bugs (e.g.
opacity conflicts that leave a label invisible — see
`tools/lint_animation.py`, planned) or aesthetic preferences. Legacy
allowlist format (deprecated — use `mark_intended_overlap` instead):

```yaml
# scenes/gepa_explainer.lint-allow.yaml
ignore:
  - snapshot: 12          # or "*" for all snapshots
    a: "VGroup[0].MathTex"
    b: "Rectangle[1]"
    reason: "formula deliberately framed"
```

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
- Reconciliation: after every assemble (or `make measure`),
  `tools/measure_runtime.py` ffprobes each beat's rendered .mp4 and writes
  `measured_sec` (per beat) + `measured_runtime_sec` (total) back into the
  script's YAML. `check_status` then fails a rendered+ chapter when
  `|measured_runtime_sec - target_runtime_sec| > tolerance_sec` — consult the
  script's **cut list**. Provenance ignores the measured lines
  (`provenance.sha256_script` hashes scripts with them removed), so the
  write-back never reads as drift; stamps older than that convention go stale
  on first measurement — run `make stamp` once to migrate.
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
  plus `companion` + `companion_sha256` when a pandoc sibling exists, plus
  `framework_commit` — the git description of the framework checkout that
  performed the stamp (`-dirty` suffix when uncommitted), so a project built
  by an external engine records which engine version built it.
- `content/{slug}-script.md` (script): `derived_from` + `derived_from_sha256`.
- `scenes/{slug}.py` (scene): a `# derived_from:` + `# derived_from_sha256:`
  header comment, added by the scene-from-script step and refreshed by
  `stamp_provenance.py`. A built scene without the marker fails the sync gate
  (`unstamped`); a hand-built scene that predates the script layer is marked
  `# derived_from: legacy …` (tolerated, visible).

`tools/check_sync.py` re-hashes and reports four links per chapter:
`upstream→local` (did the parent move? decide when to re-vendor),
`local→concept`, `concept→script` (companion hashes fold into the first two —
the worse status wins), and `script→scene`. It exits nonzero on any drift, so
it can gate a render.
Re-run `tools/stamp_provenance.py` after regenerating any layer. Section-level
hashing is a future refinement (localizes drift to a single section video).

Because the working copies are editable, `tools/normalize_notation.py` can
rewrite disallowed notation (per the project's rules) in `sources/*` only —
the read-only parent is never modified, and provenance still records its origin.

## Notation convention

Defined per project as data in `project.yaml` (`notation.rules`: literal
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
`tools/render.py` reads `project.yaml` and renders every chapter whose status is
built/rendered/approved (skip with `skip_render: true`); `render_all.sh` wraps
it: `./render_all.sh` for 1080p60, `./render_all.sh k` for 4K, optional second
arg = project dir. Rendering runs on a real machine only (cloud sandboxes
can't build manimpango).

## Skills (the workflow processors)

These four transforms ship as skills in `skills/` (copy them into
`.claude/skills/` with `make install-skills` so Claude Code loads them), plus
an `/animate-chapter` orchestrator that walks a slug through all four with
exactly two human gates (concept review, script review). Each skill starts
from `tools/scaffold.py --layer concept|script|scene`, which pre-fills
everything mechanical (front matter, provenance hashes, beat skeletons,
voiceover-block plumbing split at `<bookmark/>` markers) so agent judgment is
confined to concept prose, narration, and animations. The Chapter 5
reference implementation in `examples/probability/` remains the model to
imitate.

| Skill            | Input                      | Output                      | Runs in        |
|------------------|----------------------------|-----------------------------|----------------|
| `concept-from-tex` | `{Slug}.tex` (+ companion `.md`) | `content/{slug}.md`   | Cowork or CLI  |
| `script-from-concept` | `{slug}.md` (+ tex)  | `content/{slug}-script.md`  | Cowork or CLI  |
| `scene-from-script` | `{slug}-script.md`     | `scenes/{slug}.py`          | Cowork or CLI  |
| `render-verify`  | `scenes/{slug}.py` + script | per-beat clips + assembled `media/videos/.../_assembled/{slug}.mp4` + timing  | **CLI / real machine only** |

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
  render, TTS calls, the self-correcting render loop, frame screenshots for
  visual QA, and the ffmpeg assemble pass that stitches the per-beat clips
  into the single reviewable `_assembled/{slug}.mp4`.

Hand off via the repo: Cowork commits the markdown + scene code, you pull on
the machine and run `render-verify`.

## Linking videos into a course (not one film)

The deliverable for each chapter is **one assembled `.mp4`** stitched from
its per-beat scene clips (the per-beat files stay on disk for cheap
iteration). Across chapters the output is a set of these self-contained
chapter videos (~5-20 min, set per project) that cohere into a course
through structure -- not a single concatenated film of the whole course, and
not disconnected snippets. The per-project target lives in `project.yaml`
(`pedagogy.target_minutes_per_video`); `tools/init_project.py` suggests a
default and asks for a budget. Five mechanisms, all file-driven:

1. **`project.yaml` -- the ordering spine.** One ordered list of chapters (each
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
5. **Assembly (standard final step).** Every chapter's per-beat scenes are
   stitched into one `.mp4` by `tools/assemble.py` -- this is the reviewable
   deliverable. The per-beat files stay on disk so iterating on a single
   beat is still cheap. `make video` (and `video-draft` / `video-4k`)
   chains `render` + `assemble`; the output lands at
   `media/videos/<module>/<quality>/_assembled/<slug>.mp4`.

**Why this shape:** the right runtime depends on content density and audience —
a fast conceptual primer wants ~5 min, a worked-example walkthrough may need
~20 min. Pick a per-project budget in that range and keep videos focused
around it. Each opens by stating its objective and reactivating the last
video (spacing), and closes with a one-line key idea (retrieval cue) -- loosely
following multimedia-learning and spaced-retrieval guidance.

## Suggested layout

A **project** directory (standalone, or `ageation/` inside a host repo):

```
project.yaml    # per-project config: title, upstream dir, notation rules,
                #   chapters, render/voice/pedagogy defaults
input/          # layer 1 UPSTREAM — standalone posture only (read-only,
                #   gitignored); embedded projects point upstream_dir at the
                #   host repo's files instead
sources/        # layer 1 LOCAL editable working copies (vendored, normalizable)
content/        # layers 2 & 3 (markdown, reviewed)
scenes/         # layer 4 (generated Manim)
media/          # layer 5 (git-ignored). Manim's native per-beat layout under
                #   media/videos/<module>/<quality>/ plus the assembled
                #   deliverable at .../<quality>/_assembled/<slug>.mp4
```

The **engine** repo (this one) additionally holds:

```
tools/          # init_project, vendor_sources, stamp_provenance, check_sync,
                #   check_notation, check_status, normalize_notation, render,
                #   assemble (all take --project DIR, default `.`)
scenes/_style.py  # shared house style (palette, notation helpers, fit_to_frame)
skills/         # the processor skills (make install-skills -> .claude/skills)
examples/       # complete worked example project(s), e.g. probability
NOTATION.md     # how the notation-rule system works
PIPELINE.md     # this file
```
