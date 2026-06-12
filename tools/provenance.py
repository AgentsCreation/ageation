"""Shared helpers for content-hash provenance (stdlib only, no deps).

The pipeline records, in each derived file's YAML front matter, the SHA-256 of
the exact input it was built from. `check_sync.py` re-hashes the current inputs
and compares, so drift between the LaTeX source and the generated layers is
detectable even across clones with no git history (content hashes, not mtimes).

Front-matter keys used:
- concept .md : source, source_sha256, provenance_stamped, framework_commit
- script  .md : derived_from, derived_from_sha256, provenance_stamped
"""

import hashlib
import re


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


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
