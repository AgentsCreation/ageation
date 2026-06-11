from check_sync import worst, header_field, scene_status, OK, STALE, NOPROV, MISSING, NA


def test_worst_picks_most_severe():
    assert worst(OK, STALE) == STALE
    assert worst(OK, OK) == OK
    assert worst(NA, OK) == OK
    assert worst(MISSING, STALE, OK) == MISSING
    assert worst(NOPROV, STALE) == NOPROV


def test_header_field_reads_percent_and_html_styles(tmp_path):
    tex = tmp_path / "a.tex"
    tex.write_text("% upstream: input/X.tex\n% upstream_sha256: abc123\nbody")
    assert header_field(str(tex), "upstream") == "input/X.tex"
    assert header_field(str(tex), "upstream_sha256") == "abc123"

    md = tmp_path / "a.md"
    md.write_text("<!-- upstream: input/X.md -->\n<!-- upstream_sha256: def456 -->\nbody")
    assert header_field(str(md), "upstream") == "input/X.md"
    assert header_field(str(md), "upstream_sha256") == "def456"
    assert header_field(str(md), "nope") is None


def test_scene_status_states(tmp_path):
    script = tmp_path / "content" / "1-x-script.md"
    script.parent.mkdir()
    script.write_text("narration")
    scenes = tmp_path / "scenes"
    scenes.mkdir()

    # no target declared
    assert scene_status(str(tmp_path), "slug: 1-x", str(script)) == "no-target"

    fm = "target_scene_file: scenes/x.py"
    # target declared, scene not built yet
    assert scene_status(str(tmp_path), fm, str(script)) == "no-scene"

    scene = scenes / "x.py"
    # built scene without any provenance marker -> violation
    scene.write_text("from manim import *\n")
    assert scene_status(str(tmp_path), fm, str(script)) == "unstamped"

    # legacy marker -> tolerated
    scene.write_text("# derived_from: legacy (hand-built)\nfrom manim import *\n")
    assert scene_status(str(tmp_path), fm, str(script)) == "legacy"

    # real marker with wrong hash -> stale
    scene.write_text("# derived_from: content/1-x-script.md\n"
                     "# derived_from_sha256: 0000\nfrom manim import *\n")
    assert scene_status(str(tmp_path), fm, str(script)) == STALE

    # real marker with the right hash -> in sync
    import hashlib
    sha = hashlib.sha256(script.read_bytes()).hexdigest()
    scene.write_text("# derived_from: content/1-x-script.md\n"
                     f"# derived_from_sha256: {sha}\nfrom manim import *\n")
    assert scene_status(str(tmp_path), fm, str(script)) == OK
