---
slug: 9-derived-distributions
title: Derived Distributions
stage: script             # tex -> concept -> [script] -> scene -> render
status: draft             # draft | reviewed | approved  (human gate)
derived_from: 9-derived-distributions.md
derived_from_sha256: 0241a83516f76489a1d0a54bc76c836bd0ddbb6a09fceea52e173da212aa469f
provenance_stamped: 2026-06-11
target_scene_file: scenes/derived_distributions.py

# --- Narrative glue (links this video to its neighbours) -------------------
# objective : the learning goal, spoken in the intro_card.
# recap     : reactivates the previous chapter at the open (spacing).
# key_idea  : one-line takeaway spoken in outro_bridge (retrieval cue).
# bridge    : teases the next chapter at the close.
linking:
  objective: "Find the distribution of Y = g(X) from the density of X and the function g."
  recap: "Last chapter, Continuous Random Variables gave us the PDF and CDF for variables over a continuum."
  key_idea: "For a smooth monotone g, the derived density is f_X(x) divided by the magnitude of g's slope."
  bridge: "Next: Expectations and Bounds — summarizing a distribution and bounding its tails."

# --- Voice + timing config -------------------------------------------------
voice:
  provider: openai
  model: tts-1
  name: alloy
  rate: 1.0
words_per_minute: 150
target_runtime_sec: 330
tolerance_sec: 30

# --- Estimates vs measured -------------------------------------------------
estimated_runtime_sec: 318
measured_runtime_sec: null

beats:
  - id: function-of-rv
    scene_class: FunctionOfRandomVariable
    narration_words: 145
    est_sec: 58
    measured_sec: null
    sync_points: [mapping, preimage, cdf-method, rayleigh-square]
  - id: monotone-functions
    scene_class: MonotoneFunctions
    narration_words: 150
    est_sec: 60
    measured_sec: null
    sync_points: [monotone-cdf, change-of-variables, jacobian, gaussian-affine]
  - id: differentiable-piecewise
    scene_class: PiecewiseMonotone
    narration_words: 140
    est_sec: 56
    measured_sec: null
    sync_points: [two-preimages, sum-branches, cosine-example]
  - id: generating-rvs
    scene_class: GeneratingRandomVariables
    narration_words: 155
    est_sec: 62
    measured_sec: null
    sync_points: [cdf-is-uniform, inverse-transform, exponential-sample, discrete-case]
---

# Video Script — Derived Distributions

Narration is the source of truth for timing. Each `<bookmark mark="id"/>` is a
synchronization point. The FIRST beat opens with the shared intro card
(objective + recap); the LAST beat closes with the shared outro (key idea +
bridge).

---

## Beat: function-of-rv  (scene: FunctionOfRandomVariable)

> [INTRO CARD: state the objective, then recap that last chapter gave us the PDF
> and CDF for continuous variables.] Take a continuous variable X and apply a
> function g. <bookmark mark="mapping"/> The result, Y equals g of X, is a brand-
> new random variable. To find its distribution we trace probability backwards.
> <bookmark mark="preimage"/> The chance that Y lands in a set S is the chance
> that X lands in the preimage — the set of inputs that g sends into S. That
> gives us a general recipe, the CDF method: <bookmark mark="cdf-method"/> write
> the probability that g of X is at most y as an integral of the density of X
> over all x with g of x below y, then differentiate. Here's it in action.
> <bookmark mark="rayleigh-square"/> Square a Rayleigh variable and the CDF
> method reveals an exponential distribution falling right out.

**Cues**
- Open with `intro_card` (objective + recap).
- `mapping`: three-panel diagram — Omega, X to a real line, g to a second line.
- `preimage`: highlight a set S on the Y-axis and its pullback `g^{-1}(S)`.
- `cdf-method`: write `F_Y(y) = integral over {g(x)<=y} of f_X(u) du`.
- `rayleigh-square`: show `Y = X^2` and the result `F_Y(y) = 1 - e^{-y/2}`.

---

## Beat: monotone-functions  (scene: MonotoneFunctions)

> When g is monotone — order-preserving — the bookkeeping gets clean. <bookmark
> mark="monotone-cdf"/> For an increasing g, the CDF of Y is just the CDF of X
> evaluated at the inverse; for a decreasing g, it's one minus that. Now if g is
> also differentiable, differentiate and you get the headline formula of the
> whole chapter: <bookmark mark="change-of-variables"/> the density of Y at y
> equals the density of X at x, divided by the magnitude of g's slope, where x is
> the inverse of y. That slope term has a clear meaning. <bookmark
> mark="jacobian"/> A gentle slope stretches a thin y-interval into a wide
> x-interval, so probability piles up; a steep slope squeezes it, thinning the
> density. As a payoff, <bookmark mark="gaussian-affine"/> an affine function of
> a Gaussian is always Gaussian — stretching and shifting a bell just gives
> another bell.

**Cues**
- `monotone-cdf`: write `F_Y = F_X(g^{-1}(y))` and `1 - F_X(g^{-1}(y))`.
- `change-of-variables`: write `f_Y(y) = f_X(x) / |dg/dx|`, `x = g^{-1}(y)`.
- `jacobian`: fix a width-delta band on the y-axis, pull it back through the
  curve to show the matching x-width swelling and shrinking with the slope.
- `gaussian-affine`: morph a bell under `Y = aX + b` into a rescaled bell.

---

## Beat: differentiable-piecewise  (scene: PiecewiseMonotone)

> What if several inputs map to the same output? Then we add up their
> contributions. <bookmark mark="two-preimages"/> Pick a value y and find every x
> with g of x equal to y. Each one contributes a density term, the density of X
> there over the magnitude of the slope there. <bookmark mark="sum-branches"/>
> Sum those terms across all the branches and you have the density of Y. The
> classic example is a sampled sinusoid. <bookmark mark="cosine-example"/> Let X
> be a uniform angle on a full circle and set Y to the cosine of X. For each value
> of Y there are two angles, and adding their contributions gives a density that
> shoots up near plus and minus one — exactly where a spinning cosine lingers
> longest.

**Cues**
- `two-preimages`: draw a wavy `g`, a horizontal line at `y`, mark its crossings.
- `sum-branches`: write `f_Y(y) = sum over {g(x)=y} of f_X(x)/|dg/dx|`.
- `cosine-example`: a dot sweeping the unit circle; its horizontal projection
  building the `1 / (pi sqrt(1 - y^2))` density, peaking at the edges.

---

## Beat: generating-rvs  (scene: GeneratingRandomVariables)

> Run this machinery in reverse and you get a simulation superpower. First, a
> neat fact: <bookmark mark="cdf-is-uniform"/> feed a continuous variable into its
> own CDF and the output is uniform on zero to one. Turn that around. <bookmark
> mark="inverse-transform"/> Start with a uniform draw and apply the inverse CDF,
> and out comes a sample from whatever distribution you want — this is inverse-
> transform sampling. For an exponential, <bookmark mark="exponential-sample"/>
> the inverse CDF is minus one over lambda times the log of one minus the uniform
> draw, and that single line generates exponential samples. <bookmark
> mark="discrete-case"/> A staircase case-function does the same job for discrete
> targets, slicing the unit interval into pieces sized by the PMF. [OUTRO: for a
> smooth monotone g the derived density is f_X over the magnitude of g's slope;
> next we'll summarize a whole distribution and bound its tails.]

**Cues**
- `cdf-is-uniform`: push a sample through `F_X` and show it land uniformly.
- `inverse-transform`: uniform dots on the y-axis fired into the CDF, dropping to
  form the target histogram.
- `exponential-sample`: write `X = -(1/lambda) log(1 - Y)`.
- `discrete-case`: slice `[0,1]` into PMF-sized bins via a staircase CDF.
- Close with `outro_bridge` (key idea + bridge to Expectations and Bounds).

---

## Cut list (if over budget)
1. Drop the discrete case in `generating-rvs`; keep the continuous inverse
   transform only.
2. Cut the `gaussian-affine` payoff in `monotone-functions`.
3. Trim `differentiable-piecewise` to the cosine example, dropping the general
   sum formula derivation.
4. Shorten the three-panel mapping diagram in `function-of-rv`.
