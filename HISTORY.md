# HISTORY.md — Turning LaTeX Notes into Manim Videos

This file is a synthesis and a roadmap. It records *why* this project is built
the way it is, and gives a future Claude (or human) enough to **reproduce the
whole workflow from scratch** — taking a folder of LaTeX notes and producing
narrated, coherent Manim videos. Read this together with `PIPELINE.md` (the
detailed spec), `CLAUDE.md` (per-repo instructions), and `project.yaml` (the
per-project config + chapter spine).

> **2026-06 genericization.** The project began as a probability-specific
> pipeline; it has since been made subject-agnostic. The original probability
> course (all 12 chapters' content, sources, project.yaml, NOTATION.md, and
> the built scenes) now lives intact under **`examples/probability/`** as the
> worked example and reference implementation. Notation rules became data in
> `project.yaml` (`notation.rules`), every tool takes `--project DIR`,
> `tools/init_project.py` bootstraps a manifest from any input folder,
> `tools/render.py` replaced the hand-maintained render list, and sources may
> ship as `.tex` + companion pandoc `.md` pairs (both are vendored and
> leveraged). Sections below describe the original build; chapter-specific
> paths now resolve inside `examples/probability/`.

---

## 1. The goal

Automate the production of narrated math videos from an existing set of CC0
LaTeX probability notes (`input/Probability/`). The **product is secondary**;
the real objective is the *workflow and scaffolding* — a robust, repeatable
pipeline a non-developer can drive, and that a future agent can extend. The
human (JF) works in Cowork for authoring and in Claude Code CLI on a Mac for
rendering.

The output target is **self-contained section videos (~5–20 min each, set per
project in `project.yaml`)** that link into a coherent course — not one long
film, and not disconnected snippets.

---

## 2. The approach: a layered, file-based pipeline

Each stage reads files and writes files, so every stage is re-runnable,
diffable, and reviewable in isolation.

```
input/Probability/{Slug}.tex     (1) SOURCE     read-only, human-authored
        |  concept-from-tex
        v
content/{slug}.md                (2) CONCEPT    meta description: what/why/how
        |  script-from-concept
        v
content/{slug}-script.md         (3) SCRIPT     narration + beats + sync points
        |  scene-from-script
        v
scenes/{slug}.py                 (4) SCENE      Manim code (manim-voiceover)
        |  render (Mac / Claude Code CLI only)
        v
build/ + media/                  (5) BUILD      narrated video + .srt subtitles
```

- Layers 2–3 are **prose you review and edit**. Layer 4 is generated from layer
  3 and treated as a build artifact (edit the script, regenerate the scene; do
  not hand-patch the `.py`).
- Every markdown layer carries **self-describing YAML front matter** with a
  `status: draft | reviewed | approved` gate. A downstream stage refuses to run
  on un-approved input — this keeps the agent from racing tex→video unattended
  and burning TTS credits on un-vetted narration.

### Linking videos into a course (the "seamless" part)

Short videos are made to cohere through five file-driven mechanisms:

1. **`project.yaml` — the ordering spine.** Ordered chapters (split into section
   videos) with `status` and `prereqs`. Single source of truth for sequence.
2. **Recap / bridge.** Each `script.md` has a `linking:` block (`objective`,
   `recap`, `key_idea`, `bridge`). Each video opens reactivating the previous
   chapter and closes with the takeaway + a teaser for the next.
3. **Shared open/close template.** `_style.py` provides `intro_card`,
   `outro_bridge`, `progress_tag` so every video has the same bookends.
4. **Concept DAG (planned).** `concept.md` `concepts[].id` + `prereqs` form a
   graph; it generates accurate callbacks and catches "used before taught" bugs.
5. **Assembly (planned, optional).** ffmpeg can stitch a full cut with uniform
   encode, loudness-normalized audio, and crossfades.

Pedagogical rationale (loosely applied): pick a per-project runtime budget in
the 5–20 min range based on content density (primer vs worked-example
walkthrough) and audience; each video states its objective up front
(orienting), reactivates the prior video (spacing), and ends with a one-line
key idea (retrieval cue).

---

## 3. Software and environment decisions (hard-won — do not relitigate)

| Decision | Choice | Why |
|---|---|---|
| Env / deps | **uv** | Fast, reproducible; sidesteps broken stdlib `venv`/`ensurepip` and manages the Python toolchain. |
| Python | **3.12** (`.python-version`, `requires-python = ">=3.12,<3.13"`) | 3.14 is too new: `openai-whisper` won't build and PyTorch has no wheels; setuptools on 3.14 removes `pkg_resources`. 3.12 has wheels for everything. |
| Animation | **Manim Community ≥ 0.20.1** | Standard, actively maintained. (Note: a generic PyPI mirror may cap at 0.19.1 — 0.19 is API-compatible for these scenes.) |
| Narration | **manim-voiceover 0.3.7** | Adds TTS-driven voiceover in pure Python; emits `.srt` subtitles for free. |
| TTS backend | **gTTS** for drafts → **OpenAI** for finals (one-line swap in `make_speech_service()`) | gTTS is free/no-key (needs internet); OpenAI is higher quality (needs `OPENAI_API_KEY`). |
| `pkg_resources` | pin **`setuptools<81`** | manim-voiceover imports the deprecated `pkg_resources`, which newer setuptools removes. |
| Timing/sync | **bookmark-free sequential voiceover blocks** | Real manim-voiceover `<bookmark>` needs word-level timestamps via Whisper (→ PyTorch, heavy, no 3.14 wheels). Splitting each beat into separate `with self.voiceover(...)` blocks gives sentence-level sync with zero heavy deps. |
| Overflow | **`_style.fit_to_frame()`** on every graph | Scales mobjects down to fit `config.frame_*` minus a margin; resolution-independent, so graphs never spill at 480p or 4K. Enforced in code, not by eyeballing. |
| Notation | per-project rules as data in `project.yaml` (`notation.rules`); the probability example uses `\Pr`, `\mathrm{E}`, `\mathrm{Var}` (never `\mathbb{P}`/`\mathbb{E}`) | Matches the notes' preamble macros; enforced by `tools/check_notation.py`. See NOTATION.md for the model. |
| Drift detection | **content-hash provenance** in front matter + `tools/check_sync.py` | Source was cloned and detached from git; hashes (not mtimes/commits) reliably tell whether a video is in sync with its `.tex`. |
| Source handling | **vendor read-only parents into editable `sources/` copies** (`tools/vendor_sources.py`); copy header records upstream path/hash + git origin/commit/tag when available | Lets us normalize notation / fix typos without touching the read-only parent; two-level provenance (upstream→local→concept→script) tracks both "parent moved" and "our copy changed". |
| House style | accent **YELLOW**, muted GRAY_B, type scale TITLE 56 / SECTION 44 / BODY 34 / SMALL 28 / CAPTION 24 | Centralized in `_style.py` for cross-chapter consistency. |
| Rendering location | **Mac only, via Claude Code CLI** | The Cowork cloud sandbox **cannot render**: it can't build `manimpango` (no pango dev headers, no prebuilt wheel), so manim won't even import there. |
| System deps | **ffmpeg + a LaTeX distro** (latex, dvisvgm), declared in `Brewfile` (`brew bundle`). **NOT** sox (only for mic-record mode), **NOT** whisper/torch, **NOT** pango/cairo on macOS (wheels bundle them). | manim needs ffmpeg + LaTeX to render text/formulas. `pyproject.toml` can't express system packages (PEP 725 is still draft), so a `Brewfile` is the macOS-native manifest. |
| Architecture (2026-06-11, after the nano-evolve case study) | **engine/content split**: this repo is the engine; projects live outside it, preferably as a reserved `auto_manim/` subdirectory of the base repo (`upstream_dir` pointing back into the host; no `input/`), or standalone with `input/`. The manifest is **`project.yaml`** (renamed from course.yaml — the framework is broader than courses); `stamp_provenance.py` records `framework_commit` per concept. | One reserved name (not five prefixed ones) keeps the namespace disjoint from any host layout (e.g. the canonical article template); `--project DIR` already made the tools location-agnostic, so the posture cost zero code. Version coupling is detectable via `framework_commit`. |

### The Cowork ↔ Claude Code split (empirical)

- **Cowork (cloud):** layers 1–3 — read the tex, author/review the concept and
  script markdown, generate scene code. Text-in/text-out work that thrives in
  the cloud and benefits from conversation.
- **Claude Code CLI (Mac):** layers 4–5 — real `uv run manim` render, TTS calls,
  the self-correcting render loop, frame screenshots for QA. Hand off via the
  repo (commit markdown + scene code, pull on the Mac, render).

---

## 4. What exists now (the scaffold)

- `CLAUDE.md` — per-repo agent instructions (mission, workflow, LaTeX tips).
- `PIPELINE.md` — the detailed architecture + conventions spec.
- `project.yaml` — the 12-chapter spine: order, status, prereqs, section videos.
- `content/{slug}.md` + `content/{slug}-script.md` — **all 12 chapters**
  scaffolded (concept + script), verified faithful to the source LaTeX on both
  axes (horizontal recap/bridge chain; vertical tex→concept→script fidelity).
- `scenes/_style.py` — house style: palette, type scale, `pr()`, `section_title`,
  `fit_to_frame`, `make_pmf_chart`, and the linking template (`intro_card`,
  `outro_bridge`, `progress_tag`).
- `scenes/discrete_random_variables.py` — **Chapter 5, fully working**: four
  `VoiceoverScene` classes, bookmark-free sync, overflow-guarded, renders a
  narrated video + `.srt`. This is the reference implementation.
- `scenes/conditional_probability.py` — Chapter 4, an older hand-built
  (non-voiceover) scene from early exploration.
- `render_all.sh` — high-res render helper (`./render_all.sh` = 1080p60,
  `./render_all.sh k` = 4K, `l` = 480p draft).
- `NOTATION.md` — the project notation convention (probability `\Pr`, expectation
  `\mathrm{E}`, …), grounded in the notes' macros.
- `sources/` — editable working copies of each `.tex`, vendored from the
  read-only `input/` parents, each with a `%`-comment provenance header
  (upstream path/hash + git origin/commit/tag). The pipeline builds from these.
- `tools/` — `init_project.py` (bootstrap a draft project.yaml from any input
  folder), `vendor_sources.py` (make working copies + capture git; vendors
  companion `.md` siblings too), `stamp_provenance.py` (write hashes),
  `check_sync.py` (report upstream→local→concept→script drift),
  `check_notation.py` (enforce the project.yaml notation rules),
  `normalize_notation.py` (fix notation in working copies), `render.py`
  (render the buildable chapters per project.yaml). All take `--project DIR`
  (default `.`) and currently report clean / in-sync on the example.
- `pyproject.toml` / `.python-version` — Python 3.12; deps `manim>=0.20.1`,
  `manim-voiceover[gtts]>=0.3.7`, `setuptools<81`.

**Status:** ch4 `rendered` (old style), ch5 `built` (voiceover, verified),
ch1–3 & 6–12 `scripted` (markdown done, scene `.py` not yet generated).

---

## 5. Roadmap: reproduce the whole workflow from scratch

A future Claude can rebuild this for any LaTeX notes by following these steps.

### Step 0 — Machine prerequisites (do this on the Mac that will render)
- `brew bundle` (reads the `Brewfile`: `uv`, `ffmpeg`, MacTeX). Confirm with
  `which uv ffmpeg latex dvisvgm`. `pyproject.toml` covers only PyPI packages, so
  system tools live in the `Brewfile` (the macOS convention; PEP 725 would put
  them in pyproject but is still a draft).

### Step 1 — Initialize the project
```
uv init <project>
cd <project>
echo "3.12" > .python-version
# set requires-python = ">=3.12,<3.13" in pyproject.toml
uv add "manim>=0.20.1" "manim-voiceover[gtts]>=0.3.7" "setuptools<81"
uv run manim --version   # sanity: prints the Manim version
```
Put the source notes under `input/<Subject>/` (read-only by convention).

### Step 2 — Lay down conventions
- Write `CLAUDE.md` (mission + workflow) and `PIPELINE.md` (the layered spec,
  the linking model, the bookmark-free timing rule, the overflow rule, the
  Cowork/CLI split). Copy this repo's versions as a starting point.
- Build `scenes/_style.py` first: palette + type scale, `pr()` (notation match),
  `fit_to_frame()` (overflow guard), a chart builder (`make_pmf_chart`), and the
  linking template (`intro_card`, `outro_bridge`, `progress_tag`).

### Step 3 — Build the manifest
- Bootstrap with `python tools/init_project.py input/<Subject>`: it scans the
  input folder (detecting `.tex` + companion pandoc `.md` pairs) and writes a
  draft `project.yaml`. Then curate it: every chapter in teaching order with
  `slug`, `title`, `upstream`, `status: planned`, `prereqs` (the draft assumes
  a linear chain), notation rules, and (where known) a `videos:` list of
  per-project ~5–20 min section videos (`init_project.py` asks for the
  budget). This is the spine the later stages read.

### Step 3.5 — Vendor editable working copies
- `python tools/vendor_sources.py` copies each read-only parent `.tex` into
  `sources/{slug}.tex` with a provenance header (upstream path/hash + git
  origin/commit/tag when available), and repoints each concept's `source:` to
  the copy. The pipeline builds from `sources/`, so the parent stays pristine.
- If a source's notation conflicts with `NOTATION.md`, fix it on the copy:
  `python tools/normalize_notation.py --write`, then re-stamp.

### Step 4 — Per-chapter generation (three transforms, each gated by review)
1. **concept-from-tex:** read `{Slug}.tex` → write `content/{slug}.md` (YAML +
   the seven prose sections: What / Why / How / What else / Conceptual
   progression / Visual opportunities / Deliberately out of scope).
2. **script-from-concept:** read concept (+ tex) → write
   `content/{slug}-script.md` (YAML incl. a `linking:` block; one beat per
   section with literal narration + animation cues; a cut list). Recap names the
   previous chapter, bridge names the next (from `project.yaml`).
3. **scene-from-script:** read script → write `scenes/{slug}.py` as
   `VoiceoverScene` classes. **Follow the Chapter 5 pattern exactly:** bookmark-
   free sequential `with self.voiceover(...)` blocks timed with
   `run_time=tracker.duration`; open with `intro_card`, close with
   `outro_bridge`; route every graph through `fit_to_frame` /`make_pmf_chart`.
- Gate each step on `status` (draft → reviewed → approved) so a human can vet
  narration before any render.

### Step 5 — Render and self-correct (Mac / CLI)
```
uv run manim -ql -a scenes/{slug}.py          # draft all videos in the chapter
uv run manim -ql scenes/{slug}.py SceneClass  # a single video
./render_all.sh                                # 1080p60 finals
```
Close the loop: on a traceback, read it, fix the script/scene, re-render. The
most common first failure is a `MathTex` LaTeX error.

### Step 6 — Verify coherence (both axes)
- **Horizontal:** recap/bridge chain links correct neighbors; uniform notation
  (`\Pr`); consistent schema across files.
- **Vertical:** each chapter's concept + script faithfully represent its tex
  (no fabricated theorems/numbers). Use adversarial reviewer sub-agents.
- **Overflow:** confirm graphs pass through `fit_to_frame`.
- **Notation:** `python tools/check_notation.py` (enforces `NOTATION.md`).
- **Sync:** `python tools/stamp_provenance.py` then `python tools/check_sync.py`
  — confirms every layer is in sync with its source by content hash.

### Step 7 — (Optional) Assemble
- ffmpeg pass: uniform encode + loudness-normalize + crossfade joins → a stitched
  course cut with chapter markers, or keep a per-chapter playlist.

---

## 6. Gotchas and dead-ends already paid for (so you don't repeat them)

- **Cowork sandbox can't render.** `manimpango` has no pango dev headers and no
  prebuilt wheel there; manim won't import. Render on the Mac. (In the sandbox
  you can still do all text/markdown/codegen work and syntax-check with
  `python -m py_compile`.)
- **Python 3.14 breaks the voiceover stack.** `openai-whisper`'s old pin won't
  build; PyTorch has no 3.14 wheels; setuptools removes `pkg_resources`. Use
  3.12. Symptom on a fresh box: `ModuleNotFoundError: pkg_resources` →
  `uv add "setuptools<81"`.
- **Bookmarks need Whisper.** manim-voiceover `<bookmark>` requires word-level
  timestamps (Whisper → PyTorch). Avoid: use sequential voiceover blocks. Script
  `<bookmark>` tags are *authoring markers only*, realized as separate blocks.
  (If you ever truly need word-level sync, Azure TTS provides native word
  boundaries without Whisper.) Corollary found in practice: `OpenAIService`
  tries to transcribe BY DEFAULT and dies with "Missing packages …
  manim-voiceover[transcribe]" — always construct it with
  `transcription_model=None`.
- **SoX warning is harmless** — it's only for mic-record mode; ignore it with
  gTTS/OpenAI.
- **gTTS needs internet; OpenAI needs `OPENAI_API_KEY`.** Both cache audio by a
  hash of the narration text, so unchanged beats are never re-synthesized.
- **OpenAI `/audio/speech` requests can hang for the SDK's full 600 s default
  timeout**, then succeed instantly on retry — observed twice in one render
  (≈10 dead minutes per scene boundary). manim-voiceover's `OpenAIService`
  uses the module-level client, so configure it before use in
  `make_speech_service()`: `openai.timeout = 30; openai.max_retries = 5`.
  A stalled request then costs ~30 s, not 10 min.

---

## 7. What's not done yet (next steps)

- Build the three processor skills as repo files (`.claude/skills/` +
  an `/animate-chapter` command) so chapters generate themselves from
  `project.yaml`.
- Generate `scenes/{slug}.py` for chapters 1–3, 6–12 (currently `scripted`).
- Build the concept DAG + "used-before-taught" checker.
- Build the optional ffmpeg assembly step.
- Re-cut Chapter 4 in the voiceover style to match the rest.
