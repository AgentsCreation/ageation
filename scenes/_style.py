"""Shared house style for a video series.

Centralizing palette, type scale, notation helpers, and a bar-chart builder
here keeps every chapter visually consistent. Import these helpers instead of
hard-coding colors and font sizes in each scene.

Conventions:
- Notation helpers emit *expanded* LaTeX forms (Manim's MathTex has no access
  to a book's preamble macros). pr()/expectation()/variance() cover the common
  math-stats forms; add subject-specific helpers here as a course needs them,
  and keep them consistent with the project's notation rules in course.yaml.
- YELLOW is the single accent color used to highlight the "current" idea.
- GRAY_B is used for secondary / muted text (taglines, captions).
"""

from manim import (
    Axes,
    Create,
    FadeIn,
    GRAY_B,
    Rectangle,
    Text,
    MathTex,
    VGroup,
    Write,
    YELLOW,
    BLUE,
    WHITE,
    UP,
    DOWN,
    DEGREES,
    config,
)

# --- Palette -----------------------------------------------------------------
ACCENT = YELLOW       # the idea currently in focus
MUTED = GRAY_B        # taglines, captions, de-emphasized text
BAR = BLUE            # default PMF bar fill
INK = WHITE           # primary text

# --- Type scale (one place to retune pacing/readability) ---------------------
TITLE = 56
SECTION = 44
BODY = 34
SMALL = 28
CAPTION = 24


def pr(expr: str) -> str:
    r"""Probability expression using \Pr.

    Example: ``MathTex(pr("X = k"))`` -> ``\Pr\left(X = k\right)``.
    """
    return r"\Pr\left(" + expr + r"\right)"


def expectation(expr: str) -> str:
    r"""Expectation: ``\mathrm{E}\left[expr\right]`` (not blackboard-bold E)."""
    return r"\mathrm{E}\left[" + expr + r"\right]"


def variance(expr: str) -> str:
    r"""Variance: ``\mathrm{Var}\left(expr\right)``."""
    return r"\mathrm{Var}\left(" + expr + r"\right)"


def section_title(label: str) -> Text:
    """A section heading already sized and colored for the top of a scene."""
    return Text(label, font_size=SECTION, color=INK)


# --- Overflow safety ---------------------------------------------------------
# The camera frame is config.frame_width x config.frame_height (14.22 x 8 at
# 16:9). SAFE_MARGIN keeps content off the very edge. Every chart/graph and any
# composed group should pass through fit_to_frame so nothing ever spills past
# the visible area -- this is enforced in code rather than by eyeballing frames,
# so it holds at any render resolution.
SAFE_MARGIN = 0.5


def fit_to_frame(mobj, margin: float = SAFE_MARGIN):
    """Uniformly scale `mobj` down (never up) until it fits the safe frame area.

    Returns the same mobject for chaining. A no-op when it already fits.
    """
    max_w = config.frame_width - 2 * margin
    max_h = config.frame_height - 2 * margin
    # One uniform scale factor preserves aspect ratio and proportions.
    factor = 1.0
    if mobj.width > max_w:
        factor = min(factor, max_w / mobj.width)
    if mobj.height > max_h:
        factor = min(factor, max_h / mobj.height)
    if factor < 1.0:
        mobj.scale(factor)
    return mobj


def make_pmf_chart(
    values,
    *,
    x_max=None,
    y_max=None,
    bar_color=BAR,
    x_label="k",
    y_label=r"p_X(k)",
    bar_width_ratio=0.7,
):
    """Build a labelled PMF bar chart as a self-contained VGroup.

    Parameters
    ----------
    values : list[float]
        PMF values p_X(k) for k = 0, 1, 2, ... (index is the k value).
    x_max, y_max : float, optional
        Axis bounds. Sensible defaults are derived from ``values``.
    bar_color : Manim color
        Fill color for the bars.

    Returns
    -------
    (chart, bars) : (VGroup, VGroup)
        ``chart`` is the full group (axes + labels + bars); ``bars`` is the
        VGroup of bar rectangles alone, so callers can animate them separately.
    """
    n = len(values)
    if x_max is None:
        x_max = n
    if y_max is None:
        y_max = max(values) * 1.2 if values else 1.0

    axes = Axes(
        x_range=[0, x_max, 1],
        y_range=[0, y_max, max(round(y_max / 4, 2), 0.05)],
        x_length=8,
        y_length=4,
        axis_config={"include_numbers": True, "font_size": 20},
        tips=False,
    )
    x_lab = axes.get_x_axis_label(MathTex(x_label, font_size=SMALL))
    y_lab = axes.get_y_axis_label(MathTex(y_label, font_size=SMALL))

    bars = VGroup()
    unit_w = axes.x_axis.unit_size
    for k, p in enumerate(values):
        if p <= 0:
            continue
        bottom = axes.c2p(k, 0)
        top = axes.c2p(k, p)
        height = top[1] - bottom[1]
        bar = Rectangle(
            width=unit_w * bar_width_ratio,
            height=height,
            fill_color=bar_color,
            fill_opacity=0.85,
            stroke_width=1,
            stroke_color=INK,
        )
        bar.move_to(bottom, aligned_edge=DOWN)
        bars.add(bar)

    chart = VGroup(axes, x_lab, y_lab, bars)
    # Guarantee the whole graph (axes + labels + bars) fits the visible frame
    # before any caller scales or positions it further.
    fit_to_frame(chart)
    return chart, bars


# --- Course-linking template -------------------------------------------------
# Every video opens with intro_card and closes with outro_bridge so the whole
# series shares one structural grammar. The text comes from the script layer
# (objective / key_idea) and the manifest (neighbor titles), keeping chapters
# visually and narratively continuous without a single concatenated film.

def intro_card(title: str, objective: str, kicker: str | None = None) -> VGroup:
    """Standard opening: optional kicker, the title, then the learning goal.

    Stating the objective up front is a retention best practice -- the viewer
    knows what they're about to be able to do.
    """
    parts = VGroup()
    if kicker:
        parts.add(Text(kicker, font_size=SMALL, color=ACCENT))
    parts.add(Text(title, font_size=TITLE, color=INK))
    parts.add(Text(objective, font_size=SMALL, color=MUTED))
    parts.arrange(DOWN, buff=0.4)
    return parts


def outro_bridge(key_idea: str, next_title: str | None = None) -> VGroup:
    """Standard closing: the one-line takeaway, then a peek at what's next.

    The key idea is a retrieval cue (consolidates the video); the next-up line
    is the bridge that links this video to the following one.
    """
    parts = VGroup(
        Text("Key idea", font_size=SMALL, color=ACCENT),
        Text(key_idea, font_size=BODY, color=INK),
    )
    if next_title:
        parts.add(Text(f"Coming up:  {next_title}", font_size=SMALL, color=MUTED))
    parts.arrange(DOWN, buff=0.4)
    return parts


def progress_tag(index: int, total: int) -> Text:
    """Small 'n / total' marker for a corner -- orients the viewer in the arc."""
    return Text(f"{index} / {total}", font_size=CAPTION, color=MUTED)
