---
slug: 04-conditional-probability
title: Conditional Probability
stage: script             # tex -> concept -> [script] -> scene -> render
status: approved             # draft | reviewed | approved  (human gate)
derived_from: 04-conditional-probability.md
derived_from_sha256: 0b6fdcb2e12b64677f62686f49e5da02606bd83059897a7a76f3cd001003cb38
provenance_stamped: 2026-07-06
target_scene_file: scenes/conditional_probability.py

# --- Narrative glue (links this video to its neighbours) -------------------
# objective : the learning goal, spoken in the intro_card (retention: state
#             the goal up front).
# recap     : reactivates the previous chapter at the open (spacing).
# key_idea  : one-line takeaway spoken in outro_bridge (retrieval cue).
# bridge    : teases the next chapter at the close.
# Neighbour titles for recap/bridge come from project.yaml prereqs + order.
linking:
  objective: "Update probabilities in light of partial information."
  recap: "Last chapter, Basic Concepts, we built probability laws on a sample space."
  key_idea: "Conditioning rescales probability to what is still possible; Bayes' rule flips a conditional around."
  bridge: "Next: Discrete Random Variables — attaching numbers to outcomes so we can compute with them."

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
estimated_runtime_sec: 348
measured_runtime_sec: null

beats:
  - id: overview
    scene_class: ChapterOverview
    narration_words: 64
    est_sec: 26
    measured_sec: null
    sync_points: []
  - id: conditioning-on-events
    scene_class: ConditioningOnEvents
    narration_words: 150
    est_sec: 60
    measured_sec: null
    sync_points: [show-die, reveal-odd, relabel, definition]
  - id: total-probability
    scene_class: TotalProbability
    narration_words: 145
    est_sec: 58
    measured_sec: null
    sync_points: [partition, slice-b, theorem, urns, solve]
  - id: bayes-rule
    scene_class: BayesRule
    narration_words: 152
    est_sec: 61
    measured_sec: null
    sync_points: [two-expansions, flip, disease-setup, compute, takeaway]
---

# Video Script — Conditional Probability

Narration is the source of truth for timing. Each `<bookmark mark="id"/>` is a
synchronization point: in the generated scene, the corresponding animation is
triggered at that word via `tracker.time_until_bookmark("id")`. Animations with
no bookmark simply fill `run_time = tracker.duration` for their beat.

---

## Beat: overview  (scene: ChapterOverview)

> Last chapter we built probability laws on a sample space. Now we learn what
> happens when partial information arrives. Conditional probability lets us
> update likelihoods once we know that some event has occurred. In this video we
> condition on events, assemble probabilities from cases with the total
> probability theorem, and finish by flipping a conditional around with Bayes'
> rule.

**Animation cue:** this is the FIRST beat — open with the shared `intro_card`
(objective + recap from the `linking:` block). Then reveal the three outline
items one per clause as the last sentence is spoken.

---

## Beat: conditioning-on-events  (scene: ConditioningOnEvents)

> Roll a fair die: <bookmark mark="show-die"/> six outcomes, each with
> probability one-sixth. Now suppose someone tells you the result is odd.
> <bookmark mark="reveal-odd"/> Only three faces survive — one, three, and five —
> and since they were equally likely before, they stay equally likely after.
> <bookmark mark="relabel"/> Each climbs from one-sixth to one-third. The chance
> of rolling a three given the outcome is odd is one-third. Generalizing,
> <bookmark mark="definition"/> the conditional probability of A given B is the
> probability of A and B together, divided by the probability of B, valid
> whenever the probability of B is positive.

**Cues**
- `show-die`: fade in the six labeled faces with their one-sixth labels.
- `reveal-odd`: dim the even faces; fade out their labels.
- `relabel`: transform the three odd labels into one-third, then box the three.
- `definition`: clear the die and write Pr(A | B) = Pr(A ∩ B) / Pr(B) with the
  Pr(B) > 0 proviso beneath it.

---

## Beat: total-probability  (scene: TotalProbability)

> Often the easiest way to find a probability is divide and conquer. Split the
> sample space into a partition — <bookmark mark="partition"/> disjoint cases
> that together cover everything. Any event B <bookmark mark="slice-b"/> gets
> sliced into pieces, one inside each case. Adding those pieces back up gives
> the total probability theorem: <bookmark mark="theorem"/> the probability of B
> is the sum over cases of the probability of each case times the probability of
> B given that case. <bookmark mark="urns"/> Two urns make it concrete — pick one
> at random, then draw a ball. <bookmark mark="solve"/> Weighting each urn's green
> chance by one-half gives seven-sixteenths overall.

**Cues**
- `partition`: draw Omega as three colored strips labeled A1, A2, A3.
- `slice-b`: overlay event B across the strips; highlight each B ∩ A_k piece.
- `theorem`: transform the decomposition into the summation formula.
- `urns`: fade in the two urns of green and red balls with the prompt.
- `solve`: write the weighted sum and circumscribe the seven-sixteenths result.

---

## Beat: bayes-rule  (scene: BayesRule)

> Here's the payoff. Expand the probability of A and B two ways:
> <bookmark mark="two-expansions"/> as A-given-B times B, and as B-given-A times A.
> Set them equal and <bookmark mark="flip"/> solve for A given B — that is Bayes'
> rule. It lets us reverse a conditional we know into the one we want. Consider a
> rare-disease test. <bookmark mark="disease-setup"/> It's ninety-five percent
> accurate either way, but only one person in a hundred has the disease. You test
> positive — <bookmark mark="compute"/> plug the numbers into Bayes' rule and the
> chance you actually have it is only about sixteen percent. <bookmark mark="takeaway"/>
> For a rare condition, a positive test is still probably a false alarm.

**Cues**
- `two-expansions`: write Pr(A ∩ B) = Pr(A | B)Pr(B) = Pr(B | A)Pr(A).
- `flip`: rearrange into Bayes' rule; then expand the denominator by total
  probability.
- `disease-setup`: list the three given numbers line by line, then the question.
- `compute`: write the Bayes computation and circumscribe the 0.16 result.
- `takeaway`: highlight the false-positive moral.
- This is the LAST beat — close with the shared `outro_bridge` (key_idea +
  bridge from the `linking:` block), teasing Discrete Random Variables.

---

## Cut list (if over budget)
1. Drop the optional `independence` concept entirely (already omitted from beats).
2. In `total-probability`, cut the two-urn worked example and keep only the
   partition diagram plus the theorem.
3. In `conditioning-on-events`, shorten the relabel step and skip restating the
   one-third result in words.
