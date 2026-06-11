from provenance import split_fm, rebuild, fm_get, fm_upsert


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
