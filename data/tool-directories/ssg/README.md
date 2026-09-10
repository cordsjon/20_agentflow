# ssg — site generator tooling

Hand-curated catalog of static site generators and adjacent publishing tooling, kept as a
general toolbox: *what can I reach for when a site needs building?*

**This directory is hand-written and git-tracked.** Its siblings (`nosignups/`,
`public-apis/`) are generated sinks rewritten weekly by the `nosignups-catalog-sync` DAG and
are gitignored. The root `.gitignore` uses `data/tool-directories/*` (not a trailing slash)
specifically so this subdir can be re-included — git cannot negate a path whose parent
directory is excluded by a trailing-slash pattern.

Indexed by QMD under the `tool-directories` collection, so entries are searchable with no
config change.

## Entry format

One `.md` per tool. Keep the 9-key frontmatter contract identical to the sibling catalogs —
consistency is what makes cross-collection filtering work. Use `null` for absent values;
never omit a key.

```yaml
---
name: "Tool Name"
source: "manual"          # or the catalog it was imported from
url: "https://..."        # primary/homepage
github: null              # repo URL if distinct from url, else null
license: "MIT"            # read the LICENSE file; Codeberg/Gitea APIs report null wrongly
stars: 0                  # honest count — low stars is a real signal, not a defect
category: "site-generator"
tags: ["input:csv", "deps:stdlib-only"]
kind: "cli"               # cli | js-lib | self-host | browser-only | service
---
```

## Tag facets

Free-form, but prefer these `key:value` facets so the three toolbox questions stay answerable
from frontmatter alone:

| Facet | Answers | Example values |
|---|---|---|
| `input:` | what feeds it | `csv`, `markdown`, `mdx`, `json`, `headless-cms` |
| `output:` | what it emits | `single-file`, `multi-page`, `spa`, `hybrid` |
| `deps:` | dependency weight | `stdlib-only`, `none`, `node`, `heavy` |
| `js:` | client-side JS | `none`, `optional`, `required` |
| `editable-by:` | who can update content | `non-dev`, `dev`, `superuser` |
| `hosting:` | deploy target | `static-upload`, `cdn`, `node-server`, `self-host` |
| `usecase:` | shape of site | `storefront`, `blog`, `docs`, `portfolio` |
| `maturity:` | community risk | `solo-young`, `established`, `enterprise` |

## Body

Short prose. Lead with what it is, then a **why it's in the toolbox** line, then honest
caveats, then how it compares to something already in use. Caveats are the part that saves
time later — record them even when the tool looks good.

## Adding an entry

Manual for now. If a third entry costs the same fetch-and-transcribe work, that is the
signal to write a small `add <url>` script, not before.
