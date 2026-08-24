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
UR = ('<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" '
      'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
      'stroke-linejoin="round" aria-hidden="true"><path d="M7 7h10v10"></path>'
      '<path d="M7 17 17 7"></path></svg>')


EXTERNAL_ATTRS = ' target="_blank" rel="noreferrer"'


def menu_markup():
    rows = "".join(
        '<div class="mobile-nav-row">'
        f"<span>{n}</span>"
        f'<a class="mobile-nav-link" href="{href}"{EXTERNAL_ATTRS if ext else ""}>'
        f'{label}{UR if ext else ""}</a>'
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
