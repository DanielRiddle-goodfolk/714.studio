# Studio 7:14

Static site for Studio 7:14 — a faith-rooted whole-person wellness studio at
714 Lincoln Way, La Porte, Indiana.

Seventeen pages of plain HTML. No framework, no client-side routing, no
dependencies. The only JavaScript is ~90 lines driving the mobile menu.

**The live public site is still the Squarespace one at `714.studio`.** This repo
is its replacement, and DNS has not been cut over. Deploying here is not
launching; those are two separate decisions.

---

## Working on it

Nothing reaches `main` directly. Every change is a branch, a pull request, a
Netlify deploy preview, and a squash merge:

1. branch named `edit/short-description`
2. push, open a pull request
3. Netlify builds a preview at
   `https://deploy-preview-<PR>--<site>.netlify.app`
4. look at that preview on the device you actually care about
5. squash merge — each change becomes one revertible commit

To undo anything: every merge is a single commit, so a revert is one clean
pull request reviewed the same way.

### Rules the repo enforces

- **No direct pushes to `main`.** Enforced by GitHub, not by good intentions.
- **The Netlify build check must be green** before merge.
- **Required approvals: zero.** GitHub won't let you approve your own pull
  request, so requiring one would lock a solo owner out of his own site. The
  build check is the real gate.
- **Never enable "Require signed commits."** It silently rejects everything
  created through the API and kills the workflow.

---

## How the site is built

The 16 interior pages are **generated at deploy time**, not committed. Netlify
runs:

```bash
python3 build/content.py && python3 build/inject.py
```

That takes a few seconds and needs nothing installed.

This is deliberate. Committing the generated HTML meant 200 KB of near-identical
files, and — more annoying — a one-sentence copy change showed up in a pull
request as the same edit repeated across sixteen files. Now the diff shows the
sentence.

`index.html` **is** committed. It descends from the original Manus DOM capture,
which is a local artefact that isn't in the repo, so it counts as source rather
than output. `build/pages.py` slices the shared header and footer out of it on
every build, so the interior pages can't drift away from the home page.

### Where to change what

| To change | Edit |
|---|---|
| Home page structure or copy | `build/edits.py` |
| The doors list — order, logos, descriptions | `DOORS` in `build/edits.py` |
| A modality's copy | `MODALITIES` in `build/content.py` |
| Any other interior page | its `page_*()` function in `build/content.py` |
| Header, footer, mobile nav | `build/inject.py` |
| Styling | `css/site.css` — **never** `css/studio714.css` |

Don't hand-edit the generated HTML. The next build overwrites it.

### Running it locally

```bash
python3 build/content.py      # rebuild the 16 interior pages
python3 build/inject.py       # shared shell, mobile menu, asset links
```

Then double-click **START-PREVIEW.command**, which serves the folder and opens a
browser. Don't open `index.html` directly — pages link assets from the site root
(`/css/…`), and `file://` breaks every one of those links.

Two optional scripts:

```bash
python3 build/placeholders_svg.py   # regenerate placeholder artwork
python3 build/preview.py            # bundle all 17 pages into one shareable file
```

---

## The two stylesheets

`css/studio714.css` (161 KB) is the compiled artefact from the original Manus
build, kept **byte-for-byte unmodified**. It is the only surviving piece of that
build and still contains rules for pages whose source was lost. Treat it as
read-only.

`css/site.css` (11 KB) is everything added since — mobile menu positioning, the
mint header and hero, the doors index, button spacing, editorial helpers.

About 62% of the exported stylesheet is unused Tailwind utilities, and removing
them is worth ~75 KB. `build/purge_css.py` attempts exactly that and is **marked
unsafe** — a first pass cut it to 86 KB and broke the layout on every page. See
the notes at the top of that file before trying again. It isn't urgent.

---

## Where this site came from

The Manus export was a **rendered capture, not source code**:

| | |
|---|---|
| `index.html` (428 KB) | DOM snapshot of the **home page only**, CSS inlined |
| `css/index-*.css` (165 KB) | The **complete compiled stylesheet** — intact |
| `js/index-*.js` | **0 bytes.** The React app bundle never downloaded |
| `js/inline-script-0.js` (366 KB) | React runtime only — no app code, no content |
| images | **None.** All 16 pointed at `/manus-storage/` on Manus's server |

So the home page and the whole design system survived; the other pages did not.

The stylesheet is what made the rebuild possible. It still carries rules for
every page Manus built — `.first-visit-faq`, `.membership-options`,
`.chamber-what`, `.mind-scripture` — and those class names are a floor plan.
Each interior page here is built from classes that genuinely exist in the CSS,
rather than invented markup that would render unstyled.

---

## Two things still needed

### 1. Every image is a placeholder

The 16 files in `images/` are generated SVGs in the Studio's palette, each
labelled with what belongs in that slot. Vector rather than raster on purpose:
an SVG diff is readable in a pull request where a changed PNG is opaque, and the
whole set is 18 KB instead of 1.4 MB.

Filenames keep the original Manus stems, so real artwork drops in against an
obvious mapping. References live in exactly two places: `IMG` in
`build/pages.py` and `DOORS` in `build/edits.py`.

**If those images are still in the Manus project, exporting them is the single
highest-value next step.**

### 2. Twelve places need facts only the Studio has

Search for `NEEDS-STUDIO-INPUT`:

| Page | Needs |
|---|---|
| about | The story behind "7:14" · team names, roles, bios |
| first-visit | Cancellation policy · parking · accessibility |
| membership | Tier names, inclusions, pricing, freeze/cancel terms |
| classes-events | Live schedule, instructors, drop-in and package pricing |
| full-spectrum-chamber | Session length, pricing, contraindications |
| mind-the-truth | Session length, fees, counselor credentials |
| apothecary-consultation | Consultation length, fee, consultant credentials |
| book | Which booking platform wins |
| contact | Map embed + a real contact form |

None of these are guessed at. The Manus home page set that rule itself —
*"Current options, access, and pricing are confirmed directly through the Studio
rather than guessed inside this preview"* — and a plausible invented price is far
more damaging than an obvious gap. A gap gets filled; a wrong number gets
believed and quoted back.

---

## Decisions worth knowing

- **Naming.** The build uses **Studio 7:14** with the colon throughout. The live
  Squarespace site uses both forms. Worth settling before launch — it affects
  titles, meta, and structured data.
- **Medical claims.** Modality copy describes what an experience *is* and what it
  *supports*. It doesn't claim to treat, cure, or diagnose. `/mind-the-truth/`
  and `/apothecary-consultation/` carry explicit scope notices — biblical
  counseling isn't psychotherapy, Apothecary guidance isn't medical advice. Keep
  those.
- **No testimonials.** Real ones need consent. The home page has a marked embed
  slot (`data-embed="google-reviews"`) for live Google reviews instead.
- **Booking.** Every Book button points at the existing Squarespace scheduler at
  `714.studio`. Moving to per-page embeds is an open decision that touches every
  service page.
- **It's Not Yoga** was removed — not a current offering. Classes & Events
  remains; it's just no longer branded that way.
- **Old URLs.** `netlify.toml` carries 301s from the Squarespace paths so
  existing links and search results survive the cutover. Add to that list as more
  old URLs surface in Search Console.

---

## Structure

```
index.html              home — committed source
build/                  the scripts that generate everything else
css/studio714.css       Manus compiled CSS — read-only, byte for byte
css/site.css            everything added since
js/site.js              mobile menu, header scroll state, current-page marking
images/                 16 SVG placeholders
netlify.toml            build command, headers, redirects
CLAUDE.md               conventions and constraints for AI sessions
```

Generated at build time, and gitignored: `about/`, `apothecary-consultation/`,
`book/`, `classes-events/`, `contact/`, `first-visit/`, `membership/`,
`mind-the-truth/`, `start-here/`, `wellness/` (plus its five modality pages).
