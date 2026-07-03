# Web-presence recipes — the same workflow as the probability course repo:
# `just web-data` regenerates the site data, `just web` previews locally,
# `just deploy` publishes to GitHub Pages on demand. The video pipeline
# itself stays in the Makefile (`make help`).

# Print available recipes (default)
default:
    @just --list

# --- Website --------------------------------------------------------------

# Regenerate the data the site draws (site/data/site.json): the engine
# version and the toolbox, read from the repository itself. Stdlib only.
web-data:
    python3 scripts/site_data.py

# Serve the static site locally for preview at http://localhost:8000.
# Regenerates the site data first.
web: web-data
    python3 -m http.server 8000 --directory site

# Publish the site to GitHub Pages, on demand. Regenerates the site data and
# deploys in the cloud from whatever is on the pushed `main` branch. Does not
# commit anything. Requires `gh auth login`.
# Note: it deploys the *pushed* state of `main`, so commit and push first if
# you want your latest edits to appear.
deploy:
    gh workflow run pages.yml
    @echo "Deploy started. Watch progress with:  gh run watch"
