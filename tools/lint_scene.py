#!/usr/bin/env python3
"""Geometric scene lint — flag undeclared bbox overlaps after each Scene.play().

Replays each scene's construct() with TTS stubbed and Scene.play monkey-patched
to snapshot mobject bounding boxes when each animation comes to rest. Pairwise
overlaps between leaf mobjects are flagged unless they are declared intent.
Parent-child pairs are ignored — a label inside its container is intentional
by construction.

Declaring an intended overlap: call `_style.mark_intended_overlap(a, b,
reason=...)` in the scene on the mobjects (or groups) that are meant to
overlap — the mark survives regrouping and Transform because it rides on the
mobjects themselves. The legacy per-scene allowlist sidecar
(<scene>.lint-allow.yaml, index-addressed paths) is still honored but
deprecated: its selectors break on any regroup. Use --verbose to audit which
overlaps the marks suppressed.

What it catches (≈44% of GEPA-style review rounds, per the design memo):
  - Text bbox intersecting a later-drawn shape (label-in-ring)
  - Crossing arrows / lines passing through a label bbox
  - Near-miss: gaps under a min-buffer tolerance (off by default)

What it does NOT catch:
  - Behavioral bugs (animation conflicts, opacity issues) — see PIPELINE.md
    for the planned tools/lint_animation.py
  - Aesthetic choices (which side of a node a label sits on, table position)
  - Z-order occlusion where bbox overlap is actually intentional

Usage:
  python tools/lint_scene.py [--project DIR]              # lint every chapter
  python tools/lint_scene.py --project DIR --chapter SLUG # one chapter
  python tools/lint_scene.py --scene-file PATH --scene-class NAME
"""

import argparse
import importlib.util
import os
import sys
from dataclasses import dataclass

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _project import project_parser, resolve_project, load_project

# --- Constants --------------------------------------------------------------

# Default shrink-epsilon for overlap intersection (scene units). 0.05 ≈ a
# 12-px stroke at 1080p — enough to absorb stroke-width noise without
# hiding real overlaps.
DEFAULT_TOL = 0.05

# Near-miss buffer (scene units). 0.15 ≈ one third of a default Text glyph
# height — close enough to feel cramped, far enough that legitimate tight
# layouts don't false-positive. Off (0) by default; enable per project.
NEAR_MISS_BUFFER = 0.0

# Types we treat as one node (no recursion into submobjects). Text/MathTex
# fan out into glyph VMobjects — for overlap-against-other-things, the union
# bbox of all glyphs is what humans read. Likewise Arrow's tip is a child
# but conceptually the arrow is one mark.
ATOMIC_TYPES = {
    "Text", "MarkupText", "Paragraph", "Title",
    "MathTex", "Tex", "SingleStringMathTex", "BulletedList",
    "Rectangle", "RoundedRectangle", "Square", "Circle", "Dot", "Ellipse",
    "Arrow", "DoubleArrow", "Vector", "Arrow3D",
    "Line", "DashedLine", "TangentLine", "Elbow", "CurvedArrow",
    "Polygon", "RegularPolygon", "Triangle", "Star",
    "NumberLine", "Axes", "NumberPlane",
    "ImageMobject", "SVGMobject",
    "Integer", "DecimalNumber", "Variable",
    "Table", "BarChart", "MobjectTable",
}

RED = "\033[31m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
DIM = "\033[2m"
RESET = "\033[0m"


# --- Data model -------------------------------------------------------------

@dataclass
class Entry:
    path: str           # dotted parent chain, e.g. "VGroup[2].Text[0]"
    cls: str            # class name
    bmin: tuple         # (x, y, z) bottom-left corner of bbox
    bmax: tuple         # (x, y, z) top-right corner of bbox
    marks: tuple = ()   # ((token, reason), ...) from _style.mark_intended_overlap,
                        # including marks inherited from enclosing groups
    ends: tuple = None  # ((x, y), (x, y)) real start/end for line-like types;
                        # a CurvedArrow's endpoints are nowhere near its bbox
                        # corners, so connection rules need the real thing


# --- Target discovery -------------------------------------------------------

def split_front_matter(path: str) -> dict | None:
    """Parse the YAML front matter of a markdown file. None on failure."""
    text = open(path, encoding="utf-8").read()
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end < 0:
        return None
    return yaml.safe_load(text[4:end]) or {}


def pick_targets(root: str, manifest: dict, args) -> list[tuple[str, str, str]]:
    """Return [(label, scene_file_abs, scene_class), ...]."""
    if args.scene_file and args.scene_class:
        return [("(explicit)",
                 os.path.join(root, args.scene_file) if not os.path.isabs(args.scene_file)
                 else args.scene_file,
                 args.scene_class)]

    out = []
    for ch in manifest.get("chapters") or []:
        slug = ch.get("slug")
        if not slug or (args.chapter and args.chapter != slug):
            continue
        script_path = os.path.join(root, "content", f"{slug}-script.md")
        if not os.path.exists(script_path):
            continue
        front = split_front_matter(script_path) or {}
        target = front.get("target_scene_file")
        if not target:
            continue
        target = target.split("#")[0].strip()
        scene_file_abs = os.path.join(root, target)
        if not os.path.exists(scene_file_abs):
            # Scripted-but-not-built chapters have a target with no scene
            # yet; a missing scene must not fail the whole lint pass.
            if args.chapter:
                raise SystemExit(f"scene file not found: {scene_file_abs}")
            continue

        classes = set()
        for beat in front.get("beats") or []:
            sc = beat.get("scene_class")
            if sc:
                classes.add(sc)
        for cls in sorted(classes):
            out.append((slug, scene_file_abs, cls))

    return out


# --- Scene replay -----------------------------------------------------------

def _stub_voiceover():
    """Replace VoiceoverScene.voiceover with a no-op context manager.

    The scene calls self.voiceover(text=...) inside construct(); without
    stubbing, this synthesizes TTS audio for every block (slow + needs
    network / API key). The stubbed tracker returns 0-duration so any
    `run_time=tracker.duration` animations complete instantly.

    A scene builds its speech service (via _style.speech_service()) before
    set_speech_service is even called, so an openai-voiced project would fail
    construction here on the missing voice.name / API key -- even though this
    static geometric lint never synthesizes a single word. Force the free
    gtts path (unless the caller already pinned AGEATION_TTS) so lint_scene
    runs on any project regardless of its final voice config.
    """
    os.environ.setdefault("AGEATION_TTS", "gtts")
    from contextlib import contextmanager
    try:
        from manim_voiceover import VoiceoverScene
    except ImportError:
        return  # not a voiceover project; nothing to stub

    class _FakeTracker:
        duration = 0.001  # near-zero; play() still advances mobjects to target

        def time_until_bookmark(self, mark):
            return 0

    @contextmanager
    def _fake_voiceover(self, text=None, ssml=None, **kwargs):
        yield _FakeTracker()

    VoiceoverScene.voiceover = _fake_voiceover
    VoiceoverScene.set_speech_service = lambda *a, **kw: None


def _configure_manim_for_lint():
    """Tell manim not to write any output. Lower frame_rate so each play()
    iterates as few frames as possible — we only need the post-play steady
    state, not the frames in between."""
    from manim import config
    config.write_to_movie = False
    config.disable_caching = True
    config.format = None
    config.preview = False
    config.frame_rate = 1
    config.verbosity = "ERROR"


def _load_scene_module(path: str):
    """Import the scene's .py file as a module without polluting sys.modules."""
    if not os.path.exists(path):
        raise SystemExit(f"scene file not found: {path}")
    name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def capture(scene_path: str, scene_class: str) -> list[dict]:
    """Run the scene's construct() and snapshot mobjects after every play()."""
    _configure_manim_for_lint()
    _stub_voiceover()

    from manim import Scene
    real_play = Scene.play
    real_wait = Scene.wait

    snapshots: list[dict] = []

    def patched_play(self, *animations, **kwargs):
        result = real_play(self, *animations, **kwargs)
        snapshots.append(_snapshot_scene(self, len(snapshots)))
        return result

    def patched_wait(self, *args, **kwargs):
        # Skip waits entirely — they're pure pauses and not relevant to layout.
        return None

    Scene.play = patched_play
    Scene.wait = patched_wait

    try:
        mod = _load_scene_module(scene_path)
        cls = getattr(mod, scene_class, None)
        if cls is None:
            raise SystemExit(
                f"scene class {scene_class!r} not found in {scene_path}")
        cls().render()
    finally:
        Scene.play = real_play
        Scene.wait = real_wait

    return snapshots


# --- Snapshot construction --------------------------------------------------

def _snapshot_scene(scene, index: int) -> dict:
    """Walk scene.mobjects -> atomic leaves, record bboxes."""
    entries: list[Entry] = []
    for i, root in enumerate(scene.mobjects):
        path = f"{type(root).__name__}[{i}]"
        _walk(root, path, entries)
    return {"index": index, "entries": entries}


def _walk(m, path: str, entries: list[Entry], inherited: tuple = ()):
    cls = type(m).__name__
    own = getattr(m, "_lint_overlap_marks", None)
    marks = inherited
    if own:
        merged = dict(inherited)
        merged.update(own)
        marks = tuple(merged.items())
    if cls in ATOMIC_TYPES or not getattr(m, "submobjects", None):
        if not _is_visible(m) or not _has_extent(m):
            return
        try:
            bmin, bmax = _bbox(m)
        except Exception:
            return
        ends = None
        if cls in GRAPH_LINE_TYPES:
            try:
                s, e = m.get_start(), m.get_end()
                ends = ((float(s[0]), float(s[1])), (float(e[0]), float(e[1])))
            except Exception:
                pass
        entries.append(Entry(path=path, cls=cls, bmin=bmin, bmax=bmax,
                             marks=marks, ends=ends))
    else:
        for j, child in enumerate(m.submobjects):
            child_path = f"{path}.{type(child).__name__}[{j}]"
            _walk(child, child_path, entries, marks)


def _is_visible(m) -> bool:
    """Conservative: True unless we can prove fill + stroke are both 0."""
    fo = so = None
    try:
        fo = m.get_fill_opacity()
    except Exception:
        pass
    try:
        so = m.get_stroke_opacity()
    except Exception:
        pass
    if fo == 0 and so == 0:
        return False
    return True


def _has_extent(m) -> bool:
    try:
        return float(m.width) > 0 or float(m.height) > 0
    except Exception:
        return False


def _bbox(m) -> tuple[tuple, tuple]:
    from manim import DL, UR
    bmin = tuple(float(x) for x in m.get_corner(DL))
    bmax = tuple(float(x) for x in m.get_corner(UR))
    return bmin, bmax


# --- Overlap detection ------------------------------------------------------

def overlaps(a: Entry, b: Entry, tol: float) -> bool:
    """True if 2D bboxes overlap after shrinking each by tol."""
    ax0, ay0 = a.bmin[0] + tol, a.bmin[1] + tol
    ax1, ay1 = a.bmax[0] - tol, a.bmax[1] - tol
    bx0, by0 = b.bmin[0] + tol, b.bmin[1] + tol
    bx1, by1 = b.bmax[0] - tol, b.bmax[1] - tol
    return ax0 < bx1 and bx0 < ax1 and ay0 < by1 and by0 < ay1


def overlap_amount(a: Entry, b: Entry) -> float:
    """Min of the X and Y overlap extents; 0 if disjoint."""
    ox = min(a.bmax[0], b.bmax[0]) - max(a.bmin[0], b.bmin[0])
    oy = min(a.bmax[1], b.bmax[1]) - max(a.bmin[1], b.bmin[1])
    return min(ox, oy) if ox > 0 and oy > 0 else 0.0


def bbox_gap(a: Entry, b: Entry) -> float:
    """Euclidean gap between non-overlapping 2D bboxes."""
    dx = max(0.0, a.bmin[0] - b.bmax[0], b.bmin[0] - a.bmax[0])
    dy = max(0.0, a.bmin[1] - b.bmax[1], b.bmin[1] - a.bmax[1])
    return (dx * dx + dy * dy) ** 0.5


def is_ancestor_path(p_ancestor: str, p_child: str) -> bool:
    """True if p_ancestor is a strict prefix of p_child in the dotted chain."""
    return p_child.startswith(p_ancestor + ".")


# Container shapes whose interior is, by convention, meant to hold things.
# A Text sitting inside its Rectangle box, or a ParametricFunction plotted
# inside its Axes, is intentional — don't flag.
CONTAINER_TYPES = {
    "Rectangle", "RoundedRectangle", "Square", "Circle", "Ellipse",
    "Polygon", "RegularPolygon", "Triangle", "Star",
    "Axes", "NumberLine", "NumberPlane",
    "Table", "MobjectTable", "BarChart",
    "SurroundingRectangle", "BackgroundRectangle",
}

# Line-like types whose endpoints commonly attach to graph nodes (Dots/rings).
# A bushy tree edge whose corner lands on a dot or ring center is intentional.
GRAPH_LINE_TYPES = {"Line", "Arrow", "DashedLine", "CurvedArrow",
                    "DoubleArrow", "Vector", "TangentLine", "Elbow"}
GRAPH_NODE_TYPES = {"Dot", "Circle"}


def _bbox_contains(outer: Entry, inner: Entry, slack: float = 0.05) -> bool:
    """True if outer's bbox fully covers inner's, with a small slack."""
    return (outer.bmin[0] - slack <= inner.bmin[0]
            and outer.bmax[0] + slack >= inner.bmax[0]
            and outer.bmin[1] - slack <= inner.bmin[1]
            and outer.bmax[1] + slack >= inner.bmax[1])


def _is_container_pattern(a: Entry, b: Entry) -> bool:
    """A 'label inside container' overlap; intentional by design."""
    if a.cls in CONTAINER_TYPES and _bbox_contains(a, b):
        return True
    if b.cls in CONTAINER_TYPES and _bbox_contains(b, a):
        return True
    return False


def _is_graph_connection(a: Entry, b: Entry, threshold: float = 0.08) -> bool:
    """True if a Line/Arrow endpoint sits at/inside a graph-node (Dot or ring).

    Two patterns count as a connection:
    (1) line bbox-corner within `threshold` of the node's center, OR
    (2) line bbox-corner anywhere inside the node's bbox (handles rings,
        whose bbox is larger than the dot they wrap).

    Either way the edge endpoint is meeting the node by construction, so the
    inevitable bbox-intersection isn't a layout bug.
    """
    if a.cls in GRAPH_LINE_TYPES and b.cls in GRAPH_NODE_TYPES:
        line, node = a, b
    elif b.cls in GRAPH_LINE_TYPES and a.cls in GRAPH_NODE_TYPES:
        line, node = b, a
    else:
        return False
    nx = (node.bmin[0] + node.bmax[0]) / 2
    ny = (node.bmin[1] + node.bmax[1]) / 2
    for cx, cy in _line_endpoints(line):
        if ((cx - nx) ** 2 + (cy - ny) ** 2) ** 0.5 <= threshold:
            return True
        if (node.bmin[0] <= cx <= node.bmax[0]
                and node.bmin[1] <= cy <= node.bmax[1]):
            return True
    return False


def _line_endpoints(line: Entry) -> tuple:
    """The line's real endpoints when captured, else its bbox corners.

    Straight lines' endpoints coincide with bbox corners, but a CurvedArrow's
    do not -- the real ends are what actually anchor to a node/container.
    """
    if line.ends is not None:
        return line.ends
    return (
        (line.bmin[0], line.bmin[1]), (line.bmax[0], line.bmin[1]),
        (line.bmin[0], line.bmax[1]), (line.bmax[0], line.bmax[1]),
    )


def _is_line_into_container(a: Entry, b: Entry) -> bool:
    """True if a line-like mobject's endpoint lands inside a container shape.

    An arrow anchored to something inside an Ellipse/box (the dominant class
    of hand-allowlisted false positives in practice: arrows out of an
    omega_box, arrows into a Venn region) necessarily bbox-intersects the
    container. A line merely passing *through* keeps both bbox corners
    outside and is still flagged.
    """
    if a.cls in GRAPH_LINE_TYPES and b.cls in CONTAINER_TYPES:
        line, cont = a, b
    elif b.cls in GRAPH_LINE_TYPES and a.cls in CONTAINER_TYPES:
        line, cont = b, a
    else:
        return False
    slack = 0.08  # an arrow ending just at a container's edge still connects
    for cx, cy in _line_endpoints(line):
        if (cont.bmin[0] - slack <= cx <= cont.bmax[0] + slack
                and cont.bmin[1] - slack <= cy <= cont.bmax[1] + slack):
            return True
    return False


def _both_inside_same_container(a: Entry, b: Entry,
                                entries: list[Entry]) -> bool:
    """True if some other entry is a container that holds both a and b.

    Catches: two ParametricFunction plotted on the same Axes; two Text
    siblings inside the same card Rectangle; a DashedLine guide drawn on
    top of an Axes that already contains the curve. The container's
    presence in the scene is the user's declaration of intent."""
    for c in entries:
        if c is a or c is b:
            continue
        if c.cls not in CONTAINER_TYPES:
            continue
        if _bbox_contains(c, a) and _bbox_contains(c, b):
            return True
    return False


def _shared_mark_reason(a: Entry, b: Entry) -> str | None:
    """The reason string of a mark both entries carry, or None."""
    tokens_b = {t for t, _ in b.marks}
    for token, reason in a.marks:
        if token in tokens_b:
            return reason or "(no reason given)"
    return None


def violations(snap: dict, tol: float, buffer: float) -> tuple[list, list]:
    """(violations, suppressed) for this snapshot.

    violations: (snap_idx, a, b, kind, magnitude) tuples.
    suppressed: (snap_idx, a, b, reason) tuples -- overlapping pairs skipped
    because both carry the same mark_intended_overlap mark (declared intent
    stays auditable via --verbose).
    """
    out, suppressed = [], []
    es = snap["entries"]
    for i, a in enumerate(es):
        for b in es[i + 1:]:
            if (is_ancestor_path(a.path, b.path)
                    or is_ancestor_path(b.path, a.path)):
                continue
            reason = _shared_mark_reason(a, b)
            if reason is not None:
                if overlaps(a, b, tol):
                    suppressed.append((snap["index"], a, b, reason))
                continue
            if (_is_container_pattern(a, b)
                    or _is_graph_connection(a, b)
                    or _is_line_into_container(a, b)
                    or _both_inside_same_container(a, b, es)):
                continue
            if overlaps(a, b, tol):
                out.append((snap["index"], a, b, "overlap", overlap_amount(a, b)))
            elif buffer > 0:
                gap = bbox_gap(a, b)
                if 0 < gap < buffer:
                    out.append((snap["index"], a, b, "near-miss", gap))
    return out, suppressed


# --- Allowlist sidecar ------------------------------------------------------

def load_allow(scene_path: str) -> list[tuple]:
    """Load <scene>.lint-allow.yaml. Returns [(snap_or_*, frozenset(paths))]."""
    allow_path = scene_path.rsplit(".py", 1)[0] + ".lint-allow.yaml"
    if not os.path.exists(allow_path):
        return []
    data = yaml.safe_load(open(allow_path)) or {}
    out = []
    for entry in data.get("ignore") or []:
        snap = entry.get("snapshot", "*")
        a = entry.get("a", "")
        b = entry.get("b", "")
        out.append((snap, frozenset({a, b})))
    return out


def is_allowed(v: tuple, allow: list[tuple]) -> bool:
    snap_idx, a, b, _kind, _mag = v
    key = frozenset({a.path, b.path})
    for snap, pair in allow:
        if (snap == "*" or snap == snap_idx) and pair == key:
            return True
    return False


# --- Report -----------------------------------------------------------------

def report(label: str, scene_class: str, snapshots: list[dict],
           allow: list[tuple], tol: float, buffer: float,
           verbose: bool = False) -> int:
    print(f"\n{label} : {scene_class}")
    total = suppressed_total = 0
    for snap in snapshots:
        found, suppressed = violations(snap, tol, buffer)
        for v in found:
            if is_allowed(v, allow):
                continue
            snap_idx, a, b, kind, mag = v
            color = RED if kind == "overlap" else YELLOW
            print(f"  snapshot {snap_idx:3d}  "
                  f"{color}{a.path}{RESET}  <->  "
                  f"{color}{b.path}{RESET}  "
                  f"{DIM}({kind} {mag:.2f}u){RESET}")
            total += 1
        suppressed_total += len(suppressed)
        if verbose:
            for snap_idx, a, b, reason in suppressed:
                print(f"  snapshot {snap_idx:3d}  {DIM}{a.path}  <->  "
                      f"{b.path}  (intended: {reason}){RESET}")
    color = RED if total else GREEN
    marked = (f", {suppressed_total} declared-intent overlap(s)"
              if suppressed_total else "")
    print(f"  {len(snapshots)} snapshots, "
          f"{color}{total}{RESET} unallowed violation(s){marked}.")
    return total


# --- CLI --------------------------------------------------------------------

def parse_args():
    p = project_parser(__doc__)
    p.add_argument("--chapter", help="lint only this chapter slug")
    p.add_argument("--scene-file",
                   help="scene .py path; with --scene-class, skips project.yaml")
    p.add_argument("--scene-class",
                   help="scene class name; used with --scene-file")
    p.add_argument("--tol", type=float, default=DEFAULT_TOL,
                   help=f"scene-unit shrink epsilon (default {DEFAULT_TOL})")
    p.add_argument("--buffer", type=float, default=NEAR_MISS_BUFFER,
                   help=f"near-miss buffer in scene units; 0 disables "
                        f"(default {NEAR_MISS_BUFFER})")
    p.add_argument("--verbose", action="store_true",
                   help="also list overlaps suppressed by mark_intended_overlap")
    return p.parse_args()


def main():
    args = parse_args()
    root = resolve_project(args.project)
    manifest = load_project(root)
    targets = pick_targets(root, manifest, args)
    if not targets:
        print("No scenes to lint. Either project.yaml has no chapter with a "
              "script's target_scene_file, or pass --scene-file + --scene-class.")
        sys.exit(0)

    fails = 0
    for label, scene_path, scene_class in targets:
        try:
            snaps = capture(scene_path, scene_class)
        except SystemExit:
            raise
        except Exception as exc:
            print(f"\n{label} : {scene_class}\n  {RED}ERROR{RESET}: "
                  f"{type(exc).__name__}: {exc}")
            fails += 1
            continue
        allow = load_allow(scene_path)
        fails += report(label, scene_class, snaps, allow, args.tol,
                        args.buffer, verbose=args.verbose)

    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
