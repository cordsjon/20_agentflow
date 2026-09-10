---
name: "MicroStore"
source: "manual"
url: "https://codeberg.org/Marking-Time/MicroStore"
github: null
license: "MIT"
stars: 1
category: "site-generator"
tags: ["input:csv", "output:single-file", "deps:stdlib-only", "js:none", "editable-by:non-dev", "hosting:static-upload", "usecase:storefront", "maturity:solo-young"]
kind: "cli"
---

Python CLI that reads a local CSV data store and emits one self-contained `index.html`
(embedded CSS, no JavaScript) for a small brick-and-mortar store front.

**Why it's in the toolbox:** the extreme low end of the SSG spectrum — no framework, no
package manager, no build pipeline, no domain required. Stdlib-only Python 3.4+. Output is a
single file plus an `/img` folder, uploadable through a hosting provider's web UI by someone
who has never used a terminal for anything else.

**Client-deliverable read:** the strongest fit is a client who must self-update via a
spreadsheet and cannot absorb ongoing build/hosting cost. Data lives in `data/store.csv` and
`data/products.csv`, edited in any spreadsheet app; a `sale` cell drives an optional sales
section; an `img` cell wires a product photo. Requires two initial runs (first scaffolds
directories and yields a blank page, second populates).

**Caveats:** 1 star, created 2026-07-26, single author — no community, you own any bug you
hit. No incremental build, no templating layer, no i18n. Trades all extensibility for
readability; the author's stated goal is that a superuser can edit the script directly.

**Compare against:** Astro (used on gtxs.eu/contexteng.de) sits at the opposite end —
content collections, Zod-typed frontmatter, node toolchain. MicroStore is what you reach for
when the toolchain itself is the cost you're trying to remove.
