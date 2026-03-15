#!/usr/bin/env python3
"""
Generate DIN A1 landscape poster: Steuerberater Document Processing Solution
Maps architecture, regulatory constraints, modules, and autoresearch evolution.
"""

from reportlab.lib.pagesizes import A1
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.pdfgen import canvas
import math, os

# ─── Page ─────────────────────────────────────────────────────────
PAGE_W, PAGE_H = A1[1], A1[0]  # 841 × 594 mm landscape
M = 12 * mm  # margin
CONTENT_W = PAGE_W - 2 * M
HEADER_H = 38 * mm
FOOTER_H = 10 * mm
TOP_Y = PAGE_H - HEADER_H - 6 * mm
BOT_Y = FOOTER_H + 4 * mm
AVAIL_H = TOP_Y - BOT_Y  # ~528mm usable

# ─── Colors ───────────────────────────────────────────────────────
C = {
    "bg": HexColor("#0f1117"), "card": HexColor("#1a1d27"), "card2": HexColor("#141720"),
    "blue": HexColor("#3b82f6"), "cyan": HexColor("#06b6d4"), "green": HexColor("#22c55e"),
    "red": HexColor("#ef4444"), "amber": HexColor("#f59e0b"), "purple": HexColor("#a855f7"),
    "pink": HexColor("#ec4899"), "txt": HexColor("#f1f5f9"), "txt2": HexColor("#94a3b8"),
    "muted": HexColor("#64748b"), "border": HexColor("#2a2d3a"),
    "thead": HexColor("#1e293b"), "trow": HexColor("#0f172a"), "trow2": HexColor("#1a1f2e"),
    "rbg": HexColor("#3b1117"), "abg": HexColor("#3b2e0a"), "gbg": HexColor("#0a2e1a"),
    "bbg": HexColor("#0a1a3b"), "hdr": HexColor("#0c0e14"),
}
SEV_C = {"CRIMINAL":(C["red"],C["rbg"]), "BERUFSRECHT":(C["amber"],C["abg"]),
         "STEUERRECHT":(C["amber"],C["abg"]), "ZIVILRECHT":(C["amber"],C["abg"]),
         "BUSSGELD":(C["red"],C["rbg"]), "RECOMMENDED":(C["green"],C["gbg"]),
         "ORDNUNGSW.":(C["amber"],C["abg"])}

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "StB_Document_Pipeline_Poster_A1.pdf")

def rr(c, x, y, w, h, r=3*mm, fill=None, stroke=None, sw=0.5):
    c.saveState()
    c.setFillColor(fill or C["card"])
    if stroke:
        c.setStrokeColor(stroke); c.setLineWidth(sw)
        c.roundRect(x,y,w,h,r,fill=1,stroke=1)
    else:
        c.roundRect(x,y,w,h,r,fill=1,stroke=0)
    c.restoreState()

def arrow(c, x1,y1,x2,y2, color=None, w=1.5):
    color = color or C["muted"]
    c.saveState(); c.setStrokeColor(color); c.setLineWidth(w); c.setLineCap(1)
    c.line(x1,y1,x2,y2)
    a=math.atan2(y2-y1,x2-x1); al=3*mm
    c.setFillColor(color); p=c.beginPath()
    p.moveTo(x2,y2)
    p.lineTo(x2-al*math.cos(a-.3),y2-al*math.sin(a-.3))
    p.lineTo(x2-al*math.cos(a+.3),y2-al*math.sin(a+.3))
    p.close(); c.drawPath(p,fill=1,stroke=0); c.restoreState()

def sec(c, x, y, title, accent=None, sub=None, sz=16):
    accent = accent or C["blue"]
    c.saveState()
    c.setFillColor(accent); c.rect(x,y-1,50,3.5,fill=1,stroke=0)
    c.setFillColor(C["txt"]); c.setFont("Helvetica-Bold",sz); c.drawString(x,y-sz-3,title)
    ny = y-sz-7
    if sub:
        c.setFillColor(C["txt2"]); c.setFont("Helvetica",8.5); c.drawString(x,ny-2,sub); ny-=12
    c.restoreState(); return ny

def wrap(c, text, font, size, maxw):
    lines=[""];
    for w in text.split():
        t = lines[-1]+" "+w if lines[-1] else w
        if c.stringWidth(t,font,size)<maxw: lines[-1]=t
        else: lines.append(w)
    return lines

def create_poster():
    c = canvas.Canvas(OUT, pagesize=(PAGE_W, PAGE_H))
    c.setTitle("Steuerberater Document Processing Pipeline")
    c.setAuthor("STEUB Use Cases Project")

    # ─── Background ───────────────────────────────────────────────
    c.setFillColor(C["bg"]); c.rect(0,0,PAGE_W,PAGE_H,fill=1,stroke=0)

    # ─── Header ───────────────────────────────────────────────────
    c.setFillColor(C["hdr"]); c.rect(0,PAGE_H-HEADER_H,PAGE_W,HEADER_H,fill=1,stroke=0)
    c.setFillColor(C["blue"]); c.rect(0,PAGE_H-HEADER_H,PAGE_W,2,fill=1,stroke=0)
    c.setFillColor(C["txt"]); c.setFont("Helvetica-Bold",32)
    c.drawString(M, PAGE_H-24*mm, "Steuerberater Document Processing Pipeline")
    c.setFillColor(C["txt2"]); c.setFont("Helvetica",14)
    c.drawString(M, PAGE_H-33*mm, "Python-on-Windows Solution  ·  Regulatory Compliance  ·  Autoresearch Evolution  ·  100% On-Premise")

    # Badges top-right
    for i,(lbl,bg,fg) in enumerate([("§203 COMPLIANT",C["abg"],C["amber"]),("ZERO CLOUD",C["rbg"],C["red"]),("100% ON-PREMISE",C["gbg"],C["green"])]):
        tw=c.stringWidth(lbl,"Helvetica-Bold",10)+14
        bx=PAGE_W-M-tw - i*(tw+8)
        rr(c,bx,PAGE_H-21*mm,tw,18,r=9,fill=bg,stroke=fg,sw=1)
        c.saveState(); c.setFillColor(fg); c.setFont("Helvetica-Bold",10)
        c.drawString(bx+7,PAGE_H-18*mm,lbl); c.restoreState()

    c.setFillColor(C["muted"]); c.setFont("Helvetica",7)
    c.drawRightString(PAGE_W-M, PAGE_H-HEADER_H+3, "STEUB Use Cases  ·  March 2026  ·  DIN A1 (841×594mm)")

    # ─── Column geometry ──────────────────────────────────────────
    GAP = 7*mm
    # 3 visual columns: col1 (pipeline), col2 (modules+banned), col3+4 (reg table + autoresearch)
    c1w = 195*mm; c2w = 195*mm; c34w = CONTENT_W - c1w - c2w - 2*GAP
    c1x = M; c2x = c1x+c1w+GAP; c3x = c2x+c2w+GAP

    # ═══════════════════════════════════════════════════════════════
    # COL 1: PIPELINE (8 steps filling full height)
    # ═══════════════════════════════════════════════════════════════
    cy = sec(c, c1x, TOP_Y, "SOLUTION ARCHITECTURE", C["blue"], "Python-on-Windows · GoBD-compliant · 8-step pipeline")

    steps = [
        ("1  SCAN", "NAPS2 CLI", "eSCL / WIA / TWAIN · ADF, duplex, flatbed", C["cyan"],
         "Scanner input — 300 DPI color default (BSI RESISCAN). Network scanners via AirScan/eSCL, local via WIA. Auto-selects feeder vs flatbed. Full duplex support for double-sided documents."),
        ("2  PREPROCESS", "OpenCV 4.10 + Pillow", "Deskew · binarize · denoise · enhance", C["blue"],
         "Adaptive Sauvola binarization, Hough-transform deskew, CLAHE contrast enhancement. Parameters optimized by Autoresearch loop A1 on synthetic data. Handles faded thermal receipts and low-quality faxes."),
        ("3  OCR", "pytesseract / EasyOCR", "Text recognition · HOCR output · 100+ languages", C["purple"],
         "Tesseract for printed text (German + English default). EasyOCR for handwriting/degraded scans. Config auto-tuned by Autoresearch loop A2. Outputs HOCR with word-level bounding boxes + confidence scores."),
        ("4  LAYOUT", "Custom + OpenCV", "Zone detection · table extraction · field mapping", C["pink"],
         "Identifies header, address block, line items, totals, footer. Table extraction via line detection + cell segmentation. Autoresearch A4 tunes detection thresholds. Maps zones to extraction fields."),
        ("5  EXTRACT", "Ollama (local LLM)", "Structured field extraction via optimized prompts", C["amber"],
         "Llama 3.2 / Mistral via Ollama — 100% local, no data egress. Extracts: Rechnungsnr., Datum, Betrag, USt-Satz, Steuernr., IBAN, Zahlungsziel. Prompts optimized by Autoresearch A5. Output: JSON."),
        ("6  REVIEW", "PyQt6 Desktop UI", "Human-in-the-loop verification & approval", C["red"],
         "§ 57 StBerG: MANDATORY. Side-by-side: original scan + OCR text + extracted fields. Low-confidence words highlighted in red. Amounts flagged if OCR confidence <80%. 'Freigegeben von' + timestamp logged."),
        ("7  ARCHIVE", "ocrmypdf → PDF/A-2b", "GoBD-compliant archival · immutable · hashed", C["green"],
         "Sandwich PDF (image + invisible text layer). PDF/A-2b for 10-year archival (§147 AO). SHA-256 integrity hash per document. JBIG2 compression for B&W, JPEG for color. Compression tuned by A3."),
        ("8  EXPORT", "DATEV DMS / Flatfile", "Kanzlei system integration · CSV / XML", C["cyan"],
         "Outputs to DATEV import folder, Agenda, or flat CSV/XML. Extracted fields mapped to DATEV Buchungssatz format. Includes: Belegdatum, Belegnummer, Betrag, Konto, Gegenkonto, Steuerschlüssel."),
    ]

    n = len(steps)
    step_gap = 5*mm
    step_h = (cy - BOT_Y - (n-1)*step_gap) / n  # fill available height

    for i,(name,lib,short,color,detail) in enumerate(steps):
        sy = cy - i*(step_h+step_gap)  # top of card
        rr(c, c1x, sy-step_h, c1w, step_h, fill=C["card"])
        # Left accent bar
        c.saveState(); c.setFillColor(color)
        c.roundRect(c1x+1.5, sy-step_h+4, 4, step_h-8, 2, fill=1,stroke=0)
        # Step name
        c.setFont("Helvetica-Bold",12); c.drawString(c1x+12, sy-14, name)
        # Library
        c.setFillColor(C["txt"]); c.setFont("Helvetica-Bold",9)
        c.drawString(c1x+12, sy-26, lib)
        # Short desc
        c.setFillColor(C["cyan"]); c.setFont("Helvetica",8)
        c.drawString(c1x+12, sy-37, short)
        # Detail text (wrapped)
        c.setFillColor(C["txt2"]); c.setFont("Helvetica",7)
        lines = wrap(c, detail, "Helvetica", 7, c1w-24)
        for j,ln in enumerate(lines[:5]):
            c.drawString(c1x+12, sy-50 - j*10, ln)
        c.restoreState()
        # Arrow
        if i < n-1:
            mx = c1x + c1w/2
            arrow(c, mx, sy-step_h, mx, sy-step_h-step_gap, C["muted"], 1)

    # ═══════════════════════════════════════════════════════════════
    # COL 2: MODULES + BANNED + KEY METRICS + DOC TYPES + CHECKLIST
    # ═══════════════════════════════════════════════════════════════
    cy2 = sec(c, c2x, TOP_Y, "PYTHON MODULE STACK", C["cyan"], "All local · open source · zero cloud dependencies")

    modules = [
        ("pytesseract", "OCR engine wrapper", "Tesseract 5.x binary", C["purple"]),
        ("easyocr", "Deep learning OCR", "80+ langs, GPU/CPU", C["purple"]),
        ("ocrmypdf", "OCR → PDF/A pipeline", "Industry gold standard", C["green"]),
        ("opencv-python", "Image processing", "4.10+ headless", C["blue"]),
        ("Pillow", "Image primitives", "PIL fork, 11.0+", C["blue"]),
        ("scikit-image", "Sauvola, morphology", "Advanced algorithms", C["blue"]),
        ("pikepdf", "PDF manipulation", "QPDF-based, fast", C["cyan"]),
        ("PyMuPDF", "PDF rendering/search", "MuPDF engine", C["cyan"]),
        ("ollama", "Local LLM inference", "llama3, mistral, phi-3", C["amber"]),
        ("NAPS2", "Scanner frontend", "eSCL/WIA/TWAIN CLI", C["cyan"]),
        ("PyQt6", "Desktop review UI", "Native Qt widgets", C["pink"]),
        ("typer", "CLI automation", "Click-based, typed", C["muted"]),
        ("jbig2enc", "B&W PDF compress", "JBIG2 encoding", C["green"]),
        ("deskew", "Skew angle detect", "Hough/projection", C["blue"]),
        ("reportlab", "PDF generation", "Poster & reports", C["muted"]),
    ]

    my = cy2 - 2*mm
    mh = 14  # row height
    for i,(name,desc,detail,color) in enumerate(modules):
        iy = my - i*mh
        if i%2==0:
            c.saveState(); c.setFillColor(C["card2"]); c.rect(c2x,iy-mh+2,c2w,mh,fill=1,stroke=0); c.restoreState()
        c.saveState()
        c.setFillColor(color); c.circle(c2x+7, iy-5, 2.5, fill=1, stroke=0)
        c.setFillColor(C["txt"]); c.setFont("Helvetica-Bold",8); c.drawString(c2x+14, iy-7, name)
        c.setFillColor(C["txt2"]); c.setFont("Helvetica",7); c.drawString(c2x+82, iy-7, desc)
        c.setFillColor(C["muted"]); c.setFont("Helvetica",6.5); c.drawString(c2x+c2w-55*mm, iy-7, detail)
        c.restoreState()

    # ─── Banned ───────────────────────────────────────────────────
    ban_y = my - len(modules)*mh - 10*mm
    sec(c, c2x, ban_y, "ELIMINATED SERVICES", C["red"], "§ 203 StGB / DSGVO Art. 44+ — criminal liability")

    banned = [
        "OpenAI API (ChatGPT, GPT-4, Whisper) — US cloud, § 203 violation",
        "Anthropic API (Claude) — US cloud, CLOUD Act exposure",
        "Google Cloud Vision / Document AI — US processor, Schrems II",
        "AWS Textract / Comprehend — US cloud, no § 203 agreement",
        "Azure AI Document Intelligence — US parent, CLOUD Act",
        "Any cloud-hosted OCR service — data leaves Kanzlei network",
        "External Streamlit / web hosting — exposes documents to internet",
        "Hugging Face Inference API — sends data to external servers",
    ]

    by = ban_y - 26
    for i,item in enumerate(banned):
        iy = by - i*13
        c.saveState()
        c.setFillColor(C["red"]); c.setFont("Helvetica-Bold",8); c.drawString(c2x+4, iy, "✗")
        c.setFillColor(HexColor("#fca5a5")); c.setFont("Helvetica",7); c.drawString(c2x+16, iy, item)
        c.restoreState()

    # ─── Key metrics box ──────────────────────────────────────────
    km_y = by - len(banned)*13 - 8*mm
    km_h = 42*mm
    rr(c, c2x, km_y-km_h, c2w, km_h, fill=C["bbg"], stroke=C["blue"])

    c.saveState(); c.setFillColor(C["blue"]); c.setFont("Helvetica-Bold",11)
    c.drawString(c2x+10, km_y-12, "KEY METRICS"); c.restoreState()

    metrics = [
        ("100+", "OCR languages (Tesseract + EasyOCR)"),
        ("PDF/A-2b", "Archival format output (GoBD Rn.136)"),
        ("300 DPI", "Minimum scan resolution (BSI RESISCAN)"),
        ("10 years", "Retention: Belege, Rechnungen (§ 147 AO)"),
        ("6 years", "Retention: Geschäftsbriefe (§ 147 AO)"),
        ("5 years", "Retention: GwG KYC documents (GwG § 8)"),
        ("SHA-256", "Integrity hash per archived document"),
        ("€0", "Total software cost — 100% open source"),
    ]
    for i,(num,desc) in enumerate(metrics):
        ky = km_y - 26 - i*14
        c.saveState()
        c.setFillColor(C["cyan"]); c.setFont("Helvetica-Bold",9); c.drawString(c2x+10, ky, num)
        c.setFillColor(C["txt2"]); c.setFont("Helvetica",7.5); c.drawString(c2x+68, ky, desc)
        c.restoreState()

    # ─── Document type profiles ───────────────────────────────────
    dt_y = km_y - km_h - 8*mm
    sec(c, c2x, dt_y, "DOCUMENT TYPE PROFILES", C["pink"], "Which autoresearch loop helps most per document type")

    doc_types = [
        ("Eingangsrechnungen", "A5 Extract", "A2 OCR", "Betrag, USt, Datum accuracy"),
        ("Lohnsteuerbeschein.", "A4 Layout", "A1 Preproc", "Table/zone detection F1"),
        ("Kontoauszüge", "A2 OCR (numbers)", "A4 Layout", "Number CER specifically"),
        ("Handschriftl. Belege", "A1 Preprocess", "A2 EasyOCR", "Overall CER on handwriting"),
        ("Finanzamtsbescheide", "A4 Layout", "A5 Extract", "Structured form fields"),
        ("Verträge", "A5 LLM Summary", "A3 Compress", "Summary quality + size"),
        ("Quittungen", "A1 Preprocess", "A2 OCR", "CER on faded thermal paper"),
    ]

    dy = dt_y - 16
    # Header
    c.saveState(); c.setFillColor(C["thead"]); c.rect(c2x, dy-12, c2w, 12, fill=1, stroke=0)
    c.setFillColor(C["blue"]); c.setFont("Helvetica-Bold",6.5)
    c.drawString(c2x+4, dy-9, "DOCUMENT TYPE"); c.drawString(c2x+68, dy-9, "PRIMARY LOOP")
    c.drawString(c2x+116, dy-9, "SECONDARY"); c.drawString(c2x+152, dy-9, "METRIC FOCUS")
    c.restoreState()

    for i,(dtype,prim,sec_,metric) in enumerate(doc_types):
        ry = dy - 12 - (i+1)*13
        bg = C["trow2"] if i%2==0 else C["trow"]
        c.saveState(); c.setFillColor(bg); c.rect(c2x, ry, c2w, 13, fill=1, stroke=0)
        c.setFillColor(C["txt"]); c.setFont("Helvetica",6.5); c.drawString(c2x+4, ry+4, dtype)
        c.setFillColor(C["amber"]); c.setFont("Helvetica-Bold",6.5); c.drawString(c2x+68, ry+4, prim)
        c.setFillColor(C["txt2"]); c.setFont("Helvetica",6.5); c.drawString(c2x+116, ry+4, sec_)
        c.setFillColor(C["muted"]); c.setFont("Helvetica",6); c.drawString(c2x+152, ry+4, metric)
        c.restoreState()

    # ─── Pre-deployment checklist ─────────────────────────────────
    ck_y = dy - 12 - (len(doc_types)+1)*13 - 8*mm
    sec(c, c2x, ck_y, "PRE-DEPLOYMENT CHECKLIST", C["green"], "Required before production go-live")

    checks = [
        "Verfahrensdokumentation written & signed (GoBD Rn.151)",
        "Schutzbedarfsanalyse per document type (TR-RESISCAN)",
        "AV-Verträge reviewed — no cloud processors confirmed",
        "Verarbeitungsverzeichnis updated (DSGVO Art. 30)",
        "Löschkonzept implemented (6/10-year auto-flagging)",
        "Berufshaftpflicht insurer notified of AI workflows",
        "Mandanteninformation issued (§ 62 StBerG)",
        "Staff trained: scan quality check + review duties",
        "BitLocker / FileVault verified on all workstations",
        "§ 203 Verpflichtungserklärung signed by all staff",
    ]

    cky = ck_y - 18
    for i,item in enumerate(checks):
        iy = cky - i*12
        c.saveState()
        c.setFillColor(C["green"]); c.setFont("Helvetica",8); c.drawString(c2x+4, iy, "☐")
        c.setFillColor(C["txt2"]); c.setFont("Helvetica",7); c.drawString(c2x+16, iy, item)
        c.restoreState()

    # ═══════════════════════════════════════════════════════════════
    # COLS 3+4: REGULATORY TABLE (top 60%) + AUTORESEARCH (bottom 40%)
    # ═══════════════════════════════════════════════════════════════
    cy3 = sec(c, c3x, TOP_Y, "REGULATORY CONSTRAINTS FOR STEUERBERATER", C["red"],
              "Every legal obligation mapped to a concrete technical rule and pipeline impact")

    reg_table = [
        ("§ 203 StGB", "Verschwiegenheitspflicht (professional secrecy)", "CRIMINAL", "Zero cloud processing — all data on-premise", "Eliminates all cloud OCR/LLM/storage"),
        ("§ 203 StGB", "No disclosure to third parties", "CRIMINAL", "No telemetry transmitting document content", "Disable analytics, crash reports with data"),
        ("§ 203 Abs.3", "§ 203 secrecy agreement for processors", "CRIMINAL", "Cloud providers need secrecy contract (most refuse)", "On-premise is only practical option"),
        ("§ 57 StBerG", "Eigenverantwortung (personal responsibility)", "BERUFSRECHT", "Human-in-the-loop for all tax-relevant outputs", "Mandatory review step before archival/export"),
        ("§ 57 StBerG", "AI outputs = advisory only (Vorschlag)", "BERUFSRECHT", "LLM results marked as suggestion, never final", "Disclaimer on all AI-generated content"),
        ("§ 33 StBerG", "Personal liability for errors (Haftung)", "ZIVILRECHT", "OCR errors must be catchable by human reviewer", "Confidence scores, flag uncertain numbers"),
        ("§ 33 StBerG", "Preserve original evidence", "ZIVILRECHT", "Sandwich PDF: scan image behind text layer", "Never text-only output, always image+text"),
        ("GoBD Rn.136", "Maschinelle Auswertbarkeit (machine readability)", "STEUERRECHT", "PDF/A with searchable OCR text layer required", "ocrmypdf --output-type pdfa-2"),
        ("GoBD Rn.59", "Unveränderbarkeit (immutability of records)", "STEUERRECHT", "Write-once archive, no post-archival modification", "NTFS read-only or DMS immutability"),
        ("GoBD Rn.151", "Verfahrensdokumentation (procedural docs)", "STEUERRECHT", "Written procedure for entire scan workflow", "Document must exist before go-live"),
        ("AO § 147", "10-year retention (Belege, Rechnungen)", "STEUERRECHT", "Automated retention tracking + deletion after expiry", "Retention DB with expiry date flagging"),
        ("AO § 147", "6-year retention (Geschäftsbriefe)", "STEUERRECHT", "Separate retention class for correspondence", "Document type classification required"),
        ("DSGVO Art.44", "No personal data transfer outside EU/EEA", "BUSSGELD", "No US cloud services (CLOUD Act, Schrems II risk)", "Even EU-hosted US providers problematic"),
        ("DSGVO Art.17", "Recht auf Löschung (right to erasure)", "BUSSGELD", "Deletion mechanism after retention period expires", "Automated Löschkonzept implementation"),
        ("DSGVO Art.28", "AV-Vertrag for any data processor", "BUSSGELD", "External processing needs Data Processing Agreement", "On-premise pipeline avoids this entirely"),
        ("DSGVO Art.32", "Encryption at rest for personal data", "BUSSGELD", "BitLocker (Win) / FileVault (Mac) on all drives", "System prerequisite check at setup"),
        ("DSGVO Art.9", "Special category data protection", "BUSSGELD", "Financial data = highest protection class", "Access control + audit logging required"),
        ("BSI RESISCAN", "Ersetzendes Scannen (replacement scanning)", "RECOMMENDED", "Min 300 DPI color, SHA-256 hash, quality check", "Default: 300 DPI color + hash per document"),
        ("BSI RESISCAN", "Schutzbedarfsanalyse per document type", "RECOMMENDED", "Protection needs assessment before going live", "Pre-deployment analysis required"),
        ("GwG § 8", "Anti-money-laundering document retention", "ORDNUNGSW.", "5 years after mandate end for KYC documents", "Separate retention class for GwG docs"),
        ("GwG § 6", "Document searchability for investigations", "ORDNUNGSW.", "Quick retrieval for suspicious activity reports", "Full-text search via OCR text layer"),
        ("BOStB § 4", "Supervision of all tools by Steuerberater", "BERUFSRECHT", "All automated workflows under professional supervision", "Audit trail: who approved what, when"),
        ("§ 67 StBerG", "Berufshaftpflicht notification", "ZIVILRECHT", "Professional liability insurer must be informed", "Notify insurer of AI-assisted workflows"),
    ]

    # Table dimensions — fill available space
    tab_w = c34w
    tab_header_h = 16
    n_rows = len(reg_table)
    # Reserve bottom 40% of available height for autoresearch
    auto_section_h = AVAIL_H * 0.38
    table_avail = AVAIL_H * 0.62 - 28  # minus section title
    row_h = min(20, (table_avail - tab_header_h) / n_rows)

    # Column widths
    cws = [62, 108, 58, tab_w - 62 - 108 - 58 - 92, 92]
    labels = ["REGULATION", "CONSTRAINT", "SEVERITY", "TECHNICAL RULE", "PIPELINE IMPACT"]

    # Header row
    hx = c3x; hy = cy3 - 2*mm
    c.saveState(); c.setFillColor(C["thead"])
    c.roundRect(hx, hy-tab_header_h, tab_w, tab_header_h, 2, fill=1, stroke=0)
    c.setFillColor(C["blue"]); c.setFont("Helvetica-Bold",7.5)
    cx = hx+4
    for j,lbl in enumerate(labels): c.drawString(cx, hy-tab_header_h+5, lbl); cx+=cws[j]
    c.restoreState()

    # Data rows
    for i,(reg,constraint,severity,rule,impact) in enumerate(reg_table):
        ry = hy - tab_header_h - (i+1)*row_h
        bg = C["trow2"] if i%2==0 else C["trow"]
        c.saveState(); c.setFillColor(bg); c.rect(hx,ry,tab_w,row_h,fill=1,stroke=0)
        cx = hx+4
        # Regulation
        c.setFillColor(C["cyan"]); c.setFont("Helvetica-Bold",7); c.drawString(cx, ry+row_h-8, reg)
        cx += cws[0]
        # Constraint (wrap)
        c.setFillColor(C["txt"]); c.setFont("Helvetica",6.5)
        cl = wrap(c, constraint, "Helvetica", 6.5, cws[1]-6)
        for j,ln in enumerate(cl[:2]): c.drawString(cx, ry+row_h-8-j*8, ln)
        cx += cws[1]
        # Severity badge
        sc,sb = SEV_C.get(severity,(C["muted"],C["card"]))
        bw = c.stringWidth(severity,"Helvetica-Bold",6.5)+10
        c.setFillColor(sb); c.roundRect(cx, ry+row_h-12, bw, 12, 2, fill=1, stroke=0)
        c.setFillColor(sc); c.setFont("Helvetica-Bold",6.5); c.drawString(cx+5, ry+row_h-9, severity)
        cx += cws[2]
        # Rule (wrap)
        c.setFillColor(C["txt2"]); c.setFont("Helvetica",6)
        rl = wrap(c, rule, "Helvetica", 6, cws[3]-6)
        for j,ln in enumerate(rl[:2]): c.drawString(cx, ry+row_h-8-j*8, ln)
        cx += cws[3]
        # Impact (wrap)
        c.setFillColor(C["muted"]); c.setFont("Helvetica",6)
        il = wrap(c, impact, "Helvetica", 6, cws[4]-6)
        for j,ln in enumerate(il[:2]): c.drawString(cx, ry+row_h-8-j*8, ln)
        c.restoreState()

    # ═══════════════════════════════════════════════════════════════
    # AUTORESEARCH SECTION (below table, spanning cols 3-4)
    # ═══════════════════════════════════════════════════════════════
    auto_top = hy - tab_header_h - (n_rows+1)*row_h - 6*mm
    sec(c, c3x, auto_top, "AUTORESEARCH EVOLUTION (KARPATHY LOOP)", C["purple"],
        "Autonomous overnight optimization loops — synthetic data only, § 203 safe")

    loops = [
        ("A1","Image\nPreprocess","CER","~300","Deskew, binarize, denoise,\ncontrast, sharpness",C["blue"],"preprocess.py"),
        ("A2","OCR Engine\nConfig","WER+Num","~200","PSM, OEM, whitelist,\nengine routing",C["purple"],"ocr_config.json"),
        ("A3","PDF\nCompress","Size×SSIM","~500","JBIG2 threshold, JPEG\nquality, per-page",C["green"],"compress.py"),
        ("A4","Layout\nAnalysis","F1","~200","Zone detection, table\nextraction rules",C["pink"],"layout.py"),
        ("A5","LLM Prompt\nOptimize","Accuracy","~100","System prompt, few-shot,\nCoT, output fmt",C["amber"],"prompts.md"),
        ("A6","Date Regex\nPatterns","F1","~1000","German date formats,\npriority order",C["cyan"],"patterns.py"),
    ]

    loop_top = auto_top - 18
    loop_gap = 4*mm
    loop_w = (tab_w - 5*loop_gap) / 6
    loop_h = (auto_section_h - 80*mm)  # leave room for firewall + phases
    loop_h = max(loop_h, 44*mm)

    for i,(tag,name,metric,rate,desc,color,file) in enumerate(loops):
        lx = c3x + i*(loop_w+loop_gap)
        ly = loop_top - loop_h
        rr(c, lx, ly, loop_w, loop_h, fill=C["card"])
        c.saveState(); c.setFillColor(color)
        c.roundRect(lx+2, ly+loop_h-4, loop_w-4, 3, 1.5, fill=1,stroke=0)
        c.setFont("Helvetica-Bold",13); c.drawString(lx+8, ly+loop_h-18, tag)
        c.setFillColor(C["txt"]); c.setFont("Helvetica-Bold",8)
        for j,nl in enumerate(name.split("\n")):
            c.drawString(lx+8, ly+loop_h-30-j*10, nl)
        c.setFillColor(C["cyan"]); c.setFont("Helvetica",7)
        c.drawString(lx+8, ly+loop_h-54, f"Metric: {metric}")
        c.setFillColor(C["muted"]); c.drawString(lx+8, ly+loop_h-64, f"~{rate} exp/night")
        c.setFillColor(C["txt2"]); c.setFont("Helvetica",6)
        for j,dl in enumerate(desc.split("\n")):
            c.drawString(lx+8, ly+loop_h-78-j*8, dl)
        c.setFillColor(C["muted"]); c.setFont("Helvetica",6)
        c.drawString(lx+8, ly+6, file)
        c.restoreState()

    # ─── Synthetic data firewall ──────────────────────────────────
    fw_top = loop_top - loop_h - 6*mm
    fw_h = 22*mm
    rr(c, c3x, fw_top-fw_h, tab_w, fw_h, fill=C["rbg"], stroke=C["red"], sw=1.5)
    c.saveState()
    c.setFillColor(C["red"]); c.setFont("Helvetica-Bold",11)
    c.drawString(c3x+12, fw_top-13, "SYNTHETIC DATA FIREWALL  —  § 203 StGB Compliance Boundary")
    c.setFillColor(HexColor("#fca5a5")); c.setFont("Helvetica",8)
    c.drawString(c3x+12, fw_top-26, "All autoresearch loops run EXCLUSIVELY on synthetic data (Faker invoices, ICDAR benchmarks). Never client documents.")
    c.drawString(c3x+12, fw_top-38, "Only optimized CONFIG FILES cross into production. Production pipeline uses human-in-the-loop review (§ 57 StBerG).")
    c.drawString(c3x+12, fw_top-50, "Research environment is fully isolated — no client data exposure, no § 203 applicability, no supervision required.")
    c.restoreState()

    # ─── Evolution phases ─────────────────────────────────────────
    ph_top = fw_top - fw_h - 6*mm
    ph_h = max(26*mm, BOT_Y + 2*mm - (ph_top - 30*mm))  # fill to bottom
    ph_gap = 4*mm
    ph_w = (tab_w - 3*ph_gap) / 4

    phases = [
        ("PHASE 1","Static Pipeline","Manual ocrmypdf defaults.\nNo optimization loops.\nBaseline CER ~8-15%.\nPDF/A output only.",C["blue"],"CURRENT","0 weeks"),
        ("PHASE 2","OCR Autoresearch","A1 + A2 loops active.\n15-40% CER improvement.\nCPU only, no GPU needed.\n~500 experiments/night.",C["purple"],"QUICK WIN","+2 weeks"),
        ("PHASE 3","Full Integration","All A1-A6 loops active.\nLLM extraction >90% acc.\nGPU recommended for A5.\nFull field extraction.",C["amber"],"TARGET","+6 weeks"),
        ("PHASE 4","Feedback Loop","Anonymized prod metrics.\nSelf-improving pipeline.\nAdapts to new doc types.\nDrift detection.",C["green"],"VISION","+10 weeks"),
    ]

    for i,(tag,name,desc,color,badge,time) in enumerate(phases):
        px = c3x + i*(ph_w+ph_gap)
        py = ph_top - ph_h
        rr(c, px, py, ph_w, ph_h, fill=C["card"])
        c.saveState(); c.setFillColor(color)
        c.roundRect(px+2, py+ph_h-4, ph_w-4, 3, 1.5, fill=1,stroke=0)
        c.setFont("Helvetica-Bold",9); c.drawString(px+8, py+ph_h-16, tag)
        # Badge
        bw=c.stringWidth(badge,"Helvetica-Bold",6.5)+8
        c.setFillColor(C["card2"]); c.roundRect(px+ph_w-bw-6,py+ph_h-18,bw,12,2,fill=1,stroke=0)
        c.setFillColor(color); c.setFont("Helvetica-Bold",6.5); c.drawString(px+ph_w-bw-2,py+ph_h-15,badge)
        c.setFillColor(C["txt"]); c.setFont("Helvetica-Bold",8.5); c.drawString(px+8, py+ph_h-28, name)
        c.setFillColor(C["txt2"]); c.setFont("Helvetica",7)
        for j,dl in enumerate(desc.split("\n")):
            c.drawString(px+8, py+ph_h-42-j*10, dl)
        c.setFillColor(C["muted"]); c.setFont("Helvetica",7); c.drawString(px+8, py+6, time)
        c.restoreState()
        if i<len(phases)-1:
            arrow(c, px+ph_w, py+ph_h/2, px+ph_w+ph_gap, py+ph_h/2, C["muted"], 1)

    # ─── Footer ───────────────────────────────────────────────────
    c.saveState(); c.setFillColor(C["hdr"]); c.rect(0,0,PAGE_W,FOOTER_H,fill=1,stroke=0)
    c.setFillColor(C["blue"]); c.rect(0,FOOTER_H,PAGE_W,1.5,fill=1,stroke=0)
    c.setFillColor(C["muted"]); c.setFont("Helvetica",7)
    c.drawString(M, 3.5*mm, "STEUB Use Cases  ·  10_STEUB-usecases  ·  PDFScanner.app v2025.3 Analysis → Python-on-Windows  ·  All OSS (Apache/MIT/BSD)  ·  Autoresearch: github.com/karpathy/autoresearch")
    c.drawRightString(PAGE_W-M, 3.5*mm, "Generated 2026-03-15  ·  cordsjon/10_STEUB-usecases")
    c.restoreState()

    c.save()
    print(f"Poster saved: {OUT}")
    return OUT

if __name__ == "__main__":
    create_poster()
