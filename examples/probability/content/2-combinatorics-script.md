---
slug: 2-combinatorics
title: Combinatorics
stage: script             # tex -> concept -> [script] -> scene -> render
status: draft             # draft | reviewed | approved  (human gate)
derived_from: 2-combinatorics.md
derived_from_sha256: 9b3f1ff38436bf4d3184b88c7fae9765fe4b38822c4785408f25826f49c759a8
provenance_stamped: 2026-07-03
target_scene_file: scenes/combinatorics.py

# --- Narrative glue (links this video to its neighbours) -------------------
# objective : the learning goal, spoken in the intro_card (retention: state
#             the goal up front).
# recap     : reactivates the previous chapter at the open (spacing).
# key_idea  : one-line takeaway spoken in outro_bridge (retrieval cue).
# bridge    : teases the next chapter at the close.
# Neighbour titles for recap/bridge come from project.yaml prereqs + order.
linking:
  objective: "Count outcomes systematically so equally likely probability becomes computable."
  recap: "Last chapter, Mathematical Review, gave us sets and the Cartesian product."
  key_idea: "For equally likely outcomes, probability is favorable count over total count."
  bridge: "Next: Basic Concepts — the axioms that make probability rigorous beyond counting."

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
estimated_runtime_sec: 350
measured_runtime_sec: null

beats:
  - id: counting-principle
    scene_class: CountingPrinciple
    narration_words: 135
    est_sec: 54
    measured_sec: null
    sync_points: [intro-die, product-grid, generalize, coin-die]
  - id: permutations
    scene_class: CountingPermutations
    narration_words: 140
    est_sec: 56
    measured_sec: null
    sync_points: [fill-slots, factorial, k-perm, songs-example]
  - id: combinations
    scene_class: CountingCombinations
    narration_words: 140
    est_sec: 56
    measured_sec: null
    sync_points: [list-perms, fold-unordered, divide-kfact, binom-formula]
  - id: partitions
    scene_class: PartitionsAndMultinomial
    narration_words: 130
    est_sec: 52
    measured_sec: null
    sync_points: [split-groups, multinomial, stars-bars]
  - id: examples
    scene_class: CombinatorialExamples
    narration_words: 130
    est_sec: 52
    measured_sec: null
    sync_points: [pick3, megamillions, sinking-boat, bridge]
---

# Video Script — Combinatorics

Narration is the source of truth for timing. Each `<bookmark mark="id"/>` is a
synchronization point: in the generated scene, the corresponding animation is
triggered at that word via `tracker.time_until_bookmark("id")`. Animations with
no bookmark simply fill `run_time = tracker.duration` for their beat.

---

## Beat: counting-principle  (scene: CountingPrinciple)

> Last chapter we learned that a sample space is a set and the Cartesian product
> glues two sets together. Now we put that to work. <bookmark mark="intro-die"/>
> Roll a fair die: six equally likely faces, so the probability of any one face
> is one over six, and the probability of rolling a prime is three out of six.
> When outcomes are equally likely, probability is just counting. <bookmark
> mark="product-grid"/> The counting principle says the Cartesian product of a
> set with m elements and a set with n elements has m times n elements. <bookmark
> mark="generalize"/> Chain r experiments together and you simply multiply all
> their counts. <bookmark mark="coin-die"/> Flip a coin and roll a die: two
> times six is twelve possible outcomes.

**Animation cue:** this is the FIRST beat, so it opens with the shared
intro_card stating the objective and recapping "Mathematical Review."

**Cues**
- `intro-die`: show a die, highlight faces {2,3,5}, write 3/6.
- `product-grid`: reuse the {1,2,3} × {a,b} grid, annotate `m · n`.
- `generalize`: write `n_1 · n_2 · ... · n_r`.
- `coin-die`: coin (2) and die (6) fanning into a 12-cell grid.

---

## Beat: permutations  (scene: CountingPermutations)

> A permutation is an ordered arrangement of a set — a list with no repeats.
> <bookmark mark="fill-slots"/> To build one, count the choices: n options for
> the first slot, n minus one for the second since one is used up, and so on
> down to one. <bookmark mark="factorial"/> Multiply them all and you get n
> factorial, written n with an exclamation point. Three items give three
> factorial, which is six arrangements. <bookmark mark="k-perm"/> If you only
> rank k of the n items, you stop early, and the count is n factorial over
> n-minus-k factorial. <bookmark mark="songs-example"/> A band with four songs
> choosing an ordered set of two to play has four factorial over two factorial,
> which is twelve possible set lists.

**Cues**
- `fill-slots`: empty slots filling from a pool that shrinks n, n-1, n-2.
- `factorial`: write `n! = n(n-1)...1`; show the six permutations of {1,2,3}.
- `k-perm`: write `n!/(n-k)!`; gray out the unranked items.
- `songs-example`: four song tiles, pick ordered pairs, count to 12.

---

## Beat: combinations  (scene: CountingCombinations)

> A combination is an unordered subset — order no longer matters. <bookmark
> mark="list-perms"/> Take the two-permutations of one through four: there are
> twelve ordered lists. <bookmark mark="fold-unordered"/> But one-two and
> two-one are the same subset, so each subset got counted twice — in general,
> k factorial times. <bookmark mark="divide-kfact"/> Divide the ordered count by
> k factorial to remove the ordering. <bookmark mark="binom-formula"/> That gives
> the binomial coefficient, n choose k, equal to n factorial over k factorial
> times n-minus-k factorial. Choosing a k-subset is the same as choosing the
> n-minus-k you leave behind, so n choose k equals n choose n-minus-k. And
> summing n choose k over all k gives two to the n — the number of subsets of an
> n-element set.

**Cues**
- `list-perms`: the twelve ordered 2-lists of {1,2,3,4}.
- `fold-unordered`: animate each pair and its reverse merging into one loop.
- `divide-kfact`: overlay `÷ k!`.
- `binom-formula`: write `C(n,k) = n!/(k!(n-k)!)` and the symmetry identity.

---

## Beat: partitions  (scene: PartitionsAndMultinomial)

> Combinations split a set into two groups: the chosen and the rest. <bookmark
> mark="split-groups"/> Generalize to r labeled groups of sizes n-one through
> n-r. <bookmark mark="multinomial"/> Counting these splits gives the multinomial
> coefficient, n factorial divided by the product of each group's factorial. Roll
> a die nine times and ask for exactly three ones, three threes, and three
> fives: that's nine factorial over three factorial cubed, which is one thousand
> six hundred eighty. <bookmark mark="stars-bars"/> And if we only fix the number
> of groups, not their sizes, the stars-and-bars picture counts the assignments:
> n balls and r-minus-one dividers on a line, giving n-plus-r-minus-one choose n.

**Cues**
- `split-groups`: one row of balls partitioning into r dashed loops.
- `multinomial`: write `n!/(n_1! n_2! ... n_r!)`; show the die example = 1680.
- `stars-bars`: 5 balls + 2 bars sliding to read off the partition (0, 2, 3).

---

## Beat: examples  (scene: CombinatorialExamples)

> Let's spend this counting power. <bookmark mark="pick3"/> In Pick 3, you choose
> three digits zero through nine; played in exact order the chance is one in a
> thousand, but played in any order with three distinct digits it rises to three
> factorial over a thousand. <bookmark mark="megamillions"/> Mega Millions asks
> for five white balls from fifty-six plus one Mega ball from forty-six; the
> grand prize odds are one over fifty-six choose five, times one over
> forty-six — about one in a hundred seventy-five million. <bookmark
> mark="sinking-boat"/> And six couples split across two rescue boats: the chance
> no couple lands together on one boat is two to the sixth over twelve choose
> six. <bookmark mark="bridge"/> Counting carried us a long way — but it only
> works when outcomes are equally likely. Next, in Basic Concepts, we build the
> axioms that make probability rigorous even when they're not.

**Animation cue:** this is the LAST beat, so it closes with the shared
outro_bridge — speak the key_idea before `sinking-boat` and the bridge to
"Basic Concepts" on `bridge`, with the progress_tag for Chapter 2.

**Cues**
- `pick3`: a lottery slip filling with three digits, odds 1/1000 then 3!/1000.
- `megamillions`: a Mega Millions card, odds counter rolling to 1/175,711,536.
- `sinking-boat`: two boats, six couples splitting, write `2^6 / C(12,6)`.
- `bridge`: fade to the chapter-3 title card.

---

## Cut list (if over budget)
1. Drop the optional `sampling-table` framing (the four urn modes) from
   narration; keep only the formulas.
2. Trim `examples` to a single lottery (Mega Millions); cut Pick 3 and the boat.
3. Cut the stars-and-bars portion of `partitions`, keeping the multinomial.
4. Shorten `permutations` by dropping the band set-list example.
