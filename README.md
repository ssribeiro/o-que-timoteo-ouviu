# ebook-page

A one-page static site to sell Luan's ebook. **Prototype, not a product yet** — the page says so in
its footer and the build refuses to remove that line.

## Edit
All words and prices live in `content.yaml`, nowhere else. Two languages: `pt-BR` (default, set by
`language:`) and `en`, switched on the page by a CSS-only toggle (no JavaScript).

Placeholders are marked `« »` and must be replaced before any real launch:
- `price`, `cover_image`
- per language: `title`, `subtitle`, `author` (currently «Luan»), the three `points`
- `buy_url` — empty means the button reads "Avise-me quando lançar" and is disabled. Set it to a real
  `https://` checkout link to turn it into a working "Comprar" button.

Cover: put the image next to `content.yaml` and set `cover_image` to its name. If the file does not
exist, the build draws an SVG placeholder with the title.

## Build
    python3 build.py            # writes dist/index.html
Requires Python 3 and PyYAML (`import yaml`). A missing or invalid field stops the build with the
field's name.

## Test
    python3 -m unittest discover -s tests

## Preview (tailnet demo only)
    ./serve.sh                  # PORT=9000 ./serve.sh to change port
Then open `http://<this-machine-tailnet-name>:8765/`.

## Branches
Work on `dev`. `prod` stays empty until the QA gate allows a promotion.
