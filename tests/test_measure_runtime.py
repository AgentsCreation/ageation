"""measure_runtime write-back + check_status tolerance enforcement."""

from measure_runtime import upsert_measured
from check_status import runtime_problem

FM = """slug: 5-x
status: approved             # human gate
target_runtime_sec: 360
tolerance_sec: 30         # build fails review if |actual - target| > tolerance
# --- Estimates vs measured -------------------------------------------------
estimated_runtime_sec: 332
measured_runtime_sec: null
beats:
  - id: overview
    scene_class: ChapterOverview
    est_sec: 23
    measured_sec: null
    sync_points: []
  - id: gallery
    scene_class: PMFGallery
    est_sec: 56
    measured_sec: null
    sync_points: [a, b]"""


def test_upsert_measured_rewrites_placeholders_only():
    out = upsert_measured(FM, {"overview": 23.4, "gallery": 57.02}, 80.42)
    assert "measured_runtime_sec: 80.4" in out
    assert "    measured_sec: 23.4" in out
    assert "    measured_sec: 57.0" in out
    assert "measured_sec: null" not in out
    # hand-written comments and untouched fields survive verbatim
    assert "# build fails review if |actual - target| > tolerance" in out
    assert "# --- Estimates vs measured" in out
    assert "est_sec: 23" in out and "sync_points: [a, b]" in out


def test_upsert_measured_is_idempotent_shape():
    once = upsert_measured(FM, {"overview": 23.4, "gallery": 57.0}, 80.4)
    twice = upsert_measured(once, {"overview": 25.0, "gallery": 57.0}, 82.0)
    assert twice.count("measured_runtime_sec:") == 1
    assert twice.count("measured_sec:") == 2
    assert "measured_sec: 25.0" in twice


def test_upsert_measured_inserts_when_placeholder_absent():
    fm = ("target_runtime_sec: 100\n"
          "beats:\n"
          "  - id: only\n"
          "    scene_class: Only\n"
          "    est_sec: 10")
    out = upsert_measured(fm, {"only": 12.3}, 12.3)
    lines = out.split("\n")
    i = lines.index("    est_sec: 10")
    assert lines[i + 1] == "    measured_sec: 12.3"
    assert "measured_runtime_sec: 12.3" in out


def test_runtime_problem_within_tolerance():
    fm = "target_runtime_sec: 360\ntolerance_sec: 30\nmeasured_runtime_sec: 380.0"
    problem, warning = runtime_problem("s", "rendered", fm)
    assert problem is None and warning is None


def test_runtime_problem_over_tolerance():
    fm = "target_runtime_sec: 360\ntolerance_sec: 30\nmeasured_runtime_sec: 401.0"
    problem, warning = runtime_problem("s", "rendered", fm)
    assert problem and "tolerance" in problem
    assert warning is None


def test_runtime_problem_unmeasured_warns_not_fails():
    fm = "target_runtime_sec: 360\ntolerance_sec: 30\nmeasured_runtime_sec: null"
    problem, warning = runtime_problem("s", "rendered", fm)
    assert problem is None
    assert warning and "make measure" in warning


def test_runtime_problem_no_contract_is_silent():
    problem, warning = runtime_problem("s", "rendered", "slug: s")
    assert problem is None and warning is None
