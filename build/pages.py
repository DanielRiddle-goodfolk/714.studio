#!/usr/bin/env python3
"""
Build the 16 interior pages the Manus export linked to but never shipped.

The export's app bundle (/assets/index-*.js) came down as 0 bytes, so the copy
for these routes is gone. The *stylesheet* survived intact, though, and it still
carries complete rules for every page — .first-visit-faq, .membership-options,
.chamber-what, .team-index and so on. Those class names are the floor plan, so
each page here is built from classes that genuinely exist in the CSS rather than
invented markup that would render unstyled.

Editorial rule, carried over from the home page's own stated stance: this file
does not invent prices, class schedules, staff bios, or testimonials. Where a
real business fact is needed, the page says so plainly and points at the Studio.
Search for NEEDS-STUDIO-INPUT to find every such spot.
"""
from pathlib import Path
import html as _html
import re

ROOT = Path(__file__).resolve().parent.parent


def _shell() -> tuple[str, str]:
    """Slice the shared header and footer straight out of the home page.

    These used to be committed as build/_head.html and build/_foot.html, which
    meant they could drift: an edit to index.html left the interior pages still
    carrying the old header. Deriving them on every build makes that impossible.
    """
    home = (ROOT / "index.html").read_text(encoding="utf-8")
    open_tag, close_tag = '<main id="main-content">', "</main>"
    try:
        i = home.index(open_tag)
        j = home.index(close_tag) + len(close_tag)
    except ValueError as exc:                      # pragma: no cover
        raise SystemExit(
            "index.html has no <main id=\"main-content\"> … </main> block; "
            "the interior pages cannot be assembled without it") from exc
    return home[:i], home[j:]


HEAD, FOOT = _shell()

PHONE = "(219) 809-2028"
TEL = "tel:+12198092028"
EMAIL = "hello@714.studio"
BOOK = "https://714.studio"          # existing Squarespace booking, per the home page

IMG = {
    "hero":      "/images/studio714_hero_apothecary_bd122de0.svg",
    "chamber":   "/images/studio714_wellness_chamber_v2_6e08f656.svg",
    "hands":     "/images/studio714_hands_apothecary_v2_470a7799.svg",
    "movement":  "/images/studio714_movement_breath_v2_11fe1e27.svg",
    "sauna":     "/images/current_sauna_409b73d6.svg",
    "nervous":   "/images/current_nervous_system_c083cb8d.svg",
    "boots":     "/images/studio714_compression_boots.svg",
    "root":      "/images/studio714_root_system_v2_15159731.svg",
    "l_apoth":   "/images/logo_apothecary_554918b9.svg",
    "l_mind":    "/images/logo_mind_the_truth_1f88ac61.svg",
    "l_massage": "/images/logo_get_well_massage_343812ef.svg",
    "l_reclaim": "/images/logo_reclaim_health_spa_09abc004.svg",
}

ARROW = ('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" '
         'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
         'stroke-linejoin="round" class="lucide lucide-arrow-right" aria-hidden="true">'
         '<path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg>')
# External links get the same arrow as internal ones. The up-right "leaves the
# site" variant was removed at Will's request — see strip_external_icons in
# build/inject.py, which also cleans the committed home page.
ARROW_UR = ARROW


# ---------------------------------------------------------------- helpers

def link(href, label, external=False):
    if external:
        return (f'<a class="editorial-link" href="{href}" target="_blank" rel="noreferrer">'
                f'<span>{label}</span>{ARROW_UR}</a>')
    return f'<a href="{href}" class="editorial-link"><span>{label}</span>{ARROW}</a>'


def action(href, label, style="ink", external=False):
    ext = ' target="_blank" rel="noreferrer"' if external else ""
    return (f'<a class="action-link action-{style}" href="{href}"{ext}>{label}'
            f'{ARROW_UR if external else ARROW}</a>')


def chapter(num, label):
    return (f'<div class="chapter-label"><span class="chapter-number">{num}</span>'
            f'<span>{label}</span></div>')


def intro(label, heading, body, align="left"):
    return (f'<div class="section-intro section-intro-{align}">'
            f'<p class="utility-label">{label}</p><h2>{heading}</h2>'
            f'<div class="section-intro-copy"><p>{body}</p></div></div>')


def faq(items):
    rows = "".join(
        f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in items)
    return f'<div class="faq-static-list">{rows}</div>'


def opening(h1, lead, img, alt, caption=None, logo=None):
    """The split hero used by most interior pages."""
    cap = f"<figcaption>{caption}</figcaption>" if caption else ""
    mark = f'<img class="page-parent-logo" alt="" src="{logo}">' if logo else ""
    return (f'<section class="page-opening"><div class="page-opening-copy">{mark}'
            f"<h1>{h1}</h1><p>{lead}</p></div>"
            f'<figure><img alt="{alt}" src="{img}">{cap}</figure></section>')


def simple_opening(label, h1, lead):
    return (f'<section class="simple-page-opening"><div class="editorial-width">'
            f'<p class="utility-label">{label}</p><h1>{h1}</h1><p>{lead}</p></div></section>')


def closer(heading, body, actions):
    return (f'<section class="editorial-width" style="padding-block:var(--s714-section)">'
            f'<div class="first-visit-final"><div><h2>{heading}</h2></div>'
            f'<div><p>{body}</p><div class="opening-actions" style="margin-top:1.75rem">'
            f"{actions}</div></div></div></section>")


NOTE = ('<p class="marginal-note"><strong>NEEDS-STUDIO-INPUT.</strong> {}</p>')


def build(slug, title, description, main, nav_key=None):
    """Assemble a page from the shared shell and write it to disk."""
    head = HEAD
    head = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", head, flags=re.S)
    head = re.sub(r'(<meta name="description" content=")[^"]*(")',
                  lambda m: m.group(1) + _html.escape(description, quote=True) + m.group(2), head)
    head = re.sub(r'(<meta property="og:title" content=")[^"]*(")',
                  lambda m: m.group(1) + _html.escape(title, quote=True) + m.group(2), head)

    # Mark the active nav item so the header reflects where you are
    if nav_key:
        head = head.replace(f'href="{nav_key}" class="desktop-nav-link"',
                            f'href="{nav_key}" class="desktop-nav-link" aria-current="page"')

    doc = head + '<main id="main-content">' + main + "</main>" + FOOT

    out = ROOT / (("index.html" if slug == "/" else slug.strip("/") + "/index.html"))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    return out
