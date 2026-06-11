# derived_from: legacy (hand-built before the script layer existed; re-cut in
# the voiceover style is pending — see HISTORY.md §7)
from manim import *


class ChapterOverview(Scene):
    """High-level title card and outline."""

    def construct(self):
        title = Text("Conditional Probability", font_size=56)
        tagline = Text(
            "Computing likelihoods from partial information",
            font_size=30,
            color=GRAY_B,
        )
        tagline.next_to(title, DOWN, buff=0.5)

        self.play(Write(title))
        self.play(FadeIn(tagline, shift=UP * 0.3))
        self.wait(2)

        group = VGroup(title, tagline)
        self.play(group.animate.to_edge(UP))
        self.wait(1)

        items = VGroup(
            Text("1.  Conditioning on events", font_size=34),
            Text("2.  The total probability theorem", font_size=34),
            Text("3.  Bayes' rule", font_size=34),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.6)
        items.next_to(group, DOWN, buff=1.0)

        for item in items:
            self.play(FadeIn(item, shift=RIGHT * 0.4))
            self.wait(1)

        self.wait(2)
        self.play(FadeOut(items), FadeOut(group))
        self.wait(1)


class ConditioningOnEvents(Scene):
    """Die example, then the formal definition of conditional probability."""

    def construct(self):
        title = Text("Conditioning on Events", font_size=44)
        self.play(Write(title))
        self.wait(1)
        self.play(title.animate.to_edge(UP))

        # Six die outcomes as numbered squares with probability labels
        squares = VGroup()
        labels = VGroup()
        for k in range(1, 7):
            sq = Square(side_length=1.0, color=BLUE)
            sq.set_fill(BLUE, opacity=0.25)
            num = MathTex(str(k), font_size=44)
            num.move_to(sq)
            squares.add(VGroup(sq, num))
        squares.arrange(RIGHT, buff=0.45)
        squares.next_to(title, DOWN, buff=0.9)

        for k, cell in enumerate(squares):
            p = MathTex(r"\tfrac{1}{6}", font_size=38)
            p.next_to(cell, DOWN, buff=0.35)
            labels.add(p)

        fair = Text("A fair die: six equally likely outcomes", font_size=28)
        fair.next_to(labels, DOWN, buff=0.7)

        self.play(LaggedStart(*[FadeIn(c) for c in squares], lag_ratio=0.15))
        self.play(LaggedStart(*[Write(p) for p in labels], lag_ratio=0.15))
        self.play(FadeIn(fair))
        self.wait(2)

        # Side information: the outcome is odd
        info = Text('Side information: "the outcome is odd"', font_size=28, color=YELLOW)
        info.move_to(fair)
        self.play(ReplacementTransform(fair, info))
        self.wait(1)

        evens = VGroup(squares[1], squares[3], squares[5])
        even_labels = VGroup(labels[1], labels[3], labels[5])
        self.play(
            evens.animate.set_opacity(0.15),
            FadeOut(even_labels),
        )
        self.wait(1)

        new_labels = VGroup()
        for idx in (0, 2, 4):
            p = MathTex(r"\tfrac{1}{3}", font_size=38, color=YELLOW)
            p.move_to(labels[idx])
            new_labels.add(p)
        self.play(
            *[
                ReplacementTransform(labels[idx], p)
                for idx, p in zip((0, 2, 4), new_labels)
            ]
        )
        self.wait(2)

        # Compute Pr(3 | odd)
        calc = MathTex(
            r"\Pr(3 \mid \{1,3,5\})",
            r"=",
            r"\frac{\Pr(3 \cap \{1,3,5\})}{\Pr(\{1,3,5\})}",
            r"=",
            r"\frac{1/6}{1/2}",
            r"=",
            r"\frac{1}{3}",
            font_size=40,
        )
        calc.next_to(info, DOWN, buff=0.6)

        box = SurroundingRectangle(squares[2], color=YELLOW, buff=0.08)
        self.play(Create(box))
        self.play(Write(calc[0:3]))
        self.wait(2)
        self.play(Write(calc[3:5]))
        self.wait(1)
        self.play(Write(calc[5:7]))
        self.wait(2)

        # Formal definition
        self.play(
            FadeOut(squares),
            FadeOut(new_labels),
            FadeOut(info),
            FadeOut(box),
            FadeOut(calc),
        )

        def_text = Text("Definition", font_size=34, color=YELLOW)
        def_text.next_to(title, DOWN, buff=0.8)
        definition = MathTex(
            r"\Pr(A \mid B)", r"=", r"\frac{\Pr(A \cap B)}{\Pr(B)}",
            font_size=52,
        )
        definition.next_to(def_text, DOWN, buff=0.7)
        condition = MathTex(r"\text{provided that } \Pr(B) > 0", font_size=34, color=GRAY_B)
        condition.next_to(definition, DOWN, buff=0.6)

        self.play(FadeIn(def_text))
        self.play(Write(definition))
        self.wait(1)
        self.play(FadeIn(condition))
        self.wait(1)

        remark = Text(
            "Conditional probabilities form a valid probability law",
            font_size=26,
            color=GRAY_B,
        )
        remark.next_to(condition, DOWN, buff=0.7)
        self.play(FadeIn(remark))
        self.wait(3)


class TotalProbability(Scene):
    """Partition diagram, the theorem, and the two-urn example."""

    def construct(self):
        title = Text("The Total Probability Theorem", font_size=44)
        self.play(Write(title))
        self.wait(1)
        self.play(title.animate.to_edge(UP))

        # Partition of the sample space with an overlapping event B
        omega = Rectangle(width=7.5, height=3.4, color=WHITE)
        omega.next_to(title, DOWN, buff=0.7)
        x0 = omega.get_left()[0]
        cuts = [x0, x0 + 2.5, x0 + 5.0, x0 + 7.5]
        colors = [RED, GREEN, BLUE]
        regions = VGroup()
        for i in range(3):
            r = Rectangle(
                width=cuts[i + 1] - cuts[i],
                height=3.4,
                stroke_color=WHITE,
                fill_color=colors[i],
                fill_opacity=0.25,
            )
            r.move_to([(cuts[i] + cuts[i + 1]) / 2, omega.get_center()[1], 0])
            regions.add(r)

        region_labels = VGroup(
            *[
                MathTex(f"A_{i+1}", font_size=40).move_to(
                    regions[i].get_top() + DOWN * 0.45
                )
                for i in range(3)
            ]
        )
        omega_label = MathTex(r"\Omega", font_size=40)
        omega_label.next_to(omega, LEFT, buff=0.3).shift(UP * 1.2)

        ellipse = Ellipse(width=5.0, height=1.8, color=YELLOW)
        ellipse.move_to(omega.get_center() + DOWN * 0.4)
        b_label = MathTex("B", font_size=40, color=YELLOW)
        b_label.move_to(ellipse.get_center() + DOWN * 1.4)
        b_arrow = Arrow(
            b_label.get_top(), ellipse.get_bottom() + UP * 0.1,
            buff=0.1, color=YELLOW, stroke_width=3,
        )

        self.play(Create(omega), FadeIn(omega_label))
        self.play(LaggedStart(*[FadeIn(r) for r in regions], lag_ratio=0.2))
        self.play(LaggedStart(*[Write(l) for l in region_labels], lag_ratio=0.2))
        self.wait(1)
        self.play(Create(ellipse), FadeIn(b_label), Create(b_arrow))
        self.wait(1)

        # Highlight the pieces B ∩ A_k
        pieces = VGroup()
        for i in range(3):
            piece = Intersection(
                regions[i], ellipse,
                fill_color=colors[i], fill_opacity=0.85, stroke_width=0,
            )
            pieces.add(piece)
        decomposition = MathTex(
            r"B = (B \cap A_1) \cup (B \cap A_2) \cup (B \cap A_3)",
            font_size=38,
        )
        decomposition.next_to(omega, DOWN, buff=1.1)
        self.play(LaggedStart(*[FadeIn(p) for p in pieces], lag_ratio=0.3))
        self.play(Write(decomposition))
        self.wait(2)

        theorem = MathTex(
            r"\Pr(B)", r"=", r"\sum_{k=1}^{n} \Pr(A_k) \Pr(B \mid A_k)",
            font_size=44,
        )
        theorem.move_to(decomposition)
        self.play(ReplacementTransform(decomposition, theorem))
        self.wait(3)

        diagram = VGroup(
            omega, omega_label, regions, region_labels,
            ellipse, b_label, b_arrow, pieces,
        )
        self.play(
            FadeOut(diagram),
            theorem.animate.scale(0.85).next_to(title, DOWN, buff=0.35),
        )
        self.wait(1)

        # Two-urn example
        def urn(n_green, n_red, name):
            balls = VGroup()
            for i in range(n_green):
                balls.add(Circle(radius=0.13, color=GREEN, fill_opacity=1))
            for i in range(n_red):
                balls.add(Circle(radius=0.13, color=RED, fill_opacity=1))
            balls.arrange_in_grid(rows=3, buff=0.1)
            container = SurroundingRectangle(balls, color=WHITE, buff=0.2)
            label = Text(name, font_size=24)
            label.next_to(container, DOWN, buff=0.2)
            return VGroup(balls, container, label)

        urn1 = urn(5, 3, "Urn 1")
        urn2 = urn(3, 9, "Urn 2")
        urns = VGroup(urn1, urn2).arrange(RIGHT, buff=1.6)
        urns.next_to(theorem, DOWN, buff=0.45)

        prompt = Text(
            "Pick an urn at random, then draw a ball. Probability it is green?",
            font_size=25,
        )
        prompt.next_to(urns, DOWN, buff=0.35)

        self.play(FadeIn(urn1), FadeIn(urn2))
        self.play(FadeIn(prompt))
        self.wait(2)

        solution = MathTex(
            r"\Pr(g)",
            r"= \Pr(g \mid U_1)\Pr(U_1) + \Pr(g \mid U_2)\Pr(U_2)",
            font_size=36,
        )
        numbers = MathTex(
            r"= \frac{5}{8} \cdot \frac{1}{2} + \frac{3}{12} \cdot \frac{1}{2}",
            r"= \frac{7}{16}",
            font_size=36,
        )
        solution.next_to(prompt, DOWN, buff=0.35)
        self.play(Write(solution))
        self.wait(2)
        numbers.next_to(solution, DOWN, buff=0.3)
        numbers.align_to(solution[1], LEFT)
        self.play(Write(numbers[0]))
        self.wait(1)
        self.play(Write(numbers[1]))
        self.play(Circumscribe(numbers[1], color=YELLOW))
        self.wait(3)


class BayesRule(Scene):
    """Derivation of Bayes' rule and the disease-test example."""

    def construct(self):
        title = Text("Bayes' Rule", font_size=44)
        self.play(Write(title))
        self.wait(1)
        self.play(title.animate.to_edge(UP))

        # Derivation from the two expansions of Pr(A ∩ B)
        step1 = MathTex(
            r"\Pr(A \cap B)", r"=", r"\Pr(A \mid B)\Pr(B)",
            r"=", r"\Pr(B \mid A)\Pr(A)",
            font_size=44,
        )
        step1.next_to(title, DOWN, buff=0.8)
        self.play(Write(step1[0:3]))
        self.wait(1)
        self.play(Write(step1[3:5]))
        self.wait(2)

        bayes = MathTex(
            r"\Pr(A \mid B)", r"=", r"\frac{\Pr(A)\Pr(B \mid A)}{\Pr(B)}",
            font_size=48,
        )
        bayes.next_to(step1, DOWN, buff=0.8)
        self.play(Write(bayes))
        self.wait(2)

        expanded = MathTex(
            r"\Pr(A_i \mid B)",
            r"=",
            r"\frac{\Pr(A_i)\Pr(B \mid A_i)}{\sum_{k=1}^{n}\Pr(A_k)\Pr(B \mid A_k)}",
            font_size=48,
        )
        expanded.move_to(bayes)
        note = Text(
            "with the denominator expanded by total probability",
            font_size=24,
            color=GRAY_B,
        )
        note.next_to(expanded, DOWN, buff=0.5)
        self.play(ReplacementTransform(bayes, expanded), FadeIn(note))
        self.wait(3)

        self.play(FadeOut(step1), FadeOut(note), FadeOut(expanded))

        # Disease-test example
        setup = VGroup(
            Text("A test for a rare disease:", font_size=30, color=YELLOW),
            MathTex(r"\Pr(P \mid D) = 0.95 \quad \text{(positive if diseased)}", font_size=34),
            MathTex(r"\Pr(\overline{P} \mid \overline{D}) = 0.95 \quad \text{(negative if healthy)}", font_size=34),
            MathTex(r"\Pr(D) = 0.01 \quad \text{(prevalence)}", font_size=34),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        setup.next_to(title, DOWN, buff=0.6)

        for line in setup:
            self.play(FadeIn(line, shift=RIGHT * 0.3))
            self.wait(1)

        question = Text(
            "You test positive. What is the chance you have the disease?",
            font_size=28,
        )
        question.next_to(setup, DOWN, buff=0.6)
        self.play(Write(question))
        self.wait(2)

        self.play(FadeOut(setup), question.animate.next_to(title, DOWN, buff=0.5))

        calc1 = MathTex(
            r"\Pr(D \mid P)",
            r"= \frac{\Pr(D)\Pr(P \mid D)}{\Pr(D)\Pr(P \mid D) + \Pr(\overline{D})\Pr(P \mid \overline{D})}",
            font_size=40,
        )
        calc1.next_to(question, DOWN, buff=0.7)
        self.play(Write(calc1))
        self.wait(2)

        calc2 = MathTex(
            r"= \frac{0.01 \cdot 0.95}{0.01 \cdot 0.95 + 0.99 \cdot 0.05}",
            r"\approx 0.16",
            font_size=44,
        )
        calc2.next_to(calc1, DOWN, buff=0.6)
        self.play(Write(calc2[0]))
        self.wait(2)
        self.play(Write(calc2[1]))
        self.play(Circumscribe(calc2[1], color=YELLOW))
        self.wait(2)

        takeaway = Text(
            "For a rare disease, a positive test is still probably a false positive.",
            font_size=28,
            color=YELLOW,
        )
        takeaway.next_to(calc2, DOWN, buff=0.8)
        self.play(FadeIn(takeaway, shift=UP * 0.3))
        self.wait(3)
