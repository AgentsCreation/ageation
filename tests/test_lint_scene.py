"""lint_scene: mark_intended_overlap suppression + endpoint-in-container rule.

These replay real (tiny) scenes through capture(), so they exercise the same
monkey-patched path `make lint-scene` uses.
"""

import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "scenes"))

from lint_scene import capture, violations  # noqa: E402  (tools/ via conftest)

SCENE_SRC = f"""
import sys
sys.path.insert(0, {os.path.join(REPO, 'scenes')!r})
from manim import *
from _style import mark_intended_overlap


class UnmarkedOverlap(Scene):
    def construct(self):
        # Two Texts colliding: no container/graph heuristic applies.
        a = Text("aaaaaa").shift(LEFT * 0.1)
        b = Text("bbbbbb").shift(RIGHT * 0.1)
        self.play(FadeIn(a), FadeIn(b))


class MarkedOverlap(Scene):
    def construct(self):
        a = Text("aaaaaa").shift(LEFT * 0.1)
        b = Text("bbbbbb").shift(RIGHT * 0.1)
        mark_intended_overlap(a, b, reason="deliberate collision for the test")
        self.play(FadeIn(a), FadeIn(b))


class MarkedGroupSurvivesRegroup(Scene):
    def construct(self):
        a = Text("aaaaaa").shift(LEFT * 0.1)
        b = Text("bbbbbb").shift(RIGHT * 0.1)
        mark_intended_overlap(a, b, reason="marks ride the mobjects")
        regrouped = VGroup(VGroup(a), VGroup(b))  # selector paths all change
        self.play(FadeIn(regrouped))


class ArrowIntoEllipse(Scene):
    def construct(self):
        region = Ellipse(width=2.0, height=1.0)
        arrow = Arrow(start=RIGHT * 3, end=RIGHT * 0.5, buff=0)
        self.play(FadeIn(region), FadeIn(arrow))
"""


def _write_scene(tmp_path):
    p = tmp_path / "lint_fixture.py"
    p.write_text(SCENE_SRC)
    return str(p)


def _total_violations(scene_path, scene_class):
    snaps = capture(scene_path, scene_class)
    found = suppressed = 0
    for snap in snaps:
        f, s = violations(snap, tol=0.05, buffer=0.0)
        found += len(f)
        suppressed += len(s)
    return found, suppressed


def test_unmarked_overlap_is_flagged(tmp_path):
    found, suppressed = _total_violations(_write_scene(tmp_path), "UnmarkedOverlap")
    assert found > 0
    assert suppressed == 0


def test_marked_overlap_is_suppressed_and_audited(tmp_path):
    found, suppressed = _total_violations(_write_scene(tmp_path), "MarkedOverlap")
    assert found == 0
    assert suppressed > 0


def test_marks_survive_regrouping(tmp_path):
    found, suppressed = _total_violations(_write_scene(tmp_path),
                                          "MarkedGroupSurvivesRegroup")
    assert found == 0
    assert suppressed > 0


def test_arrow_endpoint_inside_container_not_flagged(tmp_path):
    found, _ = _total_violations(_write_scene(tmp_path), "ArrowIntoEllipse")
    assert found == 0
