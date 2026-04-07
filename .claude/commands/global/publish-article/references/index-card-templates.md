# Index Card Templates

When adding a new article, you MUST update the correct index files. Read the current index files first to get the latest counts, then apply these patterns.

## File Locations

- Claude Code index: `~/projects/deploy/site/projects/ai-use-cases/claude-code/index.html`
- AI Use Cases index: `~/projects/deploy/site/projects/ai-use-cases/index.html`

---

## 1. Claude Code Index — Case Card Format

Used in `claude-code/index.html`. Add new cards at the TOP of the `<div class="cases">` grid.

```html
<a class="case-card" href="{{slug}}.html">
  <div class="case-card__eyebrow">{{Category}} &middot; {{Subcategory}}</div>
  <h3>{{Article Title}}</h3>
  <p>{{1-2 sentence description}}</p>
  <div class="case-card__stats">
    <span class="case-card__stat"><strong>{{N}}</strong> {{metric}}</span>
    <span class="case-card__stat"><strong>{{N}}</strong> {{metric}}</span>
    <span class="case-card__stat"><strong>{{N}}</strong> {{metric}}</span>
  </div>
  <span class="arrow">&rarr;</span>
</a>
```

**Notes:**
- Eyebrow uses `&middot;` as separator
- Stats use `<strong>` for the number/value
- 2-3 stats per card

---

## 2. AI Use Cases Index — Card Format

Used in `ai-use-cases/index.html`. Add new cards inside the appropriate `<section class="group">`.

### For claude-code articles, add to the "Development & DevOps" section:

```html
<div class="card" onclick="window.location='claude-code/{{slug}}.html'" data-category="development" data-title="{{Full Title}}" data-date="{{YYYY-MM-DD}}">
  <div class="card__top">
    <span class="card__label">{{Category}} &middot; {{Subcategory}}</span>
    <span class="card__accent card__accent--teal"></span>
  </div>
  <h2>{{Article Title}}</h2>
  <p>{{1-2 sentence description}}</p>
  <div class="card__meta">
    <span class="tag">{{Tag1}}</span>
    <span class="tag">{{Tag2}}</span>
    <span class="tag">{{Tag3}}</span>
  </div>
  <span class="arrow">&rarr;</span>
</div>
```

### For top-level ai-use-cases articles:

```html
<div class="card" onclick="window.location='{{slug}}.html'" data-category="{{category}}" data-title="{{Full Title}}" data-date="{{YYYY-MM-DD}}">
  <div class="card__top">
    <span class="card__label">{{Category}} &middot; {{Subcategory}}</span>
    <span class="card__accent card__accent--{{color}}"></span>
  </div>
  <h2>{{Article Title}}</h2>
  <p>{{1-2 sentence description}}</p>
  <div class="card__meta">
    <span class="tag">{{Tag1}}</span>
    <span class="tag">{{Tag2}}</span>
    <span class="tag">{{Tag3}}</span>
  </div>
  <span class="arrow">&rarr;</span>
</div>
```

**Accent colors by category:**
- `development` → `card__accent--teal`
- `analysis` → `card__accent--amber`
- `architecture` → `card__accent--violet`
- `prototyping` → `card__accent--rose`
- `education` → `card__accent--blue`

---

## 3. Count Updates Checklist

Every time you add a card, update ALL of these:

### In `ai-use-cases/index.html`:
- [ ] Hero stats: `<strong>N</strong> use cases` — increment by 1
- [ ] Filter pill "All": `All <span class="count">N</span>` — increment by 1
- [ ] Filter pill for the category: e.g. `Development <span class="count">N</span>` — increment by 1
- [ ] Group header count: `<span class="group__count">N cases</span>` — increment by 1
- [ ] Footer: `Last updated YYYY-MM-DD` — set to today

### In `claude-code/index.html`:
- No counts to update (no count display in this index)

---

## 4. Category Mapping

| data-category | Group Section | Accent | Filter Pill |
|---|---|---|---|
| development | Development & DevOps | teal | Development |
| analysis | Analysis & Strategy | amber | Analysis |
| architecture | Architecture & Protocol | violet | Architecture |
| prototyping | Prototyping & Data | rose | Prototyping |
| education | Education & Research | blue | Education |

If an article doesn't fit these categories, you may need to create a new group section.
