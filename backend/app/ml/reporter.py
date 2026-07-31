"""
PDF reporter pre Dental AI - profesionálne reporty s farbenými overlay obrázkami,
tabuľkou nálezov, zdravotným skóre, meraniami a odporúčaniami.
Všetky popisky sú v slovenčine.
"""
from __future__ import annotations

import io
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    Image as RLImage, HRFlowable, KeepTogether,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ---------------------------------------------------------------------------
# Font registration (supports Slovak diacritics)
# ---------------------------------------------------------------------------
def _register_unicode_font() -> str:
    candidates = [
        ("DejaVuSans", "C:/Windows/Fonts/DejaVuSans.ttf"),
        ("Arial", "C:/Windows/Fonts/arial.ttf"),
        ("Calibri", "C:/Windows/Fonts/calibri.ttf"),
        ("Segoe UI", "C:/Windows/Fonts/segoeui.ttf"),
        ("Verdana", "C:/Windows/Fonts/verdana.ttf"),
        ("Tahoma", "C:/Windows/Fonts/tahoma.ttf"),
    ]
    for name, path in candidates:
        try:
            pdfmetrics.registerFont(TTFont(name, path))
            return name
        except Exception:
            continue
    return "Helvetica"


UNICODE_FONT: str = _register_unicode_font()
UNICODE_FONT_BOLD: str = UNICODE_FONT  # same face, bold applied via tags

# ---------------------------------------------------------------------------
# Color constants
# ---------------------------------------------------------------------------
COLOR_PRIMARY = colors.HexColor("#0D9488")      # teal
COLOR_PRIMARY_DARK = colors.HexColor("#0F766E")
COLOR_PRIMARY_LIGHT = colors.HexColor("#CCFBF1")
COLOR_ACCENT = colors.HexColor("#14B8A6")
COLOR_BG = colors.HexColor("#F0FDFA")
COLOR_TEXT = colors.HexColor("#134E4A")
COLOR_GREY = colors.HexColor("#94A3B8")
COLOR_ROW_ALT = colors.HexColor("#F1F5F9")

# Severity palette
SEVERITY_COLORS = {
    "urgent":   colors.HexColor("#DC2626"),  # red
    "treat_soon": colors.HexColor("#F59E0B"),  # amber
    "watch":    colors.HexColor("#10B981"),  # emerald
}
SEVERITY_BG = {
    "urgent":   colors.HexColor("#FEF2F2"),
    "treat_soon": colors.HexColor("#FFFBEB"),
    "watch":    colors.HexColor("#ECFDF5"),
}

# ---------------------------------------------------------------------------
# Slovak labels & severity (backward-compatible)
# ---------------------------------------------------------------------------
SK_LABELS = {
    "Caries": "Kaz",
    "Deep Caries": "Hlbokejší kaz",
    "Crown": "Korunka",
    "Implant": "Implantát",
    "Malaligned": "Zlá poloha zuba",
    "Mandibular Canal": "Mandibulárny kanál",
    "Missing teeth": "Chýbajúci zub",
    "Periapical lesion": "Periapikálna lézia",
    "Retained root": "Retinovaný koreň",
    "Root Canal Treatment": "Endodoncia",
    "Root Piece": "Koreňový fragment",
    "Impacted tooth": "Retinovaný zub",
    "impacted tooth": "Retinovaný zub",
    "Filling": "Plomba",
    "plating": "Dlaha",
    "wire": "Drôt",
    "Cyst": "Cysta",
    "Root resorption": "Resorpcia koreňa",
    "Primary teeth": "Mliečne zuby",
}

SK_SEVERITY = {
    "urgent": "Urgentné",
    "treat_soon": "Liečiť čoskoro",
    "watch": "Sledovať",
}

# Recommendation text by class
SK_RECOMMENDATIONS = {
    "Caries": "Okamžitá stomatologická konzultácia, prípadne vŕtanie.",
    "Deep Caries": "Urgentná liečba – riziko zápalu nervu. Endodoncia môže byť potrebná.",
    "Crown": "Pravidelná kontrola stavu korunky a podložia.",
    "Implant": "Kontrola implantátu a peri-implantárnych tkanív.",
    "Malaligned": "Ortodontické vyšetrenie, prípadne úprava.",
    "Mandibular Canal": "Informácia pre plánovanie chirurgických zákrokov.",
    "Missing teeth": "Náhrada chýbajúceho zuba – implantát alebo mostík.",
    "Periapical lesion": "Urgentná liečba – endodoncia alebo extrakcia.",
    "Retained root": "Chirurgické odstránenie retinovaného koreňa.",
    "Root Canal Treatment": "Kontrola endodontického ošetrenia (RTG kontrola).",
    "Root Piece": "Odstránenie koreňového zvyšku.",
    "Impacted tooth": "Chirurgické alebo ortodontické riešenie retinovaného zuba.",
    "impacted tooth": "Chirurgické alebo ortodontické riešenie retinovaného zuba.",
    "Filling": "Kontrola integrity plomby.",
    "plating": "Kontrola dlhy a fixácie.",
    "wire": "Kontrola drôtovej fixácie.",
    "Cyst": "Chirurgické odstránenie cysty, histologické vyšetrenie.",
    "Root resorption": "Sledovanie progresie, prípadne endodoncia.",
    "Primary teeth": "Sledovanie výmeny mliečnych zubov.",
}

# BGR -> hex for legend colors (from detector.py COLOR_MAP)
BGR_COLORS = {
    "Caries": (0, 215, 255),
    "Deep Caries": (0, 0, 255),
    "Crown": (209, 206, 0),
    "Implant": (180, 130, 0),
    "Malaligned": (160, 80, 60),
    "Mandibular Canal": (255, 200, 180),
    "Missing teeth": (160, 50, 60),
    "Periapical lesion": (140, 20, 211),
    "Retained root": (40, 60, 130),
    "Root Canal Treatment": (60, 140, 220),
    "Root Piece": (40, 40, 100),
    "Impacted tooth": (200, 100, 20),
    "impacted tooth": (200, 100, 20),
    "Filling": (220, 230, 240),
    "plating": (180, 180, 140),
    "wire": (200, 200, 200),
    "Cyst": (40, 20, 130),
    "Root resorption": (130, 40, 60),
    "Primary teeth": (200, 220, 240),
}


def sk_label(raw: str) -> str:
    return SK_LABELS.get(raw, SK_LABELS.get(raw.lower() if raw else "", raw or ""))


def sk_sev(raw: str) -> str:
    return SK_SEVERITY.get(raw, raw or "")


def sk_recommendation(label: str) -> str:
    return SK_RECOMMENDATIONS.get(label, "Kontrola u stomatológa.")


# ---------------------------------------------------------------------------
# Health score computation
# ---------------------------------------------------------------------------
_SEVERITY_WEIGHT = {"urgent": 30, "treat_soon": 15, "watch": 5}

def _compute_health_score(detections: list[dict]) -> dict:
    """Compute health score (0-100) and breakdown."""
    base = 100
    breakdown = {"Urgentné": 0, "Liečiť čoskoro": 0, "Sledovať": 0}
    for det in detections:
        sev = det.get("severity", "watch")
        w = _SEVERITY_WEIGHT.get(sev, 5)
        base -= w
        sk = SK_SEVERITY.get(sev, sev)
        breakdown[sk] = breakdown.get(sk, 0) + 1
    score = max(0, min(100, base))
    return {"score": score, "breakdown": breakdown, "total": len(detections)}


def _score_color(score: int) -> colors.Color:
    if score >= 80:
        return colors.HexColor("#10B981")
    elif score >= 60:
        return colors.HexColor("#F59E0B")
    else:
        return colors.HexColor("#DC2626")


def _score_label(score: int) -> str:
    if score >= 80:
        return "Dobrý"
    elif score >= 60:
        return "Uspokojivý"
    else:
        return "Vyžaduje pozornosť"


# ---------------------------------------------------------------------------
# Recommendation logic
# ---------------------------------------------------------------------------
def _generate_recommendations(detections: list[dict]) -> list[str]:
    """Generate prioritized recommendations from detections."""
    recs = []
    for det in sorted(detections, key=lambda d: {"urgent": 0, "treat_soon": 1, "watch": 2}.get(d.get("severity", "watch"), 3)):
        label = det.get("label", "")
        tooth = det.get("tooth_number", "?")
        rec = sk_recommendation(label)
        entry = f"• {sk_label(label)} ({tooth}): {rec}"
        if entry not in recs:
            recs.append(entry)
    return recs


def _followup_interval(detections: list[dict]) -> str:
    severities = {d.get("severity", "watch") for d in detections}
    if "urgent" in severities:
        return "3 mesiace"
    elif "treat_soon" in severities:
        return "6 mesiacov"
    return "12 mesiacov"


# ---------------------------------------------------------------------------
# PDF Style helpers
# ---------------------------------------------------------------------------
def _styles():
    ss = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle", parent=ss["Title"], fontSize=22, fontName=UNICODE_FONT,
        textColor=COLOR_PRIMARY_DARK, leading=26, spaceAfter=2*mm,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle", parent=ss["Normal"], fontSize=11, fontName=UNICODE_FONT,
        textColor=COLOR_GREY, leading=14, spaceAfter=4*mm,
    )
    h2 = ParagraphStyle(
        "H2", parent=ss["Heading2"], fontSize=14, fontName=UNICODE_FONT,
        textColor=COLOR_PRIMARY_DARK, leading=18, spaceBefore=6*mm, spaceAfter=3*mm,
    )
    h3 = ParagraphStyle(
        "H3", parent=ss["Heading3"], fontSize=11, fontName=UNICODE_FONT,
        textColor=COLOR_PRIMARY, leading=14, spaceBefore=3*mm, spaceAfter=2*mm,
    )
    body = ParagraphStyle(
        "Body", parent=ss["Normal"], fontSize=10, fontName=UNICODE_FONT,
        textColor=COLOR_TEXT, leading=14, spaceAfter=2*mm,
    )
    small = ParagraphStyle(
        "Small", parent=ss["Normal"], fontSize=8, fontName=UNICODE_FONT,
        textColor=COLOR_GREY, leading=10,
    )
    cell = ParagraphStyle(
        "Cell", parent=ss["Normal"], fontSize=9, fontName=UNICODE_FONT,
        textColor=COLOR_TEXT, leading=11,
    )
    cell_bold = ParagraphStyle(
        "CellBold", parent=ss["Normal"], fontSize=9, fontName=UNICODE_FONT,
        textColor=colors.white, leading=11,
    )
    score_big = ParagraphStyle(
        "ScoreBig", parent=ss["Normal"], fontSize=36, fontName=UNICODE_FONT,
        textColor=COLOR_PRIMARY_DARK, alignment=1, leading=40,
    )
    score_label_style = ParagraphStyle(
        "ScoreLabel", parent=ss["Normal"], fontSize=12, fontName=UNICODE_FONT,
        textColor=COLOR_TEXT, alignment=1, leading=14,
    )
    footer = ParagraphStyle(
        "Footer", parent=ss["Normal"], fontSize=7, fontName=UNICODE_FONT,
        textColor=COLOR_GREY, alignment=1, leading=9,
    )
    return {
        "title": title_style, "subtitle": subtitle_style, "h2": h2, "h3": h3,
        "body": body, "small": small, "cell": cell, "cell_bold": cell_bold,
        "score_big": score_big, "score_label": score_label_style, "footer": footer,
    }


# ---------------------------------------------------------------------------
# Main PDF generation
# ---------------------------------------------------------------------------
def generate_pdf(
    result: dict,
    output_path: str = None,
    image_path: str = None,
    patient_id: str = None,
    xray_type: str = "panoramic",
    measurements: list = None,
) -> bytes:
    """Generate a professional dental PDF report.

    Parameters
    ----------
    result : dict
        Analysis result dictionary (from /analyze endpoint).
    output_path : str, optional
        If given, writes PDF to this path. Always returns bytes.
    image_path : str, optional
        Path to the overlay image to embed. If None, tries result['overlay_path'].
    patient_id : str, optional
        Anonymised patient identifier. Falls back to job_id.
    xray_type : str
        Type of X-ray: panoramic, bitewing, periapical.
    measurements : list[dict], optional
        CEJ-to-bone-crest measurements. Each dict: {'tooth', 'value_mm', 'side'}.

    Returns
    -------
    bytes : PDF content.
    """
    S = _styles()
    now = datetime.now()
    job_id = result.get("job_id", "")
    pid = patient_id or f"PAT-{job_id[:8].upper()}"
    detections = result.get("detections", [])

    # Sort detections: urgent first, then treat_soon, then watch
    sev_order = {"urgent": 0, "treat_soon": 1, "watch": 2}
    detections = sorted(detections, key=lambda d: sev_order.get(d.get("severity", "watch"), 3))

    # Determine overlay image path
    if image_path is None:
        image_path = result.get("overlay_path") or result.get("enhanced_image_path")

    # X-ray type label
    xray_labels = {
        "panoramic": "Panoramatický",
        "bitewing": "Bitingový",
        "periapical": "Periapikálny",
    }
    xray_label = xray_labels.get(xray_type, xray_type)

    # Build story
    story = []

    # ── HEADER ───────────────────────────────────────────────────────────
    story.append(Paragraph("DenteScope AI", S["title"]))
    story.append(Paragraph("Správa z analýzy RTG snímky", S["subtitle"]))
    story.append(Spacer(1, 1*mm))
    story.append(HRFlowable(width="100%", thickness=1.5, color=COLOR_PRIMARY, spaceAfter=3*mm))

    # Info row as a table
    info_data = [
        [Paragraph(f"<b>Dátum:</b> {now.strftime('%d.%m.%Y %H:%M')}", S["cell"]),
         Paragraph(f"<b>Pacient:</b> {pid}", S["cell"]),
         Paragraph(f"<b>Typ RTG:</b> {xray_label}", S["cell"])],
        [Paragraph(f"<b>ID úlohy:</b> {job_id}", S["cell"]),
         Paragraph(f"<b>Súbor:</b> {result.get('filename', '-')}", S["cell"]),
         Paragraph(f"<b>Prah:</b> {result.get('conf_threshold', 0):.2f}", S["cell"])],
    ]
    info_table = Table(info_data, colWidths=[60*mm, 55*mm, 55*mm])
    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_BG),
        ("BOX", (0, 0), (-1, -1), 0.5, COLOR_PRIMARY),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, COLOR_PRIMARY_LIGHT),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 5*mm))

    # ── HEALTH SCORE ─────────────────────────────────────────────────────
    score_data = _compute_health_score(detections)
    score = score_data["score"]
    sc = _score_color(score)
    sl = _score_label(score)

    # Visual gauge
    gauge_filled = int(score / 100 * 30)
    gauge_empty = 30 - gauge_filled
    gauge_bar = "█" * gauge_filled + "░" * gauge_empty

    story.append(Paragraph("Zdravotné skóre", S["h2"]))
    score_content = [
        [
            Paragraph(f"<font size='36' color='{sc.hexval()}'>{score}</font>", S["cell"]),
            Paragraph(f"<font size='11' color='{COLOR_TEXT.hexval()}'>/ 100</font>", S["cell"]),
            Paragraph(f"<font size='12' color='{sc.hexval()}'>{sl}</font>", S["cell"]),
        ],
    ]
    score_table = Table(score_content, colWidths=[35*mm, 25*mm, 60*mm])
    score_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, 0), 1, COLOR_PRIMARY_LIGHT),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 2*mm))

    # Gauge text
    story.append(Paragraph(f"<font face='{UNICODE_FONT}' size='9' color='#64748B'>{gauge_bar}</font>", S["body"]))
    story.append(Spacer(1, 2*mm))

    # Breakdown
    if score_data["breakdown"]:
        bd_rows = [[
            Paragraph("<b>Kategória</b>", S["cell_bold"]),
            Paragraph("<b>Počet</b>", S["cell_bold"]),
        ]]
        for cat, count in score_data["breakdown"].items():
            if count > 0:
                bd_rows.append([
                    Paragraph(cat, S["cell"]),
                    Paragraph(str(count), S["cell"]),
                ])
        if len(bd_rows) > 1:
            bd_table = Table(bd_rows, colWidths=[80*mm, 30*mm])
            bd_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), COLOR_PRIMARY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_ROW_ALT]),
                ("GRID", (0, 0), (-1, -1), 0.3, COLOR_PRIMARY_LIGHT),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ]))
            story.append(bd_table)
    story.append(Spacer(1, 4*mm))

    # ── OVERLAY IMAGE ────────────────────────────────────────────────────
    if image_path and os.path.isfile(image_path):
        story.append(Paragraph("Farebný overlay", S["h2"]))
        try:
            img = RLImage(image_path, width=170*mm, height=120*mm)
            story.append(img)
            story.append(Spacer(1, 3*mm))
            # Legend
            legend_items = []
            seen_labels = set()
            for det in detections:
                lbl = det.get("label", "")
                if lbl in seen_labels:
                    continue
                seen_labels.add(lbl)
                bgr = BGR_COLORS.get(lbl, (127, 255, 0))
                hex_color = "#{:02X}{:02X}{:02X}".format(bgr[2], bgr[1], bgr[0])
                legend_items.append(
                    f"<font color='{hex_color}'>■</font> {sk_label(lbl)}"
                )
            if legend_items:
                story.append(Paragraph(
                    "Legenda: " + " &nbsp;·&nbsp; ".join(legend_items),
                    S["small"]
                ))
            story.append(Spacer(1, 3*mm))
        except Exception:
            pass  # skip image if unreadable

    # ── FINDINGS TABLE ───────────────────────────────────────────────────
    story.append(Paragraph("Tabuľka nálezov", S["h2"]))
    header_cells = [
        Paragraph("<b>Zub (FDI)</b>", S["cell_bold"]),
        Paragraph("<b>Nález</b>", S["cell_bold"]),
        Paragraph("<b>Závažnosť</b>", S["cell_bold"]),
        Paragraph("<b>Istota</b>", S["cell_bold"]),
        Paragraph("<b>Odporúčanie</b>", S["cell_bold"]),
    ]
    table_data = [header_cells]

    if not detections:
        table_data.append([
            Paragraph("-", S["cell"]),
            Paragraph("Žiadne nálezy", S["cell"]),
            Paragraph("-", S["cell"]),
            Paragraph("-", S["cell"]),
            Paragraph("Žiadne nálezy", S["cell"]),
        ])
    else:
        for det in detections:
            tooth = det.get("tooth_number") or "-"
            label = sk_label(det.get("label", ""))
            conf = f"{float(det.get('confidence', 0)) * 100:.1f}%"
            sev_key = det.get("severity", "watch")
            sev_display = sk_sev(sev_key)
            rec = sk_recommendation(det.get("label", ""))
            table_data.append([
                Paragraph(str(tooth), S["cell"]),
                Paragraph(label, S["cell"]),
                Paragraph(sev_display, S["cell"]),
                Paragraph(conf, S["cell"]),
                Paragraph(rec, S["cell"]),
            ])

    findings_table = Table(table_data, colWidths=[22*mm, 35*mm, 28*mm, 20*mm, 65*mm])
    ts = [
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.4, COLOR_PRIMARY_LIGHT),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_ROW_ALT]),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]
    # Color-code severity cells
    if detections:
        for i, det in enumerate(detections, start=1):
            sev_key = det.get("severity", "watch")
            bg = SEVERITY_BG.get(sev_key, COLOR_ROW_ALT)
            ts.append(("BACKGROUND", (2, i), (2, i), bg))
    findings_table.setStyle(TableStyle(ts))
    story.append(findings_table)
    story.append(Spacer(1, 6*mm))

    # ── MEASUREMENTS ─────────────────────────────────────────────────────
    if measurements:
        story.append(Paragraph("Merania CEJ – hrebeň kosti", S["h2"]))
        m_header = [
            Paragraph("<b>Zub</b>", S["cell_bold"]),
            Paragraph("<b>Hodnota (mm)</b>", S["cell_bold"]),
            Paragraph("<b>Strana</b>", S["cell_bold"]),
            Paragraph("<b>Stav</b>", S["cell_bold"]),
        ]
        m_data = [m_header]
        for m in measurements:
            val = m.get("value_mm", 0)
            if val <= 2:
                status = "Normálne"
                status_color = "#10B981"
            elif val <= 4:
                status = "Mierna strata"
                status_color = "#F59E0B"
            elif val <= 6:
                status = "Stredná strata"
                status_color = "#F97316"
            else:
                status = "Závažná strata"
                status_color = "#DC2626"
            m_data.append([
                Paragraph(str(m.get("tooth", "?")), S["cell"]),
                Paragraph(f"{val:.1f}", S["cell"]),
                Paragraph(str(m.get("side", "-")), S["cell"]),
                Paragraph(f"<font color='{status_color}'>{status}</font>", S["cell"]),
            ])
        m_table = Table(m_data, colWidths=[25*mm, 35*mm, 30*mm, 40*mm])
        m_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), COLOR_PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_ROW_ALT]),
            ("GRID", (0, 0), (-1, -1), 0.3, COLOR_PRIMARY_LIGHT),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(m_table)
        story.append(Spacer(1, 5*mm))

    # ── RECOMMENDATIONS ──────────────────────────────────────────────────
    story.append(Paragraph("Odporúčania", S["h2"]))
    recs = _generate_recommendations(detections)
    if recs:
        for r in recs:
            story.append(Paragraph(r, S["body"]))
    else:
        story.append(Paragraph("Žiadne špeciálne odporúčania.", S["body"]))
    story.append(Spacer(1, 3*mm))

    # Follow-up
    fu = _followup_interval(detections)
    story.append(Paragraph(
        f"<b>Odporúčaná kontrola:</b> {fu}",
        S["body"]
    ))
    story.append(Spacer(1, 5*mm))

    # Urgent items highlight
    urgent_dets = [d for d in detections if d.get("severity") == "urgent"]
    if urgent_dets:
        story.append(Paragraph("⚠️ Urgentné nálezy", S["h3"]))
        for d in urgent_dets:
            tooth = d.get("tooth_number", "?")
            label = sk_label(d.get("label", ""))
            story.append(Paragraph(
                f"<font color='#DC2626'>● {label} ({tooth})</font> – {sk_recommendation(d.get('label', ''))}",
                S["body"]
            ))
        story.append(Spacer(1, 3*mm))

    # ── QUADRANT LEGEND ──────────────────────────────────────────────────
    story.append(Paragraph("Legenda kvadrantov", S["h3"]))
    story.append(Paragraph(
        "Q1 = ľavý horný &nbsp;·&nbsp; Q2 = pravý horný &nbsp;·&nbsp; "
        "Q3 = ľavý dolný &nbsp;·&nbsp; Q4 = pravý dolný",
        S["body"]
    ))
    story.append(Spacer(1, 8*mm))

    # ── FOOTER ───────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_GREY, spaceAfter=3*mm))
    story.append(Paragraph(
        "Tento report bol vygenerovaný pomocou Dental AI (DenteScope).",
        S["footer"]
    ))
    story.append(Paragraph(
        "Nie je náhradou za odborné vyšetrenie stomatológom.",
        S["footer"]
    ))
    story.append(Paragraph(
        f"DenteScope v1.0 · {now.strftime('%d.%m.%Y %H:%M')}",
        S["footer"]
    ))

    # Build PDF
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=18*mm, bottomMargin=18*mm,
    )
    doc.build(story)
    pdf_bytes = buf.getvalue()
    buf.close()

    # Write to output_path if provided
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)

    return pdf_bytes
