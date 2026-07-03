# derived_from: content/5-discrete-random-variables-script.md
# derived_from_sha256: 7328f0af1a4abffd5d8ac70da74830d9f85997c81ae6b5b6ae11e4c461a6a2f4
"""Chapter 5 -- Discrete Random Variables (narrated with manim-voiceover).

Source notes : input/Probability/5Discrete_Random_Variables.tex
Script        : content/5-discrete-random-variables-script.md

Timing model (bookmark-free, portable)
---------------------------------------
Narration drives the animation. Rather than one big narration with
``<bookmark/>`` tags (which require word-level timestamps from Whisper or
Azure), each beat is split into several *sequential* ``with self.voiceover(
text=...) as tracker:`` blocks -- one per synchronization point. The animation
for each block is timed with ``run_time=tracker.duration``, so the visuals match
the voice sentence by sentence with no extra dependencies. This runs on free
gTTS out of the box.

Rendering (on a machine with Manim installed; NOT the Cowork sandbox)
--------------------------------------------------------------------
Draft (free Google TTS, needs internet):
    uv run manim -pql scenes/discrete_random_variables.py ChapterOverview
Final: switch make_speech_service() to OpenAIService (needs OPENAI_API_KEY).
"""

import os
import sys
from math import comb, exp, factorial

# Ensure sibling modules (e.g. _style) import regardless of working directory.
sys.path.insert(0, os.path.dirname(__file__))

from manim import *  # noqa: F401,F403
from manim_voiceover import VoiceoverScene

from _style import (
    ACCENT,
    MUTED,
    BAR,
    INK,
    TITLE,
    SECTION,
    BODY,
    SMALL,
    CAPTION,
    pr,
    section_title,
    make_pmf_chart,
    intro_card,
    outro_bridge,
    progress_tag,
    fit_to_frame,
    mark_intended_overlap,
    speech_service,
)


def make_speech_service():
    """Voice comes from project.yaml (project.voice) via _style.speech_service.

    Drafts are free: tools/render.py exports AGEATION_TTS=gtts for -ql, and
    the env var beats the configured provider. Finals read the per-project
    voice (a deliberate editorial decision -- speech_service errors rather
    than defaulting when voice.name is missing).

    No transcription_model: we sync via separate voiceover blocks instead of
    bookmarks, so word-level timing (Whisper) is not required.
    """
    return speech_service()


# --- PMF generators (plain Python, kept out of the Scene classes) ------------

def bernoulli_pmf(p=0.25):
    return [1 - p, p]


def binomial_pmf(n=8, p=0.25):
    return [comb(n, k) * p**k * (1 - p) ** (n - k) for k in range(n + 1)]


def poisson_pmf(lam=2.0, kmax=8):
    return [lam**k / factorial(k) * exp(-lam) for k in range(kmax + 1)]


def geometric_pmf(p=0.25, kmax=12):
    # Indexed from k=0 so it lines up on the integer axis; p_X(k) = (1-p)^k * p.
    return [(1 - p) ** k * p for k in range(kmax + 1)]


class ChapterOverview(VoiceoverScene):
    """Beat: overview -- title card + outline revealed clause by clause."""

    def construct(self):
        self.set_speech_service(make_speech_service())

        # Shared course intro: kicker + title + objective, with a recap of the
        # previous chapter and a progress marker.
        intro = intro_card(
            "Discrete Random Variables",
            "Turn outcomes into numbers, and describe them with a PMF.",
            kicker="Chapter 5  ·  Probability",
        )
        tag = progress_tag(5, 12).to_corner(DR, buff=0.4)

        with self.voiceover(
            text="Last chapter, we conditioned probabilities on partial "
                 "information. Now we take the next step — turning the outcomes "
                 "themselves into numbers."
        ):
            self.play(FadeIn(intro[0], shift=DOWN * 0.2), run_time=0.6)
            self.play(Write(intro[1]), run_time=1.1)
            self.play(FadeIn(intro[2], shift=UP * 0.2), run_time=0.7)
            self.play(FadeIn(tag), run_time=0.4)

        self.play(intro.animate.to_edge(UP), run_time=0.8)

        items = VGroup(
            Text("1.  Random variables as functions", font_size=BODY),
            Text("2.  Probability mass functions", font_size=BODY),
            Text("3.  The important named distributions", font_size=BODY),
            Text("4.  Binomial converges to Poisson", font_size=BODY),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.55)
        items.next_to(intro, DOWN, buff=0.8)

        clauses = [
            "In this chapter we turn outcomes into numbers,",
            "describe them with a probability mass function,",
            "meet the distributions you'll see again and again,",
            "and finish with a surprising limit.",
        ]
        for clause, item in zip(clauses, items):
            with self.voiceover(text=clause):
                self.play(FadeIn(item, shift=RIGHT * 0.4), run_time=0.6)

        self.play(*[FadeOut(m) for m in self.mobjects])


class RandomVariableMapping(VoiceoverScene):
    """Beat: rv-mapping -- X as a function from outcomes to the real line."""

    def construct(self):
        self.set_speech_service(make_speech_service())

        title = section_title("A Random Variable is a Function")
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))

        box = RoundedRectangle(
            corner_radius=0.2, width=4.2, height=4.2, color=INK
        ).shift(LEFT * 3.5 + DOWN * 0.3)
        omega = MathTex(r"\Omega", font_size=BODY).next_to(
            box.get_corner(UL), DR, buff=0.2
        )

        colors = [RED, BLUE, GREEN, GRAY_B, TEAL]
        positions = [
            box.get_center() + np.array(p)
            for p in [
                [-0.9, 1.0, 0], [0.8, 0.7, 0], [-0.6, -0.6, 0],
                [0.9, -0.9, 0], [0.1, 0.1, 0],
            ]
        ]
        outcomes = VGroup()
        for i, (c, pos) in enumerate(zip(colors, positions), start=1):
            dot = Dot(point=pos, radius=0.18, color=c)
            lab = Text(str(i), font_size=20, color=INK).move_to(pos)
            outcomes.add(VGroup(dot, lab))

        line = NumberLine(
            x_range=[0, 6, 1], length=4.5, include_numbers=True, font_size=22,
        ).shift(RIGHT * 3.2 + DOWN * 0.3)
        rlabel = MathTex(r"\mathbb{R}", font_size=BODY).next_to(line, UP, buff=0.3)

        targets = [1, 4, 2, 5, 3]
        arrows = VGroup()
        for grp, t in zip(outcomes, targets):
            arrows.add(CurvedArrow(
                grp.get_center() + RIGHT * 0.25,
                line.number_to_point(t),
                angle=-PI / 6, color=ACCENT, stroke_width=3, tip_length=0.18,
            ))

        defn = MathTex(r"X : \Omega \to \mathbb{R}", font_size=BODY, color=ACCENT)
        defn.to_edge(DOWN, buff=0.6)

        # The mapping figure is a deliberate tangle: five curved arrows fan
        # out of the outcome cloud, cross each other, and land on the line.
        mark_intended_overlap(
            arrows, outcomes, line,
            reason="mapping arrows deliberately sweep across the figure")

        with self.voiceover(
            text="Here is a sample space Omega, with a handful of outcomes."
        ):
            self.play(Create(box), Write(omega))
            self.play(LaggedStartMap(FadeIn, outcomes, lag_ratio=0.2))

        with self.voiceover(
            text="A random variable is just a function: it sends each outcome "
                 "to a point on the real line."
        ):
            self.play(Create(line), Write(rlabel))
            # Not LaggedStartMap(Create, arrows, ...): its identity arg_creator
            # *-unpacks each Arrow's tip into positional slots (TypeError at
            # render) -- the CLAUDE.md composite-mobject gotcha.
            self.play(LaggedStart(*[Create(a) for a in arrows], lag_ratio=0.25),
                      run_time=2)

        with self.voiceover(
            text="Different outcomes can land on the same number — that's "
                 "allowed."
        ):
            self.play(Indicate(arrows, color=ACCENT))

        with self.voiceover(
            text="Formally, we write X maps Omega to the real numbers."
        ):
            self.play(Write(defn))

        self.play(*[FadeOut(m) for m in self.mobjects])


class PMFGallery(VoiceoverScene):
    """Beat: pmf-gallery -- named distributions, one per voiceover block."""

    def construct(self):
        self.set_speech_service(make_speech_service())

        title = section_title("Important Discrete Distributions")
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))

        gallery = [
            ("Bernoulli", r"p_X(x)=\begin{cases}1-p & x=0\\ p & x=1\end{cases}",
             bernoulli_pmf(0.25),
             "The simplest case is the Bernoulli — a single coin flip, all the "
             "mass on zero and one."),
            ("Binomial  (n=8,\\ p=0.25)",
             r"p_X(k)=\binom{n}{k}p^k(1-p)^{n-k}", binomial_pmf(8, 0.25),
             "Add up n independent flips and you get the binomial."),
            ("Poisson  (\\lambda=2)",
             r"p_X(k)=\frac{\lambda^k}{k!}e^{-\lambda}", poisson_pmf(2.0, 8),
             "Counting rare events over time gives the Poisson."),
            ("Geometric  (p=0.25)",
             r"p_X(k)=(1-p)^{k-1}p", geometric_pmf(0.25, 12),
             "And waiting for the first success gives the geometric, whose "
             "bars decay by a constant factor."),
        ]

        with self.voiceover(
            text="The probability mass function lists how much probability "
                 "sits on each value."
        ):
            self.wait(0.3)

        prev = None
        for name, formula, values, narration in gallery:
            label = Text(name, font_size=BODY, color=ACCENT)
            label.next_to(title, DOWN, buff=0.4)
            tex = MathTex(formula, font_size=SMALL).next_to(label, DOWN, buff=0.3)
            chart, bars = make_pmf_chart(values, x_label="k")
            chart.scale(0.8).to_edge(DOWN, buff=0.5)

            with self.voiceover(text=narration):
                if prev is not None:
                    self.play(FadeOut(prev), run_time=0.4)
                self.play(FadeIn(label), Write(tex), run_time=0.6)
                self.play(Create(chart[0]), Write(chart[1]), Write(chart[2]),
                          run_time=0.8)
                self.play(LaggedStartMap(GrowFromEdge, bars, edge=DOWN,
                                         lag_ratio=0.08), run_time=1.0)
            prev = VGroup(label, tex, chart)

        self.play(*[FadeOut(m) for m in self.mobjects])


class BinomialToPoisson(VoiceoverScene):
    """Beat: binomial-to-poisson -- bars settle onto the Poisson limit."""

    def construct(self):
        self.set_speech_service(make_speech_service())
        # lambda must stay below every n in n_values: p = lambda/n is a
        # probability (STYLE_BOOK 12, "validate parameters"). The old
        # lam=10.0 made n=5 use p=2 -- the first frame charted garbage.
        lam = 2.0
        kmax = 10

        title = section_title("Binomial Converges to Poisson")
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))

        formula = MathTex(
            r"\lim_{n\to\infty}\binom{n}{k}\left(\tfrac{\lambda}{n}\right)^k"
            r"\left(1-\tfrac{\lambda}{n}\right)^{n-k}"
            r"=\frac{\lambda^k}{k!}e^{-\lambda}",
            font_size=SMALL,
        ).next_to(title, DOWN, buff=0.35)
        fit_to_frame(formula)  # long formula -> never let it run off the sides
        self.play(Write(formula))

        target = [lam**k / factorial(k) * exp(-lam) for k in range(kmax + 1)]
        y_max = max(target) * 1.6
        axes = Axes(
            x_range=[0, kmax, 2],
            y_range=[0, y_max, 0.05],
            x_length=9,
            y_length=3.6,
            axis_config={"include_numbers": True, "font_size": 18},
            tips=False,
        ).to_edge(DOWN, buff=0.5)
        fit_to_frame(axes)  # bars are built from axes.c2p, so guard it first
        x_lab = axes.get_x_axis_label(MathTex("k", font_size=SMALL))

        def bars_for(values, color, opacity):
            unit_w = axes.x_axis.unit_size
            grp = VGroup()
            for k, p in enumerate(values):
                height = max(axes.c2p(k, p)[1] - axes.c2p(k, 0)[1], 1e-3)
                rect = Rectangle(
                    width=unit_w * 0.6, height=height,
                    fill_color=color, fill_opacity=opacity,
                    stroke_width=1, stroke_color=INK,
                )
                rect.move_to(axes.c2p(k, 0), aligned_edge=DOWN)
                grp.add(rect)
            return grp

        poisson_ref = bars_for(target, ACCENT, 0.18)
        ref_label = Text("Poisson(2)", font_size=CAPTION, color=ACCENT)
        ref_label.next_to(axes, UP, buff=0.1).to_edge(RIGHT, buff=1.0)

        n_values = [5, 15, 25, 35]
        binom = [
            [comb(n, k) * (lam / n) ** k * (1 - lam / n) ** (n - k)
             if k <= n else 0.0 for k in range(kmax + 1)]
            for n in n_values
        ]

        n_label = Text("n = 5", font_size=BODY, color=INK)
        n_label.next_to(axes, UP, buff=0.1).to_edge(LEFT, buff=1.0)
        current = bars_for(binom[0], BAR, 0.85)
        # The whole point of this beat: solid binomial bars drawn over the
        # ghost Poisson bars on one shared axes. Marked before the first
        # play() so every snapshot sees the intent; Transform() keeps
        # `current` as the live mobject, so the mark survives every n step.
        mark_intended_overlap(
            axes, poisson_ref, current,
            reason="binomial bars settle onto the Poisson ghost bars")

        with self.voiceover(
            text="Here's the payoff. Fix a rate lambda, and let each of n "
                 "trials succeed with probability lambda over n."
        ):
            self.play(Create(axes), Write(x_lab))
            self.play(FadeIn(poisson_ref), FadeIn(ref_label))

        with self.voiceover(
            text="With just five trials the binomial is coarse."
        ):
            self.play(FadeIn(n_label),
                      LaggedStartMap(GrowFromEdge, current, edge=DOWN,
                                     lag_ratio=0.05))

        captions = [
            (15, "Fifteen trials, and it sharpens."),
            (25, "Twenty-five trials."),
            (35, "Thirty-five — and the bars settle right onto the Poisson "
                 "curve."),
        ]
        for (n, narration), values in zip(captions, binom[1:]):
            new_label = Text(f"n = {n}", font_size=BODY, color=INK)
            new_label.move_to(n_label)
            new_bars = bars_for(values, BAR, 0.85)
            with self.voiceover(text=narration):
                self.play(Transform(current, new_bars),
                          Transform(n_label, new_label),
                          run_time=1.2)

        with self.voiceover(
            text="The binomial, in the limit, becomes Poisson."
        ):
            self.play(Indicate(poisson_ref, scale_factor=1.05, color=ACCENT))

        self.play(*[FadeOut(m) for m in self.mobjects])

        # Shared course outro: one-line takeaway + bridge to the next chapter.
        outro = outro_bridge(
            "A discrete random variable is fully described by its PMF.",
            next_title="Discrete Expectations",
        )
        with self.voiceover(
            text="The key idea to carry forward: a discrete random variable is "
                 "fully described by its probability mass function. Coming up "
                 "next, we collapse a whole P-M-F into a single number — its "
                 "expectation."
        ):
            self.play(FadeIn(outro[0], shift=DOWN * 0.2), run_time=0.6)
            self.play(Write(outro[1]), run_time=1.1)
            self.play(FadeIn(outro[2], shift=UP * 0.2), run_time=0.7)
        self.wait(0.5)
        self.play(FadeOut(outro))
