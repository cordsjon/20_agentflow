# gtxs.eu — Static Site Publishing Infrastructure

## Overview

**gtxs.eu** is the public-facing portfolio site for jcords projects. It hosts project showcases, documentation pages, and use-case writeups as static HTML deployed via FTP.

- **Live URL:** `https://gtxs.eu/projects/`
- **Mirror:** `https://getaccess.cloud/` (VPS rsync)
- **Deploy repo:** `~/projects/deploy/`

## Architecture

```
~/projects/deploy/
├── deploy.sh          # CLI deploy manager (add/remove/build/push)
├── site.json          # Project registry (title, slug, description, date, github)
├── .env               # FTP + VPS credentials (gitignored)
├── .env.example       # Credential template
└── site/
    ├── index.html     # Auto-generated from site.json via `deploy.sh build`
    └── projects/
        ├── convergence/index.html
        ├── sidequest/index.html + screenshot.png
        ├── keto/index.html + screenshot.png + sources.html
        ├── shepherd/index.html + screenshot.png + pipeline.html + skills-in-action.html
        └── ai-use-cases/
            ├── index.html              # Section landing page (3 cards)
            ├── claude-code.html        # Claude Code use case
            ├── claude-for-excel.html   # Claude for Excel use case
            └── notebook-lm.html        # NotebookLM use case
```

## Deploy Commands

```bash
cd ~/projects/deploy

# Register a new project page
./deploy.sh add "Project Name" --source ./path/to/page.html [--slug slug] [--desc "..."]

# Remove a project
./deploy.sh remove <slug>

# List registered projects
./deploy.sh list

# Rebuild index.html from site.json
./deploy.sh build

# Rebuild + FTP upload to gtxs.eu
./deploy.sh push

# Rebuild + rsync to VPS (getaccess.cloud)
./deploy.sh push-vps

# Rebuild + upload to both targets
./deploy.sh push-all

# Preview locally
./deploy.sh preview
```

## Adding Content from Any Project

Each project can publish pages to gtxs.eu. The workflow:

1. **Create an HTML page** in your project (self-contained, single-file preferred)
2. **Register it** via `~/projects/deploy/deploy.sh add "Title" --source ./your-page.html --slug your-slug`
3. **Deploy** via `~/projects/deploy/deploy.sh push` (FTP) or `push-all` (FTP + VPS)

The deploy script copies the HTML + any local assets (CSS, JS, images) into `site/projects/<slug>/`.

## Design System

All pages follow a consistent dark-theme design:

- **Fonts:** DM Serif Display (headings), Source Sans 3 (body), IBM Plex Mono (code/mono)
- **Colors:** `--bg-deep: #0a0c10`, `--accent-teal: #48c7b0`, `--accent-amber: #f0b957`, `--accent-blue: #5b9cf5`
- **Pattern:** CSS custom properties, grid cards, fadeUp animations, glassmorphism nav
- **Responsive:** Mobile breakpoint at 600px

## site.json Registry

The `site.json` file controls what appears on the index page. Structure:

```json
{
  "site_title": "jcords",
  "site_tagline": "Projects & Experiments",
  "projects": [
    {
      "title": "Display Name",
      "slug": "url-slug",
      "description": "Card description text.",
      "date": "YYYY-MM-DD",
      "github": "https://github.com/..."  // optional
    }
  ]
}
```

## Credentials

Stored in `~/projects/deploy/.env` (gitignored):

- `FTP_HOST` / `FTP_USER` / `FTP_PASS` / `FTP_REMOTE_DIR` — Hostinger FTP for gtxs.eu
- `VPS_HOST` / `VPS_USER` / `VPS_PATH` / `VPS_KEY` — SSH/rsync to getaccess.cloud

## Current Projects (as of 2026-03-15)

| Slug | Title | Subpages |
|------|-------|----------|
| ai-use-cases | AI Use Cases | claude-code, claude-for-excel, notebook-lm |
| convergence | Convergence | - |
| sidequest | Sidequest (ASES) | - |
| keto | KETO Data Foundation | sources |
| shepherd | Shepherd / Agentflow | pipeline, skills-in-action |
