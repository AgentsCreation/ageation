"""scaffold.py: deterministic layer stubs that keep provenance green."""

import py_compile

import pytest
import yaml

from provenance import split_fm, sha256_script
from check_sync import scene_status, OK
from scaffold import (scaffold_concept, scaffold_script, scaffold_scene,
                      beat_narrations, class_name_for)

MANIFEST = {
    "project": {
        "title": "Demo",
        "shape": "course",
        "voice": {"provider": "openai", "name": "nova", "rate": 1.0},
        "pedagogy": {"target_minutes_per_video": 6},
    },
    "chapters": [
        {"slug": "1-intro", "title": "Introduction", "status": "planned"},
        {"slug": "2-sets", "title": "Sets", "status": "planned",
         "prereqs": ["1-intro"]},
        {"slug": "3-maps", "title": "Maps", "status": "planned"},
    ],
}


@pytest.fixture
def project(tmp_path):
    (tmp_path / "sources").mkdir()
    (tmp_path / "content").mkdir()
    (tmp_path / "sources" / "2-sets.tex").write_text(
        "\\section{What is a set}\n\\section{Operations}\nbody\n")
    return tmp_path


def test_concept_scaffold(project):
    out = scaffold_concept(str(project), MANIFEST, "2-sets", force=False)
    text = open(out).read()
    fm_text, body = split_fm(text)
    assert "source: sources/2-sets.tex" in fm_text
    assert "source_sha256: " in fm_text
    assert "status: draft" in fm_text
    assert "- 1-intro" in fm_text            # prereqs carried over
    assert "What is a set" in body           # tex outline aid
    assert "## Deliberately out of scope" in body
    with pytest.raises(SystemExit):
        scaffold_concept(str(project), MANIFEST, "2-sets", force=False)


def test_concept_requires_vendored_source(project):
    with pytest.raises(SystemExit, match="vendor_sources"):
        scaffold_concept(str(project), MANIFEST, "3-maps", force=False)


def write_concept(project, concepts_yaml=""):
    (project / "content" / "2-sets.md").write_text(
        "---\n"
        "slug: 2-sets\n"
        "title: Sets\n"
        "status: reviewed\n"
        "source: sources/2-sets.tex\n"
        f"{concepts_yaml}"
        "estimated_runtime_sec: 300\n"
        "---\nconcept body\n")


def test_script_scaffold(project):
    write_concept(project,
                  "concepts:\n"
                  "  - id: what-is\n    name: n\n    importance: core\n"
                  "  - id: ops\n    name: n\n    importance: core\n")
    out = scaffold_script(str(project), MANIFEST, "2-sets", force=False)
    fm_text, body = split_fm(open(out).read())
    fm = yaml.safe_load(fm_text)
    assert fm["target_scene_file"] == "scenes/sets.py"
    assert fm["target_runtime_sec"] == 300
    assert [b["id"] for b in fm["beats"]] == ["overview", "what-is", "ops"]
    assert all(b["measured_sec"] is None for b in fm["beats"])
    assert "openai" in fm["voice"]["provider"]
    # neighbour titles reach the linking block
    assert "Introduction" in fm["linking"]["recap"]
    assert "Maps" in fm["linking"]["bridge"]
    assert "## Beat: ops" in body


def test_scene_scaffold_roundtrip(project):
    write_concept(project)
    script = project / "content" / "2-sets-script.md"
    script.write_text(
        "---\n"
        "slug: 2-sets\n"
        "status: approved\n"
        "derived_from: 2-sets.md\n"
        "target_scene_file: scenes/sets.py\n"
        "linking:\n"
        "  objective: Know sets.\n"
        "  key_idea: Sets collect things.\n"
        "beats:\n"
        "  - id: overview\n    scene_class: ChapterOverview\n    measured_sec: null\n"
        "  - id: ops\n    scene_class: Operations\n    measured_sec: null\n"
        "---\n"
        "## Beat: overview  (scene: ChapterOverview)\n\n"
        "> First sentence. <bookmark mark=\"a\"/> Second sentence.\n\n"
        "## Beat: ops  (scene: Operations)\n\n"
        "> Only sentence.\n")
    out = scaffold_scene(str(project), MANIFEST, "2-sets", force=False)
    text = open(out).read()
    # provenance header matches the volatile-normalized script hash
    assert f"# derived_from_sha256: {sha256_script(str(script))}" in text
    assert "class ChapterOverview(VoiceoverScene)" in text
    assert "class Operations(VoiceoverScene)" in text
    # bookmark split -> two sequential voiceover blocks in the first beat
    assert text.count("        with self.voiceover(") == 3
    assert "'First sentence.'" in text and "'Second sentence.'" in text
    assert "intro_card(" in text and "outro_bridge(" in text
    py_compile.compile(out, doraise=True)
    # the scaffolded scene is already in-sync with its script
    assert scene_status(str(project), "target_scene_file: scenes/sets.py",
                        str(script)) == OK


def test_beat_narrations_split():
    body = ('## Beat: x  (scene: X)\n\n'
            '> One. <bookmark mark="m"/> Two.\n> Three.\n\nAnimation cues\n')
    chunks = beat_narrations(body)
    assert chunks == {"x": ["One.", "Two. Three."]}


def test_class_name_for():
    assert class_name_for("rv-mapping") == "RvMapping"
    assert class_name_for("overview") == "Overview"
