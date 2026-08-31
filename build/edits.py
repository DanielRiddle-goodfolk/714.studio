#!/usr/bin/env python3
"""
Home-page edits requested after the first review pass.

These live here rather than being hand-typed into index.html because index.html
is regenerated from the Manus capture by clean.py — anything edited directly
there would be wiped on the next rebuild. Run order:

    clean.py  ->  edits.py  ->  inject.py

Idempotent: safe to re-run.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOME = ROOT / "index.html"

GOOGLE_REVIEWS = """<section class="reviews-section editorial-width" id="reviews">
<div class="reviews-head">
<div class="chapter-label"><span class="chapter-number">05</span><span>Stories</span></div>
<h2>What guests say.</h2>
<p>Reviews come straight from Google, so they stay current and none of them are written here.</p>
</div>
<div class="reviews-embed" data-embed="google-reviews" role="region" aria-label="Google reviews">
<p class="utility-label">Embed slot · Google reviews</p>
<p class="reviews-embed-note">Live reviews will render in this space once the plugin is connected. The box is sized to roughly what a three-card review row will occupy, so the surrounding layout is honest about the room it needs.</p>
</div>
<a href="/contact/" class="editorial-link"><span>Share a question with the Studio</span><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-arrow-right" aria-hidden="true"><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg></a>
</section>"""


ARROW = ('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" '
         'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
         'stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"></path>'
         '<path d="m12 5 7 7-7 7"></path></svg>')
# External rows use the same arrow as internal ones — no "leaves the site" badge.
ARROW_UR = ARROW

# The single combined list, in the order Will specified. Brands and modalities
# sit together on purpose — from a visitor's side they're all just "doors".
#
# Each entry is a dict so the section stays a framework rather than a fixed
# layout. Only `num`, `name`, `desc` and `href` are required:
#
#   logo   filename in /images/. Omit it and the name is set in the display face
#          instead — that path is a first-class option, not a fallback, so a
#          door with no wordmark still looks deliberate.
#   scale  optional multiplier on the logo's height, for when a real wordmark
#          sits optically small or large against the others. Real logos vary
#          wildly in proportion, so this is the knob to reach for rather than
#          re-cropping artwork.
#   ext    true for links that leave the site.
D = dict
DOORS = [
    D(num="01", name="Get Well Massage", logo="logo_get_well_massage_343812ef.svg",
      scale=1.28, href="/wellness/get-well-massage/",
      desc="Restorative touch and whole-body care."),
    D(num="02", name="Mind the Truth&reg;", logo="logo_mind_the_truth_1f88ac61.svg",
      href="/mind-the-truth/",
      desc="Faith-rooted counsel, prayer, and enduring hope."),
    D(num="03", name="PEMF Therapy", href="/wellness/pemf/",
      desc="Supports the body&rsquo;s own electrical language at the cellular level."),
    D(num="04", name="Far Infrared Sauna", href="/wellness/far-infrared-sauna/",
      desc="Deep, calming warmth that supports circulation and whole-body renewal."),
    D(num="05", name="The Chair", href="/wellness/nervous-system-trainer/",
      desc="Nervous System Trainer &mdash; repeated signals of safety, no technique to master."),
    D(num="06", name="Compression Boots", href="/wellness/compression-boots/",
      desc="Sequential air compression for circulation and lymphatic support."),
    D(num="07", name="The Apothecary", logo="logo_apothecary_554918b9.svg",
      href="https://714.studio/apothecary", ext=True,
      desc="Pure inputs, thoughtful tools, education, and guided selection."),
    D(num="08", name="Reclaim Health Spa", logo="logo_reclaim_health_spa_09abc004.svg",
      href="/wellness/",
      desc="Restorative technology, cellular support, and whole-body renewal."),
    D(num="09", name="Turnaround Lifestyle", logo="logo_turnaround_lifestyle_7094c24a.svg",
      href="/start-here/",
      desc="Intentional change, coaching, and a new direction."),
]


def find_block(html: str, opener: str, tag: str):
    """Locate a full element by its opening string, counting nested tags.

    Regex can't be trusted here: the pages are pretty-printed, so whitespace
    sits between closing tags, and these blocks nest the same tag several deep.
    Returns (start, end) offsets covering the whole element, or None.
    """
    start = html.find(opener)
    if start == -1:
        return None
    depth, i = 0, start
    open_tag, close_tag = f"<{tag}", f"</{tag}>"
    while i < len(html):
        nxt_open = html.find(open_tag, i)
        nxt_close = html.find(close_tag, i)
        if nxt_close == -1:
            return None
        if nxt_open != -1 and nxt_open < nxt_close:
            depth += 1
            i = nxt_open + len(open_tag)
        else:
            depth -= 1
            i = nxt_close + len(close_tag)
            if depth == 0:
                return (start, i)
    return None


def doors_list() -> str:
    rows = []
    for d in DOORS:
        logo, ext = d.get("logo"), d.get("ext", False)

        # A wordmark already states the name, so it carries the alt text and the
        # row shows no second label — otherwise every brand row reads twice.
        plain = re.sub(r"<[^>]+>|&\w+;", "", d["name"])

        if logo:
            scale = d.get("scale")
            style = f' style="--door-logo-scale:{scale}"' if scale else ""
            mark = f'<img class="door-logo" alt="{plain}"{style} src="/images/{logo}">'
        else:
            mark = f'<span class="door-name">{d["name"]}</span>'

        ext_attr = ' target="_blank" rel="noreferrer"' if ext else ""
        rows.append(
            f'<a class="door-row{" has-logo" if logo else " has-name"}" '
            f'href="{d["href"]}"{ext_attr}>'
            f'<span class="door-number">{d["num"]}</span>'
            f'<span class="door-mark">{mark}</span>'
            f'<span class="door-copy"><span>{d["desc"]}</span></span>'
            f'<span class="door-go">{ARROW_UR if ext else ARROW}</span></a>')
    return f'<div class="door-index">{"".join(rows)}</div>'


def edit(html: str) -> str:
    # 1 — mint hero. Applied via a class so the exported stylesheet stays untouched;
    #     the rule itself lives in css/site.css.
    html = html.replace('<section class="home-opening">',
                        '<section class="home-opening is-mint">', 1)

    # 2 — drop the GoodFolk sub-line under "Different doors."
    html = re.sub(
        r'<div class="section-intro-copy"><p>Each GoodFolk identity keeps its own voice[^<]*</p></div>',
        "", html)

    # 3 — "Enter this chapter" reads as jargon; make it plain
    html = html.replace("<span>Enter this chapter</span>", "<span>Learn more</span>")

    # 4 — replace the "Restoration is personal" stories block with a Google
    #     reviews embed slot. Matched on its own <section>, not on the copy, so
    #     the whole block goes rather than leaving orphaned wrappers.
    m = re.search(r'<section class="stories-section editorial-width">.*?</section>', html, re.S)
    if m:
        html = html[:m.start()] + GOOGLE_REVIEWS + html[m.end():]

    # 5 — swap the 6-card GoodFolk grid for one combined list in Will's order.
    span = find_block(html, '<div class="goodfolk-index">', "div")
    if span:
        html = html[:span[0]] + doors_list() + html[span[1]:]

    # The kicker said "six chapters of care"; the list is nine now.
    html = html.replace("One family · six chapters of care",
                        "One family · nine ways in")

    # 6 — the "Featured wellness modalities" block now duplicates that list, so it goes.
    span = find_block(html, '<section class="featured-wellness">', "section")
    if span:
        html = html[:span[0]] + html[span[1]:]

    # 7a — the Manus capture carried the Studio's old social accounts.
    #      Correcting them here means the footer, which pages.py slices for every
    #      interior page, is right everywhere from one edit.
    html = html.replace("https://www.instagram.com/studio714official/",
                        "https://www.instagram.com/studio714_wellness/")
    html = html.replace("https://www.facebook.com/profile.php?id=61581823811677",
                        "https://www.facebook.com/studio714lp")

    # 7 — The Apothecary feature and the Mind the Truth block both restate what
    #     the doors index above already covers, so both come out. (This also
    #     retires "It's Not Yoga", which shared the second block.)
    for opener in ('<section class="apothecary-feature editorial-width">',
                   '<section class="dual-feature editorial-width">'):
        span = find_block(html, opener, "section")
        if span:
            html = html[:span[0]] + html[span[1]:]

    return html


if __name__ == "__main__":
    html = HOME.read_text(encoding="utf-8")
    out = edit(html)

    checks = {
        "mint hero":            'home-opening is-mint' in out,
        "goodfolk line gone":   "Each GoodFolk identity keeps" not in out,
        "learn more":           "Enter this chapter" not in out,
        "reviews slot":         'data-embed="google-reviews"' in out,
        "old stories gone":     "Restoration is personal" not in out,
        "doors list":           out.count('class="door-row') == len(DOORS),
        "logo rows":            out.count("has-logo") == sum(1 for d in DOORS if d.get("logo")),
        "yoga gone":            "Not Yoga" not in out,
        "apothecary block gone": "apothecary-feature" not in out,
        "mind block gone":      "dual-feature" not in out,
        "goodfolk grid gone":   "goodfolk-chapter" not in out,
        "featured block gone":  "featured-modality" not in out,
        "instagram updated":    "studio714official" not in out,
        "facebook updated":     "profile.php?id=" not in out,
    }
    for k, ok in checks.items():
        print(("  ok  " if ok else "  FAIL ") + k)
    if not all(checks.values()):
        sys.exit("edits did not fully apply")

    HOME.write_text(out, encoding="utf-8")
    print("home page updated")
