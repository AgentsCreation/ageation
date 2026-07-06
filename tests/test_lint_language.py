"""lint_language: video-number references, register terms, sentence budgets."""

from lint_language import check_scene, check_script


def lint_scene_src(tmp_path, src: str):
    p = tmp_path / "scene.py"
    p.write_text(src)
    return check_scene(str(p))


def lint_script_md(tmp_path, md: str):
    p = tmp_path / "x-script.md"
    p.write_text(md)
    return check_script(str(p))


def rules(findings):
    return [r for r, _, _ in findings]


def violations(findings):
    return [r for r, _, v in findings if v]


# --- video-number ----------------------------------------------------------

def test_video_number_digits_and_spelled(tmp_path):
    f = lint_scene_src(tmp_path, '\n'.join([
        'self.voiceover(text="Back in video 22 we split the stream.")',
        'self.voiceover(text="Video twenty-six proved the jump heights.")',
        'Text("video 31\'s Rayleigh energy")',
    ]))
    assert violations(f).count("video-number") == 3


def test_structural_video_forms_allowed(tmp_path):
    f = lint_scene_src(tmp_path, '\n'.join([
        'self.voiceover(text="Last video we met the CDF.")',
        'self.voiceover(text="In this video one idea stands out.")',
        'self.voiceover(text="The video that introduced CDFs proved it.")',
        'Text("Coming up: the next video")',
    ]))
    assert "video-number" not in rules(f)


def test_video_number_in_script_narration(tmp_path):
    f = lint_script_md(tmp_path, "\n".join([
        "## Beat: recap  (scene: Recap)",
        "",
        "> Back in video thirty-five the Chebyshev bound did this work.",
    ]))
    assert violations(f) == ["video-number"]


def test_cues_are_not_narration(tmp_path):
    # Only blockquote narration is linted; cue lines are authoring notes.
    f = lint_script_md(tmp_path, "\n".join([
        "## Beat: b  (scene: B)",
        "",
        "> A clean spoken line.",
        "",
        "**Cues**",
        "- `mark`: reuse the figure from video 12 here.",
    ]))
    assert f == []


def test_mathtex_text_groups_are_scanned(tmp_path):
    # Prose inside \text{...} is on-screen text; raw LaTeX is not scanned.
    f = lint_scene_src(tmp_path, '\n'.join([
        r'MathTex(r"\text{video 37\'s two Gaussians: } f_X \times f_Y")',
        r'MathTex(r"p_{X \mid S}(x) = 1")',
    ]))
    assert violations(f) == ["video-number"]


# --- terminology -------------------------------------------------------------

def test_bare_bell_flagged_bell_curve_once_allowed(tmp_path):
    f = lint_scene_src(tmp_path, '\n'.join([
        'self.voiceover(text="The bell slides to the right.")',
        'self.voiceover(text="Its density is the bell curve.")',
    ]))
    assert violations(f) == ["bare-bell"]


def test_bell_curve_refrain_flagged(tmp_path):
    f = lint_scene_src(tmp_path, '\n'.join([
        'self.voiceover(text="The bell curve appears.")',
        'self.voiceover(text="The bell curve returns.")',
    ]))
    assert violations(f) == ["bell-curve-n"]


def test_ramp_flagged_in_text_and_voice(tmp_path):
    f = lint_scene_src(tmp_path, '\n'.join([
        'Text("Ramps and hybrids")',
        'self.voiceover(text="The CDF ramps up smoothly.")',
    ]))
    assert violations(f).count("ramp") == 2


# --- length advisories -------------------------------------------------------

def test_long_block_and_sentence_are_advisories(tmp_path):
    long_sentence = "word " * 45
    f = lint_scene_src(
        tmp_path, f'self.voiceover(text="{long_sentence.strip()}.")')
    assert "long-block" in rules(f) or "long-sentence" in rules(f)
    assert violations(f) == []   # advisories never gate


def test_bookmarks_bound_script_segments(tmp_path):
    # 60 words + 60 words split by a bookmark: neither segment is long.
    seg = ("w " * 60).strip()
    f = lint_script_md(tmp_path, "\n".join([
        "## Beat: b  (scene: B)",
        "",
        f'> {seg} <bookmark mark="m"/> {seg}.',
    ]))
    assert "long-block" not in rules(f)


def test_clean_files_are_clean(tmp_path):
    assert lint_scene_src(
        tmp_path,
        'self.voiceover(text="The Gaussian density slides right.")\n'
        'Text("Smooth and hybrids")\n') == []
    assert lint_script_md(tmp_path, "\n".join([
        "## Beat: b  (scene: B)",
        "",
        "> The density is a smooth progression from zero to one.",
    ])) == []


# --- repeated-opener ---------------------------------------------------------

def _opener_project(tmp_path, openers):
    """A minimal project: a spine of chapters whose scripts open as given."""
    from lint_language import opener_findings
    (tmp_path / "content").mkdir()
    yaml_lines = ["chapters:"]
    for i, opener in enumerate(openers, start=1):
        slug = f"{i:02d}-ch{i}"
        yaml_lines.append(f"  - slug: {slug}")
        (tmp_path / "content" / f"{slug}-script.md").write_text("\n".join([
            "## Beat: overview  (scene: ChapterOverview)",
            "",
            f"> {opener}",
        ]))
    (tmp_path / "project.yaml").write_text("\n".join(yaml_lines))
    return opener_findings(str(tmp_path))


def test_consecutive_last_video_family_flagged(tmp_path):
    # "Last video" and "In the last chapter" are the SAME formula to the ear.
    f = _opener_project(tmp_path, [
        "Last video, we counted permutations.",
        "In the last chapter we built the model.",
    ])
    assert [(slug, rule) for slug, rule, _, _ in f] == \
        [("02-ch2", "repeated-opener")]
    assert all(not v for _, _, _, v in f)   # advisory, never gates


def test_alternating_openers_are_clean(tmp_path):
    f = _opener_project(tmp_path, [
        "Last video, we counted permutations.",
        "Previously, we split a set into groups.",
        "Last time we saw the axioms.",
    ])
    assert f == []


def test_identical_nonrecap_openers_flagged(tmp_path):
    f = _opener_project(tmp_path, [
        "In this video we build the model from scratch.",
        "In this video we build the law from scratch.",
    ])
    assert [slug for slug, _, _, _ in f] == ["02-ch2"]
