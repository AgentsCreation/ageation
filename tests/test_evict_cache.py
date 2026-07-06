"""evict_cache: surgical removal of TTS voiceover-cache entries + orphan mp3s."""

import json
import os
import subprocess
import sys

TOOLS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools")


def run(*args, cwd=None):
    return subprocess.run(
        [sys.executable, os.path.join(TOOLS, "evict_cache.py"), *args],
        capture_output=True, text=True, cwd=cwd)


def make_cache(root, entries):
    vo = root / "media" / "voiceovers"
    vo.mkdir(parents=True)
    for e in entries:
        for k in ("original_audio", "final_audio"):
            if e.get(k):
                (vo / e[k]).write_bytes(b"mp3")
    (vo / "cache.json").write_text(json.dumps(entries))
    return vo


def read_cache(vo):
    return json.loads((vo / "cache.json").read_text())


def test_text_selector_evicts_entry_and_orphan_mp3(tmp_path):
    vo = make_cache(tmp_path, [
        {"input_text": "these densities carried the chapter",
         "input_data": {"service": "openai"},
         "original_audio": "these-1.mp3", "final_audio": "these-1.mp3"},
        {"input_text": "the uniform distribution is flat",
         "input_data": {"service": "openai"},
         "original_audio": "unif-2.mp3", "final_audio": "unif-2.mp3"},
    ])
    r = run("--project", str(tmp_path), "--text", "these densities")
    assert r.returncode == 0, r.stderr
    kept = read_cache(vo)
    assert len(kept) == 1
    assert kept[0]["input_text"].startswith("the uniform")
    assert not (vo / "these-1.mp3").exists()   # orphan deleted
    assert (vo / "unif-2.mp3").exists()         # survivor kept


def test_shared_mp3_is_not_deleted_while_referenced(tmp_path):
    # Two entries (draft + final) reference the same mp3; evicting one must
    # not delete the file the other still needs.
    vo = make_cache(tmp_path, [
        {"input_text": "hello world", "input_data": {"service": "gtts"},
         "final_audio": "shared.mp3"},
        {"input_text": "hello world", "input_data": {"service": "openai"},
         "final_audio": "shared.mp3"},
    ])
    r = run("--project", str(tmp_path), "--provider", "gtts")
    assert r.returncode == 0, r.stderr
    assert len(read_cache(vo)) == 1
    assert (vo / "shared.mp3").exists()   # still referenced by the openai entry


def test_dry_run_changes_nothing(tmp_path):
    vo = make_cache(tmp_path, [
        {"input_text": "drop me", "input_data": {"service": "openai"},
         "final_audio": "drop.mp3"},
    ])
    r = run("--project", str(tmp_path), "--text", "drop", "--dry-run")
    assert r.returncode == 0, r.stderr
    assert len(read_cache(vo)) == 1        # untouched
    assert (vo / "drop.mp3").exists()


def test_no_selector_is_refused(tmp_path):
    make_cache(tmp_path, [{"input_text": "x", "final_audio": "x.mp3"}])
    r = run("--project", str(tmp_path))
    assert r.returncode != 0
    assert "no selector" in (r.stdout + r.stderr)
