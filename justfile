# Web-presence recipes: `just web` previews the site locally, `just deploy`
# publishes to GitHub Pages on demand. The site is fully static — no build
# step. The video pipeline itself stays in the Makefile (`make help`).

# Print available recipes (default)
default:
    @just --list

# --- Website --------------------------------------------------------------

# Serve the static site locally for preview (default http://localhost:8000).
# Pass a port if 8000 is busy:  just web 8080
web port="8000":
    python3 -m http.server {{port}} --directory site

# Publish the site to GitHub Pages, on demand. Deploys in the cloud from
# whatever is on the pushed `main` branch; does not commit anything. Requires
# `gh auth login`.
# Note: it deploys the *pushed* state of `main`, so commit and push first if
# you want your latest edits to appear.
deploy:
    gh workflow run pages.yml
    @echo "Deploy started. Watch progress with:  gh run watch"
