# QA gate: dev → prod — 2026-09-27

## Rubric (written before inspection)
Promise: "a small page to sell an ebook" (*O que Timóteo Ouviu*, personal favor for a friend/pastor).
Visitor asks: what is it, who wrote it, price, how to buy, is it trustworthy (no dead links, works
on phone), can I read it in English. Owner asks: nothing invented as fact, "prototype" footer in
both languages, disabled button self-explains, zero external requests (fonts/scripts/trackers/
images), HTML parses, placeholder author judged for a demo. Mechanical checks: HTML validity, no
`http(s)` URLs in dist/index.html beyond a set buy_url, page size, CSS-only toggle, `unittest`
green, build fails loudly on a missing field. Plus five more visitor questions.

## Checks
- Build: `python3 build.py` → exit 0, `dist/index.html` written, 4037 bytes (3.9 KB).
- Tests: `python3 -m unittest discover -s tests` → **10/10 passed** (0.379s), incl. missing-field,
  footer-lock, non-https-rejected, tag-balance, no-http-url tests.
- HTML validity (independent `html.parser` pass, not just the test's copy): doctype present,
  `errors: []`, open-tag `stack: []` — balanced and parseable.
- No `http(s)` URLs in `dist/index.html`: `grep -oE 'https?://...'` → zero matches (buy_url is "").
- No external requests: no `<script>`, `<link>`, or `googleapis`/CDN reference in template.html or
  dist output — confirmed by grep, zero hits.
- CSS-only toggle: `template.html` uses `<input type=radio>` + `~` sibling selectors
  (`#l-pt:checked ~ nav label`, `#l-pt:checked ~ main .lang-en{display:none}`) — no JS anywhere.
- Mobile: fetched with an iPhone Safari UA on a live `serve.sh` instance — byte-identical
  (4037 B) to desktop fetch; static file, no UA branching, correctly responsive per template CSS.
- Build fails loudly: `tests/test_build.py::test_missing_top_field_fails_loudly` and
  `::test_missing_translated_field_fails_loudly` delete a field and assert non-zero exit + the
  field's name in stderr — both pass; `load()` in build.py checks every field before rendering.
- `prod` branch: confirmed empty (one shared root commit with `dev`, 366 deletions vs `dev` tip).

## Defects
1. **[Environment, not code]** `http://127.0.0.1:8765/` — the URL given for this task — is bound to
   an unrelated service, `bin/ed-files` (pid observed live, `0.0.0.0:8765`), serving a directory
   listing of the whole `~/automation` repo, **not** this page. `curl` there returns 2868 B of
   ed-files output. Verified this project's own `serve.sh` is correct by running it on
   `PORT=8766`: served `dist/index.html` byte-for-byte (4037 B), desktop and mobile alike. Fix the
   port before pointing anyone at "the live page" — this repo's code is not at fault.
2. **[Low, content.yaml:16,30]** Placeholder author `«nome do autor»` / `«author name»` renders
   verbatim on the page. The guillemets read as an obvious placeholder, not an invented fact, so it
   is not a trust problem — but it looks unfinished for a demo shown to the author. Recommend
   `build.py`'s `block()` (around line 68) hide the `.author` line via CSS when the value still
   starts with `«`, until a real name is set.
3. **[Low, UX]** "Avise-me quando lançar" / "Notify me at launch" implies a capture mechanism, but
   the button is a disabled `<button>` with no email/contact field in template.html or
   content.yaml — no real visitor can actually register interest yet. Consistent with "prototype,"
   not a launch blocker, but note it before calling this a working coming-soon page.
4. **[None]** No invented facts found: subtitle in both languages carries "provisional"/"provisório"
   inline, visible to every visitor without digging into the source — the provisionality rubric
   item is met.

## Five more visitor questions
- *What ebook format (PDF/EPUB/Kindle)?* — unanswered anywhere. Acceptable for a "coming soon" page.
- *How do I actually get notified at launch?* — see defect 3, no mechanism yet.
- *Who is behind this / is it legitimate?* — no about/contact info; fine for a favor-for-a-friend
  demo, wanted before a real public launch.
- *Does this site track me?* — no scripts, trackers, or analytics found; answers positively.
- *Does it work with JavaScript disabled?* — yes, confirmed CSS-only toggle, no `<script>` at all.

## Verdict: **ALLOW** — promote `dev` → `prod`
All mechanical gates pass (tests, HTML validity, zero external requests, footer lock, build fails
loudly, size 3.9 KB). Defects 2–3 are cosmetic/disclosed by the prototype footer, not trust issues.
**Condition:** correct the demo URL before sharing it (defect 1 is environmental, outside this
repo — do not merge a "fix" for it into `dev`). Recommend, not required: hide the placeholder
author line before showing the friend, and decide whether "notify me" needs a real form before
public traffic.
