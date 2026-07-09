"""Shared helpers for content-hash provenance (stdlib only, no deps).

The pipeline records, in each derived file's YAML front matter, the SHA-256 of
the exact input it was built from. `check_sync.py` re-hashes the current inputs
and compares, so drift between the LaTeX source and the generated layers is
detectable even across clones with no git history (content hashes, not mtimes).

This module also resolves the *engine* version (`framework_version` /
`framework_provenance`) — via `git describe --tags --always`, degrading from a
release tag to a bare commit hash — so a project can record which ageation
built it, both per-concept (`framework_commit`) and in a top-level BUILD.yaml.

Front-matter keys used:
- concept .md : source, source_sha256, provenance_stamped, framework_commit
- script  .md : derived_from, derived_from_sha256, provenance_stamped
"""

import hashlib
import os
import re
import subprocess


def framework_root() -> str:
    """Absolute path to the ageation engine checkout (this file's repo)."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _git(fw_root: str, *args: str):
    return subprocess.run(
        ["git", "-C", fw_root, *args],
        capture_output=True, text=True, timeout=10)


def framework_dirty(fw_root: str) -> bool:
    """True if the engine tree has uncommitted tracked changes.

    Dirtiness is computed via `git status` with `.env*` excluded rather than
    `describe --dirty`: sandboxed sessions are denied stat() on .env-pattern
    files, which made git report a clean tree as dirty. Secrets-adjacent
    files have no bearing on which framework built a video anyway.
    """
    s = _git(fw_root, "status", "--porcelain", "--untracked-files=no",
             "--", ":(exclude).env*")
    return s.returncode != 0 or bool(s.stdout.strip())


def framework_version(fw_root: str | None = None) -> str:
    """Git description of the framework checkout that performed a stamp.

    Uses `--tags` so a tagged release reports the tag (e.g. v0.2.0-3-gb0e713a);
    with no tags reachable it degrades to the abbreviated commit hash via
    `--always`. Projects live outside the framework repo (engine/content
    split), so the content hashes alone can't say which framework generated a
    snapshot. The `-dirty` suffix flags stamps made from an uncommitted tree.
    """
    fw_root = fw_root or framework_root()
    try:
        version = _git(fw_root, "describe", "--tags", "--always").stdout.strip()
        if not version:
            return "unavailable"
        if framework_dirty(fw_root):
            version += "-dirty"
        return version
    except Exception:
        return "unavailable"


def _package_version(fw_root: str) -> str:
    """`[project].version` from the engine's pyproject.toml, or 'unavailable'."""
    try:
        import tomllib
        with open(os.path.join(fw_root, "pyproject.toml"), "rb") as f:
            data = tomllib.load(f)
        return (data.get("project") or {}).get("version") or "unavailable"
    except Exception:
        return "unavailable"


def framework_provenance(fw_root: str | None = None) -> dict:
    """Structured record of the engine version, for a project's BUILD.yaml.

    Keys: version (git describe, tag-or-hash, possibly -dirty), commit (short
    hash), package_version (pyproject), dirty (bool). All fields degrade to
    'unavailable'/False rather than raising when git or pyproject is missing.
    """
    fw_root = fw_root or framework_root()
    dirty = False
    version = "unavailable"
    commit = "unavailable"
    try:
        version = _git(fw_root, "describe", "--tags", "--always").stdout.strip() \
            or "unavailable"
        dirty = framework_dirty(fw_root)
        if version != "unavailable" and dirty:
            version += "-dirty"
        commit = _git(fw_root, "rev-parse", "--short", "HEAD").stdout.strip() \
            or "unavailable"
    except Exception:
        pass
    return {
        "version": version,
        "commit": commit,
        "package_version": _package_version(fw_root),
        "dirty": dirty,
    }


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# Runtime measurements are written back into the script's front matter by the
# render/assemble stage (measured_sec per beat, measured_runtime_sec total).
# They are *outputs* of the pipeline, not authored content -- so the
# script->scene provenance hash must ignore them, or every measurement pass
# would mark every built scene STALE.
_VOLATILE_SCRIPT_LINE = re.compile(
    r"(?m)^[ \t]*(measured_sec|measured_runtime_sec):[^\n]*\n?")


def sha256_script(path: str) -> str:
    """SHA-256 of a script .md with volatile measurement lines removed.

    Identical to sha256_file for any file that carries no measured_* lines.
    """
    with open(path, encoding="utf-8") as f:
        text = f.read()
    normalized = _VOLATILE_SCRIPT_LINE.sub("", text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def split_fm(text: str):
    """Return (front_matter_text, body) or (None, text) if no front matter."""
    m = re.match(r"^---\n(.*?)\n---\n?", text, re.S)
    if not m:
        return None, text
    return m.group(1), text[m.end():]


def rebuild(fm: str, body: str) -> str:
    return "---\n" + fm + "\n---\n" + body


def fm_get(fm: str, key: str):
    """Get a TOP-LEVEL scalar value (ignores indented/nested keys)."""
    m = re.search(r"(?m)^" + re.escape(key) + r":[ \t]*(.*)$", fm)
    if not m:
        return None
    v = m.group(1).strip()
    if len(v) >= 2 and v[0] in "\"'" and v[-1] == v[0]:
        v = v[1:-1]
    return v


def fm_upsert(fm: str, key: str, value: str, after: str | None = None) -> str:
    """Set a top-level key, replacing in place or inserting after `after`."""
    line = f"{key}: {value}"
    if re.search(r"(?m)^" + re.escape(key) + r":", fm):
        return re.sub(r"(?m)^" + re.escape(key) + r":.*$", line, fm, count=1)
    if after:
        m = re.search(r"(?m)^" + re.escape(after) + r":.*$", fm)
        if m:
            return fm[:m.end()] + "\n" + line + fm[m.end():]
    return fm.rstrip("\n") + "\n" + line
