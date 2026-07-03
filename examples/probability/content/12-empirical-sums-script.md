---
slug: 12-empirical-sums
title: Empirical Sums
stage: script             # tex -> concept -> [script] -> scene -> render
status: draft             # draft | reviewed | approved  (human gate)
derived_from: 12-empirical-sums.md
derived_from_sha256: 4c531fab8a67c4592561b0121e9d3e63b5763c3ec28a57a7823148302dfe195c
provenance_stamped: 2026-07-03
target_scene_file: scenes/empirical_sums.py

# --- Narrative glue (links this video to its neighbours) -------------------
# objective : the learning goal, spoken in the intro_card (retention: state
#             the goal up front).
# recap     : reactivates the previous chapter at the open (spacing).
# key_idea  : one-line takeaway spoken in outro_bridge (retrieval cue).
# bridge    : teases the next chapter — here, a course-closing send-off, since
#             this is the FINAL chapter of Undergraduate Probability I.
# Neighbour titles for recap/bridge come from project.yaml prereqs + order.
linking:
  objective: "Add many independent variables and discover the two laws that govern their average and their spread."
  recap: "Last chapter, Random Vectors, taught us to add independent variables by convolving their densities."
  key_idea: "Average enough i.i.d. variables and the mean is certain; standardize their sum and the shape is always Gaussian."
  bridge: "That closes Undergraduate Probability I — and these two theorems are the doorway to statistics and inference, where averages become estimates and the bell curve becomes a confidence interval."

# --- Voice + timing config -------------------------------------------------
voice:
  provider: openai        # gtts (free draft) -> openai/elevenlabs (final)
  model: tts-1
  name: alloy
  rate: 1.0
words_per_minute: 150     # used only for the pre-TTS estimate
target_runtime_sec: 660
tolerance_sec: 45         # build fails review if |actual - target| > tolerance

# --- Estimates vs measured -------------------------------------------------
# est_sec are computed from narration_words / wpm (cheap, pre-render).
# measured_sec is written back by the render stage from tracker.duration.
estimated_runtime_sec: 624
measured_runtime_sec: null

beats:
  - id: types-of-convergence
    scene_class: TypesOfConvergence
    narration_words: 160
    est_sec: 64
    measured_sec: null
    sync_points: [sequence, in-probability, mean-square, in-distribution]
  - id: law-of-large-numbers
    scene_class: LawOfLargeNumbers
    narration_words: 175
    est_sec: 70
    measured_sec: null
    sync_points: [average, variance-shrinks, chebyshev, die-demo]
  - id: central-limit-theorem
    scene_class: CentralLimitTheorem
    narration_words: 180
    est_sec: 72
    measured_sec: null
    sync_points: [standardize, skewed-start, grow-n, snap-to-normal]
  - id: heavy-tails-and-closeout
    scene_class: HeavyTailsAndCloseout
    narration_words: 145
    est_sec: 58
    measured_sec: null
    sync_points: [cauchy, never-settles, course-wrap]
---

# Video Script — Empirical Sums

Narration is the source of truth for timing. Each `<bookmark mark="id"/>` is a
synchronization point: in the generated scene, the corresponding animation is
triggered at that word via `tracker.time_until_bookmark("id")`. Animations with
no bookmark simply fill `run_time = tracker.duration` for their beat.

This is the FIRST beat of the chapter, so it opens with the shared intro card
(objective + recap). This is also the FINAL chapter of the course, so the LAST
beat closes with the shared outro carrying a course-wrap send-off (key_idea +
bridge).

---

## Beat: types-of-convergence  (scene: TypesOfConvergence)

> Last chapter we added two independent variables by convolving their densities.
> Now we let the adding never stop, and ask what an infinite sequence of random
> variables actually converges to. <bookmark mark="sequence"/> Picture a whole
> sequence, X-one, X-two, X-three, and so on, all defined on the same experiment.
> There are three useful ways it can settle down. <bookmark mark="in-probability"/>
> Convergence in probability means the chance of straying from the limit by any
> fixed margin shrinks to zero. <bookmark mark="mean-square"/> Convergence in mean
> square is stronger: the average squared error vanishes — and that one implies
> convergence in probability, courtesy of Chebyshev. <bookmark mark="in-distribution"/>
> And convergence in distribution is the gentlest of all: only the shape of the
> CDF has to settle, even if the variables themselves keep jiggling. Keep those
> three in mind — our two big theorems are each one of them.

**Animation cue:** open with the shared `intro_card` (objective + recap from the
`linking:` block), then proceed.
- `sequence`: lay out a row of distribution thumbnails marching off to the right.
- `in-probability`: shade the tail beyond `±epsilon`, animate it shrinking.
- `mean-square`: show `E[|X_n - X|²] -> 0`, draw the arrow to in-probability.
- `in-distribution`: morph one CDF curve onto a target CDF.

---

## Beat: law-of-large-numbers  (scene: LawOfLargeNumbers)

> Here is the first headline. Take independent, identically distributed draws,
> add them up into a sum S-n, and divide by n to get the empirical average.
> <bookmark mark="average"/> Its expected value sits exactly at the true mean, no
> matter how many terms you take. <bookmark mark="variance-shrinks"/> But its
> variance is the original variance divided by n — so as n grows, the spread
> collapses toward zero. <bookmark mark="chebyshev"/> Feed that vanishing variance
> into Chebyshev's inequality and the probability of straying from the mean is
> squeezed to zero. That's the law of large numbers: the empirical average
> converges in probability to the true mean. <bookmark mark="die-demo"/> Roll a
> die over and over, count the fraction of sixes, and watch it wander, then home
> in on one-sixth. The average doesn't just hover near the mean — it locks onto
> it.

**Cues**
- `average`: write `S_n / n`, mark `E[S_n/n] = E[X]` holding fixed.
- `variance-shrinks`: animate `Var = Var[X]/n` collapsing the histogram of the
  average for growing n, faint line at the true mean.
- `chebyshev`: overlay the Chebyshev tail bound `Var[X]/(n epsilon²)` shrinking.
- `die-demo`: running die-roll meter converging onto `1/6`.

---

## Beat: central-limit-theorem  (scene: CentralLimitTheorem)

> The second headline is even more astonishing. The law of large numbers told us
> *where* the average lands; the central limit theorem tells us the *shape* of the
> fluctuations around it. <bookmark mark="standardize"/> Take the sum, subtract its
> mean, and divide by sigma times the square root of n — that's standardizing it.
> <bookmark mark="skewed-start"/> Now here's the magic: it doesn't matter what the
> individual variables look like. Start with something lopsided and ugly. <bookmark mark="grow-n"/>
> Add more and more of them, standardizing as you go, <bookmark mark="snap-to-normal"/>
> and the histogram snaps onto the standard normal bell curve — every single time.
> That universality is why the Gaussian shows up everywhere in nature and
> engineering, and why a large sum can always be approximated with a normal CDF.

**Cues**
- `standardize`: write `(S_n - n·E[X]) / (sigma·sqrt(n))`.
- `skewed-start`: show a deliberately skewed source distribution.
- `grow-n`: rebuild the standardized-sum histogram for n = 1, 2, 5, 30.
- `snap-to-normal`: overlay a fixed standard-normal curve; pulse it as the
  histogram locks on.

---

## Beat: heavy-tails-and-closeout  (scene: HeavyTailsAndCloseout)

> One honest caveat before we close. The law of large numbers needs a finite
> variance, and some distributions don't have one. <bookmark mark="cauchy"/> The
> Cauchy distribution is the classic offender: average n independent Cauchy draws
> and, remarkably, the average is still exactly Cauchy — same heavy tails, same
> spread. <bookmark mark="never-settles"/> It never settles down, because there's
> no finite second moment for Chebyshev to grab onto. So the fine print matters.
> But for the vast world of well-behaved variables, these two theorems are the
> payoff of the entire course: average to pin down the mean, standardize to reveal
> the bell. <bookmark mark="course-wrap"/> From random outcomes, to variables, to
> expectation and bounds, to vectors and sums — it all leads here.

**Cues**
- `cauchy`: a Cauchy average histogram that stays wide and heavy-tailed for
  growing n, contrasted against a well-behaved average that narrows.
- `never-settles`: mark "no finite variance — Chebyshev fails."
- `course-wrap`: a brief montage of earlier-chapter motifs, then the shared
  `outro_bridge` carrying the course-closing key_idea + send-off to
  statistics / inference.

---

## Cut list (if over budget)
1. Drop the optional `heavy-tails-and-closeout` Cauchy demo; keep only the brief
   course-wrap and outro.
2. In `types-of-convergence`, fold mean-square and in-probability into one beat
   and skip the explicit Chebyshev arrow.
3. Trim the `die-demo` in the LLN beat, leaving the variance-shrinks histogram to
   carry the law.
