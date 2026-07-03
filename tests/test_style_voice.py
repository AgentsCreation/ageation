"""speech_service() config resolution (scenes/_style.py) + parse_dotenv.

These tests cover the pure decision logic: project.yaml discovery, .env key
lifting, the AGEATION_TTS override, and the no-default-voice rule. The gtts
branch constructs a real GTTSService (no network at init); the openai branch
is exercised only up to its guard so no API key is ever needed.
"""

import os
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "scenes"))

import _style  # noqa: E402
from _project import parse_dotenv  # noqa: E402  (tools/ via conftest)


def write_manifest(root, voice: dict):
    lines = ["project:", "  title: T", "  voice:"]
    for k, v in voice.items():
        lines.append(f"    {k}: {v}")
    (root / "project.yaml").write_text("\n".join(lines) + "\n")


def test_find_project_root_walks_up(tmp_path):
    (tmp_path / "project.yaml").write_text("project:\n  title: T\n")
    nested = tmp_path / "scenes"
    nested.mkdir()
    assert _style._find_project_root(str(nested)) == str(tmp_path)


def test_find_project_root_missing(tmp_path):
    assert _style._find_project_root(str(tmp_path)) is None


def test_load_dotenv_key_lifts_unexported(tmp_path, monkeypatch):
    monkeypatch.delenv("SOME_TEST_KEY", raising=False)
    (tmp_path / ".env").write_text('SOME_TEST_KEY="s3cret"\n# comment\n')
    _style._load_dotenv_key(str(tmp_path), "SOME_TEST_KEY")
    assert os.environ.get("SOME_TEST_KEY") == "s3cret"
    monkeypatch.delenv("SOME_TEST_KEY", raising=False)


def test_load_dotenv_key_never_overrides_shell(tmp_path, monkeypatch):
    monkeypatch.setenv("SOME_TEST_KEY", "from-shell")
    (tmp_path / ".env").write_text("SOME_TEST_KEY=from-file\n")
    _style._load_dotenv_key(str(tmp_path), "SOME_TEST_KEY")
    assert os.environ["SOME_TEST_KEY"] == "from-shell"


def test_openai_without_voice_name_is_an_error(tmp_path, monkeypatch):
    write_manifest(tmp_path, {"provider": "openai"})
    monkeypatch.setenv("AGEATION_PROJECT", str(tmp_path))
    monkeypatch.delenv("AGEATION_TTS", raising=False)
    with pytest.raises(RuntimeError, match="voice.name"):
        _style.speech_service()


def test_unknown_provider_is_an_error(tmp_path, monkeypatch):
    write_manifest(tmp_path, {"provider": "espeak"})
    monkeypatch.setenv("AGEATION_PROJECT", str(tmp_path))
    monkeypatch.delenv("AGEATION_TTS", raising=False)
    with pytest.raises(RuntimeError, match="espeak"):
        _style.speech_service()


def test_ageation_tts_overrides_config(tmp_path, monkeypatch):
    # openai in config, but the draft switch forces gtts -- and the gtts
    # branch must not demand a voice name or an API key.
    write_manifest(tmp_path, {"provider": "openai", "name": "nova"})
    monkeypatch.setenv("AGEATION_PROJECT", str(tmp_path))
    monkeypatch.setenv("AGEATION_TTS", "gtts")
    monkeypatch.chdir(tmp_path)
    svc = _style.speech_service()
    assert type(svc).__name__ == "GTTSService"


def test_no_manifest_falls_back_to_gtts(tmp_path, monkeypatch):
    monkeypatch.delenv("AGEATION_PROJECT", raising=False)
    monkeypatch.delenv("AGEATION_TTS", raising=False)
    monkeypatch.chdir(tmp_path)  # nowhere to find project.yaml
    svc = _style.speech_service()
    assert type(svc).__name__ == "GTTSService"


def test_parse_dotenv_shapes(tmp_path):
    p = tmp_path / ".env"
    p.write_text("# c\nA=1\nB='two'\nnoequals\n C = spaced \n")
    d = parse_dotenv(str(p))
    assert d == {"A": "1", "B": "two", "C": "spaced"}
    assert parse_dotenv(str(tmp_path / "missing")) == {}
