# System prerequisites for the Manim video pipeline (macOS / Homebrew).
# This is the system-package counterpart to pyproject.toml (which only covers
# PyPI packages). Install everything with:
#
#     brew bundle
#
# Then the Python side:  uv sync

brew "uv"        # Python toolchain + virtual-env/dependency manager
brew "ffmpeg"    # audio/video encoding for Manim renders + gTTS mp3->wav

# LaTeX is required for MathTex (provides `latex` and `dvisvgm`).
# MacTeX is the full distribution Manim recommends (~5 GB).
cask "mactex"

# Lean alternative to MacTeX (~100 MB): comment out the cask above and use
#     brew install --cask basictex
# then install packages on demand as Manim reports them missing:
#     sudo tlmgr update --self && sudo tlmgr install standalone preview dvisvgm

# Not needed on macOS:
# - pango/cairo: Manim's wheels (manimpango, pycairo) bundle them on macOS.
#   (The pango build problem only affected the Linux cloud sandbox.)
# - sox: only required for manim-voiceover's microphone-recording mode, which
#   this project does not use (gTTS / OpenAI TTS instead).
