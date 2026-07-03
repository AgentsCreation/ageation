---
slug: 10-expectations-and-bounds
title: Expectations and Bounds
stage: script             # tex -> concept -> [script] -> scene -> render
status: draft             # draft | reviewed | approved  (human gate)
derived_from: 10-expectations-and-bounds.md
derived_from_sha256: a35c36b06030632ea8ff8348b73673e8bd7c84dd70f92b2a1507cd318d880f4f
provenance_stamped: 2026-07-03
target_scene_file: scenes/expectations_and_bounds.py

# --- Narrative glue (links this video to its neighbours) -------------------
# objective : the learning goal, spoken in the intro_card.
# recap     : reactivates the previous chapter at the open (spacing).
# key_idea  : one-line takeaway spoken in outro_bridge (retrieval cue).
# bridge    : teases the next chapter at the close.
linking:
  objective: "Pack moments into one function and bound probabilities you can't compute exactly."
  recap: "Last chapter, Derived Distributions found the law of Y = g(X) from the density of X."
  key_idea: "Expectation both summarizes a distribution and, through dominating functions, bounds its tails."
  bridge: "Next: Random Vectors — carrying expectation and these bounds into many dimensions."

# --- Voice + timing config -------------------------------------------------
voice:
  provider: openai
  model: tts-1
  name: alloy
  rate: 1.0
words_per_minute: 150
target_runtime_sec: 340
tolerance_sec: 30

# --- Estimates vs measured -------------------------------------------------
estimated_runtime_sec: 336
measured_runtime_sec: null

beats:
  - id: moment-generating-functions
    scene_class: MomentGeneratingFunctions
    narration_words: 160
    est_sec: 64
    measured_sec: null
    sync_points: [definition, extract-moments, exponential-mgf, gaussian-mgf, affine-rule]
  - id: dominating-and-markov
    scene_class: DominatingAndMarkov
    narration_words: 150
    est_sec: 60
    measured_sec: null
    sync_points: [dominating, indicator, markov-line, markov-bound]
  - id: chebyshev-chernoff
    scene_class: ChebyshevChernoff
    narration_words: 160
    est_sec: 64
    measured_sec: null
    sync_points: [chebyshev-general, variance-bound, chernoff-pencil, optimize]
  - id: jensen
    scene_class: JensenInequality
    narration_words: 130
    est_sec: 52
    measured_sec: null
    sync_points: [convex, tangent, jensen-result, variance-corollary]
---

# Video Script — Expectations and Bounds

Narration is the source of truth for timing. Each `<bookmark mark="id"/>` is a
synchronization point. The FIRST beat opens with the shared intro card
(objective + recap); the LAST beat closes with the shared outro (key idea +
bridge).

---

## Beat: moment-generating-functions  (scene: MomentGeneratingFunctions)

> [INTRO CARD: state the objective, then recap that last chapter we found the law
> of Y equals g of X.] We start with a remarkably compact gadget. <bookmark
> mark="definition"/> The moment generating function is the expected value of e
> to the s X — a single function of s that secretly stores every moment of X. To
> retrieve them, <bookmark mark="extract-moments"/> differentiate n times and set
> s to zero; out pops the n-th moment. One derivative gives the mean, two give
> the second moment. <bookmark mark="exponential-mgf"/> For an exponential
> variable the function is lambda over lambda minus s, and cranking out
> derivatives gives mean one over lambda and variance one over lambda squared.
> <bookmark mark="gaussian-mgf"/> For a standard normal it's the elegant e to the
> s squared over two. And there's a handy shortcut: <bookmark mark="affine-rule"/>
> for Y equals a X plus b, the function is e to the s b times M of a s — affine
> transforms are almost free.

**Cues**
- Open with `intro_card` (objective + recap).
- `definition`: write `M_X(s) = E[e^{sX}]`.
- `extract-moments`: an MGF "machine" — crank `d^n/ds^n` at `s=0`, moments drop.
- `exponential-mgf`: write `M_X(s) = lambda/(lambda - s)`.
- `gaussian-mgf`: write `M_X(s) = e^{s^2/2}`.
- `affine-rule`: write `M_Y(s) = e^{sb} M_X(as)`.

---

## Beat: dominating-and-markov  (scene: DominatingAndMarkov)

> Now to bounds, and one idea powers nearly all of them. <bookmark
> mark="dominating"/> If one nonnegative function sits below another everywhere,
> then its expectation sits below too — domination of functions becomes
> domination of expectations. The trick is to bound a probability by writing it
> as the expectation of an indicator. <bookmark mark="indicator"/> The
> probability that X is at least a is the expected value of the indicator of the
> interval from a onward — a step that jumps from zero to one at a. <bookmark
> mark="markov-line"/> Lay the straight line x over a on top of that step; for
> nonnegative x the line is always above. <bookmark mark="markov-bound"/> Take
> expectations and you get the Markov inequality: the probability that X is at
> least a is at most the mean of X over a. A bound from the mean alone.

**Cues**
- `dominating`: draw `h(x)` above `g(x)`; annotate `E[g(X)] <= E[h(X)]`.
- `indicator`: draw the step `1_{[a,inf)}(x)`; write `Pr(X>=a) = E[1_S(X)]`.
- `markov-line`: overlay the line `x/a` dominating the step.
- `markov-bound`: write `Pr(X >= a) <= E[X]/a`.

---

## Beat: chebyshev-chernoff  (scene: ChebyshevChernoff)

> Swap that straight line for other dominating functions and the bounds multiply.
> <bookmark mark="chebyshev-general"/> The Chebyshev inequality says: for any
> nonnegative function h, the infimum of h over a set S, times the probability of
> S, is at most the expected value of h of X. <bookmark mark="variance-bound"/>
> Choose h of x equal to x squared and you recover the famous tail bound — the
> probability that the magnitude of X exceeds b is at most the second moment over
> b squared. Now push harder. <bookmark mark="chernoff-pencil"/> Dominate the
> same step with a whole pencil of exponentials, e to the s times x minus a, one
> for every positive s. Each gives a valid bound involving the moment generating
> function. <bookmark mark="optimize"/> Pick the lowest of them all — the
> infimum over s — and you get the Chernoff bound, which decays exponentially in
> a and is far sharper than Markov or Chebyshev.

**Cues**
- `chebyshev-general`: write `i_S Pr(X in S) <= E[h(X)]`.
- `variance-bound`: write `Pr(|X| >= b) <= E[X^2]/b^2`.
- `chernoff-pencil`: draw a family of `e^{s(x-a)}` curves over the step.
- `optimize`: write `Pr(X >= a) <= inf_{s>0} e^{-sa} M_X(s)`; snap to the lowest.

---

## Beat: jensen  (scene: JensenInequality)

> One last inequality comes not from domination but from the shape of a single
> function. <bookmark mark="convex"/> Take a convex function g — one that curves
> upward, with nonnegative second derivative. At the mean of X, draw the tangent
> line; convexity guarantees the whole curve sits above that tangent. <bookmark
> mark="tangent"/> Replace g by its tangent inside an expectation — the tangent
> is linear, so its expectation is just its value at the mean. <bookmark
> mark="jensen-result"/> The result is Jensen's inequality: the expected value of
> g of X is at least g of the expected value of X. <bookmark
> mark="variance-corollary"/> Apply it to x squared and you learn that the mean
> of the square beats the square of the mean — which is exactly why variance is
> never negative. [OUTRO: expectation both summarizes a distribution and, through
> dominating functions, bounds its tails; next we carry all of this into many
> dimensions with random vectors.]

**Cues**
- `convex`: draw an upward-curving `g` with its chord above it.
- `tangent`: draw the tangent at `x = E[X]` lying under the curve.
- `jensen-result`: write `E[g(X)] >= g(E[X])`.
- `variance-corollary`: write `E[X^2] >= (E[X])^2`, hence `Var[X] >= 0`.
- Close with `outro_bridge` (key idea + bridge to Random Vectors).

---

## Cut list (if over budget)
1. Drop the `affine-rule` sync point and the Gaussian MGF example, keeping the
   exponential.
2. In `chebyshev-chernoff`, cut the variance-bound specialization and go straight
   from the general Chebyshev statement to Chernoff.
3. Trim the `variance-corollary` callback in `jensen` to one sentence.
4. Shorten the MGF "machine" animation in `moment-generating-functions`.
