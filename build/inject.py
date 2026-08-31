#!/usr/bin/env python3
"""
Post-process every built page: wire in the stylesheet supplement, the behaviour
script, and the mobile menu markup the React sheet used to render.

Idempotent — safe to re-run after rebuilding pages.
"""
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def analytics_tag() -> str:
    """The GA4 script tag — emitted only for Netlify production builds.

    Two conditions, both required:
      GA_MEASUREMENT_ID   set in Netlify's environment variables
      CONTEXT=production  set by Netlify itself, per deploy context

    Gating on CONTEXT means deploy previews and branch builds never receive the
    tag at all, rather than receiving it and relying on a runtime check. This
    workflow produces a preview per pull request, so without that gate the real
    numbers would fill up with our own review traffic.

    js/analytics.js keeps a hostname guard anyway, as a second line of defence
    for local builds or a mis-set context.
    """
    gid = os.environ.get("GA_MEASUREMENT_ID", "").strip()
    if not gid:
        return ""
    if os.environ.get("CONTEXT", "").strip() != "production":
        return ""
    return f'<script src="/js/analytics.js" data-ga-id="{gid}" defer></script>'


NAV = [
    ("01", "/start-here/", "Start Here", False),
    ("02", "/wellness/", "Wellness", False),
    ("03", "https://714.studio/apothecary", "Apothecary", True),
    ("04", "/apothecary-consultation/", "Apothecary Consultation", False),
    ("05", "/mind-the-truth/", "Mind the Truth&reg;", False),
    ("06", "/membership/", "Membership", False),
    ("07", "/classes-events/", "Classes &amp; Events", False),
    ("08", "/about/", "About", False),
    ("09", "/first-visit/", "First Visit / FAQ", False),
    ("10", "/contact/", "Contact", False),
]

X = ('<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" '
     'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
     'stroke-linejoin="round" aria-hidden="true"><path d="M18 6 6 18"></path>'
     '<path d="m6 6 12 12"></path></svg>')


EXTERNAL_ATTRS = ' target="_blank" rel="noreferrer"'


def strip_external_icons(html: str) -> str:
    """Remove the "this link leaves the site" indicators.

    The Manus build marked external links two ways: a box-and-arrow badge
    (lucide-external-link) beside the nav and footer text, and an up-right arrow
    (lucide-arrow-up-right, plus a literal ↗) where internal links get an
    ordinary right arrow. Will asked for both gone.

    This lives here rather than in edits.py because inject.py is the one step
    that touches every page — the home page, which is committed, and the sixteen
    generated at build time. Putting it anywhere else would mean doing it twice.

    The badge is deleted outright: it sat beside text and carried nothing else.
    The up-right arrows become ordinary right arrows rather than disappearing,
    so those rows keep the same affordance as the internal rows beside them.

    Purely visual. target="_blank" is untouched, so these links still open in a
    new tab; there is simply no longer a glyph announcing it.
    """
    html = re.sub(
        r'<svg[^>]*class="[^"]*lucide-external-link[^"]*".*?</svg>', "", html, flags=re.S)

    html = re.sub(
        r'(<svg[^>]*class="[^"]*)lucide-arrow-up-right([^"]*"[^>]*>)'
        r'<path d="M7 7h10v10"></path><path d="M7 17 17 7"></path></svg>',
        r'\1lucide-arrow-right\2<path d="M5 12h14"></path>'
        r'<path d="m12 5 7 7-7 7"></path></svg>', html)

    # Some up-right arrows carry no class at all (the doors index builds its own).
    html = re.sub(
        r'<svg([^>]*)><path d="M7 7h10v10"></path><path d="M7 17 17 7"></path></svg>',
        r'<svg\1><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg>', html)

    return html.replace("↗", "→")


def menu_markup():
    rows = "".join(
        '<div class="mobile-nav-row">'
        f"<span>{n}</span>"
        f'<a class="mobile-nav-link" href="{href}"{EXTERNAL_ATTRS if ext else ""}>'
        f'{label}</a>'
        "</div>"
        for n, href, label, ext in NAV)
    return (
        '<div class="mobile-menu-scrim" hidden></div>'
        '<aside id="mobile-menu" class="mobile-menu-panel" role="dialog" aria-modal="true" '
        'aria-label="Site navigation" hidden>'
        '<div class="mobile-menu-heading">'
        '<img alt="Studio 7:14 — Wellness by Design" src="/images/logo_studio_714_810622d5.svg">'
        f'<button class="menu-close" type="button" aria-label="Close navigation">{X}</button>'
        "</div>"
        f'<nav class="mobile-navigation" aria-label="Primary navigation">{rows}</nav>'
        '<a class="action-link action-ink mobile-book" href="/book/">Book Now</a>'
        '<p class="mobile-menu-note">714 Lincoln Way, La Porte · 7am–7pm daily</p>'
        "</aside>"
    )


def patch(path: Path) -> bool:
    html = path.read_text(encoding="utf-8")
    orig = html

    # stylesheet supplement, right after the exported stylesheet
    if "/css/site.css" not in html:
        html = html.replace(
            '<link rel="stylesheet" href="/css/studio714.css">',
            '<link rel="stylesheet" href="/css/studio714.css">\n'
            '    <link rel="stylesheet" href="/css/site.css">', 1)

    # mobile menu markup + script, just before </body>
    if 'id="mobile-menu"' not in html:
        html = html.replace("</body>", menu_markup() + '<script src="/js/site.js"></script></body>', 1)

    # GA4, production builds only. Idempotent: a rebuild neither duplicates the
    # tag nor leaves a stale one behind if the environment variable is removed.
    html = re.sub(r'<script src="/js/analytics\.js"[^>]*></script>', "", html)
    tag = analytics_tag()
    if tag:
        html = html.replace("</body>", tag + "</body>", 1)

    # The menu trigger needs to point at the panel. Guard on the attribute
    # already being present rather than de-duplicating afterwards: the previous
    # regex used an r-string replacement containing \" and wrote literal
    # backslashes into the markup, twice over.
    if 'aria-controls="mobile-menu"' not in html:
        html = html.replace(
            '<button class="menu-trigger" type="button"',
            '<button class="menu-trigger" type="button" aria-controls="mobile-menu"', 1)

    # no "leaves the site" indicators on any page
    html = strip_external_icons(html)

    # the scrim should not be hidden-attr'd (CSS handles visibility)
    html = html.replace('<div class="mobile-menu-scrim" hidden></div>',
                        '<div class="mobile-menu-scrim"></div>')

    if html != orig:
        path.write_text(html, encoding="utf-8")
        return True
    return False


if __name__ == "__main__":
    n = 0
    for p in sorted(ROOT.rglob("index.html")):
        if patch(p):
            n += 1
            print("patched", p.relative_to(ROOT))
    print(f"{n} page(s) updated")
