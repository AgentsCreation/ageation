---
slug: 07-discrete-vectors
title: Discrete Vectors
stage: script             # tex -> concept -> [script] -> scene -> render
status: draft             # draft | reviewed | approved  (human gate)
derived_from: 07-discrete-vectors.md
derived_from_sha256: 601f615c2386b42abb2913aaf87b7a5148eb5b6ec6247e2e9fd188d1a1960e20
provenance_stamped: 2026-07-06
target_scene_file: scenes/discrete_vectors.py

# --- Narrative glue (links this video to its neighbours) -------------------
# objective : the learning goal, spoken in the intro_card (retention: state
#             the goal up front).
# recap     : reactivates the previous chapter at the open (spacing).
# key_idea  : one-line takeaway spoken in outro_bridge (retrieval cue).
# bridge    : teases the next chapter at the close.
# Neighbour titles for recap/bridge come from project.yaml prereqs + order.
linking:
  objective: "Describe two random variables together with a joint PMF and condition between them."
  recap: "Last chapter, Discrete Expectations, we summarized a single PMF with its mean and variance."
  key_idea: "The joint PMF holds everything; conditioning and convolution extract how two RVs interact."
  bridge: "Next: Continuous Random Variables — densities and integrals replace PMFs and sums."

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
estimated_runtime_sec: 352
measured_runtime_sec: null

beats:
  - id: overview
    scene_class: ChapterOverview
    narration_words: 62
    est_sec: 25
    measured_sec: null
    sync_points: []
  - id: joint-and-marginals
    scene_class: JointAndMarginals
    narration_words: 142
    est_sec: 57
    measured_sec: null
    sync_points: [show-grid, sum-rows, sum-cols, marginals-warning]
  - id: conditioning
    scene_class: ConditionalRandomVariables
    narration_words: 150
    est_sec: 60
    measured_sec: null
    sync_points: [slice-row, renormalize, cond-expect, tower]
  - id: independence-and-sums
    scene_class: IndependenceAndSums
    narration_words: 156
    est_sec: 62
    measured_sec: null
    sync_points: [factor, dice-sum, convolve, settle]
---

# Video Script — Discrete Vectors

Narration is the source of truth for timing. Each `<bookmark mark="id"/>` is a
synchronization point: in the generated scene, the corresponding animation is
triggered at that word via `tracker.time_until_bookmark("id")`. Animations with
no bookmark simply fill `run_time = tracker.duration` for their beat.

---

## Beat: overview  (scene: ChapterOverview)

> Last chapter we summarized a single random variable with its mean and variance.
> But quantities rarely come alone — they interact. In this video we pair two
> random variables into a joint PMF, recover each one's marginal, condition one on
> the other, build the conditional expectation, and finish with independence and
> the convolution rule for sums.

**Animation cue:** this is the FIRST beat — open with the shared `intro_card`
(objective + recap from the `linking:` block). Reveal the outline items — joint,
marginal, conditional, sums — one per clause as the list is spoken.

---

## Beat: joint-and-marginals  (scene: JointAndMarginals)

> Two random variables on one experiment are described by their joint PMF: the
> probability that X equals x and Y equals y, together. <bookmark mark="show-grid"/>
> Picture it as a grid, one cell per pair, the cells summing to one. To get the
> distribution of X alone, <bookmark mark="sum-rows"/> sum across each row — that's
> the marginal of X. <bookmark mark="sum-cols"/> Sum down each column for the
> marginal of Y. But beware: <bookmark mark="marginals-warning"/> the marginals do
> not determine the joint. Drawing two balls with replacement versus without gives
> identical marginals but completely different joint PMFs.

**Cues**
- `show-grid`: draw the joint PMF as a labeled grid of probabilities.
- `sum-rows`: slide row sums out to the right to form the marginal of X.
- `sum-cols`: slide column sums down to form the marginal of Y.
- `marginals-warning`: show two different joint grids sharing the same margins.

---

## Beat: conditioning  (scene: ConditionalRandomVariables)

> Conditioning extends from events to random variables. <bookmark mark="slice-row"/>
> Fix X at a value and look at just that row of the grid. <bookmark mark="renormalize"/>
> Divide it by the marginal of X and it becomes a genuine PMF — the conditional
> distribution of Y given X equals x. Average Y against that conditional and you
> get the conditional expectation, <bookmark mark="cond-expect"/> E of Y given X
> equals x, which varies with x and is therefore itself a random variable. And here
> is the elegant part — the tower rule. <bookmark mark="tower"/> Average the
> conditional expectation over X, and you recover the plain expectation of Y.

**Cues**
- `slice-row`: lift one row out of the joint grid.
- `renormalize`: divide the row by its sum so its bars total one.
- `cond-expect`: plot E[Y | X = x] as a value for each x.
- `tower`: collapse those values, weighted by p_X(x), back onto E[Y].

---

## Beat: independence-and-sums  (scene: IndependenceAndSums)

> Two random variables are independent when the joint PMF factors — <bookmark mark="factor"/>
> the probability of x and y is just the product of the two marginals. For
> independent variables the expectation of the product is the product of the
> expectations, and the variance of a sum is the sum of the variances. Now the sum
> itself: <bookmark mark="dice-sum"/> add two dice and the joint grid's
> anti-diagonals collapse into the triangular PMF of the total.
> <bookmark mark="convolve"/> In general the PMF of a sum is the convolution of the
> two marginals — slide one past the other, multiply and add at each shift.
> <bookmark mark="settle"/> Generating functions make this even cleaner, turning a
> convolution into a simple product.

**Cues**
- `factor`: show p_{X,Y}(x,y) = p_X(x) p_Y(y) with the grid splitting into a row
  times a column.
- `dice-sum`: collapse the dice grid's anti-diagonals into the triangular sum PMF.
- `convolve`: animate one PMF sliding across the other, accumulating p_U(k).
- `settle`: note G_{X+Y}(z) = G_X(z) G_Y(z) as the product shortcut.
- This is the LAST beat — close with the shared `outro_bridge` (key_idea +
  bridge from the `linking:` block), teasing Continuous Random Variables.

---

## Cut list (if over budget)
1. Drop the optional `generating-functions` material: cut the `settle` sync point
   and the product-shortcut mention.
2. In `joint-and-marginals`, cut the with/without-replacement counterexample and
   keep only the row/column marginal animation.
3. In `independence-and-sums`, trim to either the dice-sum collapse or the
   convolution slide, not both.
