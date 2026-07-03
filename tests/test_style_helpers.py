"""Promoted visual helpers + multi-line intro/outro cards (scenes/_style.py)."""

import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "scenes"))

import _style  # noqa: E402


def test_recurring_figures_build():
    for mobj in (_style.omega_box(), _style.ball("1", _style.BAR),
                 _style.die_face(5), _style.coin("H", _style.ACCENT)):
        assert len(mobj.submobjects) == 2


def test_intro_card_multiline_objective():
    card = _style.intro_card(
        "Discrete Random Variables and PMFs",
        ["Turn the outcomes of an experiment into numbers,",
         "and describe those numbers with a probability mass function."],
        kicker="Chapter 5  ·  Probability",
    )
    # kicker + title group + objective group; the objective is two Texts.
    assert len(card.submobjects) == 3
    assert len(card.submobjects[2].submobjects) == 2
    # fit_to_frame guarantee: nothing wider/taller than the safe area.
    from manim import config
    assert card.width <= config.frame_width - 2 * _style.SAFE_MARGIN + 1e-6
    assert card.height <= config.frame_height - 2 * _style.SAFE_MARGIN + 1e-6


def test_intro_card_single_string_still_works():
    card = _style.intro_card("Title", "One-line objective")
    assert len(card.submobjects) == 2  # no kicker


def test_outro_bridge_multiline_key_idea():
    out = _style.outro_bridge(["A PMF describes a discrete random variable",
                               "completely."], next_title="Expectation")
    assert len(out.submobjects) == 3  # label, idea group, coming-up line
    assert len(out.submobjects[1].submobjects) == 2
