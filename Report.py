"""
report.py — PDF Report Generator for InsightCloud.
Generates a clean, professional PDF summary of AI insights
written in simple language for non-technical users.
"""

import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY


# ─── Theme Colors ──────────────────────────────────────────
GOLD = HexColor("#B88E23")
DARK = HexColor("#2C2418")
MID = HexColor("#6B5D4A")
LIGHT_BG = HexColor("#F5ECD7")
WHITE = HexColor("#FFFFFF")
BORDER = HexColor("#E8DFC9")


def get_custom_styles():
    """Create custom paragraph styles matching InsightCloud theme."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="ReportTitle",
        fontName="Helvetica-Bold",
        fontSize=24,
        textColor=DARK,
        alignment=TA_CENTER,
        spaceAfter=24,
    ))

    styles.add(ParagraphStyle(
        name="ReportSubtitle",
        fontName="Helvetica",
        fontSize=12,
        textColor=MID,
        alignment=TA_CENTER,
        spaceBefore=8,
        spaceAfter=24,
    ))

    styles.add(ParagraphStyle(
        name="SectionHeader",
        fontName="Helvetica-Bold",
        fontSize=14,
        textColor=GOLD,
        spaceBefore=16,
        spaceAfter=8,
    ))

    styles.add(ParagraphStyle(
        name="ICBodyText",
        fontName="Helvetica",
        fontSize=11,
        textColor=DARK,
        alignment=TA_JUSTIFY,
        leading=16,
        spaceAfter=8,
    ))

    styles.add(ParagraphStyle(
        name="QuestionText",
        fontName="Helvetica-Bold",
        fontSize=12,
        textColor=DARK,
        spaceBefore=12,
        spaceAfter=4,
    ))

    styles.add(ParagraphStyle(
        name="InsightText",
        fontName="Helvetica",
        fontSize=11,
        textColor=DARK,
        alignment=TA_JUSTIFY,
        leading=16,
        spaceAfter=6,
        leftIndent=12,
    ))

    styles.add(ParagraphStyle(
        name="FooterText",
        fontName="Helvetica",
        fontSize=8,
        textColor=MID,
        alignment=TA_CENTER,
    ))

    styles.add(ParagraphStyle(
        name="MetaText",
        fontName="Helvetica",
        fontSize=10,
        textColor=MID,
        alignment=TA_CENTER,
        spaceAfter=4,
    ))

    return styles


def clean_markdown(text: str) -> str:
    """
    Convert markdown bold (**text**) to reportlab bold (<b>text</b>)
    and clean up other markdown formatting for PDF.
    """
    import re
    # Convert **bold** to <b>bold</b>
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # Convert *italic* to <i>italic</i>
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    # Remove markdown headers (### etc)
    text = re.sub(r'#{1,6}\s*', '', text)
    # Convert bullet points
    text = text.replace('• ', '  - ')
    # Clean up any remaining markdown
    text = text.replace('`', '')
    return text


def generate_insight_pdf(
    filename: str,
    rows: int,
    columns: int,
    question: str,
    answer: str,
    user_name: str = "User",
    user_role: str = "Analyst",
) -> bytes:
    """
    Generate a professional PDF report from an AI insight.

    Args:
        filename: Name of the dataset file.
        rows: Number of rows in the dataset.
        columns: Number of columns in the dataset.
        question: The user's question.
        answer: The AI-generated insight.
        user_name: Name of the user who generated the report.
        user_role: Role of the user.

    Returns:
        PDF file as bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=30 * mm,
        bottomMargin=25 * mm,
        leftMargin=25 * mm,
        rightMargin=25 * mm,
    )

    styles = get_custom_styles()
    story = []

    # ─── Header ────────────────────────────────────────────
    story.append(Paragraph("InsightCloud", styles["ReportTitle"]))
    story.append(Paragraph("AI-Powered Data Analytics Report", styles["ReportSubtitle"]))
    story.append(HRFlowable(
        width="100%", thickness=2, color=GOLD,
        spaceAfter=16, spaceBefore=4
    ))

    # ─── Report Meta ───────────────────────────────────────
    now = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    story.append(Paragraph(f"Generated on {now}", styles["MetaText"]))
    story.append(Paragraph(f"By {user_name} ({user_role})", styles["MetaText"]))
    story.append(Spacer(1, 12))

    # ─── Dataset Info ──────────────────────────────────────
    story.append(Paragraph("Dataset Information", styles["SectionHeader"]))

    dataset_data = [
        ["File Name", filename],
        ["Total Rows", f"{rows:,}"],
        ["Total Columns", str(columns)],
    ]

    dataset_table = Table(dataset_data, colWidths=[140, 340])
    dataset_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), LIGHT_BG),
        ("TEXTCOLOR", (0, 0), (0, -1), DARK),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (1, 0), (1, -1), MID),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("ALIGN", (1, 0), (1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("ROUNDEDCORNERS", [4, 4, 4, 4]),
    ]))
    story.append(dataset_table)
    story.append(Spacer(1, 16))

    # ─── Question ──────────────────────────────────────────
    story.append(Paragraph("Question Asked", styles["SectionHeader"]))
    story.append(Paragraph(f'"{question}"', styles["QuestionText"]))
    story.append(Spacer(1, 8))

    # ─── AI Insight ────────────────────────────────────────
    story.append(Paragraph("AI Insight", styles["SectionHeader"]))
    story.append(HRFlowable(
        width="100%", thickness=1, color=LIGHT_BG,
        spaceAfter=8, spaceBefore=2
    ))

    # Process the answer — split into paragraphs and clean markdown
    cleaned_answer = clean_markdown(answer)
    paragraphs = cleaned_answer.split("\n")

    for para in paragraphs:
        para = para.strip()
        if not para:
            story.append(Spacer(1, 6))
            continue

        # Check if it's a bullet point
        if para.startswith("- ") or para.startswith("  - "):
            bullet_text = para.lstrip("- ").strip()
            story.append(Paragraph(
                f"  \u2022  {bullet_text}",
                styles["InsightText"]
            ))
        else:
            story.append(Paragraph(para, styles["InsightText"]))

    story.append(Spacer(1, 20))

    # ─── Footer ────────────────────────────────────────────
    story.append(HRFlowable(
        width="100%", thickness=1, color=BORDER,
        spaceAfter=8, spaceBefore=8
    ))
    story.append(Paragraph(
        "This report was generated by InsightCloud — a cloud-native GenAI CSV analytics platform. "
        "The insights are AI-generated based on the uploaded dataset and should be verified before making decisions.",
        styles["FooterText"]
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "Powered by AWS Bedrock | Built with Streamlit | Cloud Product & Platform Engineering",
        styles["FooterText"]
    ))

    # Build the PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()