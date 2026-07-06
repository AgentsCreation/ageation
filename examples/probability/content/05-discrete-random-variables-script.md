---
slug: 05-discrete-random-variables
title: Discrete Random Variables
stage: script             # tex -> concept -> [script] -> scene -> render
status: approved             # draft | reviewed | approved  (human gate)
derived_from: 05-discrete-random-variables.md
derived_from_sha256: 2249b15af8240940739f33ae8adce39b0b5fb4c03e0c9544a4096d8f18199ec7
provenance_stamped: 2026-07-06
target_scene_file: scenes/discrete_random_variables.py

# --- Narrative glue (links this video to its neighbours) -------------------
# objective : the learning goal, spoken in the intro_card (retention: state
#             the goal up front).
# recap     : reactivates the previous chapter at the open (spacing).
# key_idea  : one-line takeaway spoken in outro_bridge (retrieval cue).
# bridge    : teases the next chapter at the close.
# Neighbour titles for recap/bridge come from project.yaml prereqs + order.
linking:
  objective: "Turn outcomes into numbers and describe them with a PMF."
  recap: "Last chapter we conditioned probabilities on partial information."
  key_idea: "A discrete RV is fully described by its probability mass function."
  bridge: "Next: expectation — collapsing a whole PMF into a single number."

# --- Voice + timing config -------------------------------------------------
voice:
  provider: gtts          # draft default; openai for finals
  model: tts-1
  name: alloy
  rate: 1.0
words_per_minute: 150     # used only for the pre-TTS estimate
target_runtime_sec: 360
tolerance_sec: 30         # build fails review if |actual - target| > tolerance

# --- Estimates vs measured -------------------------------------------------
# est_sec are computed from narration_words / wpm (cheap, pre-render).
# measured_sec is written back by the render stage from tracker.duration.
estimated_runtime_sec: 332
measured_runtime_sec: 126.0

beats:
  - id: overview
    scene_class: ChapterOverview
    narration_words: 58
    est_sec: 23
    measured_sec: 24.9
    sync_points: []
  - id: rv-mapping
    scene_class: RandomVariableMapping
    narration_words: 92
    est_sec: 37
    measured_sec: 23.6
    sync_points: [show-omega, fire-arrows, show-definition]
  - id: pmf-gallery
    scene_class: PMFGallery
    narration_words: 140
    est_sec: 56
    measured_sec: 30.5
    sync_points: [bernoulli, binomial, poisson, geometric]
  - id: binomial-to-poisson
    scene_class: BinomialToPoisson
    narration_words: 118
    est_sec: 47
    measured_sec: 47.1
    sync_points: [n5, n15, n25, n35, settle]
---

# Video Script — Discrete Random Variables

Narration is the source of truth for timing. Each `<bookmark mark="id"/>` is a
synchronization point: in the generated scene, the corresponding animation is
triggered at that word via `tracker.time_until_bookmark("id")`. Animations with
no bookmark simply fill `run_time = tracker.duration` for their beat.

---

## Beat: overview  (scene: ChapterOverview)

> Probability spaces tell us how likely events are, but they don't give us
> numbers to work with. A random variable fixes that. In this chapter we turn
> outcomes into numbers, describe them with a probability mass function, meet
> the distributions you'll see again and again, and finish with a surprising
> limit.

**Animation cue:** title card in, then reveal the four outline items as the
last sentence is spoken (one item per clause).

---

## Beat: rv-mapping  (scene: RandomVariableMapping)

> Here is a sample space <bookmark mark="show-omega"/> Omega, with a handful of
> outcomes. A random variable is just a function: <bookmark mark="fire-arrows"/>
> it sends each outcome to a point on the real line. Different outcomes can land
> on the same number — that's allowed. Formally, <bookmark mark="show-definition"/>
> we write X maps Omega to the real numbers.

**Cues**
- `show-omega`: fade in the Omega box and the colored outcomes.
- `fire-arrows`: lag-animate the curved arrows to the number line.
- `show-definition`: write `X : Omega -> R` along the bottom.

---

## Beat: pmf-gallery  (scene: PMFGallery)

> The probability mass function lists how much probability sits on each value.
> The simplest case is <bookmark mark="bernoulli"/> the Bernoulli — a single
> coin flip, all the mass on zero and one. Add up n independent flips and you
> get <bookmark mark="binomial"/> the binomial. Counting rare events over time
> gives <bookmark mark="poisson"/> the Poisson. And waiting for the first
> success gives <bookmark mark="geometric"/> the geometric, whose bars decay by
> a constant factor.

**Cues:** at each bookmark, transition to that distribution's formula and grow
its PMF bars from the axis. Keep the y-axis shared so heights are comparable.

---

## Beat: binomial-to-poisson  (scene: BinomialToPoisson)

> Here's the payoff. Fix a rate lambda, and let each of n trials succeed with
> probability lambda over n. <bookmark mark="n5"/> With just five trials the
> binomial is coarse. <bookmark mark="n15"/> Fifteen trials, and it sharpens.
> <bookmark mark="n25"/> Twenty-five — <bookmark mark="n35"/> thirty-five — and
> the bars <bookmark mark="settle"/> settle right onto the Poisson curve. The
> binomial, in the limit, becomes Poisson.

**Cues**
- `n5/n15/n25/n35`: `Transform` the bar group to each successive n; update the
  on-screen `n =` label in lockstep.
- `settle`: pulse the faint Poisson reference so the match is unmistakable.

---

## Cut list (if over budget)
1. Drop the optional `functions-of-rvs` concept entirely (already omitted).
2. Trim `pmf-gallery` to Bernoulli + binomial + Poisson (cut geometric).
3. Shorten outline reveal in `overview`.
