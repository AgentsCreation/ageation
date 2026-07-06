import yaml

from init_project import (slugify, title_from_tex, sort_key, detect_collisions,
                          write_manifest)
from _project import yaml_scalar, shape_defaults


def test_slugify_numeric_prefix_and_camel_case():
    assert slugify("5Discrete_Random_Variables") == "05-discrete-random-variables"
    assert slugify("10Expectations_and_Bounds") == "10-expectations-and-bounds"
    assert slugify("LinearAlgebra") == "linear-algebra"
    assert slugify("Intro") == "intro"
    assert slugify("1 Mathematical Review") == "01-mathematical-review"


def test_sort_key_orders_numeric_prefixes_numerically():
    names = ["10Foo.tex", "2Bar.tex", "1Baz.tex", "Appendix.tex"]
    assert sorted(names, key=sort_key) == [
        "1Baz.tex", "2Bar.tex", "10Foo.tex", "Appendix.tex"]


def test_title_from_tex_prefers_section_then_filename(tmp_path):
    tex = tmp_path / "3Basic_Concepts.tex"
    tex.write_text(r"\section{Basic Concepts of Probability}" + "\nbody")
    assert title_from_tex(str(tex), "3Basic_Concepts") == "Basic Concepts of Probability"
    bare = tmp_path / "4Some_Topic.tex"
    bare.write_text("no headings here")
    assert title_from_tex(str(bare), "4Some_Topic") == "Some Topic"


def test_detect_collisions_flags_duplicate_slugs_and_scene_files():
    chapters = [
        {"slug": "1-intro", "title": "A", "upstream": "1Intro.tex",
         "companion": None, "prereq": None},
        {"slug": "1-intro", "title": "B", "upstream": "1_intro.tex",
         "companion": None, "prereq": None},
    ]
    problems = detect_collisions(chapters)
    assert any("duplicate slug" in p for p in problems)

    chapters = [
        {"slug": "1-foo", "title": "A", "upstream": "1Foo.tex",
         "companion": None, "prereq": None},
        {"slug": "2-foo", "title": "B", "upstream": "2Foo.tex",
         "companion": None, "prereq": None},
    ]
    problems = detect_collisions(chapters)
    assert any("scene-file collision" in p for p in problems)


def test_detect_collisions_clean():
    chapters = [
        {"slug": "1-foo", "title": "A", "upstream": "1Foo.tex",
         "companion": None, "prereq": None},
        {"slug": "2-bar", "title": "B", "upstream": "2Bar.tex",
         "companion": None, "prereq": None},
    ]
    assert detect_collisions(chapters) == []


def test_yaml_scalar_quotes_only_when_needed():
    # Safe strings pass through unquoted (readable generated files)...
    assert yaml_scalar("Introduction") == "Introduction"
    assert yaml_scalar("05-discrete-random-variables") == "05-discrete-random-variables"
    # ...the risky ones get quoted so they still round-trip through safe_load.
    for value in ["Graphical Models: A Quick Tour", "true", "123", "yes",
                  "- leading dash", "it's a wrap: really", "", "#hash"]:
        loaded = yaml.safe_load(f"key: {yaml_scalar(value)}")
        assert loaded == {"key": value}, value


def test_write_manifest_survives_colon_titles(tmp_path):
    # A perfectly ordinary article/chapter title with a colon used to emit
    # invalid YAML that yaml.safe_load choked on (REVIEW.md finding 1).
    chapters = [
        {"slug": "01-intro", "title": "Graphical Models: A Quick Tour",
         "upstream": "1Intro.tex", "companion": "1Intro.md", "prereq": None},
    ]
    out = tmp_path / "project.yaml"
    write_manifest(str(out), "input/Demo", "course",
                   "My Course: Volume 1", 6, shape_defaults("course"), chapters)
    data = yaml.safe_load(out.read_text())   # must not raise
    assert data["project"]["title"] == "My Course: Volume 1"
    assert data["chapters"][0]["title"] == "Graphical Models: A Quick Tour"
    assert data["chapters"][0]["companion"] == "1Intro.md"
