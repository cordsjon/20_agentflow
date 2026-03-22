#!/usr/bin/env python3
"""
Reusable drawing primitives for DIN-format business analysis posters.
Import these into project-specific generator scripts.

Usage:
    from poster_template import PosterCanvas, DARK_THEME, A1_LANDSCAPE
"""

from reportlab.lib.pagesizes import A0, A1, A2
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
import math

# ─── Page formats (landscape) ────────────────────────────────────
A0_LANDSCAPE = (A0[1], A0[0])  # 1189 × 841 mm
A1_LANDSCAPE = (A1[1], A1[0])  # 841 × 594 mm
A2_LANDSCAPE = (A2[1], A2[0])  # 594 × 420 mm

# ─── Color themes ─────────────────────────────────────────────────
DARK_THEME = {
    "bg": "#0f1117", "card": "#1a1d27", "card2": "#141720",
    "blue": "#3b82f6", "cyan": "#06b6d4", "green": "#22c55e",
    "red": "#ef4444", "amber": "#f59e0b", "purple": "#a855f7",
    "pink": "#ec4899", "txt": "#f1f5f9", "txt2": "#94a3b8",
    "muted": "#64748b", "border": "#2a2d3a",
    "thead": "#1e293b", "trow": "#0f172a", "trow2": "#1a1f2e",
    "rbg": "#3b1117", "abg": "#3b2e0a", "gbg": "#0a2e1a",
    "bbg": "#0a1a3b", "hdr": "#0c0e14",
}

LIGHT_THEME = {
    "bg": "#ffffff", "card": "#f8fafc", "card2": "#f1f5f9",
    "blue": "#2563eb", "cyan": "#0891b2", "green": "#16a34a",
    "red": "#dc2626", "amber": "#d97706", "purple": "#9333ea",
    "pink": "#db2777", "txt": "#0f172a", "txt2": "#475569",
    "muted": "#94a3b8", "border": "#e2e8f0",
    "thead": "#1e293b", "trow": "#ffffff", "trow2": "#f8fafc",
    "rbg": "#fef2f2", "abg": "#fffbeb", "gbg": "#f0fdf4",
    "bbg": "#eff6ff", "hdr": "#0f172a",
}

SEVERITY_MAP = {
    "CRIMINAL": ("red", "rbg"), "MANDATORY": ("red", "rbg"),
    "BERUFSRECHT": ("amber", "abg"), "STEUERRECHT": ("amber", "abg"),
    "ZIVILRECHT": ("amber", "abg"), "BUSSGELD": ("red", "rbg"),
    "RECOMMENDED": ("green", "gbg"), "ADVISORY": ("green", "gbg"),
    "ORDNUNGSW.": ("amber", "abg"), "HIGH": ("red", "rbg"),
    "MEDIUM": ("amber", "abg"), "LOW": ("green", "gbg"),
}


class PosterCanvas:
    """High-level wrapper for generating business analysis posters."""

    def __init__(self, output_path, page_size=A1_LANDSCAPE, theme=None, margin=12*mm):
        self.page_w, self.page_h = page_size
        self.margin = margin
        self.theme = {k: HexColor(v) for k, v in (theme or DARK_THEME).items()}
        self.content_w = self.page_w - 2 * margin
        self.c = canvas.Canvas(output_path, pagesize=page_size)

        # Scale factor relative to A1 (for font size adaptation)
        self.scale = self.page_w / A1_LANDSCAPE[0]

    def color(self, name):
        return self.theme.get(name, self.theme["txt"])

    def font_size(self, base_size):
        """Scale font size proportionally to page format."""
        return base_size * self.scale

    # ─── Drawing primitives ───────────────────────────────────────

    def fill_background(self):
        self.c.setFillColor(self.color("bg"))
        self.c.rect(0, 0, self.page_w, self.page_h, fill=1, stroke=0)

    def rounded_rect(self, x, y, w, h, r=3*mm, fill="card", stroke=None, stroke_width=0.5):
        self.c.saveState()
        self.c.setFillColor(self.color(fill))
        if stroke:
            self.c.setStrokeColor(self.color(stroke))
            self.c.setLineWidth(stroke_width)
            self.c.roundRect(x, y, w, h, r, fill=1, stroke=1)
        else:
            self.c.roundRect(x, y, w, h, r, fill=1, stroke=0)
        self.c.restoreState()

    def arrow(self, x1, y1, x2, y2, color="muted", width=1.5):
        clr = self.color(color)
        self.c.saveState()
        self.c.setStrokeColor(clr); self.c.setLineWidth(width); self.c.setLineCap(1)
        self.c.line(x1, y1, x2, y2)
        a = math.atan2(y2-y1, x2-x1); al = 3*mm
        self.c.setFillColor(clr); p = self.c.beginPath()
        p.moveTo(x2, y2)
        p.lineTo(x2-al*math.cos(a-.3), y2-al*math.sin(a-.3))
        p.lineTo(x2-al*math.cos(a+.3), y2-al*math.sin(a+.3))
        p.close(); self.c.drawPath(p, fill=1, stroke=0)
        self.c.restoreState()

    def section_title(self, x, y, title, accent="blue", subtitle=None, size=16):
        sz = self.font_size(size)
        self.c.saveState()
        self.c.setFillColor(self.color(accent))
        self.c.rect(x, y-1, 50, 3.5, fill=1, stroke=0)
        self.c.setFillColor(self.color("txt"))
        self.c.setFont("Helvetica-Bold", sz)
        self.c.drawString(x, y-sz-3, title)
        ny = y - sz - 7
        if subtitle:
            self.c.setFillColor(self.color("txt2"))
            self.c.setFont("Helvetica", self.font_size(8.5))
            self.c.drawString(x, ny-2, subtitle)
            ny -= 12
        self.c.restoreState()
        return ny

    def text(self, x, y, text, color="txt", font="Helvetica", size=8, bold=False):
        self.c.saveState()
        self.c.setFillColor(self.color(color))
        fn = "Helvetica-Bold" if bold else font
        self.c.setFont(fn, self.font_size(size))
        self.c.drawString(x, y, text)
        self.c.restoreState()

    def word_wrap(self, text, font, size, max_width):
        sz = self.font_size(size)
        lines = [""]
        for word in text.split():
            test = lines[-1] + " " + word if lines[-1] else word
            if self.c.stringWidth(test, font, sz) < max_width:
                lines[-1] = test
            else:
                lines.append(word)
        return lines

    def severity_badge(self, x, y, severity, h=12):
        fg_name, bg_name = SEVERITY_MAP.get(severity, ("muted", "card"))
        sz = self.font_size(6.5)
        bw = self.c.stringWidth(severity, "Helvetica-Bold", sz) + 10
        self.c.saveState()
        self.c.setFillColor(self.color(bg_name))
        self.c.roundRect(x, y, bw, h, 2, fill=1, stroke=0)
        self.c.setFillColor(self.color(fg_name))
        self.c.setFont("Helvetica-Bold", sz)
        self.c.drawString(x+5, y+3, severity)
        self.c.restoreState()
        return bw

    # ─── Composite components ─────────────────────────────────────

    def pipeline_step(self, x, y, w, h, number, name, tool, short_desc, detail, accent="blue"):
        """Draw a pipeline step card with accent bar, title, tool, and detail text."""
        self.rounded_rect(x, y, w, h, fill="card")
        # Left accent bar
        self.c.saveState()
        self.c.setFillColor(self.color(accent))
        self.c.roundRect(x+1.5, y+4, 4, h-8, 2, fill=1, stroke=0)
        self.c.restoreState()

        label = f"{number}  {name}"
        self.text(x+12, y+h-14, label, color=accent, size=12, bold=True)
        self.text(x+12, y+h-26, tool, color="txt", size=9, bold=True)
        self.text(x+12, y+h-37, short_desc, color="cyan", size=8)

        lines = self.word_wrap(detail, "Helvetica", 7, w-24)
        for j, ln in enumerate(lines[:5]):
            self.text(x+12, y+h-50 - j*10, ln, color="txt2", size=7)

    def table_header(self, x, y, width, columns, col_widths):
        """Draw a table header row."""
        h = 16
        self.c.saveState()
        self.c.setFillColor(self.color("thead"))
        self.c.roundRect(x, y-h, width, h, 2, fill=1, stroke=0)
        self.c.setFillColor(self.color("blue"))
        sz = self.font_size(7.5)
        self.c.setFont("Helvetica-Bold", sz)
        cx = x + 4
        for j, col in enumerate(columns):
            self.c.drawString(cx, y-h+5, col)
            cx += col_widths[j]
        self.c.restoreState()
        return y - h

    def table_row(self, x, y, width, height, cells, col_widths, row_index=0):
        """Draw a table data row with alternating background."""
        bg = "trow2" if row_index % 2 == 0 else "trow"
        self.c.saveState()
        self.c.setFillColor(self.color(bg))
        self.c.rect(x, y, width, height, fill=1, stroke=0)
        self.c.restoreState()
        # Cells are drawn by the caller for flexibility
        return y

    def phase_card(self, x, y, w, h, tag, name, lines_text, accent="blue", badge=None, timeline=None):
        """Draw an evolution phase card."""
        self.rounded_rect(x, y, w, h, fill="card")
        self.c.saveState()
        self.c.setFillColor(self.color(accent))
        self.c.roundRect(x+2, y+h-4, w-4, 3, 1.5, fill=1, stroke=0)
        self.c.restoreState()

        self.text(x+8, y+h-16, tag, color=accent, size=9, bold=True)
        if badge:
            sz = self.font_size(6.5)
            bw = self.c.stringWidth(badge, "Helvetica-Bold", sz) + 8
            self.rounded_rect(x+w-bw-6, y+h-18, bw, 12, r=2, fill="card2")
            self.text(x+w-bw-2, y+h-15, badge, color=accent, size=6.5, bold=True)
        self.text(x+8, y+h-28, name, color="txt", size=8.5, bold=True)

        for j, dl in enumerate(lines_text.split("\n")):
            self.text(x+8, y+h-42-j*10, dl, color="txt2", size=7)

        if timeline:
            self.text(x+8, y+6, timeline, color="muted", size=7)

    def callout_box(self, x, y, w, h, title, lines, accent="red"):
        """Draw a highlighted callout/warning box."""
        bg = {"red": "rbg", "amber": "abg", "green": "gbg", "blue": "bbg"}.get(accent, "rbg")
        self.rounded_rect(x, y, w, h, fill=bg, stroke=accent, stroke_width=1.5)
        self.text(x+12, y+h-13, title, color=accent, size=11, bold=True)
        for i, line in enumerate(lines[:4]):
            light = accent if accent != "red" else None
            # Use a lighter shade for body text in callouts
            self.text(x+12, y+h-26-i*12, line, color="txt2", size=8)

    # ─── BA Framework Components ──────────────────────────────────

    def swot_grid(self, x, y, w, h, strengths, weaknesses, opportunities, threats):
        """Draw a SWOT 2x2 grid. Each quadrant takes a list of strings."""
        gap = 4
        qw = (w - gap) / 2
        qh = (h - gap) / 2
        quads = [
            ("STRENGTHS", strengths, "green", "gbg", x, y + qh + gap),
            ("WEAKNESSES", weaknesses, "red", "rbg", x + qw + gap, y + qh + gap),
            ("OPPORTUNITIES", opportunities, "blue", "bbg", x, y),
            ("THREATS", threats, "amber", "abg", x + qw + gap, y),
        ]
        for label, items, accent, bg, qx, qy in quads:
            self.rounded_rect(qx, qy, qw, qh, fill=bg, stroke=accent, stroke_width=1)
            self.text(qx + 8, qy + qh - 14, label, color=accent, size=10, bold=True)
            for i, item in enumerate(items[:8]):
                lines = self.word_wrap(f"• {item}", "Helvetica", 7, qw - 16)
                for j, ln in enumerate(lines[:2]):
                    self.text(qx + 8, qy + qh - 28 - i * 18 - j * 10, ln, color="txt2", size=7)

    def bmc_grid(self, x, y, w, h, data):
        """Draw a Business Model Canvas 9-block grid.
        data keys: partners, activities, resources, value_prop, relationships,
                   channels, segments, cost_structure, revenue_streams"""
        gap = 3
        col5 = (w - 4 * gap) / 5
        row_top = (h - 2 * gap) * 0.6
        row_bot = (h - 2 * gap) * 0.4

        blocks = [
            # (key, label, accent, x_offset, y_offset, bw, bh)
            ("partners", "KEY PARTNERS", "purple", 0, row_bot + 2*gap, col5, row_top),
            ("activities", "KEY ACTIVITIES", "blue", col5+gap, row_bot + 2*gap + row_top/2 + gap/2, col5, row_top/2 - gap/2),
            ("resources", "KEY RESOURCES", "cyan", col5+gap, row_bot + 2*gap, col5, row_top/2 - gap/2),
            ("value_prop", "VALUE PROPOSITION", "green", 2*(col5+gap), row_bot + 2*gap, col5, row_top),
            ("relationships", "CUSTOMER REL.", "pink", 3*(col5+gap), row_bot + 2*gap + row_top/2 + gap/2, col5, row_top/2 - gap/2),
            ("channels", "CHANNELS", "amber", 3*(col5+gap), row_bot + 2*gap, col5, row_top/2 - gap/2),
            ("segments", "CUSTOMER SEGMENTS", "red", 4*(col5+gap), row_bot + 2*gap, col5, row_top),
            ("cost_structure", "COST STRUCTURE", "red", 0, 0, (w - gap) / 2, row_bot),
            ("revenue_streams", "REVENUE STREAMS", "green", (w - gap) / 2 + gap, 0, (w - gap) / 2, row_bot),
        ]
        for key, label, accent, bx, by, bw, bh in blocks:
            self.rounded_rect(x + bx, y + by, bw, bh, fill="card", stroke=accent, stroke_width=0.8)
            self.text(x + bx + 6, y + by + bh - 12, label, color=accent, size=7, bold=True)
            items = data.get(key, [])
            for i, item in enumerate(items[:5]):
                lines = self.word_wrap(f"• {item}", "Helvetica", 6.5, bw - 12)
                for j, ln in enumerate(lines[:2]):
                    self.text(x + bx + 6, y + by + bh - 24 - i * 14 - j * 9, ln, color="txt2", size=6.5)

    def five_forces(self, x, y, w, h, data):
        """Draw Porter's Five Forces diagram. Center box + 4 surrounding forces with arrows.
        data keys: rivalry, new_entrants, substitutes, buyer_power, supplier_power
                   Each is {"title": str, "items": [str]}"""
        # Center box
        cw, ch = w * 0.35, h * 0.3
        cx, cy = x + (w - cw) / 2, y + (h - ch) / 2
        rivalry = data.get("rivalry", {"title": "Industry Rivalry", "items": []})
        self.rounded_rect(cx, cy, cw, ch, fill="card", stroke="red", stroke_width=1.5)
        self.text(cx + 8, cy + ch - 14, rivalry["title"], color="red", size=9, bold=True)
        for i, item in enumerate(rivalry.get("items", [])[:4]):
            self.text(cx + 8, cy + ch - 28 - i * 11, f"• {item}", color="txt2", size=7)

        # Surrounding forces: (key, default_title, accent, box_x, box_y, arrow_from, arrow_to)
        side_w, side_h = w * 0.28, h * 0.22
        forces = [
            ("new_entrants", "New Entrants", "blue", x + (w - side_w) / 2, y + h - side_h, cx + cw/2, y + h - side_h, cx + cw/2, cy + ch),
            ("substitutes", "Substitutes", "amber", x + (w - side_w) / 2, y, cx + cw/2, y + side_h, cx + cw/2, cy),
            ("buyer_power", "Buyer Power", "green", x + w - side_w, y + (h - side_h) / 2, x + w - side_w, cy + ch/2, cx + cw, cy + ch/2),
            ("supplier_power", "Supplier Power", "purple", x, y + (h - side_h) / 2, x + side_w, cy + ch/2, cx, cy + ch/2),
        ]
        for key, default_title, accent, bx, by, ax1, ay1, ax2, ay2 in forces:
            force = data.get(key, {"title": default_title, "items": []})
            self.rounded_rect(bx, by, side_w, side_h, fill="card", stroke=accent, stroke_width=1)
            self.text(bx + 6, by + side_h - 13, force.get("title", default_title), color=accent, size=8, bold=True)
            for i, item in enumerate(force.get("items", [])[:3]):
                self.text(bx + 6, by + side_h - 25 - i * 10, f"• {item}", color="txt2", size=6.5)
            self.arrow(ax1, ay1, ax2, ay2, color=accent, width=1.5)

    def pestle_grid(self, x, y, w, h, data):
        """Draw a PESTLE 2x3 grid. data keys: political, economic, social, technological, legal, environmental"""
        gap = 4
        cw = (w - 2 * gap) / 3
        ch = (h - gap) / 2
        factors = [
            ("political", "POLITICAL", "blue", 0, ch + gap),
            ("economic", "ECONOMIC", "green", cw + gap, ch + gap),
            ("social", "SOCIAL", "pink", 2 * (cw + gap), ch + gap),
            ("technological", "TECHNOLOGICAL", "cyan", 0, 0),
            ("legal", "LEGAL", "amber", cw + gap, 0),
            ("environmental", "ENVIRONMENTAL", "purple", 2 * (cw + gap), 0),
        ]
        for key, label, accent, fx, fy in factors:
            self.rounded_rect(x + fx, y + fy, cw, ch, fill="card", stroke=accent, stroke_width=0.8)
            self.text(x + fx + 6, y + fy + ch - 13, label, color=accent, size=8, bold=True)
            items = data.get(key, [])
            for i, item in enumerate(items[:6]):
                lines = self.word_wrap(f"• {item}", "Helvetica", 6.5, cw - 12)
                for j, ln in enumerate(lines[:2]):
                    self.text(x + fx + 6, y + fy + ch - 26 - i * 14 - j * 9, ln, color="txt2", size=6.5)

    def moscow_columns(self, x, y, w, h, must, should, could, wont):
        """Draw MoSCoW prioritization as 4 columns. Each arg is a list of strings."""
        gap = 4
        cw = (w - 3 * gap) / 4
        cols = [
            ("MUST HAVE", must, "red"),
            ("SHOULD HAVE", should, "amber"),
            ("COULD HAVE", could, "blue"),
            ("WON'T HAVE", wont, "muted"),
        ]
        for i, (label, items, accent) in enumerate(cols):
            cx = x + i * (cw + gap)
            self.rounded_rect(cx, y, cw, h, fill="card", stroke=accent, stroke_width=0.8)
            # Header band
            self.c.saveState()
            # Use a darker shade instead of alpha for compatibility
            from reportlab.lib.colors import Color
            ac = self.color(accent)
            self.c.setFillColor(Color(ac.red * 0.15, ac.green * 0.15, ac.blue * 0.15))
            self.c.rect(cx, y + h - 18, cw, 18, fill=1, stroke=0)
            self.c.restoreState()
            self.text(cx + 6, y + h - 14, label, color=accent, size=8, bold=True)
            for j, item in enumerate(items[:12]):
                lines = self.word_wrap(f"• {item}", "Helvetica", 6.5, cw - 12)
                for k, ln in enumerate(lines[:2]):
                    self.text(cx + 6, y + h - 32 - j * 14 - k * 9, ln, color="txt2", size=6.5)

    def gap_panel(self, x, y, w, h, current_state, desired_state, gaps):
        """Draw gap analysis: current vs desired side-by-side with gaps below.
        current_state, desired_state: {"title": str, "items": [str]}
        gaps: [{"gap": str, "action": str}]"""
        gap = 4
        panel_w = (w - gap * 2) / 2
        arrow_w = gap * 2
        panel_h = h * 0.55
        gap_h = h - panel_h - gap

        # Current state
        self.rounded_rect(x, y + gap_h + gap, panel_w, panel_h, fill="card", stroke="red", stroke_width=1)
        self.text(x + 8, y + gap_h + gap + panel_h - 14, current_state.get("title", "CURRENT STATE"), color="red", size=10, bold=True)
        for i, item in enumerate(current_state.get("items", [])[:8]):
            self.text(x + 8, y + gap_h + gap + panel_h - 30 - i * 12, f"• {item}", color="txt2", size=7)

        # Arrow
        mid_y = y + gap_h + gap + panel_h / 2
        self.arrow(x + panel_w + 4, mid_y, x + panel_w + arrow_w - 4, mid_y, color="blue", width=2)

        # Desired state
        dx = x + panel_w + arrow_w
        self.rounded_rect(dx, y + gap_h + gap, panel_w, panel_h, fill="card", stroke="green", stroke_width=1)
        self.text(dx + 8, y + gap_h + gap + panel_h - 14, desired_state.get("title", "DESIRED STATE"), color="green", size=10, bold=True)
        for i, item in enumerate(desired_state.get("items", [])[:8]):
            self.text(dx + 8, y + gap_h + gap + panel_h - 30 - i * 12, f"• {item}", color="txt2", size=7)

        # Gaps band below
        self.rounded_rect(x, y, w, gap_h, fill="card", stroke="amber", stroke_width=0.8)
        self.text(x + 8, y + gap_h - 14, "GAPS & ACTIONS", color="amber", size=9, bold=True)
        col_w = w / max(len(gaps), 1)
        for i, g in enumerate(gaps[:6]):
            gx = x + i * col_w + 8
            self.text(gx, y + gap_h - 30, g.get("gap", ""), color="txt", size=7, bold=True)
            lines = self.word_wrap(g.get("action", ""), "Helvetica", 6.5, col_w - 16)
            for j, ln in enumerate(lines[:3]):
                self.text(gx, y + gap_h - 42 - j * 9, ln, color="txt2", size=6.5)

    def value_chain(self, x, y, w, h, primary, support):
        """Draw Porter's Value Chain. primary: [{"name": str, "items": [str]}], support: [{"name": str, "items": [str]}]"""
        gap = 3
        support_h = h * 0.35
        primary_h = h - support_h - gap

        # Support activities (top band)
        self.rounded_rect(x, y + primary_h + gap, w, support_h, fill="card", stroke="purple", stroke_width=0.8)
        self.text(x + 8, y + primary_h + gap + support_h - 13, "SUPPORT ACTIVITIES", color="purple", size=9, bold=True)
        sa_w = w / max(len(support), 1)
        for i, sa in enumerate(support[:5]):
            sx = x + i * sa_w + 8
            self.text(sx, y + primary_h + gap + support_h - 28, sa.get("name", ""), color="txt", size=7, bold=True)
            for j, item in enumerate(sa.get("items", [])[:3]):
                self.text(sx, y + primary_h + gap + support_h - 40 - j * 10, f"• {item}", color="txt2", size=6.5)

        # Primary activities (bottom — arrow-shaped flow)
        pa_w = (w - (len(primary) - 1) * gap) / max(len(primary), 1)
        for i, pa in enumerate(primary[:7]):
            px = x + i * (pa_w + gap)
            accent = ["blue", "cyan", "green", "amber", "pink", "purple", "red"][i % 7]
            self.rounded_rect(px, y, pa_w, primary_h, fill="card", stroke=accent, stroke_width=0.8)
            self.text(px + 6, y + primary_h - 13, pa.get("name", ""), color=accent, size=7.5, bold=True)
            for j, item in enumerate(pa.get("items", [])[:5]):
                self.text(px + 6, y + primary_h - 27 - j * 10, f"• {item}", color="txt2", size=6.5)
            if i < len(primary) - 1:
                self.arrow(px + pa_w, y + primary_h / 2, px + pa_w + gap, y + primary_h / 2, color="muted")

    def fishbone(self, x, y, w, h, effect, causes):
        """Draw an Ishikawa fishbone diagram.
        effect: str (the problem/effect at the right)
        causes: [{"category": str, "items": [str]}] — 4-6 branches"""
        # Main spine
        spine_y = y + h / 2
        head_w = w * 0.18
        spine_x1 = x
        spine_x2 = x + w - head_w
        self.c.saveState()
        self.c.setStrokeColor(self.color("blue"))
        self.c.setLineWidth(2.5)
        self.c.line(spine_x1, spine_y, spine_x2, spine_y)
        self.c.restoreState()

        # Effect box (right)
        self.rounded_rect(spine_x2, spine_y - 20, head_w, 40, fill="card", stroke="red", stroke_width=1.5)
        self.text(spine_x2 + 6, spine_y + 6, "EFFECT", color="red", size=7, bold=True)
        lines = self.word_wrap(effect, "Helvetica-Bold", 8, head_w - 12)
        for i, ln in enumerate(lines[:2]):
            self.text(spine_x2 + 6, spine_y - 8 - i * 11, ln, color="txt", size=8, bold=True)

        # Cause branches (alternating top/bottom)
        n = min(len(causes), 6)
        bone_spacing = (spine_x2 - spine_x1) / (n + 1)
        accents = ["cyan", "green", "amber", "purple", "pink", "blue"]
        for i, cause in enumerate(causes[:6]):
            bx = spine_x1 + (i + 1) * bone_spacing
            top = (i % 2 == 0)
            branch_h = h * 0.35
            by = spine_y + 8 if top else spine_y - 8 - branch_h
            end_y = spine_y + branch_h + 8 if top else spine_y - branch_h - 8
            accent = accents[i % len(accents)]

            # Diagonal bone
            self.c.saveState()
            self.c.setStrokeColor(self.color(accent))
            self.c.setLineWidth(1.5)
            self.c.line(bx, spine_y, bx, end_y)
            self.c.restoreState()

            # Category label
            self.text(bx - 4, end_y + (4 if top else -12), cause.get("category", ""), color=accent, size=8, bold=True)
            # Sub-causes
            for j, item in enumerate(cause.get("items", [])[:4]):
                iy = end_y + (18 + j * 11 if top else -24 - j * 11)
                self.text(bx - 4, iy, f"– {item}", color="txt2", size=6.5)

    def story_map(self, x, y, w, h, journey_steps, releases):
        """Draw a user story map. Journey across the top, releases stacked below.
        journey_steps: [{"step": str, "activities": [str]}]
        releases: [{"name": str, "priority": str}] — rows below, matched to journey columns"""
        gap = 3
        header_h = h * 0.15
        step_w = (w - (len(journey_steps) - 1) * gap) / max(len(journey_steps), 1)
        body_h = h - header_h - gap

        # Journey steps (top row)
        for i, step in enumerate(journey_steps[:8]):
            sx = x + i * (step_w + gap)
            accent = ["blue", "cyan", "green", "amber", "pink", "purple", "red", "muted"][i % 8]
            self.rounded_rect(sx, y + body_h + gap, step_w, header_h, fill="card", stroke=accent, stroke_width=1)
            self.text(sx + 6, y + body_h + gap + header_h - 13, step.get("step", ""), color=accent, size=8, bold=True)
            # Activities stacked below
            activities = step.get("activities", [])
            act_h = body_h / max(len(activities), 1) - gap
            for j, act in enumerate(activities[:6]):
                ay = y + body_h - (j + 1) * (act_h + gap) + act_h
                self.rounded_rect(sx, ay, step_w, act_h, fill="card2")
                lines = self.word_wrap(act, "Helvetica", 6.5, step_w - 10)
                for k, ln in enumerate(lines[:3]):
                    self.text(sx + 5, ay + act_h - 12 - k * 9, ln, color="txt2", size=6.5)

        # Release markers on the left
        if releases:
            release_h = body_h / len(releases)
            for i, rel in enumerate(releases[:4]):
                ry = y + body_h - (i + 1) * release_h
                self.c.saveState()
                self.c.setStrokeColor(self.color("muted"))
                self.c.setDash(3, 3)
                self.c.setLineWidth(0.5)
                self.c.line(x, ry, x + w, ry)
                self.c.restoreState()

    def risk_matrix(self, x, y, w, h, risks):
        """Draw a likelihood × impact risk matrix (5x5 grid with plotted risks).
        risks: [{"name": str, "likelihood": 1-5, "impact": 1-5}]"""
        gap = 2
        label_w = 18
        label_h = 14
        grid_w = w - label_w
        grid_h = h - label_h
        cell_w = grid_w / 5
        cell_h = grid_h / 5

        # Grid cells with heat colors
        heat = [
            ["gbg", "gbg", "abg", "abg", "rbg"],
            ["gbg", "abg", "abg", "rbg", "rbg"],
            ["abg", "abg", "rbg", "rbg", "rbg"],
            ["abg", "rbg", "rbg", "rbg", "rbg"],
            ["rbg", "rbg", "rbg", "rbg", "rbg"],
        ]
        for row in range(5):
            for col in range(5):
                cx = x + label_w + col * cell_w
                cy = y + label_h + row * cell_h
                self.c.saveState()
                self.c.setFillColor(self.color(heat[row][col]))
                self.c.rect(cx, cy, cell_w - gap, cell_h - gap, fill=1, stroke=0)
                self.c.restoreState()

        # Axis labels
        for i, lbl in enumerate(["1", "2", "3", "4", "5"]):
            self.text(x + label_w + i * cell_w + cell_w / 2 - 3, y + 2, lbl, color="muted", size=7)
            self.text(x + 2, y + label_h + i * cell_h + cell_h / 2 - 3, lbl, color="muted", size=7)
        self.text(x + label_w + grid_w / 2 - 15, y - 6, "IMPACT →", color="txt2", size=6.5, bold=True)
        # Vertical label approximation
        self.text(x - 2, y + label_h + grid_h / 2, "L↑", color="txt2", size=6.5, bold=True)

        # Plot risks
        for risk in risks[:15]:
            imp = min(max(risk.get("impact", 1), 1), 5) - 1
            lik = min(max(risk.get("likelihood", 1), 1), 5) - 1
            rx = x + label_w + imp * cell_w + cell_w / 2
            ry = y + label_h + lik * cell_h + cell_h / 2
            # Dot
            self.c.saveState()
            self.c.setFillColor(self.color("txt"))
            self.c.circle(rx, ry, 4, fill=1, stroke=0)
            self.c.restoreState()
            self.text(rx + 6, ry - 3, risk.get("name", "")[:20], color="txt", size=6, bold=True)

    def raci_matrix(self, x, y, w, h, roles, tasks, assignments):
        """Draw a RACI matrix. roles: [str], tasks: [str],
        assignments: [[str]] — 2D array of R/A/C/I per task×role"""
        role_w = (w - 80) / max(len(roles), 1)
        task_col_w = 80
        row_h = min((h - 18) / max(len(tasks), 1), 20)

        # Header
        self.c.saveState()
        self.c.setFillColor(self.color("thead"))
        self.c.rect(x, y + h - 18, w, 18, fill=1, stroke=0)
        self.c.restoreState()
        self.text(x + 4, y + h - 14, "TASK", color="blue", size=7, bold=True)
        for i, role in enumerate(roles[:10]):
            self.text(x + task_col_w + i * role_w + 4, y + h - 14, role[:12], color="blue", size=6.5, bold=True)

        # Rows
        raci_colors = {"R": "red", "A": "amber", "C": "blue", "I": "muted"}
        for i, task in enumerate(tasks[:20]):
            ry = y + h - 18 - (i + 1) * row_h
            bg = "trow2" if i % 2 == 0 else "trow"
            self.c.saveState()
            self.c.setFillColor(self.color(bg))
            self.c.rect(x, ry, w, row_h, fill=1, stroke=0)
            self.c.restoreState()
            self.text(x + 4, ry + 4, task[:30], color="txt2", size=6.5)
            row_data = assignments[i] if i < len(assignments) else []
            for j, cell in enumerate(row_data[:len(roles)]):
                cell_color = raci_colors.get(cell.upper(), "muted")
                cx = x + task_col_w + j * role_w + role_w / 2 - 4
                self.text(cx, ry + 4, cell.upper(), color=cell_color, size=7, bold=True)

    def kpi_card(self, x, y, w, h, label, value, unit="", context="", trend="", accent="blue"):
        """Draw a single KPI metric card with large value display."""
        self.rounded_rect(x, y, w, h, fill="card", stroke=accent, stroke_width=0.8)
        # Accent bar top
        self.c.saveState()
        self.c.setFillColor(self.color(accent))
        self.c.rect(x + 2, y + h - 3, w - 4, 3, fill=1, stroke=0)
        self.c.restoreState()

        self.text(x + 8, y + h - 16, label, color="txt2", size=7)
        val_str = f"{value}{unit}"
        self.text(x + 8, y + h - 36, val_str, color=accent, size=18, bold=True)
        if context:
            self.text(x + 8, y + h - 48, context, color="txt2", size=6.5)
        if trend:
            trend_color = "green" if trend.startswith("+") or trend.startswith("↑") else "red" if trend.startswith("-") or trend.startswith("↓") else "muted"
            self.text(x + 8, y + 6, trend, color=trend_color, size=7, bold=True)

    def decision_matrix(self, x, y, w, h, options, criteria, scores, weights=None):
        """Draw a weighted decision matrix.
        options: [str], criteria: [str], scores: [[float]] — options×criteria,
        weights: [float] or None (equal weight)"""
        n_opts = len(options)
        n_crit = len(criteria)
        wts = weights or [1.0] * n_crit

        opt_col = 60
        crit_w = (w - opt_col - 50) / max(n_crit, 1)
        row_h = min((h - 18) / max(n_opts, 1), 22)

        # Header
        self.c.saveState()
        self.c.setFillColor(self.color("thead"))
        self.c.rect(x, y + h - 18, w, 18, fill=1, stroke=0)
        self.c.restoreState()
        self.text(x + 4, y + h - 14, "OPTION", color="blue", size=7, bold=True)
        for i, crit in enumerate(criteria[:10]):
            label = f"{crit[:10]} ({wts[i]:.0f})" if weights else crit[:14]
            self.text(x + opt_col + i * crit_w + 2, y + h - 14, label, color="blue", size=6, bold=True)
        self.text(x + w - 46, y + h - 14, "TOTAL", color="amber", size=7, bold=True)

        # Rows
        for i, opt in enumerate(options[:12]):
            ry = y + h - 18 - (i + 1) * row_h
            bg = "trow2" if i % 2 == 0 else "trow"
            self.c.saveState()
            self.c.setFillColor(self.color(bg))
            self.c.rect(x, ry, w, row_h, fill=1, stroke=0)
            self.c.restoreState()
            self.text(x + 4, ry + 5, opt[:20], color="txt", size=7)
            total = 0
            row_scores = scores[i] if i < len(scores) else []
            for j, sc in enumerate(row_scores[:n_crit]):
                total += sc * wts[j]
                sc_color = "green" if sc >= 4 else "amber" if sc >= 2 else "red"
                self.text(x + opt_col + j * crit_w + 8, ry + 5, f"{sc:.0f}", color=sc_color, size=7, bold=True)
            self.text(x + w - 40, ry + 5, f"{total:.0f}", color="amber", size=8, bold=True)

    # ─── Header & Footer ─────────────────────────────────────────

    def draw_header(self, title, subtitle, badges=None, header_h=38*mm):
        self.c.setFillColor(self.color("hdr"))
        self.c.rect(0, self.page_h-header_h, self.page_w, header_h, fill=1, stroke=0)
        self.c.setFillColor(self.color("blue"))
        self.c.rect(0, self.page_h-header_h, self.page_w, 2, fill=1, stroke=0)
        self.text(self.margin, self.page_h-24*mm, title, color="txt", size=32, bold=True)
        self.text(self.margin, self.page_h-33*mm, subtitle, color="txt2", size=14)

        if badges:
            bx = self.page_w - self.margin
            for lbl, bg_name, fg_name in reversed(badges):
                sz = self.font_size(10)
                tw = self.c.stringWidth(lbl, "Helvetica-Bold", sz) + 14
                bx -= tw + 8
                self.rounded_rect(bx, self.page_h-21*mm, tw, 18, r=9, fill=bg_name, stroke=fg_name, stroke_width=1)
                self.text(bx+7, self.page_h-18*mm, lbl, color=fg_name, size=10, bold=True)

        return self.page_h - header_h - 6*mm

    def draw_footer(self, left_text, right_text, footer_h=10*mm):
        self.c.setFillColor(self.color("hdr"))
        self.c.rect(0, 0, self.page_w, footer_h, fill=1, stroke=0)
        self.c.setFillColor(self.color("blue"))
        self.c.rect(0, footer_h, self.page_w, 1.5, fill=1, stroke=0)
        self.text(self.margin, 3.5*mm, left_text, color="muted", size=7)
        self.c.saveState()
        self.c.setFillColor(self.color("muted"))
        self.c.setFont("Helvetica", self.font_size(7))
        self.c.drawRightString(self.page_w-self.margin, 3.5*mm, right_text)
        self.c.restoreState()
        return footer_h + 4*mm

    # ─── Lifecycle ────────────────────────────────────────────────

    def save(self):
        self.c.save()
