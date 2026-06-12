---
slug: 6-discrete-expectations
title: Discrete Expectations
stage: script             # tex -> concept -> [script] -> scene -> render
status: draft             # draft | reviewed | approved  (human gate)
derived_from: 6-discrete-expectations.md
derived_from_sha256: ed4082828843146041686a8edec1f31a78d5b6c23bd59987c80754b2174632ae
provenance_stamped: 2026-06-11
target_scene_file: scenes/discrete_expectations.py

# --- Narrative glue (links this video to its neighbours) -------------------
# objective : the learning goal, spoken in the intro_card (retention: state
#             the goal up front).
# recap     : reactivates the previous chapter at the open (spacing).
# key_idea  : one-line takeaway spoken in outro_bridge (retrieval cue).
# bridge    : teases the next chapter at the close.
# Neighbour titles for recap/bridge come from project.yaml prereqs + order.
linking:
  objective: "Summarize a whole PMF with a mean and a variance."
  recap: "Last chapter, Discrete Random Variables, we described an RV by its probability mass function."
  key_idea: "Expectation collapses a PMF into a mean — the center of mass — and a variance for its spread."
  bridge: "Next: Discrete Vectors — joint PMFs, conditional expectation, and how two random variables interact."

# --- Voice + timing config -------------------------------------------------
voice:
  provider: openai        # gtts (free draft) -> openai/elevenlabs (final)
  model: tts-1
  name: alloy
  rate: 1.0
words_per_minute: 150     # used only for the pre-TTS estimate
target_runtime_sec: 360
tolerance_sec: 30         # build fails review if |actual - target| > tolerance

# --- Estimates vs measured -------------------------------------------------
# est_sec are computed from narration_words / wpm (cheap, pre-render).
# measured_sec is written back by the render stage from tracker.duration.
estimated_runtime_sec: 346
measured_runtime_sec: null

beats:
  - id: overview
    scene_class: ChapterOverview
    narration_words: 60
    est_sec: 24
    measured_sec: null
    sync_points: []
  - id: expected-values
    scene_class: ExpectedValues
    narration_words: 138
    est_sec: 55
    measured_sec: null
    sync_points: [show-pmf, weight-bars, sum-up, geometric]
  - id: functions-and-mean
    scene_class: FunctionsAndMean
    narration_words: 150
    est_sec: 60
    measured_sec: null
    sync_points: [law, indicator, masses, balance]
  - id: variance-and-moments
    scene_class: VarianceAndMoments
    narration_words: 158
    est_sec: 63
    measured_sec: null
    sync_points: [deviation, variance-formula, affine, moment-formula]
---

# Video Script — Discrete Expectations

Narration is the source of truth for timing. Each `<bookmark mark="id"/>` is a
synchronization point: in the generated scene, the corresponding animation is
triggered at that word via `tracker.time_until_bookmark("id")`. Animations with
no bookmark simply fill `run_time = tracker.duration` for their beat.

---

## Beat: overview  (scene: ChapterOverview)

> Last chapter we described a random variable completely with its probability
> mass function. That's often more detail than we want. In this video we collapse
> a whole PMF into a few descriptive numbers: the expected value, or mean; the
> variance, which measures spread; and the moments that generalize them. We'll
> also see a striking physical picture for the mean.

**Animation cue:** this is the FIRST beat — open with the shared `intro_card`
(objective + recap from the `linking:` block). Reveal the outline items — mean,
variance, moments — one per clause as the list is spoken.

---

## Beat: expected-values  (scene: ExpectedValues)

> The expected value of a discrete random variable is each possible value
> weighted by its probability, all summed together. <bookmark mark="show-pmf"/>
> Take a fair die: six outcomes, each with probability one-sixth.
> <bookmark mark="weight-bars"/> Multiply every face by one-sixth and
> <bookmark mark="sum-up"/> add them up — the mean comes out to three point five,
> even though you can never actually roll a three-point-five. The mean is a
> property of the PMF, not of any single roll. <bookmark mark="geometric"/> For a
> coin flipped until heads, where heads first appears on trial k with probability
> two-to-the-minus-k, the expected number of tosses works out to exactly two.

**Cues**
- `show-pmf`: draw the six equal bars, each labeled one-sixth.
- `weight-bars`: annotate each bar with k times one-sixth.
- `sum-up`: accumulate the terms and land on E[X] = 3.5, marking it on the axis.
- `geometric`: transition to the geometric PMF and reveal E[X] = 2.

---

## Beat: functions-and-mean  (scene: FunctionsAndMean)

> We can take the expectation of any function of X. <bookmark mark="law"/> The
> expected value of g of X is simply g of x weighted by the PMF and summed — no
> need to first work out the distribution of g of X. <bookmark mark="indicator"/>
> A neat special case: the expectation of the indicator of a set equals the
> probability that X lands in that set, linking expectation straight back to
> events. Now the picture that makes the mean intuitive.
> <bookmark mark="masses"/> Place a point mass equal to each probability at its
> value along a number line. <bookmark mark="balance"/> The mean is exactly the
> center of mass — the point where the whole arrangement balances.

**Cues**
- `law`: write E[g(X)] = sum of g(x) p_X(x).
- `indicator`: show E[indicator of S] = Pr(X in S).
- `masses`: draw point masses sized by probability on a horizontal beam.
- `balance`: slide a fulcrum to the mean so the beam balances; label it E[X].

---

## Beat: variance-and-moments  (scene: VarianceAndMoments)

> The mean tells you the center; the variance tells you the spread.
> <bookmark mark="deviation"/> Variance is the expected squared distance from the
> mean — square how far each value sits from E[X], weight by probability, and sum.
> <bookmark mark="variance-formula"/> Its square root is the standard deviation.
> For a Bernoulli the variance is p times one-minus-p; for a Poisson, both the
> mean and the variance equal lambda. <bookmark mark="affine"/> Affine maps behave
> cleanly: shifting and scaling by aX plus b sends the mean to a-times-E-of-X plus
> b, while the variance scales by a-squared and ignores the shift.
> <bookmark mark="moment-formula"/> Finally, a handy identity — the variance
> equals the second moment, E of X-squared, minus the mean squared.

**Cues**
- `deviation`: shade squared-deviation rectangles around the mean on the PMF.
- `variance-formula`: write Var[X] = E[(X − E[X])^2] and name sigma.
- `affine`: animate aX + b shifting and stretching the masses; track the mean.
- `moment-formula`: write Var[X] = E[X^2] − (E[X])^2 and circumscribe it.
- This is the LAST beat — close with the shared `outro_bridge` (key_idea +
  bridge from the `linking:` block), teasing Discrete Vectors.

---

## Cut list (if over budget)
1. Drop the optional `moments` material: cut the `moment-formula` sync point and
   the higher-moment mention.
2. In `expected-values`, drop the geometric second example and keep only the die.
3. In `variance-and-moments`, trim the affine-rules step to a single stated
   result without animating the stretch.
