"""scaffold.py: deterministic layer stubs that keep provenance green."""

import os
import py_compile

import pytest
import yaml

from provenance import split_fm, sha256_script
from check_sync import scene_status, OK
from scaffold import (scaffold_concept, scaffold_script, scaffold_scene,
                      beat_narrations, class_name_for)
from vendor_sources import resolve_upstream

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


def test_concept_without_source_or_upstream_errors(project):
    with pytest.raises(SystemExit, match="upstream"):
        scaffold_concept(str(project), MANIFEST, "3-maps", force=False)


def test_concept_vendors_on_demand(project):
    # A chapter added to an established project has no vendored copy yet;
    # the concept scaffold vendors it (with companion) from `upstream:`.
    (project / "input").mkdir()
    (project / "input" / "maps.tex").write_text("\\section{Maps}\nbody\n")
    (project / "input" / "maps.md").write_text("sidecar\n")
    manifest = {
        "project": MANIFEST["project"],
        "chapters": [{"slug": "3-maps", "title": "Maps",
                      "upstream": "input/maps.tex"}],
    }
    out = scaffold_concept(str(project), manifest, "3-maps", force=False)
    assert (project / "sources" / "3-maps.tex").exists()
    assert (project / "sources" / "3-maps.md").exists()   # companion sibling
    vendored = (project / "sources" / "3-maps.tex").read_text()
    assert "upstream_sha256" in vendored                  # provenance header
    fm_text, _ = split_fm(open(out).read())
    assert "upstream: input/maps.tex" in fm_text
    assert "companion: sources/3-maps.md" in fm_text


def test_resolve_upstream_joins_bare_name_under_dir():
    assert resolve_upstream("1Intro.tex", "notes") == os.path.join("notes", "1Intro.tex")
    assert resolve_upstream("input/x.tex", "notes") == "input/x.tex"   # already qualified
    assert resolve_upstream("x.tex", None) == "x.tex"                  # no upstream_dir
    assert resolve_upstream("/abs/x.tex", "notes") == "/abs/x.tex"     # absolute wins


def test_concept_vendors_on_demand_with_upstream_dir(project):
    # Embedded posture (the supported bootstrap path): project.yaml records a
    # BARE upstream filename and keeps the directory in project.upstream_dir.
    # The on-demand vendor must join them (REVIEW.md finding 2), and the colon
    # title must survive into the front matter (finding 1).
    (project / "notes").mkdir()
    (project / "notes" / "1Intro.tex").write_text("\\section{Intro}\nbody\n")
    (project / "notes" / "1Intro.md").write_text("sidecar\n")
    manifest = {
        "project": {**MANIFEST["project"], "upstream_dir": "notes"},
        "chapters": [{"slug": "1-intro",
                      "title": "Graphical Models: A Quick Tour",
                      "upstream": "1Intro.tex"}],
    }
    out = scaffold_concept(str(project), manifest, "1-intro", force=False)
    assert (project / "sources" / "1-intro.tex").exists()
    assert (project / "sources" / "1-intro.md").exists()   # companion via upstream_dir sibling
    fm = yaml.safe_load(split_fm(open(out).read())[0])     # colon title must parse
    assert fm["title"] == "Graphical Models: A Quick Tour"
    assert fm["upstream"] == "1Intro.tex"


def test_concept_scaffold_bootstrap_creates_dirs(tmp_path):
    # The supported bootstrap (init without --scaffold-concepts) leaves no
    # sources/ or content/ dir. A first standalone concept scaffold must
    # create them rather than crash writing into a missing directory.
    (tmp_path / "notes").mkdir()
    (tmp_path / "notes" / "1Intro.tex").write_text("\\section{Intro}\nbody\n")
    manifest = {
        "project": {**MANIFEST["project"], "upstream_dir": "notes"},
        "chapters": [{"slug": "1-intro", "title": "Intro", "upstream": "1Intro.tex"}],
    }
    out = scaffold_concept(str(tmp_path), manifest, "1-intro", force=False)
    assert os.path.exists(out)
    assert (tmp_path / "sources" / "1-intro.tex").exists()


def test_concept_on_demand_missing_upstream_errors(project):
    # A bare upstream that resolves to nothing should fail loudly, not blow up
    # later hashing a source file that was never written.
    manifest = {
        "project": {**MANIFEST["project"], "upstream_dir": "notes"},
        "chapters": [{"slug": "1-intro", "title": "Intro", "upstream": "nope.tex"}],
    }
    with pytest.raises(SystemExit, match="upstream not found"):
        scaffold_concept(str(project), manifest, "1-intro", force=False)


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
