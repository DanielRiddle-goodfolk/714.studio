#!/usr/bin/env python3
"""
Turn the Manus rendered-DOM export into clean, hand-editable static HTML.

What it strips:
  - data-loc="..."          (Manus/Vite source-map breadcrumbs)
  - the Manus previewer root div, runtime scripts, dark-mode shim <link>/<style>
  - the sonner/toast <section> React mounts
  - the #root wrapper (we keep its children)
What it rewrites:
  - /manus-storage/<file>   ->  /images/<file>
  - /assets/*.css           ->  /css/studio714.css
Also pretty-prints so a human can actually edit the result.
"""
import os
import re
import sys
from pathlib import Path

SRC = Path(os.environ.get("MANUS_CAPTURE",
                          "/mnt/user-data/uploads/manus-site-full/index.html"))
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "index.html"

# Tags we let sit on one line rather than exploding (inline / void / text-ish)
INLINE = {
    "a", "span", "strong", "em", "b", "i", "small", "sup", "sub", "code",
    "br", "img", "svg", "path", "circle", "line", "polyline", "figcaption",
    "p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "button", "label",
}
VOID = {"br", "img", "input", "meta", "link", "hr", "source"}


def strip_noise(html: str) -> str:
    # Manus previewer mount + runtime
    html = re.sub(r'<div id="manus-previewer-root"[^>]*>\s*</div>', "", html)
    html = re.sub(r'<script id="manus-runtime">.*?</script>', "", html, flags=re.S)
    html = re.sub(r'<script[^>]*manus-analytics[^>]*>\s*</script>', "", html)
    html = re.sub(r'<script[^>]*jszip[^>]*>\s*</script>', "", html)

    # All remaining scripts: this is a static site, the React bundle is dead weight
    html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.S)

    # Dark-mode extension shims that a browser extension injected into the capture
    html = re.sub(r'<link[^>]*id="dark-mode-[^"]*"[^>]*>', "", html)
    html = re.sub(r'<style[^>]*id="dark-mode-[^"]*"[^>]*>.*?</style>', "", html, flags=re.S)

    # Toast/notification React mount points — no JS, so they're inert markup
    html = re.sub(r'<section aria-label="Notifications[^>]*>\s*</section>', "", html)

    # Every inlined <style> block: it's all duplicated in the stylesheet we kept
    html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.S)

    # Vite/Manus source breadcrumbs on literally every element
    html = re.sub(r'\s*data-loc="[^"]*"', "", html)

    # Radix leftovers that only mean something with JS attached
    html = re.sub(r'\s*(aria-controls|data-state|data-slot)="[^"]*"', "", html)

    # Unwrap #root — keep children, drop the React mount div
    html = re.sub(r'<div id="root">', "", html, count=1)

    return html


def rewrite_paths(html: str) -> str:
    # Placeholders are SVG (see build/placeholders_svg.py), so the extension
    # is remapped here too. Real artwork later goes back to .jpg/.png.
    html = re.sub(r"/manus-storage/([A-Za-z0-9_]+)\.(?:png|jpe?g)",
                  r"/images/\1.svg", html)
    html = re.sub(r'<link rel="stylesheet"[^>]*href="/assets/[^"]*\.css"[^>]*>',
                  '<link rel="stylesheet" href="/css/studio714.css">', html)
    html = html.replace(' crossorigin=""', "")
    return html


def prettify(html: str) -> str:
    """Light-touch indenter. Block tags get their own line; inline tags stay put."""
    # Give block-level tags a newline to breathe
    html = re.sub(r"(<(?:div|section|header|footer|main|nav|article|figure|body|head|html)\b)",
                  r"\n\1", html)
    html = re.sub(r"(</(?:div|section|header|footer|main|nav|article|figure|body|head|html)>)",
                  r"\1\n", html)

    lines = [ln.strip() for ln in html.split("\n")]
    out, depth = [], 0
    for ln in lines:
        if not ln:
            continue
        # A closing tag at line start un-indents before printing
        if re.match(r"</(div|section|header|footer|main|nav|article|figure|body|head|html)>", ln):
            depth = max(0, depth - 1)
        out.append("  " * depth + ln)
        # An opening tag (not self-closed, not also-closed on this line) indents after
        opens = len(re.findall(r"<(div|section|header|footer|main|nav|article|figure|body|head|html)\b", ln))
        closes = len(re.findall(r"</(div|section|header|footer|main|nav|article|figure|body|head|html)>", ln))
        depth += max(0, opens - closes)
    return "\n".join(out)


def main() -> None:
    if not SRC.exists():
        # The capture is a local artefact, not committed. On a clean checkout
        # index.html is already present and this step is simply skipped.
        print(f"no Manus capture at {SRC} — leaving index.html as committed")
        return
    html = SRC.read_text(encoding="utf-8")
    before = len(html)

    html = strip_noise(html)
    html = rewrite_paths(html)
    html = prettify(html)

    # Add the doctype the capture dropped, plus font preconnects
    html = html.replace(
        "<head>",
        '<head>\n    <link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
        1,
    )
    if not html.lstrip().startswith("<!DOCTYPE"):
        html = "<!DOCTYPE html>\n" + html.lstrip()

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"{before:,} bytes  ->  {len(html):,} bytes")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
