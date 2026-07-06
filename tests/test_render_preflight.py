"""render.py draft preflight: detect a hard-coded OpenAIService in a scene.

A scene that constructs OpenAIService directly bypasses the AGEATION_TTS=gtts
draft switch and hangs the free render on an interactive key prompt; the
preflight regex is what turns that into a fast, clear failure.
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
    assert r.OPENAI_SERVICE.search(src)


def test_ignores_speech_service_call():
    r = _load()
    src = 'def make_speech_service():\n    return speech_service()\n'
    assert not r.OPENAI_SERVICE.search(src)


def test_ignores_the_word_in_a_comment_import():
    # Importing the class for a type hint / re-export is not construction.
    r = _load()
    src = "from manim_voiceover.services.openai import OpenAIService  # noqa\n"
    assert not r.OPENAI_SERVICE.search(src)
