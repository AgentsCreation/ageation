from provenance import split_fm, rebuild, fm_get, fm_upsert, sha256_file, sha256_script


FM = """slug: 5-discrete
title: "Discrete RVs"
source: sources/5-discrete.tex
nested:
  source: should-not-match"""

DOC = "---\n" + FM + "\n---\nBody text.\n"


def test_split_and_rebuild_roundtrip():
    fm, body = split_fm(DOC)
    assert fm == FM
    assert body == "Body text.\n"
    assert rebuild(fm, body) == DOC


def test_split_fm_without_front_matter():
    fm, body = split_fm("just text")
    assert fm is None
    assert body == "just text"


def test_fm_get_strips_quotes_and_ignores_nested_keys():
    assert fm_get(FM, "title") == "Discrete RVs"
    assert fm_get(FM, "source") == "sources/5-discrete.tex"
    assert fm_get(FM, "missing") is None


def test_fm_upsert_replaces_in_place():
    out = fm_upsert(FM, "source", "sources/new.tex")
    assert fm_get(out, "source") == "sources/new.tex"
    assert out.count("source:") == FM.count("source:")


def test_fm_upsert_inserts_after_anchor():
    out = fm_upsert(FM, "upstream", "input/X.tex", after="source")
    lines = out.splitlines()
    i = lines.index("source: sources/5-discrete.tex")
    assert lines[i + 1] == "upstream: input/X.tex"


def test_fm_upsert_appends_without_anchor():
    out = fm_upsert(FM, "extra", "1")
    assert out.rstrip().endswith("extra: 1")


SCRIPT = """---
target_runtime_sec: 360
measured_runtime_sec: null
beats:
  - id: a
    scene_class: A
    est_sec: 23
    measured_sec: null
---
narration
"""


def test_sha256_script_ignores_measured_lines(tmp_path):
    p = tmp_path / "s.md"
    p.write_text(SCRIPT)
    before = sha256_script(str(p))
    p.write_text(SCRIPT.replace("measured_runtime_sec: null",
                                "measured_runtime_sec: 361.4  # 2026-07-03")
                       .replace("measured_sec: null", "measured_sec: 23.1"))
    assert sha256_script(str(p)) == before
    # and they differ as whole files, proving the normalization did the work
    assert sha256_file(str(p)) != before


def test_sha256_script_sees_real_edits(tmp_path):
    p = tmp_path / "s.md"
    p.write_text(SCRIPT)
    before = sha256_script(str(p))
    p.write_text(SCRIPT.replace("narration", "rewritten narration"))
    assert sha256_script(str(p)) != before


def test_sha256_script_matches_file_hash_without_measured_lines(tmp_path):
    p = tmp_path / "s.md"
    p.write_text("---\nslug: x\n---\nbody\n")
    assert sha256_script(str(p)) == sha256_file(str(p))
