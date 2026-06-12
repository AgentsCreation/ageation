---
slug: 8-continuous-random-variables
title: Continuous Random Variables
stage: script             # tex -> concept -> [script] -> scene -> render
status: draft             # draft | reviewed | approved  (human gate)
derived_from: 8-continuous-random-variables.md
derived_from_sha256: 0666ae61d72dd3da483180153a1ee4e9c0de1a03ad73877acf8fcdf9a4d28967
provenance_stamped: 2026-06-11
target_scene_file: scenes/continuous_random_variables.py

# --- Narrative glue (links this video to its neighbours) -------------------
# objective : the learning goal, spoken in the intro_card.
# recap     : reactivates the previous chapter at the open (spacing).
# key_idea  : one-line takeaway spoken in outro_bridge (retrieval cue).
# bridge    : teases the next chapter at the close.
linking:
  objective: "Describe random variables over a continuum using the CDF and the PDF."
  recap: "Last chapter, Discrete Vectors bundled several discrete random variables into joint PMFs."
  key_idea: "A continuous random variable is captured by its density, the slope of its CDF."
  bridge: "Next: Derived Distributions — pushing a continuous variable through a function g."

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
estimated_runtime_sec: 326
measured_runtime_sec: null

beats:
  - id: cdf
    scene_class: CumulativeDistribution
    narration_words: 150
    est_sec: 60
    measured_sec: null
    sync_points: [show-cdf, staircase, rise, interval]
  - id: pdf
    scene_class: ProbabilityDensity
    narration_words: 140
    est_sec: 56
    measured_sec: null
    sync_points: [differentiate, shade-area, shrink-to-line, normalize]
  - id: expectation
    scene_class: ExpectationRevisited
    narration_words: 120
    est_sec: 48
    measured_sec: null
    sync_points: [mean-integral, variance, tail-formula, dartboard]
  - id: important-distributions
    scene_class: ImportantDistributions
    narration_words: 160
    est_sec: 64
    measured_sec: null
    sync_points: [uniform, gaussian, exponential, geometric-limit]
  - id: additional-distributions
    scene_class: AdditionalDistributions
    narration_words: 145
    est_sec: 58
    measured_sec: null
    sync_points: [gamma, rayleigh, laplace, cauchy]
---

# Video Script — Continuous Random Variables

Narration is the source of truth for timing. Each `<bookmark mark="id"/>` is a
synchronization point. The FIRST beat opens with the shared intro card
(objective + recap); the LAST beat closes with the shared outro (key idea +
bridge).

---

## Beat: cdf  (scene: CumulativeDistribution)

> [INTRO CARD: state the objective, then recap that last chapter we bundled
> several discrete variables into joint PMFs.] Now our variables range over a
> continuum, so a mass function won't do. The fix is the cumulative distribution
> function. <bookmark mark="show-cdf"/> It's defined as the probability that X is
> at most x — F of x equals the probability of the event X less than or equal to
> x. This one object works for any random variable. For a discrete variable
> <bookmark mark="staircase"/> the CDF is a staircase that jumps at each value.
> Whatever the variable, <bookmark mark="rise"/> the CDF starts at zero on the
> far left, climbs to one on the far right, and never decreases. And the
> probability of landing in an interval <bookmark mark="interval"/> is just the
> difference of the CDF at the two endpoints.

**Cues**
- Open with `intro_card` (objective + recap), then transition in.
- `show-cdf`: write `F_X(x) = Pr(X <= x)` along the top.
- `staircase`: draw a discrete staircase CDF rising by jumps.
- `rise`: morph the staircase into a smooth S-curve pinned at 0 and 1.
- `interval`: shade the height `F_X(x2) - F_X(x1)` between two dashed verticals.

---

## Beat: pdf  (scene: ProbabilityDensity)

> When the CDF is smooth and differentiable, we call X a continuous random
> variable, and its slope has a name. <bookmark mark="differentiate"/> The
> derivative of the CDF is the probability density function, f of x. Integrate
> the density back up and you recover the CDF. The density lets us read
> probabilities as areas: <bookmark mark="shade-area"/> the chance that X lands
> between x-one and x-two is the area under the curve there. Now watch what
> happens to a single point. <bookmark mark="shrink-to-line"/> Shrink that
> interval to a single value and the area vanishes — so for a continuous
> variable, the probability of any exact value is exactly zero. That's why
> endpoints never matter. Finally, <bookmark mark="normalize"/> the total area
> under any density is one, and the density is never negative.

**Cues**
- `differentiate`: show `f_X(x) = dF_X/dx` and sketch the density below the CDF.
- `shade-area`: shade `integral from x1 to x2 of f_X` under the curve.
- `shrink-to-line`: animate x1 sliding to x2 until the shaded region is a line.
- `normalize`: flood-fill the whole area and label it `= 1`, note `f_X >= 0`.

---

## Beat: expectation  (scene: ExpectationRevisited)

> Expectation carries over almost unchanged — we just swap the weighted sum for a
> weighted integral. <bookmark mark="mean-integral"/> The mean of X is the
> integral of u times the density. The variance <bookmark mark="variance"/> is
> the integral of the squared deviation from the mean, and as before it also
> equals the second moment minus the mean squared. For a nonnegative variable
> there's a slick shortcut: <bookmark mark="tail-formula"/> the mean equals the
> integral of the tail probability, the chance that X exceeds x. A dartboard
> makes it concrete. <bookmark mark="dartboard"/> Throw darts uniformly at a unit
> disk; the expected distance to the center works out to two-thirds, without ever
> writing down a density.

**Cues**
- `mean-integral`: write `E[X] = integral of u f_X(u) du`.
- `variance`: write the variance integral, then `Var[X] = E[X^2] - (E[X])^2`.
- `tail-formula`: write `E[X] = integral from 0 to inf of Pr(X > x) dx`.
- `dartboard`: draw a unit disk peppered with darts; surface `E[R] = 2/3`.

---

## Beat: important-distributions  (scene: ImportantDistributions)

> Three continuous distributions show up everywhere. <bookmark mark="uniform"/>
> The uniform spreads probability evenly over an interval — a flat density of one
> over b minus a. <bookmark mark="gaussian"/> The Gaussian, or normal, is the
> famous bell curve, set by a mean m and a spread sigma; its CDF has no
> closed form, so engineers write it with the Phi, erf, and Q functions.
> <bookmark mark="exponential"/> The exponential, with rate lambda, models
> lifetimes and waiting times between events. And here's a lovely link:
> <bookmark mark="geometric-limit"/> take geometric variables, scale them down,
> and let the number of trials grow — the bars collapse onto a smooth exponential
> curve, which inherits the memoryless property. The exponential is the only
> continuous distribution that forgets the past.

**Cues**
- `uniform`: draw the flat box PDF; sweep the support `[a,b]` wider and narrower.
- `gaussian`: draw the bell; sweep `sigma`; flash `Phi`, `erf`, and `Q` labels.
- `exponential`: draw `f_X = lambda e^{-lambda x}`; sweep `lambda`.
- `geometric-limit`: scaled geometric bars for n = 5, 20, 50 settling onto a
  fixed exponential reference curve.

---

## Beat: additional-distributions  (scene: AdditionalDistributions)

> A few more shapes round out the family, and they're beautifully
> interconnected. <bookmark mark="gamma"/> The gamma is a two-parameter family
> that flexes to fit data; the exponential, the chi-square, and the Erlang are
> all special cases of it. <bookmark mark="rayleigh"/> The Rayleigh shows up in
> wireless fading — it's the magnitude of two independent Gaussians, and its
> square is exponential. <bookmark mark="laplace"/> The Laplace is two
> exponentials spliced back to back, a sharp peak with symmetric tails. And the
> Cauchy <bookmark mark="cauchy"/> is a cautionary tale: its tails are so heavy
> that its mean and variance simply don't exist. [OUTRO: a continuous variable is
> captured by its density — the slope of its CDF — and next we'll push one of
> these variables through a function g to derive a brand-new distribution.]

**Cues**
- `gamma`: draw gamma PDFs; label the exponential, chi-square, Erlang cases.
- `rayleigh`: draw the Rayleigh; annotate `R = sqrt(X^2 + Y^2)`.
- `laplace`: draw the double-exponential peak.
- `cauchy`: draw the heavy-tailed bell; strike through "mean" and "variance".
- Close with `outro_bridge` (key idea + bridge to Derived Distributions).

---

## Cut list (if over budget)
1. Drop the optional `additional-distributions` beat entirely (gamma/Rayleigh/
   Laplace/Cauchy gallery).
2. In `important-distributions`, cut the parameter sweeps and keep one curve each.
3. Trim the dartboard demo in `expectation` to a single spoken sentence.
4. Shorten the staircase-to-smooth morph in `cdf`.
