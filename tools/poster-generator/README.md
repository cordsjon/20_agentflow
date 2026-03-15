# Poster Generator — Business Analysis PDF Tool

ReportLab-based DIN A1 poster generator for visual business analysis output.
Used by the `sh:poster-analysis` skill.

## Origin

Created for the STEUB use case project (10_STEUB-usecases) — Steuerberater Document Processing Pipeline analysis. The generator produces dark-themed, data-dense DIN A1 posters with:
- Architecture diagrams (pipeline steps)
- Module inventories
- Regulatory constraint tables
- Evolution roadmaps
- Checklist sections

## Usage

The generator at `generate_poster.py` is a **reference implementation** for the STEUB project. The `sh:poster-analysis` skill instructs the agent to create a project-specific generator adapted from this template.

## Dependencies

```bash
pip install reportlab
```

## Files

- `generate_poster.py` — STEUB reference implementation (produces 841×594mm PDF)
- `poster_template.py` — Reusable drawing primitives (extracted by skill)
