---
slug: 3-basic-concepts
title: Basic Concepts
stage: script             # tex -> concept -> [script] -> scene -> render
status: draft             # draft | reviewed | approved  (human gate)
derived_from: 3-basic-concepts.md
derived_from_sha256: 318db5d93c225ae71342a87476cddae2723dbc6ea907215616e8080eb19081d7
provenance_stamped: 2026-06-11
target_scene_file: scenes/basic_concepts.py

# --- Narrative glue (links this video to its neighbours) -------------------
# objective : the learning goal, spoken in the intro_card (retention: state
#             the goal up front).
# recap     : reactivates the previous chapter at the open (spacing).
# key_idea  : one-line takeaway spoken in outro_bridge (retrieval cue).
# bridge    : teases the next chapter at the close.
# Neighbour titles for recap/bridge come from course.yaml prereqs + order.
linking:
  objective: "Define probability axiomatically so it works for any sample space, not just equally likely ones."
  recap: "Last chapter, Combinatorics, gave us probability as counting when outcomes are equally likely."
  key_idea: "Three axioms — nonnegativity, normalization, countable additivity — define every probability law."
  bridge: "Next: Conditional Probability — how the probability of an event changes given partial information."

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
  - id: sample-space
    scene_class: SampleSpacesAndEvents
    narration_words: 130
    est_sec: 52
    measured_sec: null
    sync_points: [show-omega, circle-event, rules]
  - id: axioms
    scene_class: ProbabilityAxioms
    narration_words: 130
    est_sec: 52
    measured_sec: null
    sync_points: [axiom1, axiom2, axiom3, countable]
  - id: derived
    scene_class: DerivedProperties
    narration_words: 150
    est_sec: 60
    measured_sec: null
    sync_points: [monotone, union-formula, inclusion-exclusion, union-bound]
  - id: finite-countable
    scene_class: FiniteAndCountableModels
    narration_words: 140
    est_sec: 56
    measured_sec: null
    sync_points: [finite-sum, equally-likely, coin-until-heads, geometric-sum]
  - id: uncountable
    scene_class: UncountableModels
    narration_words: 130
    est_sec: 52
    measured_sec: null
    sync_points: [interval, length, wheel, bridge]
---

# Video Script — Basic Concepts

Narration is the source of truth for timing. Each `<bookmark mark="id"/>` is a
synchronization point: in the generated scene, the corresponding animation is
triggered at that word via `tracker.time_until_bookmark("id")`. Animations with
no bookmark simply fill `run_time = tracker.duration` for their beat.

---

## Beat: sample-space  (scene: SampleSpacesAndEvents)

> In the last chapter, Combinatorics, probability meant counting equally likely
> outcomes. Now we build the framework that works for any experiment at all.
> <bookmark mark="show-omega"/> An experiment produces one of several outcomes,
> and the set of all possible outcomes is the sample space, written capital
> Omega — exactly the set we met back in Mathematical Review. <bookmark
> mark="circle-event"/> An event is an admissible subset of that sample space,
> like rolling a prime number on a die. <bookmark mark="rules"/> A good sample
> space follows two rules: its outcomes must be distinct and mutually exclusive,
> so the result is unambiguous, and collectively exhaustive, so every possible
> outcome is covered.

**Animation cue:** this is the FIRST beat, so it opens with the shared
intro_card stating the objective and recapping "Combinatorics."

**Cues**
- `show-omega`: the Omega rectangle with seven colored numbered balls.
- `circle-event`: lasso a subset, e.g. {2,3,5}, label it "event."
- `rules`: caption "distinct & mutually exclusive" and "collectively exhaustive."

---

## Beat: axioms  (scene: ProbabilityAxioms)

> A probability law assigns every event a number, its probability, subject to
> three axioms. <bookmark mark="axiom1"/> First, nonnegativity: every
> probability is at least zero. <bookmark mark="axiom2"/> Second, normalization:
> the probability of the whole sample space is exactly one. <bookmark
> mark="axiom3"/> Third, additivity: if two events are disjoint — they share no
> outcome — the probability of their union is the sum of their probabilities.
> <bookmark mark="countable"/> This extends to countable additivity: for any
> sequence of disjoint events, the probability of their union is the sum of the
> individual probabilities. Those three rules are the entire definition. Nothing
> else is assumed.

**Cues**
- `axiom1`: card `Pr(A) ≥ 0`.
- `axiom2`: card `Pr(Ω) = 1`, the box lighting up fully.
- `axiom3`: two disjoint blobs, `Pr(A ∪ B) = Pr(A) + Pr(B)`.
- `countable`: extend to `Pr(⋃ A_k) = Σ Pr(A_k)` over a disjoint sequence.

---

## Beat: derived  (scene: DerivedProperties)

> Everything else is a consequence. <bookmark mark="monotone"/> If event A sits
> inside event B, then A's probability is at most B's — a bigger event is at
> least as likely. <bookmark mark="union-formula"/> For events that overlap, the
> probability of their union is Pr(A) plus Pr(B) minus the probability of their
> intersection, because the overlap was counted twice. <bookmark
> mark="inclusion-exclusion"/> Extending this alternating add-and-subtract to
> many events gives the inclusion-exclusion principle. <bookmark
> mark="union-bound"/> And dropping the subtracted terms gives the union bound:
> the probability that at least one event occurs is no more than the sum of their
> individual probabilities. It's the workhorse for bounding rare events when the
> exact joint probability is hard to compute.

**Cues**
- `monotone`: nested circles A ⊂ B, shade `B - A`.
- `union-formula`: two overlapping circles; add both, subtract the overlap;
  write `Pr(A∪B) = Pr(A) + Pr(B) − Pr(A∩B)`.
- `inclusion-exclusion`: three circles with alternating +/− regions.
- `union-bound`: write `Pr(⋃ A_k) ≤ Σ Pr(A_k)`; brief urn red-ball example.

---

## Beat: finite-countable  (scene: FiniteAndCountableModels)

> The axioms compute differently depending on the sample space. <bookmark
> mark="finite-sum"/> On a finite space, a probability law is fixed entirely by
> the probabilities of the individual outcomes — just add up the ones in your
> event. <bookmark mark="equally-likely"/> If those outcomes are equally likely,
> each has probability one over n, and the probability of an event becomes its
> size divided by n. That's exactly the counting model from the last chapter,
> now derived from the axioms instead of assumed. <bookmark
> mark="coin-until-heads"/> Sample spaces can also be countably infinite. Toss a
> fair coin until the first heads: the outcome is the trial number, and the
> chance the first heads lands on trial k is one over two to the k. <bookmark
> mark="geometric-sum"/> Those probabilities, one half plus one quarter plus one
> eighth and on forever, sum to exactly one, just as the axioms demand.

**Cues**
- `finite-sum`: bar of outcome weights; highlight and sum the event's bars.
- `equally-likely`: collapse to equal bars `1/n`, write `Pr(A) = |A|/n`.
- `coin-until-heads`: a coin tossed T, T, H landing on trial 3.
- `geometric-sum`: decaying bars 1/2, 1/4, 1/8 ... visibly filling to 1.

---

## Beat: uncountable  (scene: UncountableModels)

> Some sample spaces are uncountable, and here single outcomes can't carry the
> probability. <bookmark mark="interval"/> Pick a number at random from the unit
> interval, zero to one, with uniform weighting. <bookmark mark="length"/> The
> probability of landing in a sub-interval from a to b is simply its length, b
> minus a — and more generally the probability of an event is the integral over
> it, the length of the set. <bookmark mark="wheel"/> Spin the wheel of
> serendipity and it stops uniformly around the circle; the chance it lands in
> the first quadrant is one quarter. This idea — probability as length, computed
> by an integral — is the doorway to continuous models. <bookmark mark="bridge"/>
> But first, in the next chapter, Conditional Probability, we ask how the
> probability of an event changes once we learn that something else has already
> happened.

**Animation cue:** this is the LAST beat, so it closes with the shared
outro_bridge — speak the key_idea around `length` and the bridge to "Conditional
Probability" on `bridge`, with the progress_tag for Chapter 3.

**Cues**
- `interval`: the unit interval [0,1] with a uniformly weighted bar.
- `length`: shade (a, b), label its width `b − a = Pr((a,b))`.
- `wheel`: the spinning wheel; shade the first quadrant, label `1/4`.
- `bridge`: fade to the chapter-4 title card.

---

## Cut list (if over budget)
1. Drop the optional `uncountable-models` beat entirely; close after the
   countable coin example and bridge from there.
2. Trim `derived` to monotonicity and the union formula; cut inclusion-exclusion
   and shorten the union bound.
3. Cut the wheel-of-serendipity example, keeping only the unit interval.
4. Compress `axioms` by merging the additivity and countable-additivity cues.
