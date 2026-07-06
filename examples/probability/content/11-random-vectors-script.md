---
slug: 11-random-vectors
title: Random Vectors
stage: script             # tex -> concept -> [script] -> scene -> render
status: draft             # draft | reviewed | approved  (human gate)
derived_from: 11-random-vectors.md
derived_from_sha256: a6b9359ffabf27d5a6de0a5592488fbe99489e5e476a9094fe869cfbe0c6e5e2
provenance_stamped: 2026-07-06
target_scene_file: scenes/random_vectors.py

# --- Narrative glue (links this video to its neighbours) -------------------
# objective : the learning goal, spoken in the intro_card (retention: state
#             the goal up front).
# recap     : reactivates the previous chapter at the open (spacing).
# key_idea  : one-line takeaway spoken in outro_bridge (retrieval cue).
# bridge    : teases the next chapter at the close.
# Neighbour titles for recap/bridge come from project.yaml prereqs + order.
linking:
  objective: "Describe two continuous variables jointly, then condition, test independence, and add them."
  recap: "Last chapter, Expectations and Bounds, summarized one random variable with its mean, variance, and tail bounds."
  key_idea: "A pair of continuous variables lives on one joint density; marginals, conditionals, and sums all come from reshaping that surface."
  bridge: "Next, Empirical Sums: let the number of added variables grow without bound and watch the laws of large numbers and the central limit theorem emerge."

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
estimated_runtime_sec: 612
measured_runtime_sec: null

beats:
  - id: joint-distributions
    scene_class: JointDistributions
    narration_words: 165
    est_sec: 66
    measured_sec: null
    sync_points: [show-surface, shade-region, cast-marginals]
  - id: conditioning
    scene_class: ConditioningOnValues
    narration_words: 170
    est_sec: 68
    measured_sec: null
    sync_points: [slice, renormalize, conditional-mean]
  - id: independence
    scene_class: IndependenceFactorization
    narration_words: 150
    est_sec: 60
    measured_sec: null
    sync_points: [factor-check, square-match, sum-mismatch]
  - id: sums-convolution
    scene_class: SumsAndConvolution
    narration_words: 175
    est_sec: 70
    measured_sec: null
    sync_points: [flip, slide, trace-triangle, mgf-product]
  - id: gaussian-vectors
    scene_class: GaussianVectors
    narration_words: 145
    est_sec: 58
    measured_sec: null
    sync_points: [ellipse, affine-map, stays-gaussian]
---

# Video Script — Random Vectors

Narration is the source of truth for timing. Each `<bookmark mark="id"/>` is a
synchronization point: in the generated scene, the corresponding animation is
triggered at that word via `tracker.time_until_bookmark("id")`. Animations with
no bookmark simply fill `run_time = tracker.duration` for their beat.

This is the FIRST beat of the chapter, so it opens with the shared intro card
(objective + recap). The LAST beat closes with the shared outro (key_idea +
bridge).

---

## Beat: joint-distributions  (scene: JointDistributions)

> Last time we squeezed a single random variable down to a mean, a variance, and
> a few tail bounds. But most real problems couple several quantities at once,
> so today we learn to describe two continuous variables together. <bookmark mark="show-surface"/>
> The whole story lives in one object: a joint density, a surface floating over
> the plane that is never negative and whose total volume is exactly one. To find
> the probability that the pair lands in some region, <bookmark mark="shade-region"/>
> you just measure the volume sitting above that region. And if you only care
> about one variable, <bookmark mark="cast-marginals"/> you let the other run off
> to infinity — integrate it away — and the surface casts a shadow onto a single
> axis. That shadow is the marginal density.

**Animation cue:** open with the shared `intro_card` (objective + recap from the
`linking:` block), then proceed.
- `show-surface`: fade in the joint PDF surface over the xy-plane.
- `shade-region`: highlight a rectangle, fill the volume above it, label it a
  probability.
- `cast-marginals`: collapse the surface onto the x-axis to draw `f_X`, then the
  y-axis for `f_Y`.

---

## Beat: conditioning  (scene: ConditioningOnValues)

> Now suppose someone tells you the value of Y. How does that reshape what we
> believe about X? <bookmark mark="slice"/> We take a single vertical slice
> through the surface at that value of Y. That sliver has the right shape, but
> it's too small to be a probability density on its own. So <bookmark mark="renormalize"/>
> we divide by the marginal at that point, which scales the sliver back up until
> its area is one. That rescaled slice is the conditional density of X given Y
> equals y. There's a subtlety worth naming: the event Y equals exactly y has
> probability zero, yet this construction still makes perfect sense for jointly
> continuous variables. <bookmark mark="conditional-mean"/> And the average of
> that conditional slice, the conditional expectation of X given Y, is itself a
> random variable that rides along as Y changes — it's exactly the estimator you
> reach for when you want a best guess of X from a noisy observation.

**Cues**
- `slice`: cut a vertical plane at `Y = y`, lift the cross-section out.
- `renormalize`: scale the lifted slice by `1 / f_Y(y)` so its area becomes one.
- `conditional-mean`: drop a marker at `E[X | Y = y]` and sweep `y` to trace the
  curve `h(x) = E[X | Y = x]`.

---

## Beat: independence  (scene: IndependenceFactorization)

> When does knowing Y tell you nothing about X? That's independence, and it has a
> crisp test. <bookmark mark="factor-check"/> Two variables are independent
> exactly when the joint density factors into the product of the two marginals —
> the surface is just `f_X` times `f_Y`, with no leftover coupling. <bookmark mark="square-match"/>
> Pick a point uniformly from the unit square: its two coordinates factor
> cleanly, so they're independent. <bookmark mark="sum-mismatch"/> But compare one
> coordinate against the sum of both coordinates, and the factorization fails —
> knowing the sum clearly constrains the part. So those two are dependent. When
> variables do factor, conditioning changes nothing: the conditional density of Y
> given X collapses straight back to the plain marginal of Y.

**Cues**
- `factor-check`: show `f_{X,Y}` on the left, `f_X · f_Y` on the right, with an
  equals sign that turns green or red.
- `square-match`: unit-square uniform — both sides match, mark independent.
- `sum-mismatch`: the `(X, X+Y)` example — sides differ, mark dependent.

---

## Beat: sums-convolution  (scene: SumsAndConvolution)

> Here's the workhorse of the chapter: adding two independent variables. The
> density of their sum is the convolution of the two densities, and you can
> literally see what convolution does. <bookmark mark="flip"/> Take one density
> and flip it left-to-right. <bookmark mark="slide"/> Now slide it across the
> other, and at each position multiply the overlap and add it up. <bookmark mark="trace-triangle"/>
> For two uniforms on zero to one, that sliding overlap grows, peaks in the
> middle, and shrinks — tracing out a neat triangular density for the sum. There's
> a second, slicker route too. <bookmark mark="mgf-product"/> The moment generating
> function of a sum of independents is just the product of the individual ones, so
> adding random variables becomes multiplying functions — and that instantly
> explains why a Gaussian plus a Gaussian stays Gaussian, with means and variances
> simply adding.

**Cues**
- `flip`: mirror `f_Y` about the vertical axis.
- `slide`: translate the flipped copy across `f_X`, shading the overlap area.
- `trace-triangle`: plot the running overlap as `w` advances, building the
  triangular `f_W` for the sum of two uniforms.
- `mgf-product`: write `M_W(s) = M_X(s) M_Y(s)`; collapse two Gaussian bells into
  one wider bell.

---

## Beat: gaussian-vectors  (scene: GaussianVectors)

> One distribution deserves the last word, because it runs all through
> engineering: the Gaussian vector. <bookmark mark="ellipse"/> A pair of jointly
> Gaussian variables has elliptical contours, whose shape is set by a mean vector
> and a covariance matrix. <bookmark mark="affine-map"/> Now hit that vector with
> an affine map — multiply by a matrix, add a constant — and watch what happens to
> the cloud: it stretches, rotates, and shifts. <bookmark mark="stays-gaussian"/>
> The remarkable fact is that it stays Gaussian. The new mean is the old mean
> mapped through, and the new covariance is the matrix sandwiched around the old
> one. Compute those two, and you're done — which is why Gaussian vectors are so
> beloved in signal processing.

**Cues**
- `ellipse`: draw the elliptical contours of a 2D Gaussian with its mean and
  covariance.
- `affine-map`: apply `Y = A X + b`, animating the point cloud stretching and
  shifting.
- `stays-gaussian`: snap new elliptical contours onto the transformed cloud,
  label mean `A m + b` and covariance `A Σ Aᵀ`.
- Close with the shared `outro_bridge` (key_idea + bridge to Empirical Sums).

---

## Cut list (if over budget)
1. Drop the optional `gaussian-vectors` beat entirely; let `mgf-product` carry
   the "Gaussian stays Gaussian" punchline.
2. In `sums-convolution`, cut the `mgf-product` half and keep only the visual
   sliding convolution.
3. Trim `conditioning` to the slice-and-renormalize picture, dropping the
   conditional-mean / estimator aside.
