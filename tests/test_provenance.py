import subprocess

import yaml

import provenance
import stamp_provenance
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


# --- engine-version resolution (tag-or-hash) ---------------------------------

def _run(cwd, *args):
    subprocess.run(args, cwd=str(cwd), check=True, capture_output=True, text=True)


def _init_repo(path):
    _run(path, "git", "init", "-q")
    _run(path, "git", "config", "user.email", "t@example.com")
    _run(path, "git", "config", "user.name", "Tester")
    (path / "pyproject.toml").write_text('[project]\nname = "x"\nversion = "9.9.9"\n')
    _run(path, "git", "add", "-A")
    _run(path, "git", "commit", "-qm", "init")


def test_framework_version_degrades_to_hash_without_tag(tmp_path):
    _init_repo(tmp_path)
    v = provenance.framework_version(str(tmp_path))
    assert v != "unavailable"
    assert "-dirty" not in v
    int(v, 16)  # a bare abbreviated commit hash


def test_framework_version_prefers_a_reachable_tag(tmp_path):
    _init_repo(tmp_path)
    _run(tmp_path, "git", "tag", "v1.2.3")
    assert provenance.framework_version(str(tmp_path)) == "v1.2.3"


def test_framework_version_flags_dirty_tree(tmp_path):
    _init_repo(tmp_path)
    _run(tmp_path, "git", "tag", "v1.2.3")
    (tmp_path / "pyproject.toml").write_text("mutated\n")
    assert provenance.framework_version(str(tmp_path)) == "v1.2.3-dirty"


def test_framework_version_ignores_env_files_for_dirtiness(tmp_path):
    _init_repo(tmp_path)
    _run(tmp_path, "git", "tag", "v1.2.3")
    (tmp_path / ".env").write_text("SECRET=1\n")  # untracked + excluded
    assert provenance.framework_version(str(tmp_path)) == "v1.2.3"


def test_framework_provenance_reads_package_version_and_commit(tmp_path):
    _init_repo(tmp_path)
    prov = provenance.framework_provenance(str(tmp_path))
    assert prov["package_version"] == "9.9.9"
    assert prov["dirty"] is False
    int(prov["commit"], 16)


def test_framework_version_unavailable_outside_git(tmp_path):
    assert provenance.framework_version(str(tmp_path)) == "unavailable"


def test_write_build_yaml_is_parseable_and_stringifies_the_date(tmp_path):
    path, prov = stamp_provenance.write_build_yaml(str(tmp_path), "2026-07-09")
    data = yaml.safe_load(open(path))
    assert data["built"] == "2026-07-09"  # a string, not a datetime.date
    assert set(data["engine"]) == {"version", "commit", "package_version", "dirty"}
    assert data["engine"]["version"] == prov["version"]
    assert isinstance(data["engine"]["dirty"], bool)
