"""Predictable-layout helpers (scenes/_style.py, 2026-07-04 review harvest)."""

import os
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "scenes"))

import _style  # noqa: E402
from manim import MathTex, Square, Text  # noqa: E402


def test_two_column_sits_level():
    left, right = Square(2.0), Square(1.0)
    _style.two_column(left, right)
    assert abs(left.get_y() - right.get_y()) < 1e-6
    assert left.get_x() < 0 < right.get_x()


def test_eq_chain_aligns_equals_column():
    chain = _style.eq_chain(r"I^2", r"a + b", r"c", r"1")
    assert len(chain.submobjects) == 3
    x0 = chain[0][1].get_x()          # first line's "="
    for ln in chain[1:]:
        assert abs(ln[0].get_x() - x0) < 1e-4
    # Continuation lines are ("=", rhs) — the empty-leading-part trap is
    # exactly what this helper exists to prevent.
    assert len(chain[1].submobjects) == 2
    # The chain is centered as a group.
    assert abs(chain.get_x()) < 1e-6


def test_eq_chain_requires_a_rhs():
    with pytest.raises(ValueError):
        _style.eq_chain("x")


def test_even_stack_equalizes_gaps():
    a, b, c = Square(0.6), Square(1.2), Square(0.4)
    _style.even_stack(a, b, c, top=2.0, bottom=-2.0)
    gap_ab = a.get_bottom()[1] - b.get_top()[1]
    gap_bc = b.get_bottom()[1] - c.get_top()[1]
    assert abs(gap_ab - gap_bc) < 1e-6
    assert a.get_top()[1] <= 2.0 + 1e-6
    for m in (a, b, c):
        assert abs(m.get_x()) < 1e-6      # default column x = 0


def test_caption_under_centers_on_its_object():
    chart = Square(3.0).move_to([-3.2, -1.0, 0])
    cap = _style.caption_under(chart, "probability = length ratio")
    assert abs(cap.get_x() - chart.get_x()) < 1e-6
    assert cap.get_top()[1] < chart.get_bottom()[1]
    assert isinstance(cap, Text)


def test_chart_tag_is_body_sized():
    tag = _style.chart_tag(r"\lambda = 2")
    assert isinstance(tag, MathTex)
    assert tag.font_size == _style.BODY
