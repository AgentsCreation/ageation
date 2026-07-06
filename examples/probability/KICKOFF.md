# Claude Code — Kickoff Prompt

Paste the block below into Claude Code CLI from inside `~/sandbox/ManimCE`.
It hands off an established project and points the local agent at the work that
the cloud (Cowork) sessions could not do: render video, run git, install deps.

---

You are taking over an established project in this repo: a file-based pipeline
that turns LaTeX probability notes into short, narrated, linked Manim videos.
The architecture and all 12 chapters' markdown scaffolding already exist. Your
advantage over the previous Cowork sessions: you are on a Mac with a full local
environment, so you CAN render video, run git, and install packages — they could
not.

## 1. Orient yourself (read in this order)
1. `HISTORY.md` — the full story: goal, every design decision WITH rationale,
   what exists, and a reproduce-from-scratch roadmap. The decisions marked
   "do not relitigate" are settled.
2. `PIPELINE.md` — the layered pipeline spec and conventions.
3. `CLAUDE.md`, `NOTATION.md`, `project.yaml` — repo rules, fixed notation, the
   chapter spine.
4. Reference implementation (the pattern to copy): `content/5-discrete-random-
   variables.md`, `content/05-discrete-random-variables-script.md`, and
   `scenes/discrete_random_variables.py` (Chapter 5 — the only fully-built one).

## 2. Set up the environment (once)
- Finish the commit a Cowork session staged but couldn't finalize (the cloud
  mount blocks git's rename/unlink): `rm -f .git/index.lock`, then
  `git add -A && git status` (confirm `media/`, `input/`, `.venv/` are NOT
  listed), then commit. `git gc` clears stray `tmp_obj_*` objects.
- `brew bundle && uv sync` (system + Python deps).
- Re-fetch the read-only sources if `input/` is absent (it's gitignored); the
  committed `sources/` copies are enough to build from regardless.
- Sanity: `make check` (provenance + notation gates — should be green) and
  `uv run manim --version`.

## 3. The work (priority order)
1. **Prove the local pipeline.** Render Chapter 5: `./render_all.sh l`, then
   actually open frames / the video and check layout + overflow. Run the
   self-correcting loop (render → inspect a frame → fix → re-render). This is the
   step Cowork literally could not perform.
2. **Build `scene-from-script`.** A repeatable transform that reads
   `content/{slug}-script.md` and emits `scenes/{slug}.py` following the Chapter 5
   pattern EXACTLY: `VoiceoverScene`; sequential, bookmark-free
   `with self.voiceover(...)` blocks timed by `tracker.duration`;
   `intro_card`/`outro_bridge` bookends; every graph through
   `make_pmf_chart`/`fit_to_frame`; notation via the `_style` helpers
   (`pr`/`expectation`/`variance`). Package it as a `.claude/` skill or command.
3. **Generate + render Chapter 6** (Discrete Expectations) through that
   generator. Loop render→inspect→fix until clean. Then set its `project.yaml`
   status to `built`, run `uv run python tools/stamp_provenance.py`, and
   `make check`.
4. **Repeat** for the remaining chapters, gating each on the `status` field —
   do not mass-generate unreviewed chapters.

## 4. Hard rules (from HISTORY/CLAUDE/NOTATION — do not break)
- Build from `sources/` via the script layer. Never edit `input/` (read-only).
  Don't hand-patch a generated `.py` without changing its script.
- Notation: `\Pr` / `\mathrm{E}` / `\mathrm{Var}`; keep `make notation` green.
- Provenance: re-stamp after regenerating any layer; keep `make sync` green.
- Finals render at `-qh` (1080p60) or `-qk` (4K) via `render_all.sh`.
- Keep history thin: `media/` and `input/` stay gitignored. Commit per chapter.

Start by reading HISTORY.md and PIPELINE.md, then report a short plan before
generating anything.

---
