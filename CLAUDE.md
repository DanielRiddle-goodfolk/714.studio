# Studio 7:14 — notes for Claude

Read this before editing anything in this repo.

Two rules are absolute: **never invent business facts**, and **never commit to
`main`** — every change opens a branch and a pull request. Both are spelled out
below.

## What this is

A static site for Studio 7:14, a faith-rooted whole-person wellness studio at
714 Lincoln Way, La Porte, Indiana. Seventeen pages, plain HTML, no framework.

The live public site is still Squarespace at `714.studio`. DNS has not been cut
over. Deploying is not launching.

---

## The rule that matters most

**Do not invent business facts.** Not prices, not class schedules, not staff
names or bios, not testimonials, not session lengths, not policies, not
credentials. Every place that needs one is marked `NEEDS-STUDIO-INPUT` and says
so on the page itself.

This is not caution for its own sake. It is a real client's business, and a
plausible-looking invented price is far more damaging than an obvious gap — a
gap gets filled, a wrong number gets believed and quoted back at the Studio by
a customer. The original Manus build set this rule for itself and it holds.

Count `NEEDS-STUDIO-INPUT` before and after any change. It should only go down,
and only because a real answer arrived from the Studio.

**Related:** modality copy describes what an experience *is* and what it
*supports*. It never claims to treat, cure, or diagnose. `/mind-the-truth/` and
`/apothecary-consultation/` carry explicit scope notices — biblical counseling
is not psychotherapy, Apothecary guidance is not medical advice. Keep them.

---

## Pages are generated. Do not hand-edit them.

The 16 interior pages are built at deploy time and are **gitignored**. Editing
`wellness/pemf/index.html` directly accomplishes nothing: the next build
overwrites it, and the change is invisible in the pull request.

```
build/clean.py            index.html  <- the original Manus DOM capture (local only)
build/edits.py            index.html  <- post-capture edits (mint header, doors list…)
build/content.py          the 16 interior pages
build/inject.py           shared shell, mobile menu, asset links — every page
build/placeholders_svg.py placeholder artwork
build/preview.py          bundles all pages into one file for review
build/verify_css.py       screenshot every page, compare pixel-for-pixel
build/purge_css.py        UNSAFE — see below
```

Netlify runs only the middle two:

```bash
python3 build/content.py && python3 build/inject.py
```

Locally, run those two after any content change. `clean.py` needs the Manus
capture, which isn't committed; on a clean checkout it prints a notice and
leaves `index.html` alone, which is correct.

`edits.py` self-checks and exits non-zero if any of its edits failed to apply,
so a silently-missed change surfaces immediately rather than at review.

### Where to change what

| To change | Edit |
|---|---|
| Home page structure or copy | `build/edits.py` |
| The doors list — order, logos, descriptions | `DOORS` in `build/edits.py` |
| A modality's copy | `MODALITIES` in `build/content.py` |
| Any other interior page | its `page_*()` function in `build/content.py` |
| Header, footer, mobile nav | `build/inject.py` |
| Styling | `css/site.css` — **never** `css/studio714.css` |

---

## The two stylesheets

`css/studio714.css` is the compiled artefact from the original Manus build, kept
**byte-for-byte unmodified**. It is the only surviving piece of that build and
still contains rules for pages whose source was lost. Treat it as read-only so
it can be diffed or replaced wholesale if the real source ever turns up.

`css/site.css` is everything added since. All overrides go here.

**`build/purge_css.py` is marked NOT SAFE TO RUN.** About 62% of the exported
stylesheet is unused Tailwind, and removing it would save ~75 KB — but a first
attempt cut it to 86 KB and collapsed the layout on every page (several lost a
third of their height, some gained horizontal overflow). Read the notes at the
top of that file before touching it, and verify with
`build/verify_css.py capture` → change → `build/verify_css.py compare`. Every
page must come back identical. A size reduction on its own means nothing.

---

## Two bugs that already happened here

Both were introduced by me and caught late. Worth knowing so they don't recur.

**Escaped quotes in a regex replacement.** `inject.py` used
`re.sub(..., r'\1 aria-controls=\"mobile-menu\"')` — inside an r-string, `\"`
stays as a literal backslash-quote. It wrote broken markup into the menu button
on every page, twice over. Guards are now plain containment checks
(`if 'x' not in html`) rather than regex de-duplication. Prefer that.

**Committed copies of derived files.** The shared header and footer were
committed as `build/_head.html` and `build/_foot.html`. Within a day they had
drifted — after images moved to SVG, the interior pages still pointed at dead
`.png` files. `build/pages.py` now slices them out of `index.html` on every
build. Don't reintroduce cached copies of things that can be derived.

---

## Conventions

- The brand is **Studio 7:14**, with the colon, throughout.
- Plain declarative style. No exclamation marks, no marketing verbs ("unlock",
  "elevate", "transform"), no hype. Short sentences.
- Numbers (`01`, `02`) are editorial ornament, set in `--s714-apple`.
- Every interior page ends with a closing block offering a next step.
- Placeholder images are SVG, named with the original Manus stems. When real
  artwork arrives, references update in two places only: `IMG` in
  `build/pages.py` and `DOORS` in `build/edits.py`.
- **It's Not Yoga** is not a current offering and was removed. Classes & Events
  remains, just unbranded.

---

## Workflow — every edit goes through a branch

**Never commit to `main`.** No direct pushes, no API writes to `main`, no
"quick fix" on the default branch. This applies to every change without
exception: one-line fixes, typo corrections, documentation, and this file
itself. A change that seems too small to branch for is exactly the kind that
gets merged without a deploy preview and breaks a page.

Every edit follows the same path:

1. **Branch off `main`** — name it for the change (`fix/…`, `content/…`,
   `build/…`).
2. **Commit to that branch only.**
3. **Open a pull request** against `main`, describing what changed and which
   pages it affects.
4. **Check the Netlify deploy preview** — open the affected pages on it, don't
   just confirm the build went green.
5. **Human approval**, then **squash merge**.

Write access to `main` is not permission to use it — GitHub enforces the rule,
but the rule stands whether or not the enforcement is in place at that moment.
If creating a branch or opening a pull request fails, stop and say so; do not
fall back to committing on `main`.

Required approvals is **one**, and GitHub won't let anyone approve their own
pull request. So a pull request opened through the API on the owner's behalf
has to be approved by the other collaborator account, and vice versa. The
Netlify deploy preview check must pass as well.

The practical consequence: **an agent cannot merge its own work.** Claude opens
the pull request, checks the deploy preview, and stops there. A human reviews
and squash merges. Don't treat a green build as approval.

(This was zero while the repo had a single owner, who would otherwise have been
locked out of his own repo. It moved to one once there were two accounts.)

**Never enable "Require signed commits."** It rejects everything created through
the API and kills the workflow silently.

---

## Verifying a change

`build/verify_css.py` screenshots all 17 pages and compares them pixel-for-pixel
against a reference set. Use it for anything touching CSS or shared markup:

```bash
python3 -m http.server 8714 &
python3 build/verify_css.py capture     # before
# … make the change, rebuild …
python3 build/verify_css.py compare     # after
```

For content changes, check that internal links still resolve and that the
`NEEDS-STUDIO-INPUT` count went down rather than up.
