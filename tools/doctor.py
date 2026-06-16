#!/usr/bin/env python3
"""Health-check the rendering pipeline before manim spins up.

Fails LOUD before render time so a missing dep / missing API key is caught
in seconds, not after several minutes of TTS + frame generation. Wired as a
prerequisite of every `make render*` and `make video*` target.

Per project, doctor checks:

  PROJECT
    - project.yaml exists and parses
    - project.shape (if declared) is known
    - voice.provider is supported

  ENGINE
    - manim importable (manimpango is its hard dep — drafts cannot run without it)
    - ffmpeg on PATH (rendering)
    - latex on PATH (MathTex)             [WARN if absent: scenes without math compile fine]
    - dvisvgm on PATH (MathTex)           [WARN if absent: same reason]

  SECRETS (only when project's voice.provider needs one)
    - openai: OPENAI_API_KEY set in the shell, OR in `<project>/.env`
      (`.env` is gitignored per framework convention; see PIPELINE.md
      "Environment + secrets")

Each row prints PASS / FAIL / WARN with a one-line hint. Exits non-zero if
any required check fails; warnings do not gate the build.

Usage:  python tools/doctor.py [--project DIR]
"""

import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _project import (
    project_parser,
    resolve_project,
    load_project,
    project_shape,
    PROJECT_SHAPES,
)

PASS, FAIL, WARN = "PASS", "FAIL", "WARN"
KNOWN_PROVIDERS = {"gtts", "openai"}  # extend as make_speech_service grows


def parse_dotenv(path: str) -> dict:
    """Minimal .env parser: KEY=VALUE per line, # comments and blanks skipped.

    Avoids adding python-dotenv as a dep; the file format is simple enough.
    Quoted values (single or double) are stripped of their surrounding quotes.
    """
    if not os.path.exists(path):
        return {}
    out = {}
    for raw in open(path, encoding="utf-8"):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in {"'", '"'}:
            val = val[1:-1]
        if key:
            out[key] = val
    return out


def env_or_dotenv(name: str, project_root: str) -> tuple[bool, str]:
    """True if `name` is set in env or in `<project>/.env`. Returns (ok, source)."""
    if os.environ.get(name):
        return True, "shell environment"
    dotenv = parse_dotenv(os.path.join(project_root, ".env"))
    if dotenv.get(name):
        return True, f"{os.path.join(project_root, '.env')}"
    return False, ""


def row(status: str, label: str, detail: str = "") -> str:
    color = {PASS: "\033[32m", FAIL: "\033[31m", WARN: "\033[33m"}.get(status, "")
    reset = "\033[0m" if color else ""
    tail = f"  — {detail}" if detail else ""
    return f"  {color}{status}{reset}  {label}{tail}"


def main():
    args = project_parser(__doc__).parse_args()
    root = resolve_project(args.project)

    results: list[tuple[str, str, str]] = []
    required_failures = 0

    # PROJECT
    manifest_path = os.path.join(root, "project.yaml")
    if not os.path.exists(manifest_path):
        results.append((FAIL, "project.yaml present", f"missing at {manifest_path}"))
        required_failures += 1
        _print(results, required_failures)
        sys.exit(1)
    manifest = load_project(root)
    results.append((PASS, "project.yaml parses", manifest_path))

    try:
        shape = project_shape(manifest)
        detail = f"shape: {shape}  ({PROJECT_SHAPES[shape]['summary']})"
        results.append((PASS, "project.shape known", detail))
    except SystemExit as exc:
        results.append((FAIL, "project.shape known", str(exc)))
        required_failures += 1

    voice_cfg = (manifest.get("project") or {}).get("voice") or {}
    provider = voice_cfg.get("provider", "gtts")
    if provider in KNOWN_PROVIDERS:
        results.append((PASS, "voice.provider supported", provider))
    else:
        results.append((FAIL, "voice.provider supported",
                        f"unknown provider {provider!r} (known: {sorted(KNOWN_PROVIDERS)})"))
        required_failures += 1

    # ENGINE
    try:
        import manim  # noqa: F401
        results.append((PASS, "manim importable", manim.__version__))
    except ImportError as exc:
        results.append((FAIL, "manim importable", str(exc)))
        required_failures += 1

    if shutil.which("ffmpeg"):
        results.append((PASS, "ffmpeg on PATH", shutil.which("ffmpeg")))
    else:
        results.append((FAIL, "ffmpeg on PATH",
                        "install via `brew bundle` in the engine repo"))
        required_failures += 1

    if shutil.which("latex"):
        results.append((PASS, "latex on PATH", shutil.which("latex")))
    else:
        results.append((WARN, "latex on PATH",
                        "MathTex scenes will fail; ok for text-only renders"))

    if shutil.which("dvisvgm"):
        results.append((PASS, "dvisvgm on PATH", shutil.which("dvisvgm")))
    else:
        results.append((WARN, "dvisvgm on PATH",
                        "MathTex scenes will fail; ok for text-only renders"))

    # SECRETS
    if provider == "openai":
        ok, source = env_or_dotenv("OPENAI_API_KEY", root)
        if ok:
            results.append((PASS, "OPENAI_API_KEY available", source))
        else:
            results.append((FAIL, "OPENAI_API_KEY available",
                            f"set in shell, or put in {os.path.join(root, '.env')} "
                            f"(see .env.example in the engine repo)"))
            required_failures += 1
    else:
        results.append((PASS, "OPENAI_API_KEY not required",
                        f"voice.provider is {provider!r}"))

    _print(results, required_failures)
    sys.exit(1 if required_failures else 0)


def _print(results, required_failures):
    print()
    for status, label, detail in results:
        print(row(status, label, detail))
    print()
    if required_failures:
        print(f"  {required_failures} required check(s) failed — fix and re-run.")
    else:
        print("  doctor: all required checks pass.")
    print()


if __name__ == "__main__":
    main()
