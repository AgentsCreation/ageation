# STYLE_BOOK.md — House Style for the Manim Video Series

The look, feel, and authoring conventions every video in the series shares.
This is the *aesthetic* companion to the *process* docs: **PIPELINE.md** (the
layered spec), **NOTATION.md** (per-project notation rules), and **HISTORY.md**
(settled design decisions). When those and this file overlap, the rules here are
the visual realization of decisions recorded there.

The single source of enforcement is **`scenes/_style.py`** — import from it
rather than hard-coding. The reference implementation of every rule below is
`examples/probability/` (Chapter 5 for scene structure; the Chapter 3 videos —
`sample_spaces`, `probability_laws`, `model_categories`, `continuity_measure` —
for the mature two-column diagram idiom).

---

## 0. What ageation optimizes for — the register

ageation makes videos that are **educational and strongly support the
notes**, produced in a *structured, robust* way so the human time invested
is minimal and any video can be improved later. That goal is deliberately
different from artisanal mathematical animation (the 3Blue1Brown ideal):
we do not chase bespoke composition per scene. We chase **predictable
layouts, best-practice type and color, and a consistent formal register** —
and spend the creativity budget on the individual animations inside that
frame.

Concretely, the register means:

- **Formal-leaning terminology.** The narration names objects the way the
  notes do. The recurring substitutions, now enforced by
  `tools/lint_language.py`:

  | Avoid                  | Say instead                                    |
  |------------------------|------------------------------------------------|
  | "bell" (bare)          | "Gaussian density" / "PDF" / "distribution"    |
  | "bell curve" (refrain) | at most once per video, where the name matters |
  | "ramp"                 | "smooth progression" / "continuous CDF"       |
  | "masses" (spoken)      | "probability mass functions" when it names PMFs|
  | "dies" (a term → 0)    | "vanishes" ("the variance vanishes like 1/n") |

- **Sentences sized for the ear.** A spoken sentence over ~40 words reads
  breathlessly under TTS; a voiceover block over ~70 words can't sync its
  visuals. Split at clause turns; each `<bookmark/>` segment becomes its
  own sequential voiceover block. (`lint_language.py` flags both as
  advisories.)

- **Callbacks are anchored in topics, never in video numbers.** "Video 22"
  breaks the moment a video is inserted; "when we split the Poisson
  stream" never does. Chapter numbers are fine (they belong to the book);
  "last / this / next video" are fine (structural). Everything else is a
  `lint_language.py` violation.

- **Predictable layout beats clever layout.** The layout helpers in §6 are
  not suggestions — a scene that hand-places what a helper places is a
  review note waiting to happen.

---

## 1. Palette — color carries one meaning

Four named colors, defined once in `_style.py`. Do not introduce ad-hoc colors
for text; the geometry palette (BLUE/TEAL/GREEN/MAROON) is for *diagram* fills
only.

| Token   | Value  | Meaning                                                    |
|---------|--------|------------------------------------------------------------|
| `ACCENT`| YELLOW | **The one idea currently in focus.** Never decorative.     |
| `INK`   | WHITE  | Primary text and formulas.                                 |
| `MUTED` | GRAY_B | Taglines, captions, axis labels, de-emphasized prose.      |
| `BAR`   | BLUE   | Default PMF bar fill / "the countable" tier.               |

**The accent discipline is the most important rule in this document.** At any
moment exactly one thing should be yellow: the equation being derived, the
result just reached, the term being named. When the focus moves, the previous
accent object either fades or demotes to `INK`. A frame with two yellow things
competing for attention is a bug.

Diagram fills use the standard Manim geometry colors at low opacity
(`set_fill(col, opacity=0.20)` for nested regions, `0.7` for solid shells), with
`INK` strokes. When a scene mirrors another (e.g. *Continuity from Above* mirrors
*from Below*), reuse the **same radii, colors, and positions** so the pair reads
as a matched set.

---

## 2. Type scale — five sizes, no in-betweens

Defined in `_style.py`; retune pacing/readability in one place.

| Token     | pt | Use                                             |
|-----------|----|-------------------------------------------------|
| `TITLE`   | 56 | Intro-card title only.                          |
| `SECTION` | 44 | Per-scene section heading (`section_title`).    |
| `BODY`    | 34 | Main formulas, primary statements.              |
| `SMALL`   | 28 | Secondary formulas, list items, sub-derivations.|
| `CAPTION` | 24 | Labels, captions, axis labels, progress tag.    |

Pick from the scale; never pass a raw `font_size=31`. If something doesn't fit,
scale the *group* with `fit_to_frame`, don't invent a font size.

---

## 3. Everything stays inside the frame — enforced, not eyeballed

- Wrap every chart, diagram group, and composed `VGroup` in **`fit_to_frame`**
  before positioning it. It scales down (never up) to the safe area
  (`SAFE_MARGIN = 0.5` scene units off each edge) and is a no-op when it already
  fits. This holds at any render resolution — that's the point of doing it in
  code instead of by looking at a frame.
- **No line of text or math may touch or cross a frame border.** Keep a visible
  gap. When the reviewer flags "extend to close to the bottom," it still means
  *with an appropriate gap*, never flush.
- Axis labels use `axis_label_x` / `axis_label_y` (default `LABEL_BUFF = 0.40`),
  which clears multi-word labels the geometric-overlap lint can't catch.

---

## 4. Math is always typeset — never faked with prose

- Every mathematical symbol renders through `MathTex`, in a raw string
  (`r"..."`). Ω is `r"\Omega"`, never the literal character or the word "Omega";
  a union is `r"\bigcup"`, a conditional bar is `r"\mid"` (never bare `|`).
- **Notation is fixed per project in `project.yaml`** and enforced by
  `tools/check_notation.py` — it scans prose too, so the forbidden literals
  (`\mathbb{P}`, `\mathbb{E}`, `\mathbb{V}`, …) must not appear even in a
  narration or concept file. Use the expanded forms via the `_style.py` helpers:
  `pr("A \mid B")`, `expectation("X")`, `variance("X")`. `\mathbb{N}/\mathbb{Q}/
  \mathbb{R}` are allowed (they're not macro-shadowed).
- Reveal formulas **incrementally**: `Write` a line at a time,
  `TransformMatchingTex` when one form becomes another. Don't dump a full
  multi-line derivation in a single `Write`.

---

## 5. Scene skeleton — the shared structural grammar

Every video is a sequence of `VoiceoverScene` beats, one class per beat, named
to match `scene_class` in the script YAML.

**Open** with `intro_card(title, objective, kicker=...)` — kicker (accent) +
title + one-line objective (muted). **The title is the *video's own* name, not
the chapter's** — the chapter belongs in the kicker (`Chapter 5  ·  Discrete
Random Variables`), the white title states what *this* beat sequence is about
(`Functions of Random Variables`). Stating the objective up front is
deliberate. **No on-screen "Recap:" line.** The spoken recap belongs in the
narration only (the open still *reactivates* the prior video by voice); do not
render a "Recap: …" caption on the overview card — for the book/notes shape it
is redundant with the kicker + objective and just crowds the slide. **Close**
the chapter's final beat with a "Key idea" card (`outro_bridge`, or a hand-built
centered two-line version) plus a one-line bridge to what's next. A
`progress_tag(i, n)` sits in the `DR` corner to orient the viewer in the arc.

Within a beat, the section heading pattern is:

```python
title = section_title("Continuity from Below")
fit_to_frame(title)
self.play(Write(title))
self.play(title.animate.to_edge(UP))   # write centered, then dock it up
```

End every beat by clearing the stage:

```python
self.play(*[FadeOut(m) for m in self.mobjects])
```

---

## 6. The two-column diagram idiom

The mature layout for a "picture + math" beat (see `continuity_measure.py`):

- **Left column:** the diagram, vertically centered, anchored at a constant
  `C = LEFT*3.4 + DOWN*0.15`. The sample-space frame is `omega_box(...)` — a
  rounded muted rectangle with an `\Omega` label tucked at its upper-left corner.
- Any **union/limit label for the whole diagram** (`A = \bigcup_k A_k`) sits
  **below** the frame in `ACCENT`, clear of the geometry — never overlapping the
  circles.
- **Right column:** the statement, then the definitions, then the derivation —
  built top-down at `RIGHT*3.3 + UP*{1.7, 0.6, ...}`, each block
  `.next_to(previous, DOWN, buff=...)`. Long equations go on **two
  left-aligned lines** (`arrange(DOWN, aligned_edge=LEFT)`) so the second reads
  as a continuation of the first.
- Balance the gaps: title→diagram-top ≈ equation-bottom→frame-bottom; left/right
  edge gaps around a boxed group match its top gap. The reviewer's spacing notes
  are almost always about restoring this symmetry.

**Use the layout helpers (`_style.py`) — they encode the repeated notes:**

| Helper                    | The review note it retires                         |
|---------------------------|----------------------------------------------------|
| `two_column(left, right)` | "the two sides should sit level, raised toward mid-frame" — both columns centered at the same y (default −0.9), leaving the caption lane free below. |
| `eq_chain(lhs, *rhs)`     | "align the equals signs / the equations are so far apart it's unclear they're related" — one derivation, one `=` column, tight buff, centered. Continuation lines are `("=", rhs)` parts (MathTex drops empty leading parts — the trap that shipped once). |
| `even_stack(*mobjects)`   | "reclaim the space vertically to get good spacing" — equal gaps down the content zone. |
| `caption_under(chart, s)` | "center the sentence on the chart it describes" — CAPTION line on the object's own x. |
| `chart_tag(tex)`          | "the λ = … label is a bit small" — BODY-size parameter tags on charts. |

**Positioning defaults (the 2026-07-04/05 review digest):**
- **A beat's main content centers on `zone_center_y(title)`** — halfway
  between the docked title's bottom and the frame bottom (≈ −0.5). The
  reviewer stated this rule three times in one round; it beats resting
  content low. The 0.8 bottom margin remains the floor for the *lowest*
  element.
- Left charts in a two-column beat ride HIGH: `to_edge(DOWN, buff=1.2–1.4)`,
  not 0.8 — the 0.8 minimum is a floor for the *lowest* element, not a
  resting place for charts with content below them.
- Dashed reference lines start **at the y-axis** (`axes.c2p(0, v)`), never
  crossing the tick labels to the left of it.
- Tick labels must never sit under a bar/rectangle: fade the colliding tick
  or anchor labels to the shape's outer edge.
- When the narration says "area", the area is **shaded on screen at that
  moment** (fill opacity ≈ 0.3, declared with `mark_intended_overlap`).
- A beat that walks several named objects in sequence (Laplace, then
  Cauchy) transforms its **section title** at each hand-off.

---

## 7. Animation vocabulary — a small, consistent set

| Intent                        | Animation                                             |
|-------------------------------|-------------------------------------------------------|
| Introduce a formula / label   | `Write` (line by line)                                |
| Introduce a shape / axes      | `Create`                                              |
| Bring in prose / an item      | `FadeIn(m, shift=RIGHT*0.4)` (or `UP/DOWN*0.2`)       |
| Reveal a group in sequence    | `LaggedStartMap(FadeIn, group, lag_ratio=0.2–0.3)`    |
| Emphasize the just-derived    | `Indicate(m, color=ACCENT, scale_factor=1.03)`        |
| Grow nested regions           | `LaggedStartMap(GrowFromCenter, circs, lag_ratio=0.3)`|
| Clear the stage               | `FadeOut` every mobject                               |

Keep `run_time`s short and varied (0.4–1.2 s) so beats feel crisp; the narration
sets the real pace. Small directional `shift`s (0.1–0.4) give motion without
distraction.

**Two gotchas that fail at render time** (also in CLAUDE.md):
- Don't `LaggedStartMap` a single-mobject animation (`Create`, `Write`) over
  composite mobjects — its arg_creator `*`-unpacks submobjects into positional
  slots. Use `LaggedStart(*[Create(m) for m in group], lag_ratio=...)`.
  (`FadeIn` tolerates it.)
- `Axes.plot` returns a pointless curve for a **decreasing** `x_range`, crashing
  any path use. Plot increasing, then `.reverse_points()`.

---

## 8. Narration & timing — bookmark-free, narration-first

- **Narration is the source of truth for timing.** Each authoring
  synchronization marker is realized as a **separate sequential
  `with self.voiceover(text=...)` block** — no bookmarks. Visuals inside the
  block are timed to land with the words.
- Numbers and symbols are **spoken as words** in the narration ("two to the
  minus k", "Pr of A", "A-k-minus-one") while typeset on screen.
- **Respell for the TTS ear when the dictionary fails it**: the narration is
  input to a speech engine, so a word it mispronounces gets a phonetic
  spelling in the *spoken* text only — "kai square" for the Greek χ (the
  engines say "chai" otherwise). On-screen text and formulas keep the real
  spelling (`\chi^2`, "chi-square"). (2026-07-05 review note.)
- Keep each beat under ~60 s of content; target minutes per video come from
  `project.yaml` (`pedagogy.target_minutes_per_video`).

---

## 9. Voice: draft cheap, final per-video — and the pace is 1.0

- **Voice is configuration, not code.** Scenes call `_style.speech_service()`
  from `make_speech_service()`; the provider/voice come from `project.yaml`'s
  `project.voice` block (`provider`, `name`, optional `model`). No hand-edited
  provider lines in scene files.
- **Draft** renders use gTTS (free) so the human can review layout and timing
  at 480p without hitting an API: `tools/render.py` exports `AGEATION_TTS=gtts`
  for `-ql` drafts automatically, and the env var beats the config. Set it
  yourself when rendering manim by hand.
- **Final** renders use the configured OpenAI voice
  (`OpenAIService(..., model="tts-1", transcription_model=None)`, preceded by
  `configure_openai_client()` — 30 s timeout, 5 retries; the SDK default is a
  600 s stall). The final voice **is a per-video decision**: `nova` is this
  book's house voice, but *ask before defaulting* — `speech_service()`
  deliberately errors when `voice.name` is missing rather than picking one.
  `OPENAI_API_KEY` is read from the shell or lifted from `<project>/.env`
  (render.py merges it into the manim subprocess; the scene helper lifts it
  too for hand runs).
- **Speaking pace is 1.0.** Generation-time `speed` stays at the default;
  1.25 was tried and reverted. Do not raise it without being asked.
- The sandbox cannot reach the OpenAI API, so **the human runs the final nova
  render in their own terminal.** The agent's job is to wire the voice, keep the
  gates green, and hand over the scoped render command.

---

## 10. The review loop — how a video actually gets polished

1. Agent builds the beat, renders a **gTTS 480p draft**, assembles it.
2. Human reviews the single assembled `.mp4` and leaves **timestamped notes**
   (e.g. `(1:54) move the B_1 block up a bit`). Notes are precise and layout-
   focused; the human frequently edits the `.py` directly between renders.
3. Agent applies the note, re-renders **just that scene**, extracts a frame with
   ffmpeg, and reads it back to verify before moving on.
4. When the human says "ready for high res and nova," the agent re-stamps
   provenance, confirms `make check` is green, and hands over the 1080p
   command — no voice edit needed: final quality reads the configured voice
   (drafts alone force gTTS via `AGEATION_TTS`).

Corollary: when the same render request repeats, the human is iterating in their
editor between asks — **just re-render**, don't ask what changed.

---

## 11. Provenance & gates — what to re-run after an edit

- **Visual-only edits** (positions, sizes, colors — nothing in the spoken text)
  need **no re-stamp**; sync stays green on its own.
- **Narration edits** must be mirrored into the script `.md` (and, ideally, the
  concept `.md`), then re-stamped with `tools/stamp_provenance.py`.
- `make check` (`check_sync.py` + `check_notation.py`) must pass before a final
  render. `lint_scene.py` catches geometric overflow the eye misses.
- **Intended overlaps are declared in the scene**, not in a sidecar: wrap the
  overlapping mobjects in `mark_intended_overlap(a, b, ..., reason=...)`
  (from `_style`) *before the first `play()` that shows them*. The mark
  survives regrouping and `Transform`; the old index-addressed
  `<scene>.lint-allow.yaml` sidecars are deprecated (they break on any
  structural edit). Audit what marks suppress with `lint_scene.py --verbose`.
- Runtime is measured, not eyeballed: `assemble` (or `make measure`) writes
  `measured_sec` per beat back into the script, and `check_status` enforces
  `target_runtime_sec ± tolerance_sec` once a chapter is `rendered`.

---

## 12. Review lessons — the recurring notes, distilled

These are the corrections that came back over and over across Chapters 4–5
(and the 2026-07-03 Chapter 6 sessions, marked "Ch6"). They are already
implied by the sections above, but they earned their own list because each
one was a *repeated* fix. Apply them the first time, not on review.

**Series-robustness (2026-07-04 Chapter-7 review harvest):**
- **Never reference another video by NUMBER** — not in narration, not in
  on-screen text. Numbering is brittle: inserting one video later breaks
  every cross-reference. Refer to *concepts* instead ("when we built the
  joint table", "the conditional-expectation video", "last video" only when
  the immediate predecessor is meant and the order is structural).

**Terminology (2026-07-04 continuous-chapter review harvest):**
- **No "ramp"** for continuous CDFs — say "smooth progression" or simply
  "continuous CDF" (reviewer replaced the word across two videos).
- **No bare "bell"** for the Gaussian — say "Gaussian density", "PDF", or
  "distribution". The full phrase "bell curve" is acceptable sparingly,
  where the classic name itself is the point (once per video at most).

**Ch6 harvest (Meeting Expectations, videos 18–20):**
- **Charts keep a ≥0.8-unit bottom margin** (`to_edge(DOWN, buff=0.8)`), and
  two-column compositions ride slightly high so late-arriving bottom lines
  land in their own lane — plan the *final* frame's balance from the start.
- **Insert `self.wait(0.5)` between the framing block and the outline** (and
  at any paragraph turn): sequential voiceover blocks join gaplessly, which
  reads as breathless with the final voice.
- **Outline/list lines land clause-by-clause** — one voiceover sub-block per
  item, never one block with a lagged reveal.
- **One visual per spoken concept**: when narration walks alternatives
  (skewness then kurtosis), each gets its own sub-block and the swap happens
  at the clause boundary — never two stills paced by `wait()` inside one
  block.
- **Never label a marker where an axis tick already says the value** — the
  dot (plus a final `Indicate`) is enough; a duplicate accent number
  collides with the tick.
- **Voice/card harmony**: the outro's spoken key idea and the card text say
  the same words; anything on screen that isn't spoken stays `MUTED`.
- **TTS calibration**: nova at 1.0 measures ≈0.80× the gTTS draft duration
  (three chapters: 262.7→210.8, 404.8→320.2, 281.3→225.1 s). At script
  approval, set `target_runtime_sec ≈ 0.8 × draft measured`; do not budget
  as if nova were slower.

**Charts (the most-revised object — all of this lives in `make_pmf_chart`):**
- **Make it big and legible.** Axis tick numbers at `TICK` (26 — "one size
  smaller everywhere", 2026-07-05 review), axis *names* at `BODY`. A chart
  shrunk until its labels vanish is worse than one that crowds slightly;
  a chart whose ticks shout over the content is the newer failure mode.
- **Extend the x-axis one unit left** (`x_range` starts at `-1`, exclude `-1`
  from the drawn numbers) so the first bar isn't jammed against the y-axis.
- **The axis name (`k`, `x`) goes below-right of the tip**, never up where the
  bars live. The y-name must not collide with a story-note above the chart —
  if they fight, move the note or lower the chart.
- **Raise the chart off the bottom edge and leave a caption lane** beneath it;
  the bottom third is reserved for the spoken-story caption, never bars.
- **One chart on screen at a time.** Erase the current chart before the next
  beat's content arrives; reclaim and reuse the space rather than stacking.

**Reuse the established figures — don't reinvent per scene:**
- Numbered outcomes → the `ball()` disk (colored fill, `INK` stroke, **dark**
  centered number). Dice → the pip `die_face`. Copy the helper from the earlier
  chapter; a chapter that draws its own balls reads as a different series.
- Leave **a small gap between a source glyph and the tail of an arrow** leaving
  it (~0.4 units off a 0.24-radius ball) — arrows must not grow out of the disk.

**Layout & alignment:**
- **Split a long line into two centred lines** — objectives, key-idea cards, a
  telescoping second equation line, a list of event definitions. The natural
  break goes where the clause turns (`…, Y = g(X),` / `and compute its PMF…`).
- **Align commentary under what it describes.** Text about *two* graphs centres
  on their **midpoint**, not under the right-hand one. Balance outer margins so
  the left gap equals the right gap.
- **Nothing overlaps anything.** y-label vs note, arrow vs bar, caption vs
  caption. When two elements collide, move one out of the other's column or
  below the axis — don't just nudge.

**Sync visuals to the voice:**
- **Reveal each element exactly as it is named.** Split a beat's narration into
  per-phrase `with self.voiceover(...)` sub-blocks so an event line appears as
  it's spoken, the normalization equation lands on "it normalizes," each drawn
  ball leaves as its fraction is said. (Concatenated sub-blocks must equal the
  original narration verbatim — then no re-stamp is needed.)

**Narration hygiene (it's read aloud — write for the ear):**
- **No em-dash `--` in an on-screen caption** — a colon or comma reads cleaner.
- **Drop filler and repetition:** cut a leading "So" at a beat's start; never
  reuse "again and again"; prefer "frequently" over "constantly."
- **Say it precisely, not absolutely:** "possibly a tall one and a short one"
  (it depends on `p`), not a false certainty.
- **Trim commitments you may not keep:** a "Coming up: …" / "Next chapter …"
  line — *and its spoken sentence* — comes out unless the bridge is wanted.

**Math you must get right before rendering:**
- **Validate parameters.** `p = λ/n` needs `n > λ` (a binomial→Poisson panel
  with `λ=10` can't use `n=5`). A probability never exceeds 1.
- **Distinguish conditional from unconditional.** Swapping `Pr(A₂)` for
  `Pr(A₂ ∣ B)` can silently make dependent events look independent.
- **State the index range next to a PMF:** `p_X(k) = …,  k = 0, 1, …, n`.

**Outros:**
- Build multi-line text as **separate `Text` mobjects (or a `VGroup`)**, never
  one `Text` with an embedded `\n` — that renders garbled/overlapping.
- Match the house close: "Key idea" (accent) + the takeaway, split to two lines
  if long, optional one-line bridge.

**The meta-lesson:** when a fix should be uniform across the series, **push it
into the shared helper (`_style.py`)**, not the one scene in front of you — the
chart, ball, and die fixes above all became shared code so every chapter
inherits them. A per-scene patch of a shared idiom is a bug waiting for the
next chapter.

---

## 13. The deliverable

**One assembled `.mp4` per chapter** — that is what the human reviews and ships.
Per-beat clips stay on disk for cheap iteration but are not the product. Build
with `make video-draft` (480p) / `make video` (1080p60), or `render.py` +
`assemble.py` scoped to a slug. Deliverable path:
`media/videos/<module>/<quality>/_assembled/<slug>.mp4`.
