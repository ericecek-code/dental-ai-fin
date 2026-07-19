"""
PDF reporter pre Dental AI - slovenské hlavičky + stĺpec Zub.
Triedy prekladajú sa do slovenčiny. Úplne bez anglických labelov v reporte.
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Pokus o registraciu Unicode fontu (DejaVu Sans z reportlab/sample/fonts alebo systemu)
def _register_unicode_font():
    # Moznosti: cms font (WinAnsiEncoding) - NEobsahuje slovensku diakritiku
    # Reportlab standard sample font - DejaVuSans
    candidates = [
        ('DejaVuSans',           'C:/Windows/Fonts/DejaVuSans.ttf'),
        ('Arial',                'C:/Windows/Fonts/arial.ttf'),
        ('Calibri',              'C:/Windows/Fonts/calibri.ttf'),
        ('Segoe UI',             'C:/Windows/Fonts/segoeui.ttf'),
        ('Verdana',              'C:/Windows/Fonts/verdana.ttf'),
        ('Tahoma',               'C:/Windows/Fonts/tahoma.ttf'),
        ('DejaVuSans-system',    'C:/Windows/Fonts/DejaVuSans.ttf'),
    ]
    for name, path in candidates:
        try:
            pdfmetrics.registerFont(TTFont(name, path))
            return name
        except Exception:
            continue
    return 'Helvetica'  # fallback bez diakritiky

UNICODE_FONT = _register_unicode_font()
UNICODE_FONT_BOLD = UNICODE_FONT  # rovnake pre teraz

# Slovenske preklady tried (mirror of frontend/src/lib/labels.ts)
SK_LABELS = {
    "Caries":                  "Kaz",
    "Deep Caries":             "Hlboký kaz",
    "Crown":                   "Korunka",
    "Implant":                 "Implantát",
    "Malaligned":              "Zlá poloha zuba",
    "Mandibular Canal":        "Mandibulárny kanál",
    "Missing teeth":           "Chýbajúci zub",
    "Periapical lesion":       "Periapikálna lézia",
    "Retained root":           "Retinovaný koreň",
    "Root Canal Treatment":    "Endodoncia",
    "Root Piece":              "Koreňový fragment",
    "Impacted tooth":          "Retinovaný zub",
    "impacted tooth":          "Retinovaný zub",
    "Filling":                 "Plomba",
    "plating":                 "Dlaha",
    "wire":                    "Drôt",
    "Cyst":                    "Cysta",
    "Root resorption":         "Resorpcia koreňa",
    "Primary teeth":           "Mliečne zuby",
}

SK_SEVERITY = {
    "urgent":     "Urgentné",
    "treat_soon": "Liečiť čoskoro",
    "watch":      "Sledovať",
}

def sk_label(raw: str) -> str:
    return SK_LABELS.get(raw, SK_LABELS.get(raw.lower() if raw else "", raw or ""))

def sk_sev(raw: str) -> str:
    return SK_SEVERITY.get(raw, raw or "")


def generate_pdf(result: dict, output_path: str):
    """Vygeneruje PDF report v slovencine.

    Vstup: result dict (z /analyze endpoint)
    Vystup: zapise PDF do output_path
    """
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            leftMargin=18*mm, rightMargin=18*mm,
                            topMargin=18*mm, bottomMargin=18*mm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("title", parent=styles["Title"], fontSize=20,
                                 fontName=UNICODE_FONT, leading=24)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=13,
                        textColor=colors.HexColor("#1e40af"), fontName=UNICODE_FONT, leading=16)
    body = ParagraphStyle("body", parent=styles["Normal"], fontSize=10,
                          fontName=UNICODE_FONT, leading=13)
    cell_style = ParagraphStyle("cell", parent=styles["Normal"], fontSize=9,
                                fontName=UNICODE_FONT, leading=11)
    header_cell_style = ParagraphStyle("hcell", parent=styles["Normal"], fontSize=9,
                                       fontName=UNICODE_FONT, leading=11,
                                       textColor=colors.whitesmoke)

    story = []
    story.append(Paragraph("DenteScope AI · Správa z analýzy", title_style))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph(f"ID úlohy: <b>{result.get('job_id', '')}</b>", body))
    story.append(Paragraph(f"Súbor: {result.get('filename', '')}", body))
    story.append(Paragraph(f"Prah spoľahlivosti: <b>{result.get('conf_threshold', 0):.2f}</b>", body))
    story.append(Paragraph(f"Počet nálezov: <b>{result.get('detection_count', 0)}</b>", body))
    story.append(Spacer(1, 6*mm))
    story.append(Paragraph("Nájdené nálezy", h2))

    # Hlavna tabulka
    data = [["#", "Zub", "Nález", "Pravdepodobnosť", "Závažnosť"]]
    for i, det in enumerate(result.get("detections", []), start=1):
        tooth = det.get("tooth_number") or "-"
        label_sk = sk_label(det.get("label", ""))
        conf_pct = f"{float(det.get('confidence', 0)) * 100:.1f}%"
        sev_sk = sk_sev(det.get("severity", ""))
        # Wrap text v Paragraph pre spravne zalamovanie a unicode font
        data.append([
            Paragraph(str(i), cell_style),
            Paragraph(str(tooth), cell_style),
            Paragraph(label_sk, cell_style),
            Paragraph(conf_pct, cell_style),
            Paragraph(sev_sk, cell_style),
        ])

    if len(data) == 1:
        data.append(["-", "-", "Žiadne nálezy", "-", "-"])

    # Wrap header paragraphs
    header_row = [Paragraph(h, header_cell_style) for h in ["#", "Zub", "Nález", "Pravdepodobnosť", "Závažnosť"]]
    data[0] = header_row

    table = Table(data, colWidths=[12*mm, 25*mm, 58*mm, 35*mm, 40*mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e40af")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("ALIGN", (0, 1), (3, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(table)

    # Legenda kvadrantov
    story.append(Spacer(1, 6*mm))
    story.append(Paragraph("Legenda kvadrantov", h2))
    story.append(Paragraph(
        "Q1 = ľavý horný · Q2 = pravý horný · Q3 = ľavý dolný · Q4 = pravý dolný",
        body
    ))

    doc.build(story)
