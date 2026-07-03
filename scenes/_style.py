"""Shared house style for a video series.

Centralizing palette, type scale, notation helpers, and a bar-chart builder
here keeps every chapter visually consistent. Import these helpers instead of
hard-coding colors and font sizes in each scene.

Conventions:
- Notation helpers emit *expanded* LaTeX forms (Manim's MathTex has no access
  to a book's preamble macros). pr()/expectation()/variance() cover the common
  math-stats forms; add subject-specific helpers here as a project needs them,
  and keep them consistent with the project's notation rules in project.yaml.
- YELLOW is the single accent color used to highlight the "current" idea.
- GRAY_B is used for secondary / muted text (taglines, captions).
"""

from manim import (
    Axes,
    BLACK,
    Circle,
    Create,
    Dot,
    FadeIn,
    GRAY_B,
    Rectangle,
    RoundedRectangle,
    Text,
    MathTex,
    VGroup,
    Write,
    YELLOW,
    BLUE,
    WHITE,
    UP,
    DOWN,
    LEFT,
    RIGHT,
    UL,
    DR,
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


# --- Axis label spacing ------------------------------------------------------
# Manim's get_x_axis_label / get_y_axis_label default to MED_SMALL_BUFF (0.25),
# which reads as crowding the axis once a label is more than a few characters
# wide ("robot height" vs "k"). The geometric-overlap lint can't catch this --
# adjacent-not-overlapping is geometrically clean -- so it has to be a sane
# default in the style file. 0.40 in scene units clears multi-word CAPTION-
# size labels at every render resolution.
LABEL_BUFF = 0.40


def axis_label_x(axes, label, *, buff: float = LABEL_BUFF) -> Text:
    """A bottom-of-axis label with safe default spacing.

    `label` may be a string (wrapped in a styled Text) or any mobject the
    caller has already styled (passed through unchanged).
    """
    if isinstance(label, str):
        label = Text(label, font_size=CAPTION, color=MUTED)
    return axes.get_x_axis_label(label, edge=DOWN, direction=DOWN, buff=buff)


def axis_label_y(axes, label, *, buff: float = LABEL_BUFF) -> Text:
    """A left-of-axis label with safe default spacing.

    `label` may be a string (wrapped in a styled Text) or any mobject the
    caller has already styled (passed through unchanged).
    """
    if isinstance(label, str):
        label = Text(label, font_size=CAPTION, color=MUTED)
    return axes.get_y_axis_label(label, edge=LEFT, direction=LEFT, buff=buff)


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

    # x starts at -1, not 0 (STYLE_BOOK 12, charts): one spare unit keeps the
    # k=0 bar clear of the y-axis instead of straddling it.
    axes = Axes(
        x_range=[-1, x_max, 1],
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


# --- Recurring figures ---------------------------------------------------------
# The series' established glyphs. A chapter that draws its own version of one
# of these reads as a different series (STYLE_BOOK "reuse established
# figures") -- these were copy-pasted into 13 of 17 scene files before being
# promoted here. Extend this section rather than redefining locally.

def omega_box(width=4.2, height=4.2):
    """The sample-space frame: a rounded rectangle labelled Omega."""
    box = RoundedRectangle(
        corner_radius=0.2, width=width, height=height, color=MUTED
    ).set_stroke(MUTED, width=2)
    lab = MathTex(r"\Omega", font_size=BODY, color=MUTED)
    lab.next_to(box.get_corner(UL), DR, buff=0.22)
    return VGroup(box, lab)


def ball(label, color, radius=0.30, font_size=22):
    """A colored disk with a dark centered label (Chapter 2 house style)."""
    dot = Dot(radius=radius, color=color).set_fill(color, opacity=0.95)
    dot.set_stroke(INK, width=1.5)
    txt = MathTex(label, font_size=font_size, color=BLACK)
    return VGroup(dot, txt.move_to(dot.get_center()))


def die_face(n, size=0.8, color=INK, fill=None):
    """A rounded-square die face showing n pips in the standard layout (Ch 3)."""
    sq = RoundedRectangle(corner_radius=0.12, width=size, height=size)
    sq.set_stroke(color, 2.5)
    if fill is not None:
        sq.set_fill(fill, opacity=0.30)
    o = size * 0.26
    P = {
        "c": [0, 0, 0],
        "tl": [-o, o, 0], "tr": [o, o, 0],
        "bl": [-o, -o, 0], "br": [o, -o, 0],
        "ml": [-o, 0, 0], "mr": [o, 0, 0],
    }
    layout = {
        1: ["c"], 2: ["tl", "br"], 3: ["tl", "c", "br"],
        4: ["tl", "tr", "bl", "br"], 5: ["tl", "tr", "c", "bl", "br"],
        6: ["tl", "tr", "ml", "mr", "bl", "br"],
    }
    pips = VGroup(*[Dot(point=P[k], radius=size * 0.07, color=color)
                    for k in layout[n]])
    return VGroup(sq, pips)


def coin(symbol, color, radius=0.42):
    """A coin face: an outlined disk with its symbol (H/T) in the same color."""
    c = Circle(radius=radius, color=color).set_fill(color, 0.22)
    c.set_stroke(color, 4)
    return VGroup(c, Text(symbol, font_size=SMALL, color=color).move_to(c))


# --- Course-linking template -------------------------------------------------
# Every video opens with intro_card and closes with outro_bridge so the whole
# series shares one structural grammar. The text comes from the script layer
# (objective / key_idea) and the manifest (neighbor titles), keeping chapters
# visually and narratively continuous without a single concatenated film.

def _text_lines(lines, *, font_size, color, buff=0.18) -> VGroup:
    """One centred Text per line (never \\n inside a Text -- it renders garbled).

    Accepts a single string or a sequence of strings; long titles/objectives
    split at the clause turn into two centred lines (STYLE_BOOK layout rule).
    """
    if isinstance(lines, str):
        lines = [lines]
    group = VGroup(*[Text(line, font_size=font_size, color=color)
                     for line in lines])
    group.arrange(DOWN, buff=buff)
    return group


def intro_card(title, objective, kicker: str | None = None) -> VGroup:
    """Standard opening: optional kicker, the title, then the learning goal.

    Stating the objective up front is a retention best practice -- the viewer
    knows what they're about to be able to do. `title` and `objective` accept
    a string or a sequence of lines, so a two-line objective needs no
    hand-rolled card.
    """
    parts = VGroup()
    if kicker:
        parts.add(Text(kicker, font_size=SMALL, color=ACCENT))
    parts.add(_text_lines(title, font_size=TITLE, color=INK))
    parts.add(_text_lines(objective, font_size=SMALL, color=MUTED))
    parts.arrange(DOWN, buff=0.4)
    return fit_to_frame(parts)


def outro_bridge(key_idea, next_title: str | None = None) -> VGroup:
    """Standard closing: the one-line takeaway, then a peek at what's next.

    The key idea is a retrieval cue (consolidates the video); the next-up line
    is the bridge that links this video to the following one. `key_idea`
    accepts a string or a sequence of lines.
    """
    parts = VGroup(
        Text("Key idea", font_size=SMALL, color=ACCENT),
        _text_lines(key_idea, font_size=BODY, color=INK),
    )
    if next_title:
        parts.add(Text(f"Coming up:  {next_title}", font_size=SMALL, color=MUTED))
    parts.arrange(DOWN, buff=0.4)
    return fit_to_frame(parts)


def progress_tag(index: int, total: int) -> Text:
    """Small 'n / total' marker for a corner -- orients the viewer in the arc."""
    return Text(f"{index} / {total}", font_size=CAPTION, color=MUTED)


# --- Declared intent for the geometric lint ------------------------------------
# Some overlaps are the point of the composition: a Venn diagram's ellipses,
# an arrow deliberately crossing into a region, a label sitting on a wedge.
# The old mechanism -- index-addressed allowlist sidecars like
# "VGroup[1].VGroup[4].Arrow[3]" -- broke on any regrouping. Marking the
# mobjects themselves survives every regroup/Transform by construction
# (manim copies carry attributes), and keeps the declaration next to the
# code that creates the overlap.

_intended_overlap_next_token = [1]


def mark_intended_overlap(*mobjects, reason: str):
    """Declare that these mobjects are meant to overlap each other.

    tools/lint_scene.py skips any pair of leaves that share a mark (marks on
    a group apply to everything inside it). Each call is one intent group --
    call again for an unrelated overlap. Zero effect on rendering.

    Returns the single mobject (or the tuple) for chaining.
    """
    token = _intended_overlap_next_token[0]
    _intended_overlap_next_token[0] += 1
    for m in mobjects:
        # Mark the whole family, not just the group: manim animations
        # (LaggedStartMap, FadeIn of a group) re-parent submobjects into
        # fresh Groups, so a mark that only lives on the original group
        # would not be found above the leaves afterwards.
        family = m.get_family() if hasattr(m, "get_family") else [m]
        for member in family:
            marks = dict(getattr(member, "_lint_overlap_marks", {}))
            marks[token] = reason
            member._lint_overlap_marks = marks
    return mobjects[0] if len(mobjects) == 1 else mobjects


# --- Speech service from project config ---------------------------------------
# Voice is configuration, not code: project.yaml's `project.voice` block names
# the provider/voice once per project, and the draft/final switch is the
# AGEATION_TTS environment variable (render.py sets it to gtts for -ql drafts).
# Scenes just call speech_service() -- no more hand-commenting provider lines
# in every make_speech_service().

def _find_project_root(start: str) -> str | None:
    """Walk up from `start` looking for a directory containing project.yaml."""
    import os
    d = os.path.abspath(start)
    for _ in range(8):
        if os.path.exists(os.path.join(d, "project.yaml")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return None


def _load_dotenv_key(root: str, name: str) -> None:
    """Set os.environ[name] from `<root>/.env` when not already exported.

    manim-voiceover reads the process environment, so a key that lives only in
    the project's .env (the doctor.py convention) must be lifted in here.
    """
    import os
    if os.environ.get(name):
        return
    path = os.path.join(root, ".env")
    if not os.path.exists(path):
        return
    for raw in open(path, encoding="utf-8"):
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        if key.strip() != name:
            continue
        val = val.strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in {"'", '"'}:
            val = val[1:-1]
        if val:
            os.environ[name] = val
        return


def speech_service():
    """Build the TTS service for a scene from project.yaml + environment.

    Resolution order for the provider:
      1. AGEATION_TTS env var (``gtts`` or ``openai``) -- the draft/final
         switch; tools/render.py sets ``gtts`` automatically for -ql drafts.
      2. project.yaml ``project.voice.provider``.
      3. ``gtts`` when no project.yaml is found (safe, free fallback).

    The project root is located via the AGEATION_PROJECT env var when set
    (render.py exports it), else by walking up from the calling scene file.
    An openai provider requires ``project.voice.name`` -- the voice is a
    per-video editorial decision, so there is deliberately no default.
    """
    import inspect
    import os

    root = os.environ.get("AGEATION_PROJECT")
    if not root:
        caller = inspect.stack()[1].filename
        root = _find_project_root(os.path.dirname(caller)) or _find_project_root(os.getcwd())

    voice_cfg = {}
    if root:
        import yaml
        with open(os.path.join(root, "project.yaml"), encoding="utf-8") as fh:
            manifest = yaml.safe_load(fh) or {}
        voice_cfg = (manifest.get("project") or {}).get("voice") or {}

    provider = os.environ.get("AGEATION_TTS") or voice_cfg.get("provider") or "gtts"
    provider = provider.strip().lower()

    if provider == "gtts":
        from manim_voiceover.services.gtts import GTTSService
        return GTTSService(lang="en", tld="com")

    if provider == "openai":
        name = voice_cfg.get("name")
        if not name:
            raise RuntimeError(
                "voice.provider is openai but project.yaml sets no voice.name -- "
                "the voice is a per-video decision; add `name:` under project.voice")
        if root:
            _load_dotenv_key(root, "OPENAI_API_KEY")
        from manim_voiceover.services.openai import OpenAIService
        configure_openai_client()
        return OpenAIService(voice=name,
                             model=voice_cfg.get("model", "tts-1"),
                             transcription_model=None)

    raise RuntimeError(f"unknown TTS provider {provider!r} (expected gtts or openai)")


# --- OpenAI client preflight -------------------------------------------------
# The openai SDK defaults to a 600 s request timeout with no retries, and
# manim-voiceover's OpenAIService uses the module-level openai client. So a
# stalled /audio/speech call costs ~10 min per occurrence before manim moves
# on -- observed twice per render in practice (see HISTORY.md gotchas). Every
# scene that constructs OpenAIService should call this helper first; a stall
# then costs ~30 s, retried up to 5 times.

def configure_openai_client(timeout: float = 30, max_retries: int = 5) -> None:
    """Set the openai SDK module-level timeout + retry policy.

    Call once before constructing OpenAIService. Safe to call repeatedly --
    overwrites the same module-level attributes each time.
    """
    import openai
    openai.timeout = timeout
    openai.max_retries = max_retries
