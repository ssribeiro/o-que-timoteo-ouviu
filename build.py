#!/usr/bin/env python3
"""Render dist/index.html from content.yaml + template.html. Stdlib + PyYAML only."""
import argparse
import html
import pathlib
import shutil
import string

import yaml

ROOT = pathlib.Path(__file__).resolve().parent
LANGS = {"pt-BR": "pt", "en": "en"}
TOP_KEYS = ("language", "price", "cover_image", "buy_url", "text")
TEXT_KEYS = ("toggle_label", "title", "subtitle", "author", "points",
             "price_label", "buy_label", "soon_label", "footer")
# Standing rule for first-contact demos: the page always says it is a prototype.
RULE_FOOTER = "protótipo — não é um produto ainda"


def fail(msg):
    raise SystemExit(f"build: {msg}")


def load(path):
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        fail(f"{path} must be a mapping")
    for key in TOP_KEYS:
        if data.get(key) is None:
            fail(f"missing field '{key}' in {path}")
    for key in ("language", "price", "cover_image", "buy_url"):
        if not isinstance(data[key], str):
            fail(f"field '{key}' must be a string")
    if data["language"] not in LANGS:
        fail(f"field 'language' must be one of {list(LANGS)}, got {data['language']!r}")
    for lang in LANGS:
        text = data["text"].get(lang)
        if not isinstance(text, dict):
            fail(f"missing field 'text.{lang}'")
        for key in TEXT_KEYS:
            if not text.get(key):
                fail(f"missing field 'text.{lang}.{key}'")
        points = text["points"]
        if not (isinstance(points, list) and len(points) == 3 and all(isinstance(p, str) and p for p in points)):
            fail(f"field 'text.{lang}.points' must be exactly three non-empty strings")
    if data["text"]["pt-BR"]["footer"] != RULE_FOOTER:
        fail(f"field 'text.pt-BR.footer' must be exactly {RULE_FOOTER!r}")
    if data["buy_url"] and not data["buy_url"].startswith("https://"):
        fail(f"field 'buy_url' must be empty or an https:// link, got {data['buy_url']!r}")
    return data


def cover_html(data, content_dir, out, title):
    src = content_dir / data["cover_image"]
    if src.is_file():
        shutil.copyfile(src, out / src.name)
        return f'<img class="cover" src="{html.escape(src.name)}" alt="{title}">'
    return (f'<svg class="cover" viewBox="0 0 300 450" role="img" aria-label="{title}">'
            '<rect width="300" height="450" fill="#2b3a55"/>'
            '<rect x="20" y="20" width="260" height="410" fill="none" stroke="#faf8f4" stroke-width="2"/>'
            f'<text x="150" y="225" text-anchor="middle" fill="#faf8f4" font-size="20">{title}</text></svg>')


def block(lang, text, price, buy_url):
    e = {k: html.escape(v) for k, v in text.items() if isinstance(v, str)}
    points = "\n".join(f"<li>{html.escape(p)}</li>" for p in text["points"])
    if buy_url:
        button = (f'<a class="buy" href="{html.escape(buy_url)}" target="_blank" '
                  f'rel="noopener">{e["buy_label"]}</a>')
    else:
        button = f'<button class="buy" type="button" disabled>{e["soon_label"]}</button>'
    return (f'<section class="lang-{LANGS[lang]}" lang="{lang}">\n'
            f'<h1>{e["title"]}</h1>\n<p class="subtitle">{e["subtitle"]}</p>\n'
            f'<p class="author">{e["author"]}</p>\n<ul>\n{points}\n</ul>\n'
            f'<p class="price"><small>{e["price_label"]}</small>{html.escape(price)}</p>\n'
            f'{button}\n<footer>{e["footer"]}</footer>\n</section>')


def render(content_path, out):
    data = load(content_path)
    out.mkdir(parents=True, exist_ok=True)
    default = data["language"]
    title = html.escape(data["text"][default]["title"])
    page = string.Template((ROOT / "template.html").read_text(encoding="utf-8")).substitute(
        lang=default,
        title=title,
        pt_checked=" checked" if default == "pt-BR" else "",
        en_checked=" checked" if default == "en" else "",
        toggles="".join(f'<label for="l-{LANGS[l]}">{html.escape(data["text"][l]["toggle_label"])}</label>'
                        for l in LANGS),
        cover=cover_html(data, content_path.parent, out, title),
        blocks="\n".join(block(l, data["text"][l], data["price"], data["buy_url"]) for l in LANGS),
    )
    (out / "index.html").write_text(page, encoding="utf-8")
    return out / "index.html"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--content", type=pathlib.Path, default=ROOT / "content.yaml")
    parser.add_argument("--out", type=pathlib.Path, default=ROOT / "dist")
    args = parser.parse_args()
    print(f"wrote {render(args.content.resolve(), args.out.resolve())}")


if __name__ == "__main__":
    main()
