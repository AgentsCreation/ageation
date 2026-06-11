# Minimal environment smoke test: confirms manim + LaTeX render end to end.
#   uv run manim -pql test_scene.py TestScene
from manim import *

class TestScene(Scene):
    def construct(self):
        eq = MathTex(r"\Pr(A \mid B) = \frac{\Pr(B \mid A)\, \Pr(A)}{\Pr(B)}")
        self.play(Write(eq))
        self.wait(1)
