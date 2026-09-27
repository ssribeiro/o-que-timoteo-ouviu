import pathlib
import re
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
BUILD = ROOT / "build.py"
FOOTER = "protótipo — não é um produto ainda"
BUY = "https://example.org/checkout?item=1&ref=x"
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


class TagBalance(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.errors, self.doctype = [], [], False

    def handle_decl(self, decl):
        self.doctype = decl.lower() == "doctype html"

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"unexpected </{tag}>, open: {self.stack}")
        else:
            self.stack.pop()


def base_content():
    return yaml.safe_load((ROOT / "content.yaml").read_text(encoding="utf-8"))


def build(content):
    with tempfile.TemporaryDirectory(prefix="ebook-page-test-") as d:
        tmp = pathlib.Path(d)
        src = tmp / "content.yaml"
        src.write_text(yaml.safe_dump(content, allow_unicode=True), encoding="utf-8")
        out = tmp / "dist"
        proc = subprocess.run([sys.executable, str(BUILD), "--content", str(src), "--out", str(out)],
                              capture_output=True, text=True)
        page = out / "index.html"
        return proc, (page.read_text(encoding="utf-8") if page.exists() else None)


class BuildTest(unittest.TestCase):
    def ok(self, content):
        proc, page = build(content)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return page

    def test_missing_top_field_fails_loudly(self):
        c = base_content()
        del c["price"]
        proc, page = build(c)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("price", proc.stderr)
        self.assertIsNone(page)

    def test_missing_translated_field_fails_loudly(self):
        c = base_content()
        del c["text"]["en"]["title"]
        proc, page = build(c)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("title", proc.stderr)
        self.assertIsNone(page)

    def test_empty_buy_url_gives_disabled_button_without_href(self):
        c = base_content()
        c["buy_url"] = ""
        page = self.ok(c)
        self.assertRegex(page, r"<button[^>]*disabled[^>]*>Avise-me quando lançar</button>")
        self.assertNotIn("href", page)

    def test_buy_url_gives_anchor_with_noopener(self):
        c = base_content()
        c["buy_url"] = BUY
        page = self.ok(c)
        href = BUY.replace("&", "&amp;")
        self.assertRegex(page, r'<a[^>]*href="' + re.escape(href) + r'"[^>]*rel="noopener"')
        self.assertNotIn("<button", page)

    def test_non_https_buy_url_is_refused(self):
        c = base_content()
        c["buy_url"] = "javascript:alert(1)"
        proc, page = build(c)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("buy_url", proc.stderr)

    def test_no_http_url_other_than_buy_url(self):
        for url in ("", BUY):
            c = base_content()
            c["buy_url"] = url
            page = self.ok(c).replace("&amp;", "&")
            found = re.findall(r"https?://[^\"'\s<>]+", page)
            self.assertEqual(found, [url] * len(found) if url else [], found)

    def test_prototype_footer_present(self):
        self.assertIn(FOOTER, self.ok(base_content()))

    def test_prototype_footer_cannot_be_removed(self):
        c = base_content()
        c["text"]["pt-BR"]["footer"] = "produto final"
        proc, _ = build(c)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("footer", proc.stderr)

    def test_output_parses_with_balanced_tags(self):
        for url in ("", BUY):
            c = base_content()
            c["buy_url"] = url
            parser = TagBalance()
            parser.feed(self.ok(c))
            parser.close()
            self.assertTrue(parser.doctype)
            self.assertEqual(parser.errors, [])
            self.assertEqual(parser.stack, [])

    def test_missing_cover_renders_inline_svg_placeholder(self):
        page = self.ok(base_content())
        self.assertIn("<svg", page)
        self.assertNotIn("<img", page)


if __name__ == "__main__":
    unittest.main()
