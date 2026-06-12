"""End-to-end: init -> scaffold -> vendor -> stamp -> gates, on a tmp project.

Exercises the same flow a new user follows, including the companion .md pair,
drift detection, and notation enforcement. Runs the tools as subprocesses (the
real interface) — needs only PyYAML, not manim.
"""

import os
import subprocess
import sys

import pytest

TOOLS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools")


def run(tool, *args, cwd=None):
    return subprocess.run(
        [sys.executable, os.path.join(TOOLS, tool), *args],
        capture_output=True, text=True, cwd=cwd)


@pytest.fixture
def project(tmp_path):
    inp = tmp_path / "input" / "Demo"
    inp.mkdir(parents=True)
    (inp / "1Linear_Algebra.tex").write_text(
        "\\section{Linear Algebra Foundations}\n"
        "Vectors live in $\\mathbb{R}^n$. We write $\\mathbb{E}[X]$ for averages.\n")
    (inp / "1Linear_Algebra.md").write_text(
        "# Linear algebra notes (high-level)\nVectors and matrices.\n")
    (inp / "2Calculus.tex").write_text("\\section{Calculus Refresher}\nLimits.\n")
    return tmp_path


def test_full_bootstrap_flow(project):
    root = str(project)

    r = run("init_course.py", "input/Demo", "--project", root,
            "--title", "Demo", "--scaffold-concepts")
    assert r.returncode == 0, r.stderr
    assert (project / "course.yaml").exists()
    assert (project / "content" / "1-linear-algebra.md").exists()
    assert (project / "content" / "2-calculus.md").exists()
    assert "1 with companion" in r.stdout

    r = run("vendor_sources.py", "--project", root)
    assert r.returncode == 0, r.stderr
    assert (project / "sources" / "1-linear-algebra.tex").exists()
    assert (project / "sources" / "1-linear-algebra.md").exists()  # companion
    assert not (project / "sources" / "2-calculus.md").exists()
    concept = (project / "content" / "1-linear-algebra.md").read_text()
    assert "companion: sources/1-linear-algebra.md" in concept

    r = run("stamp_provenance.py", "--project", root)
    assert r.returncode == 0, r.stderr
    concept = (project / "content" / "1-linear-algebra.md").read_text()
    assert "source_sha256:" in concept
    assert "companion_sha256:" in concept
    # engine/content split: the stamp records which framework built this
    assert "framework_commit:" in concept
    assert "framework_commit: unavailable" not in concept  # tests run in-repo

    r = run("check_sync.py", "--project", root)
    assert r.returncode == 0, r.stdout
    r = run("check_status.py", "--project", root)
    assert r.returncode == 0, r.stdout

    # Companion drift must trip the sync gate.
    with open(project / "sources" / "1-linear-algebra.md", "a") as f:
        f.write("drifted\n")
    r = run("check_sync.py", "--project", root)
    assert r.returncode == 1
    assert "STALE" in r.stdout

    # Re-stamp blesses the new state.
    run("stamp_provenance.py", "--project", root)
    assert run("check_sync.py", "--project", root).returncode == 0


def test_rerun_vendor_adds_companion_to_already_vendored(project):
    root = str(project)
    companion = project / "input" / "Demo" / "1Linear_Algebra.md"
    saved = companion.read_text()
    companion.unlink()  # vendor first WITHOUT the companion present

    run("init_course.py", "input/Demo", "--project", root, "--scaffold-concepts")
    run("vendor_sources.py", "--project", root)
    assert not (project / "sources" / "1-linear-algebra.md").exists()

    companion.write_text(saved)  # companion appears later; re-run picks it up
    r = run("vendor_sources.py", "--project", root)
    assert r.returncode == 0, r.stderr
    assert (project / "sources" / "1-linear-algebra.md").exists()
    concept = (project / "content" / "1-linear-algebra.md").read_text()
    assert "companion: sources/1-linear-algebra.md" in concept


def test_notation_check_and_normalize(project):
    root = str(project)
    run("init_course.py", "input/Demo", "--project", root, "--scaffold-concepts")
    run("vendor_sources.py", "--project", root)

    text = (project / "course.yaml").read_text()
    rules = ("notation:\n  rules:\n"
             "    - avoid: '\\mathbb{E}'\n"
             "      use: '\\mathrm{E}'\n"
             "      reason: expectation\n")
    (project / "course.yaml").write_text(text.replace("notation:\n  rules: []\n", rules))

    r = run("check_notation.py", "--project", root)
    assert r.returncode == 1
    assert "expectation" in r.stdout

    r = run("normalize_notation.py", "--project", root, "--write")
    assert r.returncode == 0, r.stderr
    assert run("check_notation.py", "--project", root).returncode == 0


def test_init_collision_detection(tmp_path):
    inp = tmp_path / "input" / "Demo"
    inp.mkdir(parents=True)
    (inp / "1Foo.tex").write_text("a")
    (inp / "2Foo.tex").write_text("b")  # same derived scene file: scenes/foo.py
    r = run("init_course.py", "input/Demo", "--project", str(tmp_path))
    assert r.returncode != 0
    assert "collision" in (r.stdout + r.stderr)
    assert not (tmp_path / "course.yaml").exists()


def test_status_gate_catches_overpromoted_chapter(project):
    root = str(project)
    run("init_course.py", "input/Demo", "--project", root, "--scaffold-concepts")
    text = (project / "course.yaml").read_text()
    (project / "course.yaml").write_text(
        text.replace("    status: planned", "    status: built", 1))
    r = run("check_status.py", "--project", root)
    assert r.returncode == 1
    assert "but script missing" in r.stdout
