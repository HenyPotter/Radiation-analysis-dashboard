from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime

from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Image, Paragraph
)
from reportlab.lib.enums import TA_CENTER

order_number = "123456789"
generated_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
title = "Simulace zařízení UIEHTGUWEIFGHS298"

logo_path = "logo.png"

pdfmetrics.registerFont(TTFont('ArialNarrow', 'fonts/arialnarrow.ttf'))
font_basic = "ArialNarrow"

pdfmetrics.registerFont(TTFont('ArialNarrowBold', 'fonts/arialnarrow_bold.ttf'))
font_bold = "ArialNarrowBold"

pdfmetrics.registerFont(TTFont('ArialNarrowBoldItalic', 'fonts/arialnarrow_bolditalic.ttf'))
font_bolditalic = "ArialNarrowBoldItalic"

bold_italic = ParagraphStyle(
    "Cell",
    fontName=font_bolditalic,
    fontSize=14,
    alignment=TA_CENTER,
    textColor=colors.green,
    leading=20,
)

bold_title = ParagraphStyle(
    "Cell",
    fontName=font_bold,
    fontSize=18,
    alignment=TA_CENTER,
    textColor=colors.green,
    leading=24,
)

cell_style = ParagraphStyle(
    "Cell",
    fontName=font_basic,
    fontSize=10,
    alignment=TA_CENTER,
    textColor=colors.green,
    leading=14,
)

doc = SimpleDocTemplate(
    "report_header_stretched.pdf",
    pagesize=A4,
    leftMargin=20*mm, rightMargin=20*mm,
    topMargin=20*mm, bottomMargin=20*mm
)

col_width = 68 * mm

img_reader = ImageReader(logo_path)
orig_width, orig_height = img_reader.getSize()

pixel_to_mm = 25.4 / 72
orig_width_mm = orig_width * pixel_to_mm
orig_height_mm = orig_height * pixel_to_mm

percent_width = 0.40
new_width = col_width * percent_width
new_height = orig_height_mm / orig_width_mm * new_width

logo = Image(logo_path)
logo.drawWidth = new_width
logo.drawHeight = new_height

data = [
    [logo, Paragraph("GRAS SIMULATION SUMMARY ", bold_italic), Paragraph("Order number:<br/>" + order_number, cell_style)],
    ["", Paragraph(title, bold_title), Paragraph("Generated on:<br/>" + generated_date, cell_style)],
]

col_widths = [34 * mm, 102 * mm, 34 * mm]

table = Table(data, colWidths=col_widths)

table.setStyle(TableStyle([
    ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ("SPAN", (0, 0), (0, 1)),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
]))

doc.build([table])
print("PDF generated as report_header_stretched.pdf")
