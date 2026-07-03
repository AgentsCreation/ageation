"""lint_style: the mechanizable STYLE_BOOK rules, checked statically."""

from lint_style import check_file


def lint(tmp_path, src: str):
    p = tmp_path / "scene.py"
    p.write_text(src)
    return [(rule, line) for line, rule, _ in check_file(str(p))]


def test_newline_and_emdash_in_text(tmp_path):
    rules = [r for r, _ in lint(tmp_path,
        'Text("two\\nlines")\nText("has — emdash")\nText("clean line")\n')]
    assert rules.count("text-newline") == 1
    assert rules.count("text-emdash") == 1


def test_mathtex_is_exempt_from_text_rules(tmp_path):
    assert lint(tmp_path, 'MathTex("a — b\\nc")\n') == []


def test_raw_font_size_above_caption_flagged(tmp_path):
    findings = lint(tmp_path,
        'Text("t", font_size=40)\n'      # flagged: should use scale
        'Text("t", font_size=BODY)\n'    # constant: fine
        'MathTex("x", font_size=20)\n')  # sub-caption chart internal: fine
    assert findings == [("raw-font-size", 1)]


def test_raw_accent_colors_flagged(tmp_path):
    rules = [r for r, _ in lint(tmp_path,
        'Text("t", color=YELLOW)\n'
        'Dot(fill_color=GRAY_B)\n'
        'Text("t", color=ACCENT)\n'
        'Dot(color=RED)\n')]            # non-palette colors are allowed
    assert rules == ["raw-accent", "raw-accent"]


def test_local_helper_and_hardcoded_voice(tmp_path):
    rules = [r for r, _ in lint(tmp_path,
        "def omega_box():\n    pass\n"
        "def my_own_thing():\n    pass\n"
        "svc = OpenAIService(voice='nova')\n")]
    assert "local-helper" in rules
    assert "hardcoded-voice" in rules
    assert rules.count("local-helper") == 1


def test_clean_file_is_clean(tmp_path):
    assert lint(tmp_path,
        'title = Text("Title", font_size=TITLE, color=INK)\n'
        'svc = speech_service()\n') == []
