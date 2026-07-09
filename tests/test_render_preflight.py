"""render.py draft preflight: detect a hard-coded OpenAIService in a scene.

A scene that constructs OpenAIService directly bypasses the AGEATION_TTS=gtts
draft switch and hangs the free render on an interactive key prompt; the
preflight is what turns that into a fast, clear failure. Detection is
tokenized, not regex-matched, so a mention of the class inside a comment or
docstring never false-positives -- only a real `OpenAIService(...)` call counts.
"""

import importlib.util
import os

RENDER = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools", "render.py")


def _load():
    spec = importlib.util.spec_from_file_location("render_mod", RENDER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_flags_direct_openai_construction():
    r = _load()
    src = 'def make_speech_service():\n    return OpenAIService(voice="nova")\n'
    assert r.constructs_openai_service(src)


def test_flags_construction_with_space_before_paren():
    r = _load()
    src = "svc = OpenAIService (voice='nova')\n"  # PEP8-ugly but still a call
    assert r.constructs_openai_service(src)


def test_ignores_speech_service_call():
    r = _load()
    src = 'def make_speech_service():\n    return speech_service()\n'
    assert not r.constructs_openai_service(src)


def test_ignores_import_without_call():
    # Importing the class for a type hint / re-export is not construction.
    r = _load()
    src = "from manim_voiceover.services.openai import OpenAIService  # noqa\n"
    assert not r.constructs_openai_service(src)


def test_ignores_mention_in_docstring():
    # The exact regression: the reference scene's module docstring reads
    # "...switch make_speech_service() to OpenAIService (needs OPENAI_API_KEY)."
    # The old regex `\bOpenAIService\s*\(` matched that prose and reddened CI.
    r = _load()
    src = '"""Final: switch to OpenAIService (needs OPENAI_API_KEY)."""\n'
    assert not r.constructs_openai_service(src)


def test_ignores_mention_in_comment():
    r = _load()
    src = "return speech_service()  # not OpenAIService(...) -- voice is config\n"
    assert not r.constructs_openai_service(src)


def test_falls_back_when_untokenizable():
    # A file that won't tokenize still gets a conservative textual check.
    r = _load()
    src = "def broken(:\n    OpenAIService(\n"
    assert r.constructs_openai_service(src)
