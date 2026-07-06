"""doctor.py: the OpenAI-key preflight must be quality-aware.

A 480p draft forces the free gtts voice (render.py), so it needs no key even
when the project is configured to openai for finals (REVIEW.md finding 3). The
effective provider mirrors _style.speech_service's resolution order.
"""

from doctor import effective_tts_provider


def test_draft_forces_free_voice(monkeypatch):
    monkeypatch.delenv("AGEATION_TTS", raising=False)
    provider, why = effective_tts_provider("l", "openai")
    assert provider == "gtts"
    assert "draft" in why


def test_final_uses_configured_provider(monkeypatch):
    monkeypatch.delenv("AGEATION_TTS", raising=False)
    provider, _ = effective_tts_provider("h", "openai")
    assert provider == "openai"


def test_env_override_wins_even_for_finals(monkeypatch):
    monkeypatch.setenv("AGEATION_TTS", "GTTS")   # case/space tolerant
    provider, _ = effective_tts_provider("h", "openai")
    assert provider == "gtts"


def test_env_override_can_force_openai_on_a_draft(monkeypatch):
    monkeypatch.setenv("AGEATION_TTS", "openai")
    provider, _ = effective_tts_provider("l", "gtts")
    assert provider == "openai"
