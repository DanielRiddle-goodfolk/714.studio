#!/usr/bin/env python3
"""Screenshot every page and compare against a reference set, pixel by pixel."""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parent.parent
mode = sys.argv[1]                      # "capture" or "compare"
outdir = Path(f"/tmp/shots-{mode if mode=='capture' else 'after'}")
outdir.mkdir(exist_ok=True)

pages = ["/"] + sorted(
    "/" + str(p.parent.relative_to(ROOT)) + "/"
    for p in ROOT.rglob("index.html") if p.parent != ROOT)

with sync_playwright() as pw:
    b = pw.chromium.launch()
    for url in pages:
        p = b.new_page(viewport={"width": 1440, "height": 1000})
        p.goto("http://localhost:8714" + url, wait_until="networkidle", timeout=30000)
        p.wait_for_timeout(600)
        name = (url.strip("/").replace("/", "_") or "home") + ".png"
        p.screenshot(path=str(outdir / name), full_page=True)
        p.close()
    b.close()

if mode == "compare":
    ref = Path("/tmp/shots-capture")
    worst = []
    for f in sorted(outdir.glob("*.png")):
        r = ref / f.name
        if not r.exists():
            print("  no reference:", f.name); continue
        a, c = Image.open(r).convert("RGB"), Image.open(f).convert("RGB")
        if a.size != c.size:
            worst.append((999.0, f.name, f"size {a.size} -> {c.size}")); continue
        diff = ImageChops.difference(a, c)
        bbox = diff.getbbox()
        pct = 0.0 if not bbox else (
            sum(1 for px in diff.getdata() if px != (0, 0, 0)) / (a.size[0]*a.size[1]) * 100)
        worst.append((pct, f.name, "identical" if pct == 0 else f"{pct:.3f}% pixels differ"))
    worst.sort(reverse=True)
    for pct, name, note in worst:
        flag = "OK  " if pct == 0 else ("WARN" if pct < 0.5 else "FAIL")
        print(f"{flag} {name:<34} {note}")
    print("\nall identical" if all(p == 0 for p, _, _ in worst) else "\nDIFFERENCES FOUND")
